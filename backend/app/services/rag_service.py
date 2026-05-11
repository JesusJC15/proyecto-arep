from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from uuid import uuid4

from app.core.settings import Settings
from app.repositories.base import Repository
from app.schemas.domain import (
    CorpusChunkRecord,
    CorpusDocumentRecord,
    EvidenceSource,
    RAGStatus,
    RetrievalTrace,
)
from app.services.embeddings import (
    ExternalOpenAICompatibleEmbeddingProvider,
    LocalHashEmbeddingProvider,
    EmbeddingProvider,
    cosine_similarity,
    tokenize_text,
)


RETRIEVAL_VERSION = "rag-v1-hybrid-semantic"


@dataclass
class IndexedChunk:
    chunk_id: str
    document_id: str
    title: str
    source_type: str
    source_uri: str
    clinical_topic: str
    content: str
    vector: list[float]


class RAGService:
    def __init__(self, store: Repository, settings: Settings) -> None:
        self.store = store
        self.settings = settings
        self.root = self._resolve_project_root()
        self.knowledge_base_root = self.root / "knowledge-base"
        self.manifest_path = self.knowledge_base_root / "corpus-manifest.json"
        self.index_artifact_path = (self.root / self.settings.rag_index_artifact_path).resolve()
        self.provider = self._build_provider()
        self.indexed_chunks: list[IndexedChunk] = []
        self.status: RAGStatus | None = None

    def initialize(self, force_reindex: bool = False) -> RAGStatus:
        if force_reindex or not self.index_artifact_path.exists():
            return self.rebuild_index()
        if not self.indexed_chunks:
            artifact = json.loads(self.index_artifact_path.read_text(encoding="utf-8"))
            self.indexed_chunks = [
                IndexedChunk(
                    chunk_id=item["chunk_id"],
                    document_id=item["document_id"],
                    title=item["title"],
                    source_type=item["source_type"],
                    source_uri=item["source_uri"],
                    clinical_topic=item["clinical_topic"],
                    content=item["content"],
                    vector=[float(value) for value in item["vector"]],
                )
                for item in artifact["chunks"]
            ]
        self.status = self.store.get_rag_status()
        if self.status is None:
            return self.rebuild_index()
        return self.status

    def rebuild_index(self) -> RAGStatus:
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        corpus_version = manifest["corpus_version"]
        documents: list[CorpusDocumentRecord] = []
        chunk_records: list[CorpusChunkRecord] = []
        chunk_payloads: list[str] = []
        chunk_metadata: list[dict[str, str]] = []
        for item in manifest["documents"]:
            document_path = (self.knowledge_base_root / item["path"]).resolve()
            content = document_path.read_text(encoding="utf-8").strip()
            record = CorpusDocumentRecord(
                document_id=item["document_id"],
                title=item["title"],
                source_type=item["source_type"],
                source_uri=item["source_uri"],
                clinical_topic=item["clinical_topic"],
                audience=item["audience"],
                publication_or_revision_date=item["publication_or_revision_date"],
                curation_status=item["curation_status"],
                language=item["language"],
                license_or_usage_note=item["license_or_usage_note"],
                summary=item["summary"],
                content=content,
                metadata={"path": item["path"]},
            )
            documents.append(record)
            document_chunks = self._chunk_document(record)
            chunk_records.extend(document_chunks)
            for chunk in document_chunks:
                chunk_payloads.append(f"{record.title}\n{record.summary}\n{chunk.content}")
                chunk_metadata.append(
                    {
                        "chunk_id": chunk.chunk_id,
                        "document_id": chunk.document_id,
                        "title": record.title,
                        "source_type": record.source_type,
                        "source_uri": record.source_uri,
                        "clinical_topic": record.clinical_topic,
                        "content": chunk.content,
                    }
                )

        vectors = self.provider.embed_texts(chunk_payloads)
        self.index_artifact_path.parent.mkdir(parents=True, exist_ok=True)
        artifact_payload = {
            "corpus_version": corpus_version,
            "retrieval_version": RETRIEVAL_VERSION,
            "embedding_provider": self.provider.provider_name,
            "embedding_model": self.provider.model_name,
            "chunks": [
                {
                    **metadata,
                    "vector": vector,
                }
                for metadata, vector in zip(chunk_metadata, vectors)
            ],
        }
        self.index_artifact_path.write_text(json.dumps(artifact_payload, indent=2), encoding="utf-8")
        self.indexed_chunks = [
            IndexedChunk(
                chunk_id=metadata["chunk_id"],
                document_id=metadata["document_id"],
                title=metadata["title"],
                source_type=metadata["source_type"],
                source_uri=metadata["source_uri"],
                clinical_topic=metadata["clinical_topic"],
                content=metadata["content"],
                vector=vector,
            )
            for metadata, vector in zip(chunk_metadata, vectors)
        ]
        self.status = self.store.replace_corpus(
            documents=documents,
            chunks=chunk_records,
            index_version=RETRIEVAL_VERSION,
            index_artifact_path=str(self.index_artifact_path),
            embedding_provider=self.provider.provider_name,
            embedding_model=self.provider.model_name,
            corpus_version=corpus_version,
        )
        return self.status

    def retrieve(self, query_terms: list[str]) -> RetrievalTrace:
        status = self.initialize(force_reindex=self.settings.rag_force_reindex)
        query_text = " ".join(term.strip() for term in query_terms if term.strip())
        query_vector = self.provider.embed_texts([query_text])[0]
        normalized_terms = list(dict.fromkeys(tokenize_text(query_text)))
        scored: list[tuple[float, IndexedChunk, list[str], float, float]] = []
        for chunk in self.indexed_chunks:
            cosine_score = cosine_similarity(query_vector, chunk.vector)
            chunk_terms = set(tokenize_text(chunk.title + " " + chunk.content))
            overlap_terms = sorted(set(normalized_terms) & chunk_terms)
            lexical_score = len(overlap_terms) / max(len(set(normalized_terms)), 1)
            topic_boost = 0.08 if any(term in chunk.clinical_topic.lower() for term in overlap_terms) else 0.0
            final_score = (0.72 * cosine_score) + (0.20 * lexical_score) + topic_boost
            scored.append((final_score, chunk, overlap_terms, cosine_score, lexical_score))
        ranked = sorted(scored, key=lambda item: item[0], reverse=True)[: self.settings.rag_top_k]
        evidence_sources: list[EvidenceSource] = []
        for rank, (score, chunk, overlap_terms, cosine_score, lexical_score) in enumerate(ranked, start=1):
            snippet = chunk.content[:280].strip()
            rationale = (
                f"Recuperado por similitud semantica y solapamiento lexico; "
                f"score_semantico={cosine_score:.3f}, score_lexico={lexical_score:.3f}"
            )
            evidence_sources.append(
                EvidenceSource(
                    id=f"{chunk.chunk_id}-rank-{rank}-{uuid4()}",
                    document_id=chunk.document_id,
                    chunk_id=chunk.chunk_id,
                    title=chunk.title,
                    source_type=chunk.source_type,
                    uri=chunk.source_uri,
                    snippet=snippet,
                    retrieval_score=round(score, 4),
                    rank=rank,
                    retrieval_method=f"{self.provider.provider_name}_hybrid",
                    match_rationale=rationale,
                    matched_terms=overlap_terms,
                )
            )
        return RetrievalTrace(
            query_text=query_text,
            query_terms=normalized_terms,
            retrieval_version=RETRIEVAL_VERSION,
            embedding_provider=self.provider.provider_name,
            embedding_model=self.provider.model_name,
            corpus_version=status.corpus_version,
            index_version=status.index_version,
            top_k=self.settings.rag_top_k,
            candidates_considered=len(self.indexed_chunks),
            evidence_sources=evidence_sources,
        )

    def get_status(self) -> RAGStatus:
        return self.initialize(force_reindex=False)

    def read_source_content(self, source_uri: str) -> str:
        normalized = source_uri.strip().replace("\\", "/")
        if normalized.startswith("knowledge-base/"):
            normalized = normalized.removeprefix("knowledge-base/")
        candidate = (self.knowledge_base_root / normalized).resolve()
        if self.knowledge_base_root not in candidate.parents or not candidate.is_file():
            raise FileNotFoundError(f"Source not found: {source_uri}")
        return candidate.read_text(encoding="utf-8")

    def _build_provider(self) -> EmbeddingProvider:
        if self.settings.rag_embedding_provider == "external_openai_compatible":
            assert self.settings.rag_embedding_api_url is not None
            assert self.settings.rag_embedding_api_key is not None
            return ExternalOpenAICompatibleEmbeddingProvider(
                api_url=self.settings.rag_embedding_api_url,
                api_key=self.settings.rag_embedding_api_key,
                model_name=self.settings.rag_embedding_model,
            )
        return LocalHashEmbeddingProvider(model_name=self.settings.rag_embedding_model)

    def _chunk_document(self, document: CorpusDocumentRecord) -> list[CorpusChunkRecord]:
        words = document.content.split()
        step = max(self.settings.rag_chunk_size - self.settings.rag_chunk_overlap, 1)
        chunks: list[CorpusChunkRecord] = []
        for start in range(0, len(words), step):
            window = words[start : start + self.settings.rag_chunk_size]
            if not window:
                continue
            chunk_index = len(chunks)
            chunk_content = " ".join(window).strip()
            chunks.append(
                CorpusChunkRecord(
                    chunk_id=f"{document.document_id}-chunk-{chunk_index}",
                    document_id=document.document_id,
                    chunk_index=chunk_index,
                    title=document.title,
                    content=chunk_content,
                    token_count=len(window),
                    metadata={
                        "clinical_topic": document.clinical_topic,
                        "audience": document.audience,
                    },
                )
            )
            if start + self.settings.rag_chunk_size >= len(words):
                break
        return chunks

    def _resolve_project_root(self) -> Path:
        current = Path(__file__).resolve()
        for candidate in (current.parent, *current.parents):
            if (candidate / "knowledge-base" / "corpus-manifest.json").exists():
                return candidate
        raise FileNotFoundError(
            "knowledge-base/corpus-manifest.json was not found from the current backend runtime layout"
        )

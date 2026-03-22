from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.schemas.domain import EvidenceSource


@dataclass
class CorpusDocument:
    title: str
    uri: str
    content: str


class RAGService:
    def __init__(self) -> None:
        self.documents = self._load_documents()

    def _load_documents(self) -> list[CorpusDocument]:
        root = Path(__file__).resolve().parents[3] / "knowledge-base" / "clinical-guidelines"
        documents: list[CorpusDocument] = []
        for path in sorted(root.glob("*.md")):
            content = path.read_text(encoding="utf-8")
            title = content.splitlines()[0].lstrip("# ").strip() if content else path.stem
            documents.append(CorpusDocument(title=title, uri=str(path), content=content))
        return documents

    def retrieve(self, query_terms: list[str]) -> list[EvidenceSource]:
        scored: list[tuple[int, CorpusDocument]] = []
        normalized_terms = [term.lower() for term in query_terms if term]
        for document in self.documents:
            haystack = document.content.lower()
            score = sum(1 for term in normalized_terms if term in haystack)
            scored.append((score, document))
        top_documents = [item for item in sorted(scored, key=lambda pair: pair[0], reverse=True)[:3]]
        sources: list[EvidenceSource] = []
        for index, (_, document) in enumerate(top_documents, start=1):
            snippet = " ".join(document.content.splitlines()[2:6]).strip()
            sources.append(
                EvidenceSource(
                    id=f"source-{index}",
                    title=document.title,
                    source_type="markdown",
                    uri=document.uri,
                    snippet=snippet,
                )
            )
        return sources


rag_service = RAGService()

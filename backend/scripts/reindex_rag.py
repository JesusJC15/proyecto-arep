from app.core.settings import load_settings
from app.repositories.sql_repository import SQLRepository
from app.services.rag_service import RAGService


def main() -> None:
    settings = load_settings()
    store = SQLRepository(settings.database_url)
    store.initialize(seed_demo_data=settings.seed_demo_data)
    rag_service = RAGService(store=store, settings=settings)
    status = rag_service.rebuild_index()
    print(
        {
            "corpus_version": status.corpus_version,
            "documents": status.documents,
            "chunks": status.chunks,
            "index_version": status.index_version,
            "index_artifact_path": status.index_artifact_path,
        }
    )
    store.dispose()


if __name__ == "__main__":
    main()

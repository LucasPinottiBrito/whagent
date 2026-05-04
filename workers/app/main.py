from app.core.config import get_settings
from app.services.backend_client import BackendClient
from app.services.conversation_queue import ConversationQueue
from app.workers.conversation_processor import ConversationProcessorWorker


def build_worker() -> ConversationProcessorWorker:
    settings = get_settings()
    queue = ConversationQueue.from_url(
        redis_url=settings.redis_url,
        lock_seconds=settings.conversation_lock_seconds,
        batch_size=settings.worker_batch_size,
    )
    backend_client = BackendClient(
        base_url=settings.backend_internal_api_url,
        internal_api_key=settings.backend_internal_api_key,
    )
    return ConversationProcessorWorker(
        queue=queue,
        backend_client=backend_client,
        poll_interval_seconds=settings.worker_poll_interval_seconds,
    )


def main() -> None:
    build_worker().run_forever()


if __name__ == "__main__":
    main()

from app.core.config import get_settings
from app.core.logging import configure_logging
from app.services.backend_client import BackendClient
from app.services.redis_queue import RedisQueue
from app.worker import ConversationWorker


def main() -> None:
    configure_logging()
    settings = get_settings()
    queue = RedisQueue.from_url(
        redis_url=settings.redis_url,
        lock_seconds=settings.conversation_lock_seconds,
        batch_size=settings.worker_batch_size,
    )
    backend_client = BackendClient(
        base_url=settings.backend_internal_api_url,
        internal_api_key=settings.backend_internal_api_key,
    )
    ConversationWorker(queue=queue, backend_client=backend_client).run_forever(
        poll_interval_seconds=settings.worker_poll_interval_seconds
    )


if __name__ == "__main__":
    main()

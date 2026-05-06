import logging
import time

from app.services.backend_client import BackendClient
from app.services.redis_queue import RedisQueue


logger = logging.getLogger(__name__)


class ConversationWorker:
    def __init__(self, *, queue: RedisQueue, backend_client: BackendClient):
        self.queue = queue
        self.backend_client = backend_client

    def run_forever(self, *, poll_interval_seconds: int) -> None:
        while True:
            self.run_once(now=time.time())
            time.sleep(poll_interval_seconds)

    def run_once(self, *, now: float | None = None) -> None:
        current_time = now if now is not None else time.time()
        for conversation_id in self.queue.ready_conversation_ids(now=current_time):
            token = self.queue.acquire_lock(conversation_id)
            if token is None:
                continue
            try:
                response = self.backend_client.process_conversation(conversation_id)
                if 200 <= response.status_code < 300:
                    self.queue.remove(conversation_id)
                else:
                    logger.error(
                        "backend processing failed for %s: %s %s",
                        conversation_id,
                        response.status_code,
                        getattr(response, "text", ""),
                    )
            except Exception:
                logger.exception("backend processing errored for %s", conversation_id)
            finally:
                self.queue.release_lock(conversation_id, token)

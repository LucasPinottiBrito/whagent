import time

from app.services.backend_client import BackendClient
from app.services.conversation_queue import ConversationQueue


class ConversationProcessorWorker:
    def __init__(
        self,
        *,
        queue: ConversationQueue,
        backend_client: BackendClient,
        poll_interval_seconds: int,
    ):
        self.queue = queue
        self.backend_client = backend_client
        self.poll_interval_seconds = poll_interval_seconds

    def run_forever(self) -> None:
        while True:
            self.run_once()
            time.sleep(self.poll_interval_seconds)

    def run_once(self) -> None:
        now = time.time()
        for conversation_id in self.queue.ready_conversation_ids(now=now):
            if not self.queue.acquire_lock(conversation_id):
                continue
            try:
                response = self.backend_client.process_conversation(conversation_id)
                if 200 <= response.status_code < 300:
                    self.queue.remove(conversation_id)
            finally:
                self.queue.release_lock(conversation_id)

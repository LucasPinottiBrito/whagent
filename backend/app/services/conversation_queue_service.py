import time

try:
    import redis
except ImportError:  # pragma: no cover
    redis = None


QUEUE_KEY = "queue:conversation-processing"


class ConversationQueueService:
    def __init__(self, *, redis_client, debounce_seconds: int, now_func=time.time):
        self.redis = redis_client
        self.debounce_seconds = debounce_seconds
        self.now_func = now_func

    @classmethod
    def from_url(
        cls, *, redis_url: str, debounce_seconds: int
    ) -> "ConversationQueueService":
        if redis is None:
            raise RuntimeError("redis package is not installed")
        client = redis.Redis.from_url(redis_url, decode_responses=True)
        return cls(redis_client=client, debounce_seconds=debounce_seconds)

    def schedule_conversation(self, conversation_id: str) -> float:
        # Debounce: each customer message pushes the same conversation forward.
        process_at = self.now_func() + self.debounce_seconds
        self.redis.zadd(QUEUE_KEY, {conversation_id: process_at})
        self.redis.set(
            f"debounce:conversation:{conversation_id}",
            "1",
            ex=self.debounce_seconds,
        )
        return process_at

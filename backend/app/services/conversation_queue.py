import time

try:
    import redis
except ImportError:  # pragma: no cover - dependency exists in container images
    redis = None


QUEUE_KEY = "queue:conversation-processing"


class ConversationQueue:
    def __init__(self, redis_client, debounce_seconds: int):
        self.redis = redis_client
        self.debounce_seconds = debounce_seconds

    @classmethod
    def from_url(cls, redis_url: str, debounce_seconds: int) -> "ConversationQueue":
        if redis is None:
            raise RuntimeError("redis package is not installed")
        client = redis.Redis.from_url(redis_url, decode_responses=True)
        return cls(redis_client=client, debounce_seconds=debounce_seconds)

    def schedule_conversation(self, conversation_id: str) -> float:
        process_at = time.time() + self.debounce_seconds
        self.redis.zadd(QUEUE_KEY, {conversation_id: process_at})
        self.redis.set(
            f"debounce:conversation:{conversation_id}",
            "1",
            ex=self.debounce_seconds,
        )
        return process_at

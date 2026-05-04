try:
    import redis
except ImportError:  # pragma: no cover - dependency exists in container images
    redis = None


QUEUE_KEY = "queue:conversation-processing"


class ConversationQueue:
    def __init__(self, *, redis_client, lock_seconds: int, batch_size: int):
        self.redis = redis_client
        self.lock_seconds = lock_seconds
        self.batch_size = batch_size

    @classmethod
    def from_url(
        cls, *, redis_url: str, lock_seconds: int, batch_size: int
    ) -> "ConversationQueue":
        if redis is None:
            raise RuntimeError("redis package is not installed")
        client = redis.Redis.from_url(redis_url, decode_responses=True)
        return cls(redis_client=client, lock_seconds=lock_seconds, batch_size=batch_size)

    def ready_conversation_ids(self, *, now: float) -> list[str]:
        return list(
            self.redis.zrangebyscore(
                QUEUE_KEY,
                "-inf",
                now,
                start=0,
                num=self.batch_size,
            )
        )

    def acquire_lock(self, conversation_id: str) -> bool:
        return bool(
            self.redis.set(
                f"lock:conversation:{conversation_id}",
                "1",
                nx=True,
                ex=self.lock_seconds,
            )
        )

    def remove(self, conversation_id: str) -> None:
        self.redis.zrem(QUEUE_KEY, conversation_id)

    def release_lock(self, conversation_id: str) -> None:
        self.redis.delete(f"lock:conversation:{conversation_id}")

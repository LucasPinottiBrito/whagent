from uuid import uuid4

try:
    import redis
except ImportError:  # pragma: no cover
    redis = None


QUEUE_KEY = "queue:conversation-processing"
RELEASE_LOCK_SCRIPT = """
if redis.call("get", KEYS[1]) == ARGV[1] then
  return redis.call("del", KEYS[1])
else
  return 0
end
"""


class RedisQueue:
    def __init__(self, *, redis_client, lock_seconds: int, batch_size: int, token_factory=None):
        self.redis = redis_client
        self.lock_seconds = lock_seconds
        self.batch_size = batch_size
        self.token_factory = token_factory or (lambda: str(uuid4()))

    @classmethod
    def from_url(cls, *, redis_url: str, lock_seconds: int, batch_size: int) -> "RedisQueue":
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

    def acquire_lock(self, conversation_id: str) -> str | None:
        token = self.token_factory()
        acquired = self.redis.set(
            self._lock_key(conversation_id),
            token,
            nx=True,
            ex=self.lock_seconds,
        )
        return token if acquired else None

    def remove(self, conversation_id: str) -> None:
        self.redis.zrem(QUEUE_KEY, conversation_id)

    def release_lock(self, conversation_id: str, token: str) -> bool:
        # Token comparison prevents an old worker from deleting a renewed lock.
        result = self.redis.eval(RELEASE_LOCK_SCRIPT, 1, self._lock_key(conversation_id), token)
        return bool(result)

    def _lock_key(self, conversation_id: str) -> str:
        return f"lock:conversation:{conversation_id}"

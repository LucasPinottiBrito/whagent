from app.services.redis_queue import RedisQueue
from app.worker import ConversationWorker


class FakeRedis:
    def __init__(self):
        self.sorted_sets = {"queue:conversation-processing": {"conv-1": 10}}
        self.values = {}

    def zrangebyscore(self, key, min_score, max_score, start=0, num=10):
        return [
            member
            for member, score in self.sorted_sets.get(key, {}).items()
            if float(score) <= float(max_score)
        ][start : start + num]

    def set(self, key, value, nx=False, ex=None):
        if nx and key in self.values:
            return False
        self.values[key] = value
        return True

    def get(self, key):
        return self.values.get(key)

    def delete(self, key):
        self.values.pop(key, None)

    def zrem(self, key, member):
        self.sorted_sets.get(key, {}).pop(member, None)

    def eval(self, script, numkeys, key, token):
        if self.values.get(key) == token:
            self.delete(key)
            return 1
        return 0


class FakeResponse:
    def __init__(self, status_code):
        self.status_code = status_code
        self.text = ""


class FakeBackendClient:
    def __init__(self, status_code):
        self.status_code = status_code
        self.calls = []

    def process_conversation(self, conversation_id):
        self.calls.append(conversation_id)
        return FakeResponse(self.status_code)


def test_redis_queue_ready_lock_and_safe_unlock():
    redis = FakeRedis()
    queue = RedisQueue(
        redis_client=redis,
        lock_seconds=60,
        batch_size=10,
        token_factory=lambda: "token-1",
    )

    assert queue.ready_conversation_ids(now=15) == ["conv-1"]
    token = queue.acquire_lock("conv-1")
    assert token == "token-1"
    assert queue.acquire_lock("conv-1") is None
    assert queue.release_lock("conv-1", "wrong-token") is False
    assert queue.release_lock("conv-1", "token-1") is True


def test_worker_removes_from_queue_only_on_2xx():
    redis = FakeRedis()
    queue = RedisQueue(
        redis_client=redis,
        lock_seconds=60,
        batch_size=10,
        token_factory=lambda: "token-1",
    )
    backend = FakeBackendClient(200)
    worker = ConversationWorker(queue=queue, backend_client=backend)

    worker.run_once(now=15)

    assert backend.calls == ["conv-1"]
    assert "conv-1" not in redis.sorted_sets["queue:conversation-processing"]


def test_worker_keeps_queue_item_on_backend_error():
    redis = FakeRedis()
    queue = RedisQueue(
        redis_client=redis,
        lock_seconds=60,
        batch_size=10,
        token_factory=lambda: "token-1",
    )
    backend = FakeBackendClient(500)
    worker = ConversationWorker(queue=queue, backend_client=backend)

    worker.run_once(now=15)

    assert backend.calls == ["conv-1"]
    assert "conv-1" in redis.sorted_sets["queue:conversation-processing"]

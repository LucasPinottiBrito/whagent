from app.services.conversation_queue import ConversationQueue


class FakeRedis:
    def __init__(self):
        self.sorted_sets = {}
        self.values = {}

    def zrangebyscore(self, key, min_score, max_score, start=0, num=10):
        items = self.sorted_sets.get(key, {})
        ready = [
            member
            for member, score in items.items()
            if float(score) <= float(max_score)
        ]
        return ready[start : start + num]

    def set(self, key, value, nx=False, ex=None):
        if nx and key in self.values:
            return False
        self.values[key] = value
        return True

    def delete(self, key):
        self.values.pop(key, None)

    def zrem(self, key, member):
        self.sorted_sets.get(key, {}).pop(member, None)


def test_queue_returns_ready_ids_and_lock_prevents_duplicates():
    redis = FakeRedis()
    redis.sorted_sets["queue:conversation-processing"] = {"conv-1": 10, "conv-2": 20}
    queue = ConversationQueue(redis_client=redis, lock_seconds=60, batch_size=10)

    assert queue.ready_conversation_ids(now=15) == ["conv-1"]
    assert queue.acquire_lock("conv-1") is True
    assert queue.acquire_lock("conv-1") is False

    queue.remove("conv-1")
    queue.release_lock("conv-1")

    assert "conv-1" not in redis.sorted_sets["queue:conversation-processing"]
    assert queue.acquire_lock("conv-1") is True

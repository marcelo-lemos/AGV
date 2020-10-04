import heapq
import itertools

REMOVED = '<removed>'

class Heap:
    def __init__(self):
        self.heap = list()
        self.entry_finder = dict()
        self.counter = itertools.count()

    def push(self, item, priority=0):
        if item in self.entry_finder:
            pri = self.entry_finder[item][0]
            if pri > priority:
                self.remove_item(item)
            else:
                return
        count = next(self.counter)
        entry = [priority, count, item]
        self.entry_finder[item] = entry
        heapq.heappush(self.heap, entry)

    def remove_item(self, item):
        entry = self.entry_finder.pop(item)
        entry[-1] = REMOVED

    def pop(self):
        while self.heap:
            priority, count, item = heapq.heappop(self.heap)
            if item is not REMOVED:
                del self.entry_finder[item]
                return item
        return None

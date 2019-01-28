
"""
    A list that can hold a limited amount of items.
    When appending new items if the list is full, the oldest
    items are dropped.
"""
class LimitedList:

    def __init__(self, limit=10):

        self.limit = limit
        self._list = list()

    def push(self, el):

        if len(self._list) < self.limit:
            self._list.append(el)
        else:
            # Drop item 0, append new item
            self._list.pop(0)
            self._list.append(el)

    def length(self):
        return len(self._list)

    def pop(self, ix=None):
        if ix is None:
            ix = 0
        try:
            self._list.pop(ix)
        except:
            raise KeyError("Popping item {} in list of length {}".format(ix, len(self._list)))

    def clear(self):
        self._list = list()

    def set_limit(self, l):
        """ Changes the limit. If reduced, pops elements that don't fit. """
        if l <= 0:
            raise Exception("Can't set LimitedList limit to 0.")
        
        if l < self.limit:
            last_ix = self.limit - l
            self.limit = l
            self._list = self._list[last_ix:]
        else:
            self.limit = l


    def __getitem__(self, ix):
        try:
            return self._list[ix]
        except:
            raise KeyError("Requested index {} in list of length {}.".format(ix, len(self._list)))

    def __setitem__(self, ix, item):
        try:
            self._list[ix] = item
        except Exception as e:
            raise e
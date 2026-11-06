"""
PA 9: The Garbage Collector -- starter.

Complete GCHeap below. See the assignment, Part B,
for the full requirements.

Use gc_heap.py as specified in the assignment and imported by the harness.

Design note: GCHeap.allocate(obj) takes exactly one argument per the
spec, so an allocated object that references OTHER heap handles must
expose them itself for decref's cascade to find -- via a
get_child_handles() -> list[int] method. HeapNode below is a given
example object shaped this way, used by the cyclic-structure test.
"""

from typing import Any, List

class HeapRef:
    def __init__(self, handle: int) -> None:
        self.handle = handle

class HeapNode:
    """
    Given: a minimal heap object whose fields may hold OTHER handles
    (ints). get_child_handles() is what GCHeap.decref's cascade calls
    to find them -- it must reflect the CURRENT field values, not a
    snapshot taken at creation time.
    """

    def __init__(self, **fields: Any) -> None:
        self.fields = fields

    def get_child_handles(self) -> List[int]:
        return [v for v in self.fields.values() if isinstance(v, int)]


class GCHeap:
    def __init__(self) -> None:
        self._objects = {}
        self._next_handle = 1

    def allocate(self, obj: Any) -> int:
        """Store obj, return a new handle. Initial refcount is 1 (the creating reference)."""
        handle = self._next_handle
        self._objects[handle] = (obj, 1)
        self._next_handle += 1
        return handle

    def incref(self, handle: int) -> None:
        obj, count = self._objects[handle]
        self._objects[handle] = (obj, count + 1)

    def decref(self, handle: int) -> None:
        """
        Decrement the refcount. When it hits 0: free the object, AND
        cascade-decref every handle returned by the freed object's
        get_child_handles() (if it has that method), recursively.
        """
        obj, count = self._objects[handle]
        count -= 1

        if count > 0:
            self._objects[handle] = (obj, count)
            return

        del self._objects[handle]

        if hasattr(obj, "get_child_handles"):
            for child_handle in obj.get_child_handles():
                self.decref(child_handle)


    def is_alive(self, handle: int) -> bool:
        return handle in self._objects

    def live_count(self) -> int:
        """Number of currently-alive (refcount > 0) handles."""
        return len(self._objects)

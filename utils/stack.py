from collections import deque
from typing import Any, Optional


class Stack:
    """A limited-size stack implementation using deque."""

    def __init__(self, max_size: int = 20):
        """
        Initialize the stack with an optional maximum size.

        Args:
            max_size (int): Maximum number of items the stack can hold.
                        If None or <= 0, the stack is unbounded.
        """
        if max_size is not None and max_size <= 0:
            max_size = None  # Treat invalid max_size as unbounded
        self._stack = deque(maxlen=max_size)
        self._max_size = max_size

    def push(self, item: Any) -> None:
        """
        Push an item onto the stack.

        Args:
            item: The item to add to the stack.
        """
        self._stack.append(item)

    def pop(self) -> Optional[Any]:
        """
        Pop the last item from the stack.

        Returns:
            The top item, or None if the stack is empty.
        """
        return self._stack.pop() if self._stack else None

    def peek(self) -> Optional[Any]:
        """
        Get the top item without removing it.

        Returns:
            The top item, or None if the stack is empty.
        """
        return self._stack[-1] if self._stack else None

    def is_empty(self) -> bool:
        """
        Check if the stack is empty.

        Returns:
            True if the stack is empty, False otherwise.
        """
        return len(self._stack) == 0

    def size(self) -> int:
        """
        Get the current number of items in the stack.

        Returns:
            The number of items in the stack.
        """
        return len(self._stack)

    def capacity(self) -> Optional[int]:
        """
        Get the maximum capacity of the stack.

        Returns:
            The max size if bounded, or None if unbounded.
        """
        return self._max_size

    def is_full(self) -> bool:
        """
        Check if the stack has reached its maximum capacity.

        Returns:
            True if the stack is full (or unbounded), False otherwise.
        """
        return self._max_size is None or len(self._stack) >= self._max_size

    def clear(self) -> None:
        """Remove all items from the stack."""
        self._stack.clear()

    def __repr__(self) -> str:
        """
        String representation of the stack.

        Returns:
            A string showing the stack contents.
        """
        return f"Stack({list(self._stack)}, max_size={self._max_size})"

    def __len__(self) -> int:
        """
        Support len() function.

        Returns:
            The number of items in the stack.
        """
        return len(self._stack)

    def __bool__(self) -> bool:
        """
        Support truthiness evaluation.

        Returns:
            True if the stack is non-empty, False otherwise.
        """
        return bool(self._stack)
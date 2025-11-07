# src/trie.py
"""
Trie data structure for autocomplete.

Public surface expected by tests:
- class Trie
  - insert(word: str, freq: float) -> None
  - remove(word: str) -> bool
  - contains(word: str) -> bool
  - complete(prefix: str, k: int) -> list[str]
  - stats() -> tuple[int, int, int]  # (words, height, nodes)

Complexity target (justify in docstrings):
- insert/remove/contains: O(len(word))
- complete(prefix, k): roughly O(m + k log k')
"""

class TrieNode:
    __slots__ = ("children", "is_word", "freq")

    def __init__(self):
        self.children = {}
        self.is_word = False
        self.freq = 0.0

class Trie:
    def __init__(self):
        self.root = TrieNode()
        self._words = 0
        self._nodes = 1

    def insert(self, word, freq):
        """
        Insert a word with its frequency into the trie.
        If the word already exists, update its frequency.
        Complexity: O(len(word))
        """
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
                self._nodes += 1
            node = node.children[char]
        if not node.is_word:
            self._words += 1
        node.is_word = True
        node.freq = freq

    def remove(self, word):
        """
        Remove a word from the trie if it exists.
        Clean up unused nodes.
        Complexity: O(len(word))
        """
        def _remove(node, word, index):
            if index == len(word):
                if node.is_word:
                    node.is_word = False
                    self._words -= 1
                    return not node.children  # True if no children, can delete
                return False
            char = word[index]
            if char not in node.children:
                return False
            child = node.children[char]
            should_delete = _remove(child, word, index + 1)
            if should_delete:
                del node.children[char]
                self._nodes -= 1
                return not node.children and not node.is_word
            return False

        return _remove(self.root, word, 0)

    def contains(self, word):
        """
        Check if the word exists in the trie.
        Complexity: O(len(word))
        """
        node = self.root
        for char in word:
            if char not in node.children:
                return False
            node = node.children[char]
        return node.is_word

    def complete(self, prefix, k):
        """
        Return up to k completions for the prefix, ranked by frequency descending,
        then lexicographically ascending.
        Complexity: roughly O(m + k log k') where m is nodes under prefix.
        """
        # Find the node for the prefix
        node = self.root
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]

        # Collect all words under this node
        candidates = []
        def collect(node, path):
            if node.is_word:
                candidates.append((node.freq, path))
            for char in sorted(node.children.keys()):
                collect(node.children[char], path + char)

        collect(node, prefix)

        # Sort by frequency descending, then lexicographically ascending
        candidates.sort(key=lambda x: (-x[0], x[1]))
        return [word for freq, word in candidates[:k]]

    def items(self):
        """
        Return a list of (word, freq) tuples for all words in the trie.
        """
        result = []
        def collect(node, path):
            if node.is_word:
                result.append((path, node.freq))
            for char in sorted(node.children.keys()):
                collect(node.children[char], path + char)
        collect(self.root, "")
        return result

    def stats(self):
        """
        Return (words, height, nodes).
        Height is the maximum depth of the trie.
        """
        def get_height(node):
            if not node.children:
                return 0
            return 1 + max(get_height(child) for child in node.children.values())

        height = get_height(self.root)
        return self._words, height, self._nodes

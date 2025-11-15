from collections import defaultdict
from typing import Dict, List, Optional, Tuple, Any
import pickle
from .play_classifier import PlayType


class TrieNode:
    """Node in the play sequence trie."""

    def __init__(self):
        self.children: Dict[PlayType, TrieNode] = {}
        self.next_play_counts: Dict[PlayType, int] = defaultdict(int)
        self.total_visits: int = 0
        self.epa_sum: float = 0.0
        self.epa_count: int = 0

    def get_avg_epa(self) -> float:
        """Calculate average EPA from this node."""
        return self.epa_sum / self.epa_count if self.epa_count > 0 else 0.0

    def get_next_play_probs(self, k: int = 5) -> Dict[PlayType, float]:
        """
        Get top k most likely next plays.

        Returns:
            Dictionary mapping PlayType to probability
        """
        if self.total_visits == 0:
            return {}

        sorted_plays = sorted(
            self.next_play_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:k]

        return {
            play_type: count / self.total_visits
            for play_type, count in sorted_plays
        }


class PlaySequenceTrie:
    """
    Trie data structure for storing and predicting NFL play sequences.

    Time Complexity:
        - insert_sequence: O(k) where k is sequence length
        - predict: O(k) for lookup + O(1) for probability calculation

    Space Complexity:
        - O(n * k) where n is number of sequences, k is avg length
    """

    def __init__(self, max_depth: int = 10):
        self.root = TrieNode()
        self.max_depth = max_depth
        self.total_sequences = 0

    def insert_sequence(self, play_types: List[PlayType], epas: Optional[List[float]] = None):
        """
        Insert a sequence of plays into the trie.

        Args:
            play_types: List of encoded play types
            epas: Optional list of EPA values for each play
        """
        if len(play_types) == 0:
            return

        for start_idx in range(len(play_types)):
            current = self.root

            for i in range(start_idx, min(start_idx + self.max_depth, len(play_types))):
                play_type = play_types[i]

                if play_type not in current.children:
                    current.children[play_type] = TrieNode()

                current = current.children[play_type]
                current.total_visits += 1

                if epas and i < len(epas):
                    current.epa_sum += epas[i]
                    current.epa_count += 1

                if i + 1 < len(play_types):
                    next_play = play_types[i + 1]
                    current.next_play_counts[next_play] += 1

        self.total_sequences += 1

    def predict(
        self,
        recent_plays: List[PlayType],
        k: int = 5
    ) -> Tuple[Dict[PlayType, float], int]:
        """
        Predict next k most likely plays given recent sequence.

        Args:
            recent_plays: Recent play sequence (most recent last)
            k: Number of predictions to return

        Returns:
            Tuple of (predictions dict, sequence_depth_matched)
        """
        current = self.root
        depth_matched = 0

        for play_type in recent_plays[-self.max_depth:]:
            if play_type in current.children:
                current = current.children[play_type]
                depth_matched += 1
            else:
                break

        predictions = current.get_next_play_probs(k)

        return predictions, depth_matched

    def get_statistics(self) -> Dict[str, Any]:
        """Return statistics about the trie."""
        return {
            'total_sequences': self.total_sequences,
            'max_depth': self.max_depth,
            'num_nodes': self._count_nodes(self.root),
            'avg_branching_factor': self._avg_branching_factor(self.root)
        }

    def _count_nodes(self, node: TrieNode) -> int:
        """Recursively count nodes."""
        count = 1
        for child in node.children.values():
            count += self._count_nodes(child)
        return count

    def _avg_branching_factor(self, node: TrieNode) -> float:
        """Calculate average branching factor."""
        total_children = 0
        total_nodes = 0

        def traverse(n):
            nonlocal total_children, total_nodes
            total_nodes += 1
            total_children += len(n.children)
            for child in n.children.values():
                traverse(child)

        traverse(node)
        return total_children / total_nodes if total_nodes > 0 else 0

    def save(self, filepath: str):
        """Save trie to disk."""
        with open(filepath, 'wb') as f:
            pickle.dump(self, f)

    @staticmethod
    def load(filepath: str) -> 'PlaySequenceTrie':
        """Load trie from disk."""
        with open(filepath, 'rb') as f:
            return pickle.load(f)

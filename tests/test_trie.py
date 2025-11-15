import pytest
import time
from src.models.play_trie import PlaySequenceTrie, TrieNode
from src.models.play_classifier import PlayType


def test_insert_and_predict():
    """Test basic insert and predict functionality."""
    trie = PlaySequenceTrie(max_depth=5)

    sequence = [PlayType('P_1_long_own'), PlayType('R_2_med_own'), PlayType('P_3_short_own')]
    trie.insert_sequence(sequence)

    predictions, depth = trie.predict([PlayType('P_1_long_own'), PlayType('R_2_med_own')])

    assert depth == 2
    assert PlayType('P_3_short_own') in predictions
    assert predictions[PlayType('P_3_short_own')] == 1.0


def test_multiple_sequences():
    """Test prediction probabilities with multiple sequences."""
    trie = PlaySequenceTrie(max_depth=5)

    seq1 = [PlayType('P'), PlayType('R'), PlayType('P')]
    seq2 = [PlayType('P'), PlayType('R'), PlayType('P')]
    trie.insert_sequence(seq1)
    trie.insert_sequence(seq2)

    seq3 = [PlayType('P'), PlayType('R'), PlayType('R')]
    trie.insert_sequence(seq3)

    predictions, _ = trie.predict([PlayType('P'), PlayType('R')])

    assert abs(predictions[PlayType('P')] - 2/3) < 0.01
    assert abs(predictions[PlayType('R')] - 1/3) < 0.01


def test_backoff():
    """Test that trie backs off to shorter sequences when full match not found."""
    trie = PlaySequenceTrie(max_depth=5)

    trie.insert_sequence([PlayType('P'), PlayType('R'), PlayType('X')])
    trie.insert_sequence([PlayType('P'), PlayType('Y')])

    predictions, depth = trie.predict([PlayType('P'), PlayType('Q')])

    assert depth == 1
    assert len(predictions) > 0


def test_empty_trie():
    """Test prediction on empty trie."""
    trie = PlaySequenceTrie(max_depth=5)

    predictions, depth = trie.predict([PlayType('P'), PlayType('R')])

    assert depth == 0
    assert len(predictions) == 0


def test_max_depth():
    """Test that max_depth is respected."""
    trie = PlaySequenceTrie(max_depth=3)

    sequence = [PlayType('A'), PlayType('B'), PlayType('C'), PlayType('D'), PlayType('E')]
    trie.insert_sequence(sequence)

    long_query = [PlayType('A'), PlayType('B'), PlayType('C'), PlayType('D')]
    predictions, depth = trie.predict(long_query)

    assert depth <= 3


def test_top_k_predictions():
    """Test that only top k predictions are returned."""
    trie = PlaySequenceTrie(max_depth=5)

    trie.insert_sequence([PlayType('P'), PlayType('A')])
    trie.insert_sequence([PlayType('P'), PlayType('B')])
    trie.insert_sequence([PlayType('P'), PlayType('C')])
    trie.insert_sequence([PlayType('P'), PlayType('D')])
    trie.insert_sequence([PlayType('P'), PlayType('E')])
    trie.insert_sequence([PlayType('P'), PlayType('F')])

    predictions, _ = trie.predict([PlayType('P')], k=3)

    assert len(predictions) == 3


def test_epa_tracking():
    """Test that EPA values are tracked correctly."""
    trie = PlaySequenceTrie(max_depth=5)

    sequence = [PlayType('P'), PlayType('R')]
    epas = [2.5, -1.0]
    trie.insert_sequence(sequence, epas)

    current = trie.root.children[PlayType('P')]
    assert current.epa_count == 1
    assert current.epa_sum == 2.5
    assert current.get_avg_epa() == 2.5


def test_statistics():
    """Test that trie statistics are calculated correctly."""
    trie = PlaySequenceTrie(max_depth=5)

    trie.insert_sequence([PlayType('P'), PlayType('R'), PlayType('P')])
    trie.insert_sequence([PlayType('P'), PlayType('R'), PlayType('R')])

    stats = trie.get_statistics()

    assert stats['total_sequences'] == 2
    assert stats['max_depth'] == 5
    assert stats['num_nodes'] > 0
    assert stats['avg_branching_factor'] >= 0


def test_node_visits():
    """Test that node visits are counted correctly."""
    trie = PlaySequenceTrie(max_depth=5)

    trie.insert_sequence([PlayType('P'), PlayType('R')])
    trie.insert_sequence([PlayType('P'), PlayType('R')])
    trie.insert_sequence([PlayType('P'), PlayType('P')])

    p_node = trie.root.children[PlayType('P')]
    assert p_node.total_visits == 4


def test_complexity_validation():
    """Verify O(k) time complexity for predictions."""
    trie = PlaySequenceTrie(max_depth=10)

    for i in range(10000):
        seq = [PlayType(f'P_{j}') for j in range(10)]
        trie.insert_sequence(seq)

    query = [PlayType(f'P_{j}') for j in range(5)]

    start = time.time()
    for _ in range(1000):
        trie.predict(query)
    elapsed = time.time() - start

    assert elapsed < 1.0


def test_save_and_load(tmp_path):
    """Test saving and loading trie from disk."""
    trie = PlaySequenceTrie(max_depth=5)
    trie.insert_sequence([PlayType('P'), PlayType('R'), PlayType('P')])

    filepath = tmp_path / "test_trie.pkl"
    trie.save(str(filepath))

    loaded_trie = PlaySequenceTrie.load(str(filepath))

    predictions, depth = loaded_trie.predict([PlayType('P'), PlayType('R')])
    assert PlayType('P') in predictions
    assert depth == 2

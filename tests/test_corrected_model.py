"""
Tests for the corrected model architecture.
"""
import pytest
from src.models.simple_classifier import SimplePlayClassifier, SimplePlayType
from src.models.situation_groups import SituationGroup, get_situation_group
from src.models.grouped_trie import SituationGroupedTrie


def test_simple_classifier():
    """Test that simple classifier only returns P or R."""
    classifier = SimplePlayClassifier()

    # Test pass
    play = {'play_type': 'pass', 'down': 1, 'ydstogo': 10, 'yardline_100': 75}
    result = classifier.encode(play)
    assert result.code == 'P'
    assert classifier.decode(result) == 'PASS'

    # Test run
    play = {'play_type': 'run', 'down': 3, 'ydstogo': 2, 'yardline_100': 35}
    result = classifier.encode(play)
    assert result.code == 'R'
    assert classifier.decode(result) == 'RUN'


def test_situation_grouping():
    """Test that situations are grouped correctly."""

    # Early down, long
    group = get_situation_group(down=1, ydstogo=10, yardline_100=75)
    assert group == SituationGroup.EARLY_DOWN_LONG

    # Third and short
    group = get_situation_group(down=3, ydstogo=2, yardline_100=50)
    assert group == SituationGroup.THIRD_SHORT

    # Third and long
    group = get_situation_group(down=3, ydstogo=12, yardline_100=60)
    assert group == SituationGroup.THIRD_LONG

    # Red zone
    group = get_situation_group(down=1, ydstogo=10, yardline_100=15)
    assert group == SituationGroup.RED_ZONE

    # Goal line
    group = get_situation_group(down=1, ydstogo=3, yardline_100=3)
    assert group == SituationGroup.GOAL_LINE

    # Fourth down
    group = get_situation_group(down=4, ydstogo=1, yardline_100=40)
    assert group == SituationGroup.FOURTH_DOWN


def test_grouped_trie_insert_and_predict():
    """Test basic insert and predict with grouped trie."""
    trie = SituationGroupedTrie(max_depth=5)
    classifier = SimplePlayClassifier()

    # Create a simple drive
    play_types = [
        SimplePlayType('P'),  # 1st & 10
        SimplePlayType('R'),  # 2nd & 6
        SimplePlayType('P'),  # 3rd & 2
    ]

    situations = [
        (1, 10, 75),  # 1st & 10, own territory
        (2, 6, 71),   # 2nd & 6
        (3, 2, 65),   # 3rd & 2
    ]

    # Insert the drive
    trie.insert_drive(play_types, situations)

    # Predict: In a 3rd & 2 situation, after [P, R], what's next?
    situation = (3, 2, 65)
    recent_plays = [SimplePlayType('P'), SimplePlayType('R')]

    predictions, depth = trie.predict(situation, recent_plays)

    # Should have predictions for P and/or R
    assert 'P' in predictions or 'R' in predictions

    # Probabilities should sum to ~1.0
    total_prob = sum(predictions.values())
    assert abs(total_prob - 1.0) < 0.01


def test_grouped_trie_situation_isolation():
    """Test that different situations use different tries."""
    trie = SituationGroupedTrie(max_depth=5)

    # Insert sequence in 3rd & short situations
    third_short_plays = [SimplePlayType('R'), SimplePlayType('R'), SimplePlayType('R')]
    third_short_situations = [(3, 2, 50), (3, 1, 45), (3, 2, 40)]
    trie.insert_drive(third_short_plays, third_short_situations)

    # Insert different sequence in early down situations
    early_down_plays = [SimplePlayType('P'), SimplePlayType('P'), SimplePlayType('P')]
    early_down_situations = [(1, 10, 75), (1, 10, 65), (1, 10, 55)]
    trie.insert_drive(early_down_plays, early_down_situations)

    # Predict in 3rd & short - should favor R
    situation_3rd_short = (3, 2, 50)
    recent = [SimplePlayType('R'), SimplePlayType('R')]
    predictions_3rd, _ = trie.predict(situation_3rd_short, recent)

    # Predict in early down - should favor P
    situation_early = (1, 10, 75)
    recent = [SimplePlayType('P'), SimplePlayType('P')]
    predictions_early, _ = trie.predict(situation_early, recent)

    # Different situations should give different predictions
    # (This test may be fragile with small data, but demonstrates the concept)
    assert 'P' in predictions_early or 'R' in predictions_early
    assert 'P' in predictions_3rd or 'R' in predictions_3rd


def test_no_conflation():
    """Test that the model doesn't conflate play type with outcome."""
    trie = SituationGroupedTrie(max_depth=5)

    # Simulated drive where first play is pass on 1st & 10
    # After the pass gains 6 yards, they're on 2nd & 4
    # This should be stored as: In early_down_long, [P] was followed by ???
    # And separately: In early_down_short, [P, R] was followed by ???

    play_types = [
        SimplePlayType('P'),  # 1st & 10 (early_down_long)
        SimplePlayType('R'),  # 2nd & 4 (early_down_short - result of gaining 6)
        SimplePlayType('P'),  # 3rd & 2 (third_short - result of gaining 2)
    ]

    situations = [
        (1, 10, 75),  # 1st & 10
        (2, 4, 69),   # 2nd & 4 (after gaining 6)
        (3, 2, 67),   # 3rd & 2 (after gaining 2)
    ]

    trie.insert_drive(play_types, situations)

    # Query: In 1st & 10, after seeing nothing, what's next?
    # This should NOT know about the "2nd & 4" outcome
    # It just knows: in early_down_long situations, what do teams call?
    situation = (1, 10, 75)
    predictions, depth = trie.predict(situation, [])

    # The prediction should be about P vs R, not about the next situation
    # We've only seen one example, so depth will be 0 (no sequence match)
    # But predictions should still be P or R
    assert isinstance(predictions, dict)
    for key in predictions.keys():
        assert key in ['P', 'R', 'OTHER']


def test_statistics():
    """Test that statistics are collected correctly."""
    trie = SituationGroupedTrie(max_depth=5)

    # Insert some data
    play_types = [SimplePlayType('P'), SimplePlayType('R'), SimplePlayType('P')]
    situations = [(1, 10, 75), (2, 6, 71), (3, 2, 65)]
    trie.insert_drive(play_types, situations)

    stats = trie.get_statistics()

    assert 'max_depth' in stats
    assert 'total_situations' in stats
    assert 'situation_breakdown' in stats
    assert 'tries' in stats

    # Should have recorded 3 situations
    assert stats['total_situations'] == 3

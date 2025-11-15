import pytest
from src.models.play_classifier import PlayClassifier, PlayType


def test_pass_encoding():
    classifier = PlayClassifier()
    play = {
        'play_type': 'pass',
        'down': 1,
        'ydstogo': 10,
        'yardline_100': 75
    }
    result = classifier.encode(play)
    assert result.code == 'P_1_long_own'


def test_run_encoding():
    classifier = PlayClassifier()
    play = {
        'play_type': 'run',
        'down': 3,
        'ydstogo': 2,
        'yardline_100': 35
    }
    result = classifier.encode(play)
    assert result.code == 'R_3_short_opp'


def test_special_teams():
    classifier = PlayClassifier()
    play = {
        'play_type': 'punt',
        'down': 4,
        'ydstogo': 10,
        'yardline_100': 50
    }
    result = classifier.encode(play)
    assert result.code == 'SPECIAL'


def test_distance_categories():
    """Test that distance categories are correct."""
    classifier = PlayClassifier()

    short_play = {
        'play_type': 'pass',
        'down': 2,
        'ydstogo': 3,
        'yardline_100': 40
    }
    assert classifier.encode(short_play).code == 'P_2_short_opp'

    med_play = {
        'play_type': 'run',
        'down': 2,
        'ydstogo': 5,
        'yardline_100': 40
    }
    assert classifier.encode(med_play).code == 'R_2_med_opp'

    long_play = {
        'play_type': 'pass',
        'down': 1,
        'ydstogo': 15,
        'yardline_100': 80
    }
    assert classifier.encode(long_play).code == 'P_1_long_own'


def test_field_position():
    """Test that field position is correctly categorized."""
    classifier = PlayClassifier()

    own_territory = {
        'play_type': 'pass',
        'down': 1,
        'ydstogo': 10,
        'yardline_100': 75
    }
    assert classifier.encode(own_territory).code == 'P_1_long_own'

    opp_territory = {
        'play_type': 'pass',
        'down': 1,
        'ydstogo': 10,
        'yardline_100': 25
    }
    assert classifier.encode(opp_territory).code == 'P_1_long_opp'

    midfield = {
        'play_type': 'pass',
        'down': 1,
        'ydstogo': 10,
        'yardline_100': 50
    }
    assert classifier.encode(midfield).code == 'P_1_long_opp'


def test_playtype_equality():
    """Test PlayType equality and hashing."""
    pt1 = PlayType('P_1_long_own')
    pt2 = PlayType('P_1_long_own')
    pt3 = PlayType('R_1_long_own')

    assert pt1 == pt2
    assert pt1 != pt3
    assert hash(pt1) == hash(pt2)
    assert hash(pt1) != hash(pt3)


def test_playtype_hashable():
    """Test that PlayType can be used in sets and dicts."""
    pt1 = PlayType('P_1_long_own')
    pt2 = PlayType('P_1_long_own')
    pt3 = PlayType('R_1_long_own')

    play_set = {pt1, pt2, pt3}
    assert len(play_set) == 2

    play_dict = {pt1: 1, pt2: 2, pt3: 3}
    assert len(play_dict) == 2
    assert play_dict[pt1] == 2

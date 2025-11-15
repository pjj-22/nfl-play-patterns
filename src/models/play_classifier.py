from dataclasses import dataclass
from typing import Dict, Any
import pandas as pd


@dataclass
class PlayType:
    """Represents an encoded play type."""
    code: str

    def __hash__(self):
        return hash(self.code)

    def __eq__(self, other):
        if not isinstance(other, PlayType):
            return False
        return self.code == other.code

    def __repr__(self):
        return f"PlayType({self.code})"


class PlayClassifier:
    """
    Encodes NFL plays into discrete types for trie storage.

    Encoding scheme: {P|R}_{down}_{short|med|long}_{own|opp}

    Examples:
        P_1_long_own: Pass on 1st down, long distance, own territory
        R_3_short_opp: Run on 3rd down, short distance, opponent territory
    """

    def __init__(self):
        self.encoding_map = {}
        self.decode_map = {}

    def encode(self, play: Dict[str, Any]) -> PlayType:
        """
        Encode a play into a PlayType.

        Args:
            play: Dictionary with keys: play_type, down, ydstogo, yardline_100

        Returns:
            PlayType object
        """
        if play['play_type'] not in ['pass', 'run']:
            return PlayType('SPECIAL')

        play_char = 'P' if play['play_type'] == 'pass' else 'R'
        down = int(play['down'])

        distance = play['ydstogo']
        if distance <= 3:
            dist_cat = 'short'
        elif distance <= 7:
            dist_cat = 'med'
        else:
            dist_cat = 'long'

        yardline = play['yardline_100']
        field_cat = 'own' if yardline > 50 else 'opp'

        code = f"{play_char}_{down}_{dist_cat}_{field_cat}"
        return PlayType(code)

    def encode_series(self, plays: pd.DataFrame) -> list:
        """Encode a series of plays."""
        return [self.encode(play) for _, play in plays.iterrows()]

    def get_vocabulary_size(self) -> int:
        """Return number of unique play types seen."""
        return len(self.encoding_map)

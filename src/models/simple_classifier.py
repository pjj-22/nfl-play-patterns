from dataclasses import dataclass
from typing import Dict, Any, List
import pandas as pd


@dataclass
class SimplePlayType:
    """Represents a play type (Pass or Run only)."""
    code: str  # 'P' or 'R'

    def __hash__(self):
        return hash(self.code)

    def __eq__(self, other):
        if not isinstance(other, SimplePlayType):
            return False
        return self.code == other.code

    def __repr__(self):
        return f"SimplePlayType({self.code})"


class SimplePlayClassifier:
    """Encodes plays as Pass (P) or Run (R)."""

    def encode(self, play: Dict[str, Any]) -> SimplePlayType:
        """
        Args:
            play: Dictionary with key 'play_type' ('pass' or 'run')
        """
        if play['play_type'] == 'pass':
            return SimplePlayType('P')
        elif play['play_type'] == 'run':
            return SimplePlayType('R')
        else:
            # Special teams, penalties, etc.
            return SimplePlayType('OTHER')

    def encode_series(self, plays: pd.DataFrame) -> List[SimplePlayType]:
        return [self.encode(play) for _, play in plays.iterrows()]

    def decode(self, play_type: SimplePlayType) -> str:
        if play_type.code == 'P':
            return 'PASS'
        elif play_type.code == 'R':
            return 'RUN'
        else:
            return 'OTHER'

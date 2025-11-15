"""
Simplified play classifier for corrected architecture.

Only encodes play TYPE (Pass or Run), not the game situation.
Game situations are handled separately to avoid conflating
decisions with outcomes.
"""
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
    """
    Encodes plays as just Pass (P) or Run (R).

    This is the corrected classifier that separates play TYPE
    from game SITUATION, avoiding the architectural flaw.
    """

    def encode(self, play: Dict[str, Any]) -> SimplePlayType:
        """
        Encode a play into Pass or Run only.

        Args:
            play: Dictionary with key 'play_type' ('pass' or 'run')

        Returns:
            SimplePlayType('P') or SimplePlayType('R')
        """
        if play['play_type'] == 'pass':
            return SimplePlayType('P')
        elif play['play_type'] == 'run':
            return SimplePlayType('R')
        else:
            # Special teams, penalties, etc.
            return SimplePlayType('OTHER')

    def encode_series(self, plays: pd.DataFrame) -> List[SimplePlayType]:
        """Encode a series of plays."""
        return [self.encode(play) for _, play in plays.iterrows()]

    def decode(self, play_type: SimplePlayType) -> str:
        """Convert SimplePlayType back to readable name."""
        if play_type.code == 'P':
            return 'PASS'
        elif play_type.code == 'R':
            return 'RUN'
        else:
            return 'OTHER'

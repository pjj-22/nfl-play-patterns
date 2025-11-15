"""
Situation-Grouped Trie for corrected play prediction.

Uses multiple tries (one per situation group) to predict play types
without conflating decisions with outcomes.
"""
from collections import defaultdict
from typing import Dict, List, Tuple, Optional, Any, Union
import pickle
from .play_trie import PlaySequenceTrie
from .simple_classifier import SimplePlayType
from .situation_groups import (
    SituationGroup,
    get_situation_group,
    get_score_aware_situation,
    get_team_identity_situation,
    get_combined_situation,
    get_phase1_situation
)


class SituationGroupedTrie:
    """
    Collection of tries grouped by game situation.

    Architecture:
        - Separate trie for each situation group (3rd & short, red zone, etc.)
        - Each trie stores sequences of play TYPES only (P, R)
        - No conflation of play decisions with game outcomes

    Usage:
        # Training
        trie = SituationGroupedTrie()
        for drive in drives:
            trie.insert_drive(play_types, situations)

        # Prediction
        predictions = trie.predict(current_situation, recent_play_types)
        # Returns: {'P': 0.65, 'R': 0.35}
    """

    def __init__(
        self,
        max_depth: int = 8,
        use_score: bool = False,
        features: Optional[List[str]] = None,
        use_hierarchical_fallback: bool = True,
        min_examples_threshold: int = 50
    ):
        """
        Initialize grouped trie.

        Args:
            max_depth: Maximum sequence depth for each sub-trie
            use_score: Whether to use score-aware situation groups (deprecated, use features)
            features: List of features to use (e.g., ['score', 'team_identity'])
                     If None and use_score=True, defaults to ['score']
            use_hierarchical_fallback: Whether to fall back to simpler contexts when data is sparse
            min_examples_threshold: Minimum training examples required to trust a situation group
        """
        self.max_depth = max_depth
        self.use_hierarchical_fallback = use_hierarchical_fallback
        self.min_examples_threshold = min_examples_threshold

        # Handle backward compatibility with use_score parameter
        if features is None:
            if use_score:
                self.features = ['score']
            else:
                self.features = []
        else:
            self.features = features

        # Convenience flags
        self.use_score = 'score' in self.features
        self.use_team_identity = 'team_identity' in self.features
        self.use_time_remaining = 'time_remaining' in self.features
        self.use_home_away = 'home_away' in self.features

        self.tries: Dict[Union[SituationGroup, str], PlaySequenceTrie] = {}
        self.situation_counts: Dict[Union[SituationGroup, str], int] = defaultdict(int)

        # Fallback statistics (for analysis)
        self.fallback_stats: Dict[str, int] = defaultdict(int)

        # League-wide average (computed during training or set manually)
        self.league_average: Dict[str, float] = {'P': 0.58, 'R': 0.42}

        if not self.features:
            for group in SituationGroup:
                self.tries[group] = PlaySequenceTrie(max_depth=max_depth)

    def insert_drive(
        self,
        play_types: List[SimplePlayType],
        situations: List[Tuple[int, int, int]],
        epas: Optional[List[float]] = None,
        score_diffs: Optional[List[float]] = None,
        team_pass_rates: Optional[List[float]] = None,
        game_seconds_remaining: Optional[List[float]] = None,
        posteam_types: Optional[List[str]] = None
    ):
        """
        Insert a drive into the appropriate situation-specific tries.

        Args:
            play_types: List of SimplePlayType (P or R)
            situations: List of (down, ydstogo, yardline_100) tuples
            epas: Optional EPA values for each play
            score_diffs: Optional score differentials for each play (for score-aware grouping)
            team_pass_rates: Optional team pass rates for each play (for team identity grouping)
            game_seconds_remaining: Optional game seconds remaining for each play (for time context)
            posteam_types: Optional home/away for each play (for home/away context)
        """
        if len(play_types) != len(situations):
            raise ValueError("play_types and situations must have same length")

        if self.use_score and score_diffs is not None and len(score_diffs) != len(situations):
            raise ValueError("score_diffs must match situations length when using score-aware grouping")

        if self.use_team_identity and team_pass_rates is not None and len(team_pass_rates) != len(situations):
            raise ValueError("team_pass_rates must match situations length when using team identity grouping")

        if self.use_time_remaining and game_seconds_remaining is not None and len(game_seconds_remaining) != len(situations):
            raise ValueError("game_seconds_remaining must match situations length when using time context")

        if self.use_home_away and posteam_types is not None and len(posteam_types) != len(situations):
            raise ValueError("posteam_types must match situations length when using home/away context")

        for i in range(len(play_types)):
            down, ydstogo, yardline_100 = situations[i]

            if self.use_time_remaining and self.use_home_away:
                if game_seconds_remaining is not None and posteam_types is not None:
                    situation_group = get_phase1_situation(
                        down, ydstogo, yardline_100,
                        game_seconds_remaining[i], posteam_types[i]
                    )
                else:
                    situation_group = get_situation_group(down, ydstogo, yardline_100)
            elif self.use_score and self.use_team_identity:
                if score_diffs is not None and team_pass_rates is not None:
                    situation_group = get_combined_situation(
                        down, ydstogo, yardline_100,
                        score_diffs[i], team_pass_rates[i]
                    )
                else:
                    situation_group = get_situation_group(down, ydstogo, yardline_100)
            elif self.use_score:
                if score_diffs is not None:
                    situation_group = get_score_aware_situation(down, ydstogo, yardline_100, score_diffs[i])
                else:
                    situation_group = get_situation_group(down, ydstogo, yardline_100)
            elif self.use_team_identity:
                if team_pass_rates is not None:
                    situation_group = get_team_identity_situation(down, ydstogo, yardline_100, team_pass_rates[i])
                else:
                    situation_group = get_situation_group(down, ydstogo, yardline_100)
            else:
                situation_group = get_situation_group(down, ydstogo, yardline_100)

            start_idx = max(0, i - self.max_depth)
            recent_plays = play_types[start_idx:i+1]

            recent_epas = None
            if epas:
                recent_epas = epas[start_idx:i+1]

            if situation_group not in self.tries:
                self.tries[situation_group] = PlaySequenceTrie(max_depth=self.max_depth)

            self.tries[situation_group].insert_sequence(recent_plays, recent_epas)
            self.situation_counts[situation_group] += 1

            if self.features and self.use_hierarchical_fallback:
                base_situation = get_situation_group(down, ydstogo, yardline_100)
                if base_situation not in self.tries:
                    self.tries[base_situation] = PlaySequenceTrie(max_depth=self.max_depth)
                self.tries[base_situation].insert_sequence(recent_plays, recent_epas)
                self.situation_counts[base_situation] += 1

    def _has_sufficient_data(self, situation_group: Union[SituationGroup, str]) -> bool:
        """
        Check if a situation group has enough training examples to be reliable.

        Args:
            situation_group: Situation group key

        Returns:
            True if group has >= min_examples_threshold examples
        """
        count = self.situation_counts.get(situation_group, 0)
        return count >= self.min_examples_threshold

    def _get_base_situation(self, down: int, ydstogo: int, yardline_100: int) -> SituationGroup:
        """Get the base situation group without any features."""
        return get_situation_group(down, ydstogo, yardline_100)

    def predict(
        self,
        situation: Tuple[int, int, int],
        recent_play_types: List[SimplePlayType],
        k: int = 5,
        score_diff: Optional[float] = None,
        team_pass_rate: Optional[float] = None,
        game_seconds_remaining: Optional[float] = None,
        posteam_type: Optional[str] = None
    ) -> Tuple[Dict[str, float], int]:
        """
        Predict next play type given situation and recent plays.

        Uses hierarchical fallback:
        1. Try specific context (with all features)
        2. Fall back to base situation (no features)
        3. Fall back to league average

        Args:
            situation: Tuple of (down, ydstogo, yardline_100)
            recent_play_types: Recent play sequence (P, R, P, ...)
            k: Number of predictions to return (unused, kept for compatibility)
            score_diff: Optional score differential (for score-aware grouping)
            team_pass_rate: Optional team pass rate (for team identity grouping)
            game_seconds_remaining: Optional game seconds remaining (for time context)
            posteam_type: Optional home/away (for home/away context)

        Returns:
            Tuple of (predictions dict, sequence_depth_matched)
            predictions: {'P': 0.65, 'R': 0.35}
            depth: How many recent plays were matched
        """
        down, ydstogo, yardline_100 = situation

        specific_group = self._get_specific_situation_group(
            down, ydstogo, yardline_100,
            score_diff, team_pass_rate,
            game_seconds_remaining, posteam_type
        )

        if self.use_hierarchical_fallback:
            if specific_group in self.tries and self._has_sufficient_data(specific_group):
                trie_predictions, depth = self.tries[specific_group].predict(recent_play_types, k=10)
                aggregated = self._aggregate_predictions(trie_predictions)
                if aggregated:
                    self.fallback_stats['level_1_specific'] += 1
                    return aggregated, depth

            base_group = self._get_base_situation(down, ydstogo, yardline_100)
            if base_group in self.tries and self._has_sufficient_data(base_group):
                trie_predictions, depth = self.tries[base_group].predict(recent_play_types, k=10)
                aggregated = self._aggregate_predictions(trie_predictions)
                if aggregated:
                    self.fallback_stats['level_2_base'] += 1
                    return aggregated, depth

            self.fallback_stats['level_3_league'] += 1
            return self.league_average.copy(), 0
        else:
            if specific_group not in self.tries:
                return {}, 0

            trie_predictions, depth = self.tries[specific_group].predict(recent_play_types, k=10)
            aggregated = self._aggregate_predictions(trie_predictions)
            return aggregated, depth

    def _get_specific_situation_group(
        self,
        down: int,
        ydstogo: int,
        yardline_100: int,
        score_diff: Optional[float],
        team_pass_rate: Optional[float],
        game_seconds_remaining: Optional[float],
        posteam_type: Optional[str]
    ) -> Union[SituationGroup, str]:
        """
        Determine the most specific situation group based on active features.

        Args:
            down, ydstogo, yardline_100: Game situation
            score_diff, team_pass_rate, game_seconds_remaining, posteam_type: Optional features

        Returns:
            Situation group (enum or string)
        """
        if self.use_time_remaining and self.use_home_away:
            if game_seconds_remaining is not None and posteam_type is not None:
                return get_phase1_situation(
                    down, ydstogo, yardline_100,
                    game_seconds_remaining, posteam_type
                )
        elif self.use_score and self.use_team_identity:
            if score_diff is not None and team_pass_rate is not None:
                return get_combined_situation(
                    down, ydstogo, yardline_100,
                    score_diff, team_pass_rate
                )
        elif self.use_score:
            if score_diff is not None:
                return get_score_aware_situation(down, ydstogo, yardline_100, score_diff)
        elif self.use_team_identity:
            if team_pass_rate is not None:
                return get_team_identity_situation(down, ydstogo, yardline_100, team_pass_rate)

        return get_situation_group(down, ydstogo, yardline_100)

    def _aggregate_predictions(
        self,
        predictions: Dict[SimplePlayType, float]
    ) -> Dict[str, float]:
        """
        Aggregate predictions by play type.

        Args:
            predictions: Dict from SimplePlayType to probability

        Returns:
            Dict from string ('P', 'R') to probability
        """
        aggregated = defaultdict(float)

        for play_type, prob in predictions.items():
            aggregated[play_type.code] += prob

        # Normalize to ensure probabilities sum to 1.0
        total = sum(aggregated.values())
        if total > 0:
            aggregated = {k: v / total for k, v in aggregated.items()}

        return dict(aggregated)

    def get_statistics(self) -> Dict[str, Any]:
        """Return statistics about all tries."""
        stats = {
            'max_depth': self.max_depth,
            'use_score': getattr(self, 'use_score', False),
            'use_team_identity': getattr(self, 'use_team_identity', False),
            'features': getattr(self, 'features', []),
            'use_hierarchical_fallback': getattr(self, 'use_hierarchical_fallback', False),
            'min_examples_threshold': getattr(self, 'min_examples_threshold', 50),
            'total_situations': sum(self.situation_counts.values()),
            'situation_breakdown': dict(self.situation_counts),
            'tries': {},
            'num_situation_groups': len(self.tries),
            'fallback_stats': dict(getattr(self, 'fallback_stats', {}))
        }

        min_threshold = getattr(self, 'min_examples_threshold', 50)
        sufficient_groups = sum(1 for count in self.situation_counts.values()
                               if count >= min_threshold)
        stats['groups_with_sufficient_data'] = sufficient_groups
        stats['groups_with_sparse_data'] = len(self.situation_counts) - sufficient_groups

        for group, trie in self.tries.items():
            trie_stats = trie.get_statistics()
            group_key = group.value if isinstance(group, SituationGroup) else group
            has_sufficient = self.situation_counts.get(group, 0) >= min_threshold
            stats['tries'][group_key] = {
                'total_sequences': trie_stats['total_sequences'],
                'num_nodes': trie_stats['num_nodes'],
                'avg_branching': trie_stats['avg_branching_factor'],
                'has_sufficient_data': has_sufficient
            }

        return stats

    def save(self, filepath: str):
        """Save the grouped trie to disk."""
        with open(filepath, 'wb') as f:
            pickle.dump(self, f)

    @staticmethod
    def load(filepath: str) -> 'SituationGroupedTrie':
        """Load a grouped trie from disk."""
        with open(filepath, 'rb') as f:
            return pickle.load(f)

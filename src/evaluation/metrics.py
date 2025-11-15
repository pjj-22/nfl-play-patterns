from typing import Dict, List, Tuple
import numpy as np
from dataclasses import dataclass


@dataclass
class PredictionMetrics:
    """Container for prediction metrics."""
    top1_accuracy: float
    top3_accuracy: float
    top5_accuracy: float
    avg_confidence: float
    avg_depth_matched: float
    total_predictions: int

    def __repr__(self):
        return f"""Prediction Metrics:
  Top-1 Accuracy: {self.top1_accuracy:.2%}
  Top-3 Accuracy: {self.top3_accuracy:.2%}
  Top-5 Accuracy: {self.top5_accuracy:.2%}
  Avg Confidence: {self.avg_confidence:.2%}
  Avg Depth Matched: {self.avg_depth_matched:.2f}
  Total Predictions: {self.total_predictions:,}
"""


class TrieEvaluator:
    """Evaluate trie prediction performance."""

    def __init__(self, trie, classifier):
        self.trie = trie
        self.classifier = classifier

    def evaluate_drives(
        self,
        drives_df,
        min_context: int = 3
    ) -> PredictionMetrics:
        """
        Evaluate prediction accuracy on a set of drives.

        Args:
            drives_df: DataFrame with drives
            min_context: Minimum number of plays before making predictions

        Returns:
            PredictionMetrics object
        """
        correct_top1 = 0
        correct_top3 = 0
        correct_top5 = 0
        total_confidence = 0.0
        total_depth = 0
        total_predictions = 0

        drives = drives_df.groupby(['game_id', 'drive'])

        for (game_id, drive_num), drive_plays in drives:
            if len(drive_plays) <= min_context:
                continue

            for i in range(min_context, len(drive_plays)):
                context_plays = self.classifier.encode_series(drive_plays.iloc[:i])
                actual = self.classifier.encode(drive_plays.iloc[i].to_dict())

                predictions, depth = self.trie.predict(context_plays, k=5)

                if not predictions:
                    continue

                top5_plays = list(predictions.keys())

                if len(top5_plays) >= 1 and actual in top5_plays[:1]:
                    correct_top1 += 1
                if len(top5_plays) >= 3 and actual in top5_plays[:3]:
                    correct_top3 += 1
                if actual in top5_plays[:5]:
                    correct_top5 += 1

                total_confidence += predictions.get(actual, 0.0)
                total_depth += depth
                total_predictions += 1

        if total_predictions == 0:
            return PredictionMetrics(0, 0, 0, 0, 0, 0)

        return PredictionMetrics(
            top1_accuracy=correct_top1 / total_predictions,
            top3_accuracy=correct_top3 / total_predictions,
            top5_accuracy=correct_top5 / total_predictions,
            avg_confidence=total_confidence / total_predictions,
            avg_depth_matched=total_depth / total_predictions,
            total_predictions=total_predictions
        )

    def evaluate_by_situation(
        self,
        drives_df,
        situation_col: str = 'down'
    ) -> Dict[str, PredictionMetrics]:
        """Evaluate accuracy broken down by situation."""
        results = {}

        for situation, group in drives_df.groupby(situation_col):
            metrics = self.evaluate_drives(group)
            results[situation] = metrics

        return results

"""
Evaluation metrics for the corrected model architecture.

Calculates Pass/Run prediction accuracy without conflating
play types with game outcomes.
"""
from typing import Dict
from dataclasses import dataclass
import pandas as pd
from ..models.grouped_trie import SituationGroupedTrie
from ..models.simple_classifier import SimplePlayClassifier, SimplePlayType
from ..models.situation_groups import get_situation_group


@dataclass
class BinaryPredictionMetrics:
    """Metrics for binary Pass/Run prediction."""
    pass_accuracy: float          # Accuracy when predicting pass
    run_accuracy: float           # Accuracy when predicting run
    overall_accuracy: float       # Overall accuracy (correct / total)
    pass_precision: float         # Of predicted passes, how many were correct
    run_precision: float          # Of predicted runs, how many were correct
    pass_recall: float            # Of actual passes, how many did we predict
    run_recall: float             # Of actual runs, how many did we predict
    total_predictions: int        # Total number of predictions made
    avg_pass_confidence: float    # Avg probability assigned to pass when pass was predicted
    avg_run_confidence: float     # Avg probability assigned to run when run was predicted

    def __repr__(self):
        return f"""Binary Prediction Metrics (Pass/Run):
  Overall Accuracy: {self.overall_accuracy:.2%}

  Pass Prediction:
    Precision: {self.pass_precision:.2%} (of predicted passes, {self.pass_precision:.0%} were correct)
    Recall: {self.pass_recall:.2%} (caught {self.pass_recall:.0%} of actual passes)
    Avg Confidence: {self.avg_pass_confidence:.2%}

  Run Prediction:
    Precision: {self.run_precision:.2%} (of predicted runs, {self.run_precision:.0%} were correct)
    Recall: {self.run_recall:.2%} (caught {self.run_recall:.0%} of actual runs)
    Avg Confidence: {self.avg_run_confidence:.2%}

  Total Predictions: {self.total_predictions:,}
"""


class CorrectedTrieEvaluator:
    """Evaluate the corrected grouped trie model."""

    def __init__(self, trie: SituationGroupedTrie, classifier: SimplePlayClassifier):
        self.trie = trie
        self.classifier = classifier

    def evaluate_drives(
        self,
        drives_df: pd.DataFrame,
        min_context: int = 3
    ) -> BinaryPredictionMetrics:
        """
        Evaluate Pass/Run prediction accuracy.

        Args:
            drives_df: DataFrame with plays
            min_context: Minimum plays before making predictions

        Returns:
            BinaryPredictionMetrics
        """
        # Counters for accuracy
        correct = 0
        total = 0

        # Counters for precision/recall
        true_positives_pass = 0
        false_positives_pass = 0
        false_negatives_pass = 0
        true_positives_run = 0
        false_positives_run = 0
        false_negatives_run = 0

        # Confidence tracking
        pass_confidences = []
        run_confidences = []

        drives = drives_df.groupby(['game_id', 'drive'])

        for (game_id, drive_num), drive_plays in drives:
            if len(drive_plays) <= min_context:
                continue

            # For each play after min_context, predict it
            for i in range(min_context, len(drive_plays)):
                # Get context (previous plays)
                context_plays = drive_plays.iloc[:i]
                context_types = self.classifier.encode_series(context_plays)

                # Get current situation and actual play
                current_play = drive_plays.iloc[i]
                actual_type = self.classifier.encode(current_play)

                # Skip special plays
                if actual_type.code == 'OTHER':
                    continue

                situation = (
                    int(current_play['down']),
                    int(current_play['ydstogo']),
                    int(current_play['yardline_100'])
                )

                score_diff = None
                if 'score_differential' in current_play:
                    score_diff = float(current_play['score_differential'])

                team_pass_rate = None
                if 'team_pass_rate' in current_play:
                    team_pass_rate = float(current_play['team_pass_rate'])

                game_seconds_remaining = None
                if 'game_seconds_remaining' in current_play:
                    game_seconds_remaining = float(current_play['game_seconds_remaining'])

                posteam_type = None
                if 'posteam_type' in current_play:
                    posteam_type = str(current_play['posteam_type'])

                predictions, depth = self.trie.predict(
                    situation, context_types,
                    score_diff=score_diff,
                    team_pass_rate=team_pass_rate,
                    game_seconds_remaining=game_seconds_remaining,
                    posteam_type=posteam_type
                )

                if not predictions:
                    continue

                predicted_code = max(predictions.items(), key=lambda x: x[1])[0]
                predicted_prob = predictions[predicted_code]

                total += 1
                actual_code = actual_type.code

                if predicted_code == actual_code:
                    correct += 1

                if predicted_code == 'P':
                    pass_confidences.append(predicted_prob)
                    if actual_code == 'P':
                        true_positives_pass += 1
                    else:
                        false_positives_pass += 1
                elif predicted_code == 'R':
                    run_confidences.append(predicted_prob)
                    if actual_code == 'R':
                        true_positives_run += 1
                    else:
                        false_positives_run += 1

                if actual_code == 'P' and predicted_code != 'P':
                    false_negatives_pass += 1
                if actual_code == 'R' and predicted_code != 'R':
                    false_negatives_run += 1

        # Calculate metrics
        overall_accuracy = correct / total if total > 0 else 0

        pass_precision = (
            true_positives_pass / (true_positives_pass + false_positives_pass)
            if (true_positives_pass + false_positives_pass) > 0 else 0
        )
        run_precision = (
            true_positives_run / (true_positives_run + false_positives_run)
            if (true_positives_run + false_positives_run) > 0 else 0
        )

        pass_recall = (
            true_positives_pass / (true_positives_pass + false_negatives_pass)
            if (true_positives_pass + false_negatives_pass) > 0 else 0
        )
        run_recall = (
            true_positives_run / (true_positives_run + false_negatives_run)
            if (true_positives_run + false_negatives_run) > 0 else 0
        )

        avg_pass_conf = sum(pass_confidences) / len(pass_confidences) if pass_confidences else 0
        avg_run_conf = sum(run_confidences) / len(run_confidences) if run_confidences else 0

        return BinaryPredictionMetrics(
            pass_accuracy=pass_precision * pass_recall,  # F1-ish
            run_accuracy=run_precision * run_recall,
            overall_accuracy=overall_accuracy,
            pass_precision=pass_precision,
            run_precision=run_precision,
            pass_recall=pass_recall,
            run_recall=run_recall,
            total_predictions=total,
            avg_pass_confidence=avg_pass_conf,
            avg_run_confidence=avg_run_conf
        )

    def evaluate_by_situation(
        self,
        drives_df: pd.DataFrame,
        min_context: int = 3
    ) -> Dict[str, BinaryPredictionMetrics]:
        """
        Evaluate accuracy broken down by situation group.

        Returns:
            Dictionary mapping situation group name to metrics
        """
        from ..models.situation_groups import SituationGroup

        results = {}

        # Group plays by situation
        situation_groups = {}
        for (game_id, drive_num), drive_plays in drives_df.groupby(['game_id', 'drive']):
            for idx, play in drive_plays.iterrows():
                if pd.isna(play['down']):
                    continue

                situation = (
                    int(play['down']),
                    int(play['ydstogo']),
                    int(play['yardline_100'])
                )
                group = get_situation_group(*situation)

                if group not in situation_groups:
                    situation_groups[group] = []

                situation_groups[group].append((game_id, drive_num, idx))

        # Evaluate each group
        for group, play_indices in situation_groups.items():
            # Create DataFrame for this group
            group_df = drives_df[
                drives_df.index.isin([idx for _, _, idx in play_indices])
            ]

            if len(group_df) < 100:  # Skip groups with too little data
                continue

            metrics = self.evaluate_drives(group_df, min_context)
            results[group.value] = metrics

        return results

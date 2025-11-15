# Evaluation Module

## Overview

Metrics and validation logic for assessing trie prediction accuracy.

## Components

### metrics.py

**Purpose:** Calculate prediction performance metrics

**Key Classes:**

```python
@dataclass
class PredictionMetrics:
    """Container for prediction performance metrics.

    Attributes:
        top1_accuracy: Percentage where top prediction was correct
        top3_accuracy: Percentage where correct play in top 3
        top5_accuracy: Percentage where correct play in top 5
        avg_confidence: Average probability assigned to correct play
        avg_depth_matched: Average trie depth matched
        total_predictions: Number of predictions evaluated
    """
```

**Key Functions:**

```python
class TrieEvaluator:
    """Evaluate trie prediction performance."""

    def evaluate_drives(
        self,
        drives_df: pd.DataFrame,
        min_context: int = 3
    ) -> PredictionMetrics:
        """Evaluate on a set of drives.

        For each play (after min_context), predict using prior plays.

        Args:
            drives_df: DataFrame with drive data
            min_context: Min plays before making predictions

        Returns:
            PredictionMetrics with accuracy results
        """

    def evaluate_by_situation(
        self,
        drives_df: pd.DataFrame,
        situation_col: str = 'down'
    ) -> Dict[str, PredictionMetrics]:
        """Evaluate accuracy broken down by situation.

        Args:
            drives_df: DataFrame with drive data
            situation_col: Column to group by (down, distance_category, etc.)

        Returns:
            Dict mapping situation value -> metrics
        """
```

**Metrics Explained:**

| Metric | Formula | Baseline | Target | Interpretation |
|--------|---------|----------|--------|----------------|
| **Top-1** | Correct if rank=1 | ~2% (random) | 25-35% | How often we get it exactly right |
| **Top-3** | Correct if rank≤3 | ~6% (random) | 50-65% | How often it's in top 3 |
| **Top-5** | Correct if rank≤5 | ~10% (random) | 65-75% | How often it's in top 5 |
| **Confidence** | P(correct play) | ~2% (uniform) | 30-40% | Avg probability on correct |
| **Depth** | Sequence match length | N/A | 3-5 plays | How far back we match |

**Baseline Calculation:**

With vocabulary size V=49:
- Random top-1: 1/49 ≈ 2%
- Random top-3: 3/49 ≈ 6%
- Random top-5: 5/49 ≈ 10%

**Why Top-K Accuracy?**

In real use (e.g., defensive coordinator), knowing "likely run or play-action pass" (top-3) is more useful than exact play. Top-k metrics capture this partial credit.

### validation.py

**Purpose:** Train/test split and cross-validation logic

**Key Functions:**

```python
def train_test_split_games(
    pbp: pd.DataFrame,
    test_size: float = 0.2,
    random_state: int = 42
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Split data by games (not plays) to avoid leakage.

    Args:
        pbp: Play-by-play DataFrame
        test_size: Fraction for test set
        random_state: Random seed

    Returns:
        (train_df, test_df)
    """
```

**Why Split by Games?**

**Wrong approach:**
```python
# BAD - Data leakage!
train_df, test_df = train_test_split(pbp, test_size=0.2)
```

Problem: Plays from same game/drive end up in both train and test. The trie would have seen similar sequences, inflating accuracy.

**Right approach:**
```python
# GOOD - No leakage
games = pbp['game_id'].unique()
train_games, test_games = train_test_split(games, test_size=0.2)
train_df = pbp[pbp['game_id'].isin(train_games)]
test_df = pbp[pbp['game_id'].isin(test_games)]
```

Now train and test are completely independent games.

## Usage Example

```python
from src.evaluation.metrics import TrieEvaluator
from src.evaluation.validation import train_test_split_games

# Split data
train_df, test_df = train_test_split_games(pbp, test_size=0.2)

# Build trie on training data
trie = build_trie(train_df)  # Implementation in notebooks

# Evaluate on test data
evaluator = TrieEvaluator(trie, classifier)
metrics = evaluator.evaluate_drives(test_df, min_context=3)

print(metrics)
# Prediction Metrics:
#   Top-1 Accuracy: 32.4%
#   Top-3 Accuracy: 58.7%
#   Top-5 Accuracy: 71.2%
#   Avg Confidence: 34.1%
#   Avg Depth Matched: 3.8
#   Total Predictions: 45,231
```

## Evaluation Methodology

### Standard Evaluation

1. **Split**: 80% train (by games), 20% test
2. **Build**: Construct trie on training drives
3. **Predict**: For each test drive, predict each play using prior context
4. **Measure**: Calculate top-k accuracy

### Situational Evaluation

Break down accuracy by:
- **Down** (1st, 2nd, 3rd, 4th)
- **Distance category** (short, medium, long)
- **Field position** (own, opponent)
- **Quarter** (1st, 2nd, 3rd, 4th)
- **Score differential** (winning, tied, losing)

**Example:**
```python
by_down = evaluator.evaluate_by_situation(test_df, 'down')

print("Accuracy by Down:")
for down in [1, 2, 3, 4]:
    m = by_down[down]
    print(f"  {down}: Top-1={m.top1_accuracy:.1%}, Top-3={m.top3_accuracy:.1%}")
```

Expected: 3rd down most predictable (constrained options), 1st down least predictable.

### Team-Level Evaluation

Measure predictability for each team:

```python
team_predictability = {}
for team in test_df['posteam'].unique():
    team_df = test_df[test_df['posteam'] == team]
    metrics = evaluator.evaluate_drives(team_df)
    team_predictability[team] = metrics.top3_accuracy

# Sort by predictability
sorted_teams = sorted(team_predictability.items(), key=lambda x: x[1], reverse=True)
print(f"Most predictable: {sorted_teams[0]}")
print(f"Least predictable: {sorted_teams[-1]}")
```

## Statistical Significance

When comparing metrics (e.g., does 3rd down > 1st down accuracy?), use:

```python
from scipy.stats import binomial_test

# Test if 3rd down accuracy significantly higher
n_3rd = metrics_3rd.total_predictions
k_3rd = int(n_3rd * metrics_3rd.top1_accuracy)

p_value = binomial_test(k_3rd, n_3rd, metrics_1st.top1_accuracy)
print(f"p-value: {p_value:.4f}")  # < 0.05 = significant
```

## Visualizations

Common plots (implemented in `src.visualization`):

1. **Accuracy by situation** - Bar chart of top-k accuracy
2. **Team predictability** - Horizontal bar chart
3. **Confidence distribution** - Histogram of predicted probabilities
4. **Depth matched distribution** - How far back trie matches
5. **Confusion matrix** - For specific situations (e.g., 3rd and short)

## Future Enhancements

- [ ] Cross-validation (k-fold by games)
- [ ] Temporal validation (train on early season, test on late)
- [ ] Calibration metrics (Brier score, log loss)
- [ ] Comparison to baseline models (Markov chain, random forest)

## Testing

See `tests/test_metrics.py`.

Key tests:
- Metrics calculated correctly on synthetic data
- Top-k accuracy <= top-(k+1) accuracy (monotonic)
- Random predictions give ~baseline accuracy
- Train/test split has no overlap

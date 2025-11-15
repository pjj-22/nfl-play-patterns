# Visualization Module

## Overview

Plotting functions and interactive dashboards for results presentation.

## Components

### plotters.py

**Purpose:** Standard matplotlib/seaborn plotting functions

**Key Functions:**

```python
def plot_accuracy_by_situation(
    metrics_by_situation: Dict[str, PredictionMetrics],
    title: str = "Prediction Accuracy by Situation"
) -> plt.Figure:
    """Bar chart showing top-1, top-3, top-5 accuracy by situation."""

def plot_team_predictability(
    team_scores: Dict[str, float],
    title: str = "Team Offensive Predictability"
) -> plt.Figure:
    """Horizontal bar chart of team predictability scores."""

def plot_confidence_distribution(
    predictions: List[float],
    bins: int = 50
) -> plt.Figure:
    """Histogram of prediction confidence values."""

def plot_sequence_depth_vs_accuracy(
    depths: List[int],
    accuracies: List[float]
) -> plt.Figure:
    """Scatter plot showing relationship between match depth and accuracy."""

def plot_drive_example(
    drive_plays: List[str],
    predictions: List[Dict[PlayType, float]],
    actual: List[str]
) -> plt.Figure:
    """Visual timeline of drive with predictions and actual plays."""
```

### dashboards.py

**Purpose:** Interactive visualizations (plotly, bokeh, or streamlit)

**Components:**

```python
def create_interactive_prediction_dashboard(
    trie: PlaySequenceTrie,
    classifier: PlayClassifier
) -> None:
    """Launch interactive dashboard for live predictions.

    Features:
    - Input recent play sequence
    - See top-k predictions with probabilities
    - Visualize trie path taken
    - Show historical similar sequences
    """
```

## Visualization Guidelines

### Style

Following clean, publication-ready aesthetic:

```python
import matplotlib.pyplot as plt
import seaborn as sns

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 11
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 14
```

### Color Palette

Use colorblind-friendly palettes:

```python
# For categorical data
colors = sns.color_palette("colorblind", n_colors=5)

# For sequential data
colors = sns.color_palette("Blues", n_colors=5)

# For diverging data (win/loss, above/below average)
colors = sns.diverging_palette(10, 133, as_cmap=True)
```

### Labels and Titles

- **Always include units** (%, seconds, count)
- **Descriptive titles** - What is being shown?
- **Axis labels** - What do x and y represent?
- **Legends** - Only if multiple series

### Example Plot

```python
def plot_accuracy_by_down(metrics_by_down: Dict[int, PredictionMetrics]) -> plt.Figure:
    downs = sorted([d for d in metrics_by_down.keys() if d in [1, 2, 3, 4]])
    top1 = [metrics_by_down[d].top1_accuracy * 100 for d in downs]
    top3 = [metrics_by_down[d].top3_accuracy * 100 for d in downs]

    fig, ax = plt.subplots(figsize=(10, 6))

    x = np.arange(len(downs))
    width = 0.35

    ax.bar(x - width/2, top1, width, label='Top-1', color='#1f77b4', alpha=0.8)
    ax.bar(x + width/2, top3, width, label='Top-3', color='#ff7f0e', alpha=0.8)

    ax.set_xlabel('Down')
    ax.set_ylabel('Accuracy (%)')
    ax.set_title('Prediction Accuracy by Down')
    ax.set_xticks(x)
    ax.set_xticklabels([f'{d}' for d in downs])
    ax.legend()
    ax.grid(axis='y', alpha=0.3)

    return fig
```

## Standard Visualizations

### 1. Accuracy Bar Charts

**Use case:** Compare accuracy across situations

**Variables:**
- X-axis: Situation (down, distance, field position)
- Y-axis: Accuracy (%)
- Series: Top-1, Top-3, Top-5

**Insight:** Which situations are most/least predictable?

### 2. Team Predictability Rankings

**Use case:** Show which teams are predictable

**Variables:**
- X-axis: Accuracy (%)
- Y-axis: Team (sorted by accuracy)
- Color: Above/below league average

**Insight:** Identify predictable vs unpredictable offenses

### 3. Confidence Histograms

**Use case:** Distribution of prediction probabilities

**Variables:**
- X-axis: Probability bins (0-100%)
- Y-axis: Count of predictions

**Insight:** Are predictions confident or uncertain?

### 4. Correlation Scatter Plots

**Use case:** Predictability vs team success

**Variables:**
- X-axis: Team predictability
- Y-axis: Win rate (or EPA/play)
- Points: Teams with labels

**Insight:** Does predictability correlate with winning?

### 5. Sequence Depth Analysis

**Use case:** Does longer context improve accuracy?

**Variables:**
- X-axis: Sequence depth matched (1-8 plays)
- Y-axis: Accuracy (%)
- Plot type: Line or scatter

**Insight:** Optimal context window size

## Interactive Features

### Dashboard Components

If building interactive dashboard (Phase 5 extension):

1. **Input Panel**
   - Dropdowns for recent plays
   - Select down, distance, field position
   - Click "Predict"

2. **Prediction Display**
   - Top-5 plays with probabilities
   - Visual bar chart
   - Confidence indicator

3. **Historical Context**
   - Similar sequences from history
   - Success rate of each option
   - EPA by play choice

4. **Trie Visualization**
   - Tree diagram showing path taken
   - Highlight matched sequence
   - Show branching options

## Export Functions

```python
def save_figure(fig: plt.Figure, filename: str, dpi: int = 300) -> None:
    """Save figure in multiple formats for publication.

    Saves as:
    - PNG (high-res for presentations)
    - SVG (vector for papers)
    - PDF (for LaTeX documents)
    """
    base = filename.rsplit('.', 1)[0]
    fig.savefig(f'{base}.png', dpi=dpi, bbox_inches='tight')
    fig.savefig(f'{base}.svg', bbox_inches='tight')
    fig.savefig(f'{base}.pdf', bbox_inches='tight')
```

## Usage Example

```python
from src.evaluation.metrics import TrieEvaluator
from src.visualization.plotters import plot_accuracy_by_down

# Evaluate
evaluator = TrieEvaluator(trie, classifier)
metrics_by_down = evaluator.evaluate_by_situation(test_df, 'down')

# Plot
fig = plot_accuracy_by_down(metrics_by_down)
fig.savefig('results/accuracy_by_down.png', dpi=300, bbox_inches='tight')
plt.show()
```

## Notebook Integration

Visualizations used in notebooks should:

1. **Show inline** - Use `%matplotlib inline`
2. **Include interpretation** - Markdown cell below each plot
3. **Export to `/results`** - Save publication-ready versions

**Example Notebook Cell:**

```python
# Accuracy by down
fig = plot_accuracy_by_down(metrics_by_down)
plt.show()

# Save for report
fig.savefig('../results/accuracy_by_down.png', dpi=300, bbox_inches='tight')
```

**Markdown cell below:**

```markdown
### Key Findings

- **3rd down is most predictable** (61% top-3 accuracy)
  - Limited playcalling options
  - Distance to first down constrains choices

- **1st down is least predictable** (48% top-3 accuracy)
  - Full playbook available
  - No situational pressure

- **4th down has high variance**
  - Small sample size (most teams punt)
  - Go-for-it attempts are unconventional
```

## Design Principles

Following `CLAUDE.md` guidelines:

- **Code is minimal** - Function calls, not comments
- **Interpretation in notebooks** - Not in plot functions
- **Examples in README** - This file shows how to use functions

## Future Enhancements

- [ ] Animated visualizations (drive progression over time)
- [ ] Network graph of play transitions
- [ ] Heatmaps of play type by field position
- [ ] Real-time dashboard with live NFL data
- [ ] 3D visualizations of trie structure

## Testing

Visualization code is typically not unit tested, but should be:
- **Manually reviewed** in notebooks
- **Visually inspected** for correctness
- **Reproduced** with fixed random seeds

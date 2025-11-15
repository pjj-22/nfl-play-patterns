# Source Code

## Overview

Core Python package for NFL play prediction using trie data structure.

## Package Structure

```
src/
├── __init__.py
├── data/              # Data loading and preprocessing
├── models/            # Core algorithms (trie, classifier, clustering)
├── evaluation/        # Metrics and validation logic
└── visualization/     # Plotting and dashboard functions
```

## Module Responsibilities

### `src.data`

**Purpose:** Load and preprocess NFL play-by-play data

**Key Components:**
- `loader.py` - Download data from nflfastR
- `preprocessor.py` - Clean and filter plays
- `feature_extractor.py` - Extract situational features

**See:** [src/data/README.md](data/README.md)

### `src.models`

**Purpose:** Core prediction algorithms

**Key Components:**
- `play_trie.py` - Trie data structure implementation
- `play_classifier.py` - Play encoding/decoding
- `play_clustering.py` - Graph-based play clustering

**See:** [src/models/README.md](models/README.md)

### `src.evaluation`

**Purpose:** Evaluate prediction accuracy

**Key Components:**
- `metrics.py` - Accuracy, precision, recall calculations
- `validation.py` - Train/test split and cross-validation

**See:** [src/evaluation/README.md](evaluation/README.md)

### `src.visualization`

**Purpose:** Generate visualizations and dashboards

**Key Components:**
- `plotters.py` - Standard plot functions
- `dashboards.py` - Interactive visualizations

**See:** [src/visualization/README.md](visualization/README.md)

## Installation

```bash
# From repository root
pip install -e .
```

This installs the package in editable mode, allowing imports:

```python
from src.models import PlaySequenceTrie
from src.data import load_pbp_data
```

## Usage Example

```python
from src.data.loader import load_pbp_data
from src.data.preprocessor import clean_plays
from src.models.play_trie import PlaySequenceTrie
from src.models.play_classifier import PlayClassifier

# Load and clean data
pbp = load_pbp_data(seasons=[2023])
pbp_clean = clean_plays(pbp)

# Build trie
classifier = PlayClassifier()
trie = PlaySequenceTrie(max_depth=8)

for (game_id, drive_num), drive in pbp_clean.groupby(['game_id', 'drive']):
    play_types = classifier.encode_series(drive)
    trie.insert_sequence(play_types)

# Make prediction
recent_plays = [...]  # Recent plays from current drive
predictions, depth = trie.predict(recent_plays, k=5)

for play_type, prob in predictions.items():
    print(f"{play_type.code}: {prob:.1%}")
```

## Design Principles

Following `CLAUDE.md` guidelines:

1. **Minimal comments** - Code should be self-documenting
2. **Type hints everywhere** - Function signatures must have types
3. **Brief docstrings** - API contract only, not implementation
4. **External documentation** - Complex explanations in README files

## Code Style

### Type Hints

```python
from typing import Dict, List, Tuple, Optional

def predict(
    self,
    recent_plays: List[PlayType],
    k: int = 5
) -> Tuple[Dict[PlayType, float], int]:
    ...
```

### Docstrings

```python
def insert_sequence(self, play_types: List[PlayType], epas: Optional[List[float]] = None):
    """Insert a sequence of plays into the trie.

    Args:
        play_types: List of encoded play types
        epas: Optional EPA values for each play
    """
    ...
```

### Naming

- `snake_case`: functions, variables, files
- `PascalCase`: classes
- `UPPER_CASE`: constants
- `_private`: internal methods

## Testing

All modules should have corresponding tests in `/tests`:

```
src/models/play_trie.py → tests/test_trie.py
src/models/play_classifier.py → tests/test_classifier.py
```

Run tests:

```bash
pytest tests/
```

## Dependencies

Core dependencies:
- `pandas` - Data manipulation
- `numpy` - Numerical operations
- `nfl_data_py` - NFL data source

See `requirements.txt` for full list.

## Performance Considerations

### Time Complexity Targets

- `PlaySequenceTrie.insert`: O(k) where k = sequence length
- `PlaySequenceTrie.predict`: O(k) lookup
- `PlayClassifier.encode`: O(1) per play

### Memory Management

- Tries can grow large (50-100MB for full season data)
- Use `pickle` for serialization
- Consider `max_depth` parameter to limit trie size

## Development Workflow

1. **Prototype in notebooks** - Explore ideas interactively
2. **Refactor to `/src`** - Extract working code
3. **Write tests** - Ensure correctness
4. **Document in README** - Explain design decisions
5. **Update ARCHITECTURE.md** - Note system-level changes

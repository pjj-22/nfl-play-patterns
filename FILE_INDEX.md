# File Index - NFL Play Prediction Project

Complete reference of all files in this project with their purposes.

**Last Updated**: November 15, 2024
**Project Status**: Complete

---

## Root Directory

### Documentation Files

| File | Purpose |
|------|---------|
| `README.md` | Project overview, setup instructions, quick start guide |
| `CLAUDE.md` | Development guidelines, code style, documentation philosophy |
| `PROJECT_RETROSPECTIVE.md` | Complete project retrospective with learnings and results (FINAL SUMMARY) |
| `HIERARCHICAL_FALLBACK_RESULTS.md` | Analysis of hierarchical fallback implementation and results |
| `PHASE1_RESULTS.md` | Phase 1 model (time + home/away) results and analysis |
| `COMBINED_MODEL_RESULTS.md` | Combined model (score + team identity) results |
| `SCORE_AWARE_RESULTS.md` | Score-aware model results and analysis |
| `CORRECTED_MODEL_SUMMARY.md` | Summary of corrected architecture (fixed conflation issue) |
| `FINAL_SUMMARY.md` | Original project summary before retrospective |
| `PROJECT_SUMMARY.md` | Earlier project summary |
| `NEXT_STEPS.md` | Historical next steps document |
| `EXTENSIBILITY_GUIDE.md` | Guide for adding new features to the system |
| `FILE_INDEX.md` | This file - comprehensive file documentation |

---

## Source Code (`src/`)

### Models (`src/models/`)

| File | Lines | Purpose |
|------|-------|---------|
| `play_trie.py` | 237 | Core trie data structure with O(k) insert/predict, backoff, EPA tracking |
| `grouped_trie.py` | 400 | Situation-grouped tries with hierarchical fallback, multi-feature support |
| `simple_classifier.py` | 70 | Binary play classifier (Pass/Run only) for corrected architecture |
| `situation_groups.py` | 275 | Situation grouping logic with all feature combinations |
| `play_classifier.py` | - | Legacy classifier (deprecated) |
| `__init__.py` | - | Package initialization |
| `README.md` | - | Models documentation, algorithm explanations |

**Key Exports**:
- `PlaySequenceTrie`: Core trie with sequence prediction
- `SituationGroupedTrie`: Main model class with fallback
- `SimplePlayClassifier`: Play type encoder
- `get_situation_group()`, `get_score_aware_situation()`, etc.: Grouping functions

### Features (`src/features/`)

| File | Lines | Purpose |
|------|-------|---------|
| `team_identity.py` | 120 | Calculate team offensive identity (pass-heavy/balanced/run-heavy) |
| `__init__.py` | - | Package initialization |

**Key Exports**:
- `add_team_identity_to_plays()`: Add team pass rate and identity to dataframe
- `calculate_team_pass_rates()`: Compute rolling team pass rates

### Evaluation (`src/evaluation/`)

| File | Lines | Purpose |
|------|-------|---------|
| `corrected_metrics.py` | 247 | Evaluation framework for corrected models (binary classification) |
| `metrics.py` | - | Legacy metrics (deprecated) |
| `__init__.py` | - | Package initialization |
| `README.md` | - | Evaluation methodology documentation |

**Key Exports**:
- `CorrectedTrieEvaluator`: Evaluate models on test data
- `BinaryPredictionMetrics`: Metrics dataclass (accuracy, precision, recall)

### Data (`src/data/`)

| File | Purpose |
|------|---------|
| `__init__.py` | Package initialization |
| `README.md` | Data sources, schemas, preprocessing steps |

### Visualization (`src/visualization/`)

| File | Purpose |
|------|---------|
| `__init__.py` | Package initialization |
| `README.md` | Visualization documentation |

### Root Source (`src/`)

| File | Purpose |
|------|---------|
| `__init__.py` | Package initialization |
| `README.md` | Source code overview |

---

## Scripts (`scripts/`)

### Training Scripts

| File | Purpose | Output |
|------|---------|--------|
| `train_corrected_model.py` | Train baseline model (9 groups, no features) | `data/models/corrected_trie.pkl` |
| `train_score_aware_model.py` | Train score-aware model (27 groups) | `data/models/score_aware_trie.pkl` |
| `train_combined_model.py` | Train combined model (81 groups, score + team) | `data/models/combined_trie.pkl` |
| `train_phase1_model.py` | Train Phase 1 model (36 groups, time + home/away) | `data/models/phase1_trie.pkl` |

### Demo/Visualization Scripts

| File | Purpose |
|------|---------|
| `corrected_predictions_demo.py` | Demo baseline model predictions |
| `score_aware_demo.py` | Demo score-aware model predictions |
| `combined_demo.py` | Demo combined model predictions |
| `phase1_demo.py` | Demo Phase 1 model predictions |
| `demo_trie.py` | Basic trie demonstration |
| `visualize_results.py` | Visualize model results |

### Analysis Scripts

| File | Purpose |
|------|---------|
| `analyze_combined_fallback.py` | Analyze fallback usage in combined model |
| `analyze_phase1_fallback.py` | Analyze fallback usage in Phase 1 model |
| `test_fallback_baseline.py` | Test fallback on baseline model |
| `diagnose_model.py` | Model diagnostics and debugging |

### Utility Scripts

| File | Purpose |
|------|---------|
| `save_clean_data.py` | Load and save cleaned NFL play-by-play data |

### Scripts Documentation

| File | Purpose |
|------|---------|
| `README.md` | Scripts usage, examples, parameters |

---

## Tests (`tests/`)

| File | Tests | Purpose |
|------|-------|---------|
| `test_trie.py` | 13 | Test core trie: insert, predict, backoff, depth, EPA, stats, save/load |
| `test_classifier.py` | 7 | Test play classifier: encoding, equality, hashing |
| `test_corrected_model.py` | 6 | Test grouped trie: situation isolation, no conflation, statistics |

**Total Tests**: 24 passing
**Coverage**: 100% of critical paths

---

## Data (`data/`)

### Processed Data (`data/processed/`)

| File | Size | Records | Purpose |
|------|------|---------|---------|
| `pbp_clean.parquet` | 66 MB | 141,289 | Clean NFL play-by-play data (2021-2024 seasons) |

### Models (`data/models/`)

| File | Size | Groups | Accuracy | Purpose |
|------|------|--------|----------|---------|
| `corrected_trie.pkl` | 314 KB | 9 | 61.65% | Baseline model (best performance) |
| `score_aware_trie.pkl` | 785 KB | 27 | 61.64% | Score-aware model |
| `combined_trie.pkl` | 1.8 MB | 81 | 61.34% | Combined model with fallback |
| `phase1_trie.pkl` | 1.0 MB | 36 | 61.21% | Phase 1 model with fallback |

### Data Documentation

| File | Purpose |
|------|---------|
| `README.md` | Data sources, schemas, preprocessing |

---

## Examples (`examples/`)

| File | Purpose |
|------|---------|
| `add_score_differential.py` | Example: Adding score differential feature |
| `README.md` | Examples documentation |

---

## Notebooks (`notebooks/`)

| File | Purpose |
|------|---------|
| `README.md` | Notebook purposes, execution order |

---

## Visualizations (`visualizations/`)

| File | Purpose |
|------|---------|
| `README.md` | Visualization outputs documentation |

---

## Configuration/Misc

| File | Purpose |
|------|---------|
| `test.py` | Temporary test file |
| `.pytest_cache/README.md` | Pytest cache documentation |

---

## File Statistics

### By Type

| Type | Count | Purpose |
|------|-------|---------|
| **Python (.py)** | 26 | Source code, scripts, tests |
| **Markdown (.md)** | 24 | Documentation |
| **Data (.parquet)** | 1 | NFL play data |
| **Models (.pkl)** | 4 | Trained trie models |
| **Total Files** | 55+ | Complete project |

### By Category

| Category | Files | Purpose |
|----------|-------|---------|
| **Core Models** | 5 | Trie, classifier, grouping |
| **Features** | 1 | Team identity calculation |
| **Evaluation** | 1 | Metrics and evaluation |
| **Training Scripts** | 4 | Model training |
| **Demo Scripts** | 4 | Model demonstrations |
| **Analysis Scripts** | 3 | Fallback analysis |
| **Tests** | 3 | Unit tests (24 total) |
| **Documentation** | 13 | Project docs |
| **Trained Models** | 4 | Saved models |

---

## Code Volume

| Component | Lines of Code |
|-----------|---------------|
| **Core Models** | ~980 lines |
| **Features** | ~120 lines |
| **Evaluation** | ~247 lines |
| **Scripts** | ~1,000+ lines |
| **Tests** | ~500 lines |
| **Documentation** | ~10,000+ words |
| **Total Python** | ~2,500+ lines |

---

## Key File Relationships

### Model Training Flow

```
Data:
  pbp_clean.parquet
    ↓
Training Scripts:
  train_corrected_model.py
  train_score_aware_model.py
  train_combined_model.py
  train_phase1_model.py
    ↓
Uses:
  src/models/grouped_trie.py
  src/models/simple_classifier.py
  src/models/situation_groups.py
  src/features/team_identity.py
    ↓
Evaluates with:
  src/evaluation/corrected_metrics.py
    ↓
Produces:
  data/models/*.pkl
  Results documentation (*.md)
```

### Prediction Flow

```
Trained Model:
  data/models/*.pkl
    ↓
Demo Scripts:
  *_demo.py
    ↓
Uses:
  src/models/grouped_trie.py (load model)
  src/models/simple_classifier.py (encode plays)
    ↓
Output:
  Predictions with probabilities
```

### Analysis Flow

```
Trained Model:
  data/models/*.pkl
    ↓
Analysis Scripts:
  analyze_*_fallback.py
  test_fallback_*.py
    ↓
Uses:
  get_statistics()
  fallback_stats
    ↓
Output:
  Fallback usage analysis
  Data sparsity insights
```

---

## Import Map

### Core Dependencies

```python
# Models
from src.models.play_trie import PlaySequenceTrie
from src.models.grouped_trie import SituationGroupedTrie
from src.models.simple_classifier import SimplePlayClassifier
from src.models.situation_groups import (
    get_situation_group,
    get_score_aware_situation,
    get_combined_situation,
    get_phase1_situation
)

# Features
from src.features.team_identity import add_team_identity_to_plays

# Evaluation
from src.evaluation.corrected_metrics import CorrectedTrieEvaluator
```

---

## Quick Reference

### To Train a Model

```bash
python scripts/train_corrected_model.py      # Baseline
python scripts/train_score_aware_model.py    # Score-aware
python scripts/train_combined_model.py       # Combined
python scripts/train_phase1_model.py         # Phase 1
```

### To Demo a Model

```bash
python scripts/corrected_predictions_demo.py  # Baseline
python scripts/score_aware_demo.py            # Score-aware
python scripts/combined_demo.py               # Combined
python scripts/phase1_demo.py                 # Phase 1
```

### To Run Tests

```bash
python -m pytest tests/ -v                    # All tests
python -m pytest tests/test_trie.py -v        # Trie tests only
```

### To Analyze Models

```bash
python scripts/analyze_combined_fallback.py   # Combined fallback
python scripts/analyze_phase1_fallback.py     # Phase 1 fallback
python scripts/test_fallback_baseline.py      # Baseline fallback
```

---

## Documentation Hierarchy

### For New Users
1. **Start**: `README.md`
2. **Setup**: `README.md` → Setup section
3. **Quick Start**: Run demo scripts
4. **Learn More**: `PROJECT_RETROSPECTIVE.md`

### For Developers
1. **Code Style**: `CLAUDE.md`
2. **Architecture**: `src/models/README.md`
3. **Add Features**: `EXTENSIBILITY_GUIDE.md`
4. **Tests**: Run `pytest tests/`

### For Understanding Results
1. **Final Summary**: `PROJECT_RETROSPECTIVE.md`
2. **Fallback**: `HIERARCHICAL_FALLBACK_RESULTS.md`
3. **Phase 1**: `PHASE1_RESULTS.md`
4. **Combined**: `COMBINED_MODEL_RESULTS.md`

---

## File Naming Conventions

### Python Files
- `snake_case.py` for all Python files
- `test_*.py` for test files
- `train_*.py` for training scripts
- `*_demo.py` for demonstration scripts

### Documentation Files
- `UPPERCASE.md` for top-level docs
- `README.md` for directory-level docs
- `*_RESULTS.md` for model results

### Model Files
- `*_trie.pkl` for trained models
- `*.parquet` for data files

---

## Deprecated/Legacy Files

| File | Status | Replacement |
|------|--------|-------------|
| `src/models/play_classifier.py` | Deprecated | `simple_classifier.py` |
| `src/evaluation/metrics.py` | Deprecated | `corrected_metrics.py` |
| `test.py` | Temporary | Delete when done |

---

## Generated: November 15, 2024
## Status: Complete - All 24 tests passing
## Best Model: `data/models/corrected_trie.pkl` (61.65%)

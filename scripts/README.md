# Scripts Directory

This directory contains scripts for training, evaluating, and demonstrating the **corrected** NFL play prediction model.

## Available Scripts

### 🚀 Main Scripts

#### `train_corrected_model.py`
Train the corrected situation-grouped trie model.

```bash
python scripts/train_corrected_model.py
```

**What it does:**
- Loads cleaned NFL data (141K plays)
- Splits by games (80/20 train/test)
- Builds situation-grouped tries
- Evaluates on test set
- Saves model to `data/models/corrected_trie.pkl`

**Output:**
- Overall accuracy: 61.65%
- Precision/recall by play type
- Accuracy by situation group

---

#### `corrected_predictions_demo.py`
Interactive demo of the corrected model with 6 game scenarios.

```bash
python scripts/corrected_predictions_demo.py
```

**Scenarios:**
1. Early down (1st & 10)
2. 3rd & short
3. 2nd & long
4. Red zone
5. Goal line
6. Pass-heavy drive

**Shows:** Clean Pass vs Run predictions without outcome conflation.

---

#### `visualize_results.py`
Generate visualization charts of model performance.

```bash
python scripts/visualize_results.py
```

**Creates 5 charts:**
1. **Accuracy Comparison** - Old vs new model
2. **Situation Breakdown** - Pass/Run by situation
3. **Architecture Comparison** - Visual of old vs new
4. **Precision & Recall** - By play type
5. **Sequence Patterns** - How sequences affect predictions

**Output:** Saved to `visualizations/` directory

---

### 🔍 Diagnostic Scripts

#### `diagnose_model.py`
Exposes the architectural flaw in the original model.

```bash
python scripts/diagnose_model.py
```

**What it shows:**
- How the old encoding conflated decisions with outcomes
- Example traces through the flawed architecture
- Why predictions were logically inconsistent
- Recommended fixes

**Purpose:** Educational - shows the problem before the fix.

---

### 🛠️ Utility Scripts

#### `save_clean_data.py`
Load and clean NFL play-by-play data from nflfastR.

```bash
python scripts/save_clean_data.py
```

**Output:** `data/processed/pbp_clean.parquet`

---

#### `demo_trie.py`
Basic trie demonstration with synthetic data.

```bash
python scripts/demo_trie.py
```

**Purpose:** Shows trie data structure concept without real data.

---

## Quick Start

### First Time Setup
```bash
# 1. Clean the data
python scripts/save_clean_data.py

# 2. Train the model
python scripts/train_corrected_model.py

# 3. Run demo
python scripts/corrected_predictions_demo.py

# 4. Generate visualizations
python scripts/visualize_results.py
```

### Just See Results
If model is already trained:
```bash
python scripts/corrected_predictions_demo.py
python scripts/visualize_results.py
```

---

## Files Removed

The following files from the **flawed** architecture have been deleted:

❌ `showcase_predictions.py` (old demo)
❌ `quick_examples.py` (old demo)
❌ `interactive_predictor.py` (old demo)
❌ `fixed_predictions.py` (bandaid aggregation fix)
❌ `evaluate_model.py` (trained flawed model)
❌ `test_trie_on_real_data.py` (tested old architecture)
❌ `data/models/trained_trie.pkl` (flawed model file)

**Why removed:** These used the incorrect architecture that conflated play-calling decisions with game outcomes.

---

## Architecture Overview

### Corrected Model
```
Input: Current situation + Recent play types
       ↓
Determine situation group (e.g., "3rd & short")
       ↓
Look up appropriate trie for that group
       ↓
Match recent play sequence [P, R, P]
       ↓
Return Pass/Run probabilities
       ↓
Output: {'P': 0.557, 'R': 0.443}
```

### Key Components
- **SimplePlayClassifier**: Encodes plays as just P or R
- **SituationGroupedTrie**: Multiple tries, one per situation
- **9 Situation Groups**: Early down, 3rd & short, red zone, etc.
- **Binary Prediction**: Only Pass or Run (no outcome prediction)

---

## Model Performance

```
Overall Accuracy: 61.65%
Random Baseline: 50%
Improvement: 1.23x (11.65 percentage points)

Pass Prediction:
  Precision: 65.82%
  Recall: 75.64%

Run Prediction:
  Precision: 52.24%
  Recall: 40.42%
```

---

## Documentation

For more details, see:
- `CORRECTED_MODEL_SUMMARY.md` - Full results and analysis
- `ARCHITECTURE_FLAW.md` - Detailed flaw explanation
- `BEFORE_AND_AFTER.md` - Side-by-side comparison
- `PROJECT_SUMMARY.md` - Original project overview (pre-fix)

---

## Questions?

**How is this different from the old model?**
- Old: Predicted play type + outcome (46 states) - conceptually flawed
- New: Predicts only play type (2 states) - logically correct

**Why is 61.65% good?**
- NFL teams try to be unpredictable
- Random guessing: 50%
- Naive "always pass": ~57%
- Our model: 61.65% (learns patterns)

**Can I see the old model?**
- No, files were deleted (they were incorrect)
- See `diagnose_model.py` to understand the flaw
- See `ARCHITECTURE_FLAW.md` for full analysis

---

*Last updated: November 2024*
*All scripts use the corrected architecture*

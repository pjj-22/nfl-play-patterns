# Visualizations

This directory contains charts visualizing the corrected model's performance and architecture.

## Generated Charts

All charts are created by running:
```bash
python scripts/visualize_results.py
```

---

### 1. Accuracy Comparison (`01_accuracy_comparison.png`)

**Side-by-side comparison of old vs new model:**

**Left Panel - OLD MODEL (FLAWED):**
- Task: Predict 46 compound states (play type + outcome)
- Accuracy: 18.36%
- Random baseline: 2.17%
- 8.4x improvement (but logically flawed)

**Right Panel - NEW MODEL (CORRECTED):**
- Task: Predict 2 states (Pass or Run only)
- Accuracy: 61.65%
- Random baseline: 50%
- Naive "always pass": 57%
- 1.23x improvement (logically correct)

**Key Insight:** The new model solves the RIGHT problem, not just a hard problem.

---

### 2. Situation Breakdown (`02_situation_breakdown.png`)

**Pass vs Run predictions across 6 game situations:**

Shows prediction probabilities for:
- Early Down (1st & 10)
- 3rd & Short
- 2nd & Long
- Red Zone
- Goal Line
- Pass-Heavy Drive

**Key Insights:**
- 2nd & Long → Heavy pass bias (58% pass)
- 3rd & Short after runs → Run favored (55.7% run)
- Pass-heavy drives continue passing (69.1% pass)
- Goal line most unpredictable (~50/50)

---

### 3. Architecture Comparison (`03_architecture_comparison.png`)

**Visual diagram comparing old vs new architecture:**

**Left - OLD (FLAWED):**
- Tree structure with nodes like `P_2_long_own`, `R_1_long_opp`
- Shows conflation of play type with game state
- 46 possible prediction outcomes
- Predicting unknowable future states

**Right - NEW (CORRECTED):**
- Situation groups (Early Down, 3rd & Short, Red Zone)
- Each group has its own trie storing [P, R, P, R]
- 2 possible outcomes (Pass or Run)
- Predictions conditioned on known situation

**Key Insight:** Separation of concerns - situations vs play types.

---

### 4. Precision & Recall (`04_precision_recall.png`)

**Model performance by play type:**

**Pass Predictions:**
- Precision: 65.82% (when we predict pass, we're right 66% of time)
- Recall: 75.64% (we catch 76% of actual passes)

**Run Predictions:**
- Precision: 52.24% (when we predict run, we're right 52% of time)
- Recall: 40.42% (we only catch 40% of actual runs)

**Key Insights:**
- Model better at predicting passes than runs
- Makes sense: NFL teams pass ~57% of the time
- Model learned this bias
- Better at identifying passes, worse at identifying runs

---

### 5. Sequence Patterns (`05_sequence_patterns.png`)

**How recent play sequences influence predictions (1st & 10 situations):**

**Pass Sequences:**
- After [P]: 56.4% pass
- After [P, P]: 62.1% pass
- After [P, P, P]: 69.1% pass

**Run Sequences:**
- After [R]: 58.1% pass
- After [R, R]: 51.2% pass
- After [R, R, R]: 44.3% pass

**Key Insights:**
- Pass-heavy drives continue passing
- Run-heavy drives favor more runs (pass % drops)
- Model learns continuation patterns
- Sequences matter for prediction accuracy

---

## Interpretation Guide

### What Makes These Charts Valuable?

1. **Accuracy Comparison** - Shows we fixed a fundamental flaw, not just improved numbers
2. **Situation Breakdown** - Demonstrates situational awareness
3. **Architecture Comparison** - Visualizes the conceptual difference
4. **Precision/Recall** - Shows model strengths and weaknesses
5. **Sequence Patterns** - Proves model learns from history

### How to Use in Presentations

**For Technical Audiences:**
- Start with Architecture Comparison (show the flaw)
- Move to Accuracy Comparison (show the fix)
- End with Precision/Recall (show it works)

**For Non-Technical Audiences:**
- Start with Situation Breakdown (intuitive)
- Show Sequence Patterns (understandable patterns)
- End with simple accuracy number (61.65%)

**For Portfolio/Interviews:**
- Lead with "I found and fixed an architectural flaw"
- Show Architecture Comparison
- Explain: "Old model predicted unknowable futures"
- Show corrected results
- Emphasize: Critical thinking > blind optimization

---

## Chart Specifications

- **Format:** PNG
- **DPI:** 300 (print quality)
- **Size:** Varies by chart
- **Colors:**
  - Pass predictions: Teal (#4ECDC4)
  - Run predictions: Coral (#FF6B6B)
  - Correct/Good: Green
  - Incorrect/Problem: Red
  - Neutral: Yellow

---

## Regenerating Charts

To regenerate all charts (e.g., after model retraining):

```bash
python scripts/visualize_results.py
```

This will overwrite existing charts with updated data.

---

## Future Enhancements

Potential additional visualizations:
- Team-specific predictability rankings
- Time-of-game effects (early vs late)
- Score differential impact
- Down-by-down accuracy breakdown
- Confidence distribution histograms
- ROC curves for binary classification

---

*Generated: November 2024*
*Based on corrected model architecture*

# Phase 1 Model Results: Time Remaining + Home/Away

**Date**: November 15, 2024
**Model**: Phase 1 - Time Remaining + Home/Away Context
**Situation Groups**: 36 (9 base × 2 time contexts × 2 home/away)

## Executive Summary

The Phase 1 model implements the first set of "low-hanging fruit" features from the extensibility roadmap:
- **Time remaining context** (normal vs two-minute drill)
- **Home/away indicator**

**Result**: 61.18% accuracy (-0.47 percentage points vs baseline)

This falls short of the predicted 68-70% target and reveals important insights about feature selection and data sparsity.

---

## Model Architecture

### Feature Design

**Time Context** (2 categories):
- `normal`: game_seconds_remaining > 120 (95.5% of plays)
- `two_minute`: game_seconds_remaining ≤ 120 (4.5% of plays)

**Home/Away** (2 categories):
- `home`: 50.4% of plays
- `away`: 49.6% of plays

**Total Groups**: 9 base situations × 2 time × 2 location = **36 groups**

### Training Data

- **Total plays**: 141,289 (from 1,139 games, 2021-2024 seasons)
- **Train/Test split**: 80/20 by games
- **Train set**: 112,704 plays (19,116 drives)
- **Test set**: 28,585 plays (4,817 drives)

---

## Results

### Overall Performance

| Metric | Value |
|--------|-------|
| **Overall Accuracy** | 61.18% |
| **Pass Precision** | 65.03% |
| **Pass Recall** | 76.84% |
| **Run Precision** | 51.68% |
| **Run Recall** | 37.48% |
| **Total Predictions** | 14,362 |

### Model Comparison

| Model | Accuracy | Change from Baseline |
|-------|----------|---------------------|
| Random Baseline | 50.00% | - |
| Baseline (no features) | 61.65% | +11.65 pts |
| Score-aware | 61.64% | +11.64 pts |
| Combined (score + team) | 61.27% | +10.77 pts |
| **Phase 1 (time + home/away)** | **61.18%** | **+10.68 pts** |

**Gain from baseline**: -0.47 percentage points
**Gain from random**: +11.18 percentage points

---

## Key Findings

### 1. Features Don't Improve Over Baseline

The Phase 1 features (time remaining + home/away) did **not** improve accuracy over the baseline model. In fact, they slightly decreased it.

**Why?**
- **Data sparsity**: Splitting into 36 groups reduces training data per group
- **Low signal features**: Home/away and time context may have weaker predictive power than expected
- **Feature independence**: These features may need to combine with score/team identity to show value

### 2. Two-Minute Drill Data Scarcity

Only **4.5%** of plays occur in the two-minute drill context. This creates:
- Limited training data for these situations
- High variance in predictions
- Unreliable pattern detection

**Demo observation**: In scenario 2 (3rd & 3, two-minute drill, away), the model predicted 78.8% runs - counterintuitive given urgency to pass. This suggests overfitting to sparse data.

### 3. Home/Away Has Minimal Impact

The 50.4%/49.6% split suggests home/away is nearly balanced across the dataset, providing limited discriminative power without interaction with other features.

### 4. Pass vs Run Prediction Asymmetry

The model shows strong **pass prediction** (65% precision, 77% recall) but weak **run prediction** (52% precision, 37% recall). This mirrors the baseline model's behavior, suggesting:
- Passing plays have more predictable patterns
- Running plays are more situationally diverse
- Model bias toward predicting passes

---

## Top Situation Groups

Most frequent groups in training data:

| Group | Plays | % |
|-------|-------|---|
| early_down_long_normal_home | 28,831 | 25.6% |
| early_down_long_normal_away | 28,357 | 25.2% |
| red_zone_normal_home | 6,280 | 5.6% |
| red_zone_normal_away | 5,718 | 5.1% |
| early_down_medium_normal_away | 5,058 | 4.5% |

**Observation**: Two-minute drill groups don't appear in top 15, confirming data scarcity.

---

## Model Statistics

- **Max depth**: 8 plays
- **Model size**: 775.7 KB
- **Situation groups created**: 36
- **Total situations processed**: 112,704

---

## Analysis: Why Did This Fall Short?

### Expected vs Actual

**Expected**: 68-70% accuracy (+7-9 points over baseline)
**Actual**: 61.18% accuracy (-0.47 points vs baseline)

### Root Causes

1. **Overestimated feature value**
   - Time remaining and home/away are weak signals in isolation
   - The extensibility guide may have been overly optimistic

2. **Data sparsity hurts more than features help**
   - 36 groups dilute training data
   - Baseline (9 groups) has 4x more data per group
   - More groups ≠ better predictions without sufficient data

3. **Feature interactions matter**
   - Time remaining + score differential would be stronger
   - Home/away + team identity would make more sense
   - Isolated features miss interaction effects

4. **Two-minute drill is too rare**
   - 4.5% of plays isn't enough to learn robust patterns
   - Would need multiple seasons or finer time buckets

---

## Lessons Learned

### What Worked

✅ **Architecture extensibility**: Adding features took ~100 lines of code
✅ **Clean implementation**: Modular design made iteration fast
✅ **Diagnostic value**: Negative results teach us about feature importance

### What Didn't Work

❌ **Feature selection**: Time + home/away don't add value alone
❌ **Granularity choice**: 36 groups may be too many without more data
❌ **Optimistic targets**: 68-70% was not grounded in analysis

### What to Do Differently

1. **Feature interaction analysis first**: Test if features correlate with outcomes before implementing
2. **Data sufficiency checks**: Ensure each group has 1,000+ examples minimum
3. **A/B test individual features**: Add one at a time to measure impact
4. **Consider hierarchical fallback**: Use base situation when specific group lacks data

---

## Next Steps & Recommendations

### Immediate Actions

**Option A: Abandon Phase 1 features**
- Revert to baseline or score-aware model
- These features don't justify the complexity

**Option B: Combine with existing features**
- Try: time_remaining + score_differential (score matters in two-minute drill)
- Try: home_away + team_identity (home teams play to their strengths)

**Option C: Refine time context**
- Use 4 time buckets instead of 2 (early/mid/late/two-minute)
- Requires more data or hierarchical fallback

### Phase 2 Recommendations

Before adding QB/RB ratings:
1. **Validate feature value**: Correlation analysis between QB rating and pass success rate
2. **Check data availability**: How many plays have QB rating data?
3. **Set realistic targets**: Use empirical analysis, not intuition

### Strategic Pivot

Consider shifting from **more features** to **better features**:
- Score differential is proven valuable (Phase 0 → Score-aware)
- Team identity is proven valuable (Score-aware → Combined)
- Focus on feature combinations that interact meaningfully

---

## Conclusion

The Phase 1 model demonstrates the principle that **not all features add value**, even when they seem theoretically relevant. Time remaining and home/away context, in isolation, create data sparsity that outweighs any predictive signal they provide.

**Key insight**: Feature engineering requires **empirical validation**, not just intuition. The extensibility guide's optimistic projections weren't grounded in analysis.

This is a valuable learning experience: sometimes the best next step is **not** to add features, but to **better understand** the features you have.

---

## Files

- **Training script**: `scripts/train_phase1_model.py`
- **Demo script**: `scripts/phase1_demo.py`
- **Model file**: `data/models/phase1_trie.pkl` (775.7 KB)
- **Code changes**:
  - `src/models/situation_groups.py`: Added `get_time_context()`, `get_home_away_context()`, `get_phase1_situation()`
  - `src/models/grouped_trie.py`: Added `use_time_remaining` and `use_home_away` flags
  - `src/evaluation/corrected_metrics.py`: Added Phase 1 parameter support

---

**Generated**: November 15, 2024
**Model ID**: phase1_trie
**Accuracy**: 61.18%
**Status**: ❌ Below baseline - Not recommended for production

# Hierarchical Fallback Results

**Date**: November 15, 2024
**Feature**: Hierarchical Fallback to Address Data Sparsity
**Implementation**: 3-level fallback (specific → base → league average)

## Executive Summary

Hierarchical fallback provides **marginal improvements** to models with granular features by intelligently falling back to simpler contexts when specific situations lack training data.

**Key Results**:
- **Baseline**: No change (61.65% → 61.65%)
- **Phase 1**: Minimal gain (61.18% → 61.21%, +0.03 pts)
- **Combined**: Small gain (61.27% → 61.34%, +0.07 pts)

**Insight**: Fallback helps, but the threshold of 50 examples is conservative enough that most groups already have sufficient data.

---

## Fallback Strategy

### Three-Level Hierarchy

**Level 1: Specific Context** (Use all features)
- Phase 1: "third_short_two_minute_away" (36 groups)
- Combined: "third_short_trailing_pass_heavy" (81 groups)
- Used when group has ≥50 training examples

**Level 2: Base Situation** (Strip all features)
- "third_short" (9 base groups)
- Used when Level 1 lacks data but base situation has ≥50 examples

**Level 3: League Average** (Universal fallback)
- Pass: 58%, Run: 42%
- Used as last resort when both Level 1 and 2 lack data

###Implementation

```python
def predict_with_fallback(self, situation, recent_plays, **features):
    # Level 1: Try specific context
    if specific_group in tries and has_sufficient_data(specific_group, min=50):
        return predict_from(specific_group)

    # Level 2: Fall back to base situation
    if base_group in tries and has_sufficient_data(base_group, min=50):
        return predict_from(base_group)

    # Level 3: League average
    return {'P': 0.58, 'R': 0.42}
```

---

## Results by Model

### 1. Baseline Model (No Features)

| Metric | Without Fallback | With Fallback | Change |
|--------|-----------------|---------------|--------|
| **Accuracy** | 61.65% | 61.65% | **+0.00 pts** |
| **Predictions** | 14,503 | 14,588 | +85 |
| **Groups Total** | 9 | 9 | - |
| **Sparse Groups** | 0 | 0 | - |

**Fallback Usage**:
- Level 1 (specific): 99.4%
- Level 2 (base): 0.0%
- Level 3 (league): 0.6%

**Analysis**: All 9 base groups have >1,000 examples. Fallback only kicks in for edge cases (85 predictions). No improvement.

---

### 2. Phase 1 Model (Time + Home/Away)

| Metric | Without Fallback | With Fallback | Change |
|--------|-----------------|---------------|--------|
| **Accuracy** | 61.18% | 61.21% | **+0.03 pts** |
| **Predictions** | 14,362 | 14,588 | +226 |
| **Groups Total** | 36 | 45 (36 specific + 9 base) | - |
| **Sparse Groups** | 0 | 0 | - |

**Fallback Usage**:
- Level 1 (specific): 98.5%
- Level 2 (base): 1.1% (164 predictions)
- Level 3 (league): 0.4% (62 predictions)

**Analysis**: Even two-minute drill groups have ≥50 examples. Only 1.5% of predictions use fallback, yielding minimal improvement (+0.03 pts).

---

### 3. Combined Model (Score + Team Identity)

| Metric | Without Fallback | With Fallback | Change |
|--------|-----------------|---------------|--------|
| **Accuracy** | 61.27% | 61.34% | **+0.07 pts** |
| **Predictions** | ~14,000 | 14,588 | - |
| **Groups Total** | 81 | 90 (81 specific + 9 base) | - |
| **Sparse Groups** | 9 | 9 | - |

**Sparse Groups** (all run-heavy teams):
- fourth_down_trailing_run_heavy: 12 plays
- fourth_down_leading_run_heavy: 17 plays
- fourth_down_tied_run_heavy: 20 plays
- third_short_trailing_run_heavy: 35 plays
- early_down_short_trailing_run_heavy: 36 plays
- third_medium_trailing_run_heavy: 38 plays
- third_long_trailing_run_heavy: 41 plays
- goal_line_trailing_run_heavy: 45 plays
- goal_line_leading_run_heavy: 47 plays

**Fallback Usage**:
- Level 1 (specific): 96.1%
- Level 2 (base): 3.6% (518 predictions)
- Level 3 (league): 0.3% (46 predictions)

**Analysis**: 9 sparse groups (mostly run-heavy teams in specific situations). 3.9% of predictions use fallback, yielding +0.07 point improvement. This is the most meaningful gain.

---

## Key Findings

### 1. Threshold of 50 is Conservative

With min_examples_threshold=50:
- Baseline: 0 sparse groups (all have 1,000+)
- Phase 1: 0 sparse groups (even two-minute drill has enough data)
- Combined: 9 sparse groups (mostly run-heavy teams)

**Only run-heavy team situations** fall below the threshold (only 3.6% of plays).

### 2. Fallback Usage is Proportional to Granularity

| Model | Groups | Sparse Groups | Fallback % | Accuracy Gain |
|-------|--------|---------------|------------|---------------|
| Baseline | 9 | 0 | 0.6% | +0.00 pts |
| Phase 1 | 36 | 0 | 1.5% | +0.03 pts |
| Combined | 81 | 9 | 3.9% | +0.07 pts |

**Pattern**: More granular models benefit more from fallback, but gains are still small.

### 3. Run-Heavy Teams Create Data Sparsity

All 9 sparse groups in Combined model involve **run-heavy teams** (only 3.6% of training plays):
- Run-heavy teams are rare (most teams pass 55-65%)
- When combined with score (trailing/tied/leading), groups become tiny
- Fallback helps these situations by using base situation data

### 4. Two-Minute Drill Has Enough Data

Despite being only 4.5% of plays, two-minute drill groups in Phase 1 all exceed 50 examples. The data is sufficient even for rare time contexts.

---

## Comparison Summary

### Model Accuracy Ranking (With Fallback)

| Rank | Model | Accuracy | vs Baseline | Groups | Sparse Groups |
|------|-------|----------|-------------|--------|---------------|
| 1 | **Baseline** | 61.65% | - | 9 | 0 |
| 2 | **Combined** | 61.34% | -0.31 pts | 81 | 9 |
| 3 | **Phase 1** | 61.21% | -0.44 pts | 36 | 0 |
| 4 | Random | 50.00% | -11.65 pts | - | - |

**Surprising result**: Baseline still beats all feature-enhanced models, even with fallback.

### Fallback Impact by Model

| Model | Improvement from Fallback |
|-------|---------------------------|
| Baseline | +0.00 pts (no sparse groups) |
| Phase 1 | +0.03 pts (minimal sparsity) |
| Combined | **+0.07 pts (9 sparse groups)** |

**Conclusion**: Fallback helps more granular models, but doesn't overcome the fundamental tradeoff between granularity and data sufficiency.

---

## Analysis: Why Small Gains?

### 1. Conservative Threshold

Min threshold of 50 examples means:
- Most groups qualify as "sufficient"
- Fallback rarely triggers
- Could increase threshold to 100 or 200 for more aggressive fallback

### 2. Feature-Sparse Groups Are Rare

Only 3.9% of predictions in Combined model use fallback:
- 96.1% of situations have adequate specific context
- Problem is less severe than anticipated

### 3. Base Situation is Already Good

When fallback happens:
- Level 2 (base) handles 90% of fallback cases
- Base situation (no features) is already 61.65% accurate
- Not much room for improvement

### 4. Features Add Noise, Not Signal

Fundamental issue remains:
- Score, team identity, time, home/away don't improve over baseline
- More granularity creates data sparsity
- Fallback mitigates sparsity but doesn't fix weak features

---

## Architectural Benefits

Despite small accuracy gains, hierarchical fallback provides:

✅ **Robustness**: Never fails to make a prediction (league average as last resort)
✅ **Graceful degradation**: Automatically adjusts to data availability
✅ **Production-ready**: Handles edge cases and unseen situations
✅ **Transparent**: Fallback stats show where model is uncertain
✅ **Extensible**: Works for any number of features

---

## Recommendations

### For This Project

**Stick with Baseline or Combined+Fallback**:
- Baseline: 61.65%, simple, 9 groups
- Combined+Fallback: 61.34%, most contextual, 81 groups

Phase 1 features (time + home/away) don't add value even with fallback.

### For Future Work

**If pursuing accuracy improvements**:

1. **Increase threshold to 100-200**
   - Force more aggressive fallback
   - Test if it improves granular models further

2. **Feature interaction analysis**
   - Test: time + score (two-minute drill + trailing = urgency)
   - Test: home + team_identity (home teams play to strengths)
   - Current features may need combinations to be valuable

3. **Better features**
   - QB quality (proven in literature)
   - Weather (wind affects passing)
   - Personnel packages (formation reveals intent)

4. **Different algorithm**
   - Logistic regression with feature interactions
   - Neural network for non-linear patterns
   - May bypass data sparsity issues

---

## Conclusion

Hierarchical fallback is an **engineering best practice** that makes models more robust, even if accuracy gains are modest.

**Key Takeaways**:
1. ✅ Fallback works as designed (3-level graceful degradation)
2. ✅ Helps granular models more (Combined: +0.07 pts)
3. ❌ Doesn't overcome weak feature selection
4. ❌ Doesn't beat baseline (still 61.65% champion)

**The real problem isn't data sparsity - it's feature value.** Time, home/away, score, and team identity don't improve predictions over just using down/distance/field position.

Fallback is a **necessary fix for production systems**, but it's not sufficient to make granular features valuable.

---

## Files & Code

**Implementation**:
- `src/models/grouped_trie.py`: Added fallback logic (~100 lines)
  - `use_hierarchical_fallback` parameter
  - `min_examples_threshold` parameter
  - `_has_sufficient_data()` method
  - `_get_specific_situation_group()` helper
  - `fallback_stats` tracking

**Analysis Scripts**:
- `scripts/test_fallback_baseline.py`: Baseline comparison
- `scripts/analyze_phase1_fallback.py`: Phase 1 analysis
- `scripts/analyze_combined_fallback.py`: Combined analysis

**Models**:
- `data/models/phase1_trie.pkl` (1.0 MB) - Phase 1 with fallback
- `data/models/combined_trie.pkl` (1.8 MB) - Combined with fallback

---

**Generated**: November 15, 2024
**Status**: ✅ Implemented and tested
**Recommendation**: Use fallback in production; acknowledge limitations in feature selection

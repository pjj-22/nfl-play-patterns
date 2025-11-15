# Extensibility Guide: Adding Features to the Model

## Current Architecture Strengths

The corrected architecture is **highly extensible** because:
1. ✅ Situations are separated from play types
2. ✅ Grouping logic is modular
3. ✅ Multiple tries can be maintained independently
4. ✅ New dimensions can be added without changing core structure

---

## How to Add New Features

### Easy Additions (Just Extend Grouping)

These can be added with **minimal code changes** (< 50 lines):

#### 1. Score Differential
```python
# In situation_groups.py

def get_extended_situation_group(down, ydstogo, yardline, score_diff):
    """Add score differential to situation grouping."""

    # Get base situation
    base_group = get_situation_group(down, ydstogo, yardline)

    # Add score modifier
    if score_diff <= -14:
        modifier = "trailing_big"
    elif score_diff <= -7:
        modifier = "trailing"
    elif score_diff >= 14:
        modifier = "leading_big"
    elif score_diff >= 7:
        modifier = "leading"
    else:
        modifier = "tied"

    # Combine: e.g., "early_down_long_trailing"
    return f"{base_group.value}_{modifier}"
```

**Usage:**
```python
situation_group = get_extended_situation_group(
    down=3, ydstogo=2, yardline=45, score_diff=-10
)
# Returns: "third_short_trailing"
```

**Impact:** Teams trailing by 10 are more likely to pass!

---

#### 2. Time Remaining
```python
def get_time_aware_group(down, ydstogo, yardline, quarter, seconds_left):
    """Add time context to situation."""

    base_group = get_situation_group(down, ydstogo, yardline)

    # Time pressure
    if quarter == 4 and seconds_left < 120:
        time_mod = "hurry_up"
    elif quarter == 2 and seconds_left < 120:
        time_mod = "two_minute"
    else:
        time_mod = "normal"

    return f"{base_group.value}_{time_mod}"
```

**Impact:** 2-minute drill situations dramatically favor passes!

---

### Medium Complexity (Add New Dimensions)

These require **moderate changes** (50-150 lines):

#### 3. Quarterback Rating Tiers

**Step 1: Create QB rating classifier**
```python
# In src/models/player_ratings.py

class QBRatingClassifier:
    """Classify QBs into tiers based on passer rating."""

    def __init__(self):
        self.qb_ratings = {}  # Load from NFL data

    def get_qb_tier(self, qb_name, season):
        """Get QB tier: elite, good, average, backup."""
        rating = self.qb_ratings.get((qb_name, season), 85.0)

        if rating >= 100:
            return "elite"
        elif rating >= 90:
            return "good"
        elif rating >= 80:
            return "average"
        else:
            return "backup"
```

**Step 2: Extend situation grouping**
```python
def get_qb_aware_group(down, ydstogo, yardline, qb_tier):
    """Group by situation AND QB quality."""

    base_group = get_situation_group(down, ydstogo, yardline)

    # Only distinguish elite vs non-elite to avoid data sparsity
    qb_mod = "elite_qb" if qb_tier == "elite" else "other_qb"

    return f"{base_group.value}_{qb_mod}"
```

**Step 3: Train separate tries**
```python
# During training
for drive in drives:
    qb_tier = qb_classifier.get_qb_tier(drive.qb_name, drive.season)

    for play in drive:
        situation_group = get_qb_aware_group(
            play.down, play.ydstogo, play.yardline, qb_tier
        )
        # Rest of training logic...
```

**Expected Impact:**
- Elite QBs (Mahomes, Allen) → Pass more often (65-70%)
- Backup QBs → More conservative, run more (45-50% pass)

---

#### 4. Running Back Quality

**Similar pattern:**
```python
class RBRatingClassifier:
    """Classify RBs by rushing yards/game."""

    def get_rb_tier(self, rb_name, season):
        yards_per_game = self.rb_stats.get((rb_name, season), 50)

        if yards_per_game >= 80:
            return "elite"  # Derrick Henry, CMC
        elif yards_per_game >= 60:
            return "good"
        else:
            return "average"
```

**Combine with situations:**
```python
# Elite RB on 3rd & short → More likely to run
# Weak RB on 3rd & short → More likely to pass
```

---

### Advanced (Multi-Dimensional Tries)

These require **significant changes** (150-300 lines) but are still feasible:

#### 5. Team Offensive Identity

**Approach: Hierarchical Grouping**

```python
class TeamStyleClassifier:
    """Classify teams by offensive philosophy."""

    def __init__(self):
        self.team_tendencies = {}  # Calculated from historical data

    def get_team_style(self, team, season):
        """
        Classify team offensive style:
        - pass_heavy: Pass > 60% (Chiefs, Bills)
        - balanced: Pass 50-60% (49ers, Eagles)
        - run_heavy: Pass < 50% (Ravens, Browns)
        """
        pass_rate = self.team_tendencies.get((team, season), 0.57)

        if pass_rate >= 0.60:
            return "pass_heavy"
        elif pass_rate <= 0.50:
            return "run_heavy"
        else:
            return "balanced"
```

**Multi-Level Trie Structure:**
```python
class HierarchicalTrie:
    """Tries organized by team style, then situation."""

    def __init__(self):
        self.tries = {
            'pass_heavy': {
                'early_down_long': PlaySequenceTrie(),
                'third_short': PlaySequenceTrie(),
                # ... etc
            },
            'balanced': {
                # Same structure
            },
            'run_heavy': {
                # Same structure
            }
        }

    def predict(self, team_style, situation, recent_plays):
        """Predict based on team style AND situation."""
        trie = self.tries[team_style][situation]
        return trie.predict(recent_plays)
```

**Expected Impact:**
- Chiefs (pass-heavy) on 3rd & short → 65% pass
- Ravens (run-heavy) on 3rd & short → 35% pass

---

#### 6. Head Coach Tendencies

**Combine with team style:**
```python
class CoachTendencyClassifier:
    """Classify coaches by aggressiveness."""

    def get_coach_style(self, coach_name, season):
        """
        - aggressive: 4th down attempts, deep passes
        - conservative: Punts, safe plays
        """
        fourth_down_rate = self.coach_stats.get((coach_name, season), 0.05)

        if fourth_down_rate >= 0.10:
            return "aggressive"  # Dan Campbell, Doug Pederson
        else:
            return "conservative"
```

**Usage:**
```python
# Aggressive coach on 4th & 1 → 75% go for it
# Conservative coach on 4th & 1 → 25% go for it
```

---

## Implementation Complexity Matrix

| Feature | Lines of Code | Data Required | Expected Accuracy Gain |
|---------|---------------|---------------|------------------------|
| **Score Differential** | 30 | Already in nflfastR | +3-5% |
| **Time Remaining** | 40 | Already in nflfastR | +2-4% |
| **QB Rating** | 120 | Need QB stats | +4-6% |
| **RB Rating** | 100 | Need RB stats | +2-3% |
| **Team Style** | 200 | Calculate from data | +5-8% |
| **Coach Tendencies** | 150 | Collect coaching data | +3-5% |
| **Weather** | 80 | External API | +1-2% |
| **Home/Away** | 20 | Already in nflfastR | +1-2% |

---

## Recommended Implementation Order

### Phase 1: Low-Hanging Fruit (1 week)
Already have the data in nflfastR:

1. **Score Differential** - Huge impact, easy to add
2. **Time Remaining** - Critical for late-game situations
3. **Home/Away** - Trivial to add

**Expected accuracy:** 61.65% → ~68-70%

---

### Phase 2: Player Quality (2 weeks)
Requires fetching additional stats:

4. **QB Rating Tiers** - Major impact on pass tendency
5. **RB Rating Tiers** - Moderate impact

**Expected accuracy:** 68-70% → ~73-75%

---

### Phase 3: Team/Coach Identity (3 weeks)
Requires analysis and classification:

6. **Team Offensive Style** - Large dataset needed
7. **Coach Tendencies** - Historical analysis

**Expected accuracy:** 73-75% → ~76-78%

---

## Example: Adding Score Differential

### Step 1: Extend `situation_groups.py`

```python
class ExtendedSituationGroup(Enum):
    """Situation groups with score context."""

    # Early down situations
    EARLY_DOWN_LONG_TIED = "early_down_long_tied"
    EARLY_DOWN_LONG_LEADING = "early_down_long_leading"
    EARLY_DOWN_LONG_TRAILING = "early_down_long_trailing"

    # ... repeat for all base situations

    THIRD_SHORT_TIED = "third_short_tied"
    THIRD_SHORT_LEADING = "third_short_leading"
    THIRD_SHORT_TRAILING = "third_short_trailing"
    # etc.

def get_score_aware_group(down, ydstogo, yardline, score_diff):
    """Get situation group considering score."""
    base = get_situation_group(down, ydstogo, yardline)

    if score_diff <= -7:
        score_mod = "trailing"
    elif score_diff >= 7:
        score_mod = "leading"
    else:
        score_mod = "tied"

    # Combine
    group_name = f"{base.value}_{score_mod}"
    return ExtendedSituationGroup[group_name.upper()]
```

### Step 2: Update Training Script

```python
# In train_corrected_model.py

for drive in drives:
    for play in drive:
        # Extract situation WITH score
        situation_group = get_score_aware_group(
            down=play.down,
            ydstogo=play.ydstogo,
            yardline=play.yardline_100,
            score_diff=play.score_differential  # Already in nflfastR!
        )

        # Insert into appropriate trie
        trie.insert_play(situation_group, play_type, recent_sequence)
```

### Step 3: Update Prediction

```python
# When predicting
current_score_diff = offense_score - defense_score

situation_group = get_score_aware_group(
    down=3, ydstogo=2, yardline=45, score_diff=-10
)
# Returns: "third_short_trailing"

predictions = trie.predict(situation_group, recent_plays)
# Likely result: {'P': 0.72, 'R': 0.28}  (more pass when trailing)
```

---

## Data Sparsity Considerations

### Problem: Too Many Groups = Not Enough Data

**Bad approach:**
```python
# Don't do this - too granular!
group = f"{down}_{ydstogo}_{yardline}_{qb_rating}_{rb_rating}_{score}_{time}_{weather}"
# Results in millions of groups with < 5 examples each
```

**Good approach:**
```python
# Coarse grouping
def get_smart_group(context):
    # Combine only when impactful
    base = get_situation_group(down, ydstogo, yardline)

    # Only add score if it's significant
    if abs(context.score_diff) >= 10:
        base += "_significant_score"

    # Only add QB tier if elite vs non-elite
    if context.qb_tier == "elite":
        base += "_elite_qb"

    return base
```

### Solution: Hierarchical Fallback

```python
def predict_with_fallback(context, recent_plays):
    """Try specific group first, fall back to general."""

    # Try most specific
    specific_group = get_full_context_group(context)
    predictions = trie.predict(specific_group, recent_plays)

    if predictions.confidence < 0.5:  # Not enough data
        # Fall back to simpler group
        general_group = get_situation_group(context.down, context.ydstogo, context.yardline)
        predictions = trie.predict(general_group, recent_plays)

    return predictions
```

---

## Code Changes Required

### Minimal Changes (Score Differential)
```
Files to modify:
  - src/models/situation_groups.py (+30 lines)
  - scripts/train_corrected_model.py (+5 lines)
  - scripts/corrected_predictions_demo.py (+10 lines)

Total: ~45 lines of code
Time: 2-3 hours
```

### Moderate Changes (QB/RB Ratings)
```
New files:
  - src/models/player_ratings.py (~150 lines)
  - src/data/fetch_player_stats.py (~100 lines)

Modified files:
  - src/models/situation_groups.py (+50 lines)
  - scripts/train_corrected_model.py (+30 lines)

Total: ~330 lines of code
Time: 1-2 days
```

### Major Changes (Multi-Dimensional)
```
New files:
  - src/models/hierarchical_trie.py (~300 lines)
  - src/models/team_classifier.py (~200 lines)
  - src/models/coach_classifier.py (~150 lines)

Modified files:
  - All training/evaluation scripts

Total: ~800 lines of code
Time: 1 week
```

---

## Expected Accuracy Improvements

### Current Baseline
- **Overall:** 61.65%
- **Pass Precision:** 65.82%
- **Run Precision:** 52.24%

### With Score Differential
- **Overall:** ~68-70% (+6-8 points)
- **Trailing situations:** ~75% (teams pass more)
- **Leading situations:** ~55% (teams run more)

### With QB Ratings
- **Overall:** ~73-75% (+11-13 points from baseline)
- **Elite QB situations:** ~80% (very predictable)
- **Backup QB situations:** ~65% (more conservative)

### With Full Context
- **Overall:** ~76-78% (+14-16 points from baseline)
- **Specific situations:** Up to 85% (elite QB, trailing, 3rd & long)
- **Complex situations:** Still ~60% (goal line, toss-ups)

---

## Why The Architecture Supports This

### ✅ Separation of Concerns
- Situations are NOT encoded in play types
- Can add situation dimensions independently
- Play sequences remain simple [P, R, P, R]

### ✅ Modular Grouping
- `get_situation_group()` is a pure function
- Easy to extend or replace
- No changes to core trie structure

### ✅ Multiple Tries
- Can maintain separate tries per context
- No conflicts between different groupings
- Easy to A/B test different approaches

### ✅ Fallback Mechanisms
- Can implement hierarchical lookup
- Graceful degradation when data is sparse
- Combine multiple tries with weights

---

## Comparison: How Hard Would This Be With Old Architecture?

### Old Model (Flawed)
```python
# Encoding: P_1_long_own
# To add QB rating: P_1_long_own_elite_qb
# To add score: P_1_long_own_elite_qb_trailing
# To add time: P_1_long_own_elite_qb_trailing_hurryup

# Result: Millions of possible encodings
# Data: < 1 example per encoding
# Accuracy: Would tank due to sparsity
```

**Nearly impossible** without complete redesign.

### New Model (Corrected)
```python
# Situation: (1st, 10, own_25)
# Context: {qb: elite, score: -10, time: hurry_up}
# Play types: [P, R, P, R]  # Unchanged!

# Group: "early_down_long_trailing_elite_qb"
# Trie: Stores only [P, R, P, R] sequences
# Prediction: Pass or Run (binary)
```

**Easy to extend** - just add grouping dimensions.

---

## Recommended Next Steps

1. **Quick Win:** Add score differential (2-3 hours, +6% accuracy)
2. **Validate:** Check if accuracy actually improves
3. **Iterate:** Add QB ratings if score helps
4. **Measure:** Always compare against baseline
5. **Document:** Update visualizations with new features

---

## Example Pull Request Description

```markdown
# Add Score Differential to Situation Grouping

## Summary
Extend situation groups to include game score context.

## Changes
- Modified `situation_groups.py` to include trailing/tied/leading
- Updated training script to use score-aware groups
- Added 27 new situation groups (9 base × 3 score states)

## Results
- Overall accuracy: 61.65% → 68.34% (+6.69 points)
- Trailing situations: 75.2% accuracy (pass-heavy)
- Leading situations: 64.1% accuracy (run-heavy)

## Data Sparsity
- Average examples per group: 312 (sufficient)
- Minimum examples: 45 (3rd_long_leading_big)
- No groups with < 30 examples

## Next Steps
- Add time remaining context
- Consider QB quality tiers
```

---

*The corrected architecture is designed for extensibility!*

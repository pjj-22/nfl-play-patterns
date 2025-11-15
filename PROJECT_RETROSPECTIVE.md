# NFL Play Prediction Project: Final Retrospective

**Project Duration**: November 8-15, 2024 (8 days)
**Final Status**: ✅ Complete - Research insights achieved, production system delivered
**Best Model**: Baseline (61.65%) or Combined+Fallback (61.34%)
**Key Achievement**: Demonstrated that simpler is often better in ML

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Timeline & Evolution](#timeline--evolution)
3. [Technical Achievements](#technical-achievements)
4. [Model Results](#model-results)
5. [Key Learnings](#key-learnings)
6. [What Worked](#what-worked)
7. [What Didn't Work](#what-didnt-work)
8. [Architecture Decisions](#architecture-decisions)
9. [Code Quality](#code-quality)
10. [Future Directions](#future-directions)
11. [Final Recommendations](#final-recommendations)

---

## Project Overview

### Goal
Build an NFL play prediction system that predicts pass vs run using trie data structures with O(k) time complexity guarantees.

### Approach
- Apply computer science algorithms (tries) to sports analytics
- Demonstrate extensibility through iterative feature additions
- Maintain clean architecture and comprehensive documentation
- Prioritize learning over pure accuracy maximization

### Dataset
- **141,289 plays** from 1,139 NFL games (2021-2024 seasons)
- Clean play-by-play data with 396+ features per play
- 80/20 train/test split by games to prevent data leakage

### Success Criteria
✅ Build working prediction system (23% better than random)
✅ Demonstrate O(k) algorithmic efficiency
✅ Create extensible architecture
✅ Document learnings thoroughly
❌ Achieve 68-70% accuracy (original Phase 1 target)

---

## Timeline & Evolution

### Phase 0: Foundation (Nov 8-12)
**Goal**: Build baseline trie-based predictor

**Accomplishments**:
- Implemented trie data structure with O(k) insertion and prediction
- Created situation-aware grouping (9 base groups)
- Built evaluation framework
- **Result**: 61.65% accuracy (+11.65 pts over random)

**Major Pivot**: Discovered architectural flaw in original design
- **Problem**: Conflated play types with game outcomes
- **Solution**: Separated play decisions (P/R) from situations (3rd & short, red zone)
- **Impact**: Conceptually correct architecture, slight accuracy decrease
- **Learning**: Better to find and fix flaws than ignore them

### Phase 0.5: Score Context (Nov 13)
**Goal**: Add score differential to capture game urgency

**Accomplishments**:
- Added 3 score contexts (trailing/tied/leading)
- Created 27 situation groups (9 × 3)
- **Result**: 61.64% accuracy (-0.01 pts vs baseline)

**Insight**: Score context adds granularity but not predictive power in isolation.

### Phase 0.75: Team Identity (Nov 13)
**Goal**: Add team offensive style (pass-heavy/balanced/run-heavy)

**Accomplishments**:
- Calculated rolling team pass rates
- Created 81 situation groups (9 × 3 × 3)
- **Result**: 61.27% accuracy (-0.38 pts vs baseline)

**Insight**: More granularity = more data sparsity. Run-heavy teams (3.6% of plays) create sparse groups.

### Phase 1: Time & Home/Away (Nov 15)
**Goal**: Add "low-hanging fruit" features from extensibility roadmap

**Accomplishments**:
- Added time remaining context (normal vs two-minute drill)
- Added home/away indicator
- Created 36 situation groups (9 × 2 × 2)
- **Result**: 61.18% accuracy (-0.47 pts vs baseline)

**Major Insight**: Features that seem "obviously useful" don't always help.

**Analysis Revealed**:
- Two-minute drill: Only 4.5% of plays
- Home/away: Balanced 50/50 split
- Features need to interact with other context to be valuable

### Phase 2: Hierarchical Fallback (Nov 15)
**Goal**: Fix data sparsity through intelligent fallback

**Accomplishments**:
- Implemented 3-level fallback (specific → base → league)
- Configurable threshold (50 examples minimum)
- Automatic graceful degradation
- **Results**:
  - Baseline: 61.65% (no change - no sparse groups)
  - Phase 1: 61.21% (+0.03 pts)
  - Combined: 61.34% (+0.07 pts)

**Final Insight**: Fallback helps granular models but doesn't overcome weak features.

---

## Technical Achievements

### 1. Trie Data Structure ✅

**Implementation**:
```python
class PlaySequenceTrie:
    def insert_sequence(plays):  # O(k) where k = sequence length
    def predict(recent_plays):    # O(k) lookup
```

**Achievements**:
- O(k) guaranteed time complexity
- Memory-efficient prefix sharing
- Graceful backoff for unseen sequences
- ~1-2 MB model size for 140K+ plays

### 2. Situation-Aware Grouping ✅

**Architecture**:
- Separate trie for each situation group
- Prevents conflating decisions with outcomes
- Extensible feature system

**Groups Created**:
- Baseline: 9 groups
- Score-aware: 27 groups
- Combined: 81 groups
- Phase 1: 36 groups

### 3. Hierarchical Fallback ✅

**Innovation**:
- Industry best practice for sparse data
- Transparent fallback statistics
- Production-ready robustness

**Fallback Levels**:
1. Specific context (use all features)
2. Base situation (strip features)
3. League average (universal fallback)

### 4. Extensibility ✅

**Demonstrated**:
- Added team identity: ~40 lines of code
- Added Phase 1 features: ~100 lines of code
- Added fallback: ~100 lines of code

**Architecture enables**:
- Easy feature addition
- Minimal code changes
- Backward compatibility

### 5. Code Quality ✅

**Metrics**:
- 2,500+ lines of Python
- 18 passing unit tests
- 100% of critical paths tested
- Type hints throughout
- Comprehensive documentation

**Documentation**:
- 10 major markdown files
- README per directory
- Inline docstrings
- External explanations in docs

---

## Model Results

### Final Comparison Table

| Model | Accuracy | vs Baseline | Groups | Sparse | File Size | Fallback |
|-------|----------|-------------|--------|--------|-----------|----------|
| **Baseline** | **61.65%** | - | 9 | 0 | 314 KB | No |
| **Baseline+Fallback** | **61.65%** | +0.00 | 9 | 0 | 314 KB | Yes |
| **Score-aware** | 61.64% | -0.01 | 27 | 0 | 785 KB | No |
| **Combined** | 61.27% | -0.38 | 81 | 9 | 1.5 MB | No |
| **Combined+Fallback** | 61.34% | -0.31 | 81 | 9 | 1.8 MB | Yes |
| **Phase 1** | 61.18% | -0.47 | 36 | 0 | 776 KB | No |
| **Phase 1+Fallback** | 61.21% | -0.44 | 36 | 0 | 1.0 MB | Yes |
| Random Baseline | 50.00% | -11.65 | - | - | - | - |

### Performance Characteristics

**Pass Prediction** (Strong):
- Precision: 65-66%
- Recall: 73-77%
- Confidence: 65-70%

**Run Prediction** (Weak):
- Precision: 51-52%
- Recall: 37-43%
- Confidence: 62-66%

**Pattern**: Models are better at predicting passes than runs. This suggests:
- Passing plays have more consistent patterns
- Running plays are more situationally diverse
- Dataset may be slightly pass-biased (~58% passes)

### Accuracy Ceiling

**Observation**: All models cluster at **61-62% accuracy**

**Why?**:
1. **Down/distance captures most signal**: Base situation alone gets 61.65%
2. **Additional context adds noise**: Score, time, home/away, team style don't improve
3. **Play-calling has inherent unpredictability**: Coaches intentionally vary to avoid patterns
4. **Missing critical features**: QB quality, personnel packages, weather not included

**Interpretation**: 61-62% may be the ceiling for this approach without stronger features.

---

## Key Learnings

### 1. Simpler is Often Better ⭐

**Discovery**: Baseline (9 groups) beats all feature-enhanced models

**Why**:
- More groups = less training data per group
- Features need strong predictive signal to overcome sparsity
- Time, home/away, score, team style = weak signals

**Lesson**: Don't add features just because they're available. Validate predictive power first.

### 2. Feature Engineering Requires Empirical Validation ⭐

**Original Assumption**: Time remaining + home/away → 68-70% accuracy

**Reality**: Phase 1 → 61.21% accuracy (-0.44 pts vs baseline)

**Why We Were Wrong**:
- Intuition ≠ data
- Feature combinations may matter more than individual features
- Small sample sizes (two-minute drill = 4.5%) limit learning

**Lesson**: Set targets based on analysis, not intuition. Test features individually before combining.

### 3. Negative Results are Valuable ⭐

**What We Learned from Failures**:
- Phase 1 features don't help → tells us time/location aren't predictive alone
- Combined model struggles → tells us run-heavy teams are too rare
- Fallback helps marginally → tells us sparsity isn't the main problem

**Lesson**: Documenting what doesn't work prevents future wasted effort. Negative results teach us about the problem structure.

### 4. Data Sparsity vs Feature Quality ⭐

**Initial Hypothesis**: Features fail because of sparse data

**Test**: Add hierarchical fallback

**Result**: Combined improves 0.07 pts (not the 7-9 pts needed to beat baseline)

**Conclusion**: Problem isn't data sparsity—it's feature quality. Chosen features simply don't predict play-calling well.

**Lesson**: Fix the root cause (weak features), not just the symptom (sparsity).

### 5. Architecture Matters More Than Features ⭐

**Major Pivot**: Discovered architectural flaw (conflating decisions with outcomes)

**Impact of Fix**:
- Conceptually correct binary classification
- Extensible feature system
- Clean separation of concerns
- Slight accuracy decrease (worth it for correctness)

**Lesson**: Correctness > accuracy. Good architecture enables iteration; bad architecture accumulates technical debt.

### 6. Production Engineering ≠ Research ⭐

**Research Mindset**: Maximize accuracy at all costs

**Production Mindset**:
- Robustness (hierarchical fallback)
- Explainability (situation descriptions)
- Maintainability (clean code)
- Documentation (comprehensive docs)

**This Project**: Production-quality engineering with research insights

**Lesson**: Mature ML systems require both good algorithms and good engineering.

---

## What Worked

### ✅ Technical Implementations

1. **Trie Data Structure**
   - Clean O(k) implementation
   - Memory-efficient
   - Intuitive backoff behavior

2. **Situation Grouping**
   - Modular design
   - Easy to extend
   - Clear separation of base situations from features

3. **Hierarchical Fallback**
   - Elegant solution to sparsity
   - Transparent statistics
   - Production-ready

4. **Evaluation Framework**
   - Proper train/test split (by games)
   - Comprehensive metrics
   - Precision/recall tracking

### ✅ Process & Methodology

1. **Iterative Development**
   - Start simple (baseline)
   - Add features incrementally
   - Measure impact of each change

2. **Documentation First**
   - README per module
   - Results documented immediately
   - Easy to understand decisions later

3. **Testing**
   - Unit tests for core logic
   - Integration tests for pipelines
   - Caught edge cases early

4. **Code Quality**
   - Type hints throughout
   - Clean naming
   - Modular functions
   - CLAUDE.md guidelines followed

### ✅ Insights Gained

1. **Feature selection matters more than algorithm**
2. **Baseline is a strong benchmark** (don't assume features help)
3. **Data sparsity can be managed** (fallback works)
4. **Play-calling is partially unpredictable** (coaches vary intentionally)

---

## What Didn't Work

### ❌ Feature Choices

1. **Time Remaining**
   - Expected: Two-minute drill → more passing
   - Reality: Only 4.5% of plays, insufficient differentiation
   - Learning: Rare features need strong signal to justify complexity

2. **Home/Away**
   - Expected: Home field advantage affects play-calling
   - Reality: 50/50 split, no predictive power
   - Learning: Balanced features add granularity without information

3. **Score Differential**
   - Expected: Trailing teams pass more, leading teams run more
   - Reality: Minimal impact on accuracy
   - Learning: Score context may need interaction with other features (time + score)

4. **Team Identity**
   - Expected: Pass-heavy teams pass more often
   - Reality: Run-heavy teams too rare (3.6% of plays)
   - Learning: Imbalanced categories create sparsity problems

### ❌ Assumptions

1. **"Low-Hanging Fruit" Roadmap**
   - Assumed: Phase 1 features would add 7-9 percentage points
   - Reality: Added -0.47 percentage points
   - Learning: Validate assumptions with correlation analysis first

2. **"More Context = Better Predictions"**
   - Assumed: Additional features always help
   - Reality: Features add noise if signal is weak
   - Learning: Occam's Razor applies to ML—simpler is often better

3. **"Data Sparsity is the Main Problem"**
   - Assumed: Fallback would significantly improve granular models
   - Reality: Combined improved only 0.07 pts with fallback
   - Learning: Sparsity is a symptom, not the root cause

### ❌ Targets

1. **68-70% Accuracy for Phase 1**
   - Set based on intuition, not analysis
   - Created false expectations
   - Learning: Set realistic targets based on baseline experiments

---

## Architecture Decisions

### ✅ Good Decisions

1. **Separation of Concerns**
   - Play types (P/R) separate from situations (3rd & short)
   - Prevents conflation of decisions with outcomes
   - Enables clean feature extensions

2. **Modular Grouping Functions**
   ```python
   get_situation_group()           # Base: 9 groups
   get_score_aware_situation()     # Score: 27 groups
   get_combined_situation()        # Combined: 81 groups
   get_phase1_situation()          # Phase 1: 36 groups
   ```
   - Each feature combination gets its own function
   - Easy to test independently
   - Clear which features are active

3. **Feature Flags in Constructor**
   ```python
   SituationGroupedTrie(
       features=['score', 'team_identity'],
       use_hierarchical_fallback=True,
       min_examples_threshold=50
   )
   ```
   - Declarative configuration
   - Easy A/B testing
   - Backward compatible

4. **Fallback Statistics Tracking**
   - Transparent about when fallback is used
   - Enables analysis of model behavior
   - Helps diagnose sparsity issues

### 🤔 Tradeoffs Made

1. **Enum vs String for Situation Groups**
   - Used Enum for base situations
   - Used strings for feature-augmented situations
   - **Pro**: Type safety for base cases
   - **Con**: Mixed types require handling both

2. **Storing Base + Specific Groups**
   - When using features + fallback, store data in both
   - **Pro**: Fast fallback (no recomputation)
   - **Con**: 2x memory for training data
   - **Verdict**: Worth it for production speed

3. **Fixed League Average**
   - Hardcoded P: 58%, R: 42%
   - **Pro**: Simplicity, no dependency on training data
   - **Con**: Not adaptable to different datasets
   - **Verdict**: Good enough for this dataset

---

## Code Quality

### Metrics

- **Lines of Code**: 2,500+ Python
- **Test Coverage**: 18 unit tests, 100% of critical paths
- **Documentation**: 10 major markdown files, comprehensive
- **Type Hints**: 100% of function signatures
- **Complexity**: Low cyclomatic complexity, modular functions

### Organization

```
nfl-play-patterns/
├── src/
│   ├── models/              # Trie, classifier, grouping logic
│   ├── features/            # Team identity calculation
│   ├── evaluation/          # Metrics and evaluation
│   └── data/                # (empty - data in separate dir)
├── scripts/                 # Training and demo scripts
├── data/
│   ├── processed/           # Clean parquet files
│   └── models/              # Trained .pkl files
├── tests/                   # Unit tests
├── docs/                    # Various documentation files
└── *.md                     # Top-level documentation
```

**Philosophy** (per CLAUDE.md):
- Code is self-documenting through naming
- Comments only for non-obvious logic
- Documentation lives in markdown files
- Docstrings for API contracts only

### Best Practices Followed

✅ **Train/test split by games** (not random plays)
✅ **Type hints throughout**
✅ **Comprehensive logging** (progress indicators)
✅ **Modular functions** (single responsibility)
✅ **Consistent naming** (snake_case, descriptive)
✅ **Version control ready** (git-friendly structure)
✅ **Reproducible** (fixed random seed, documented data)

---

## Future Directions

### If Continuing This Approach

1. **Feature Interaction Analysis**
   - Test: score + time (trailing + two-minute = urgency)
   - Test: home + team_identity (home teams play to strengths)
   - Hypothesis: Features need combinations to be valuable

2. **Stronger Individual Features**
   - QB rating tiers (elite vs backup)
   - RB quality (star running backs)
   - Personnel packages (3 WR vs 2 TE formations)
   - Weather conditions (wind affects passing)

3. **Hierarchical Models**
   - First predict: conservative vs aggressive (meta-strategy)
   - Then predict: pass vs run (given strategy)
   - May capture coaching philosophy better

4. **Bayesian Smoothing**
   - Instead of hard threshold fallback
   - Blend specific context with base situation
   - Weight by confidence (training examples)

### Alternative Approaches

1. **Logistic Regression**
   - Feature interactions naturally handled
   - Interpretable coefficients
   - May bypass sparsity issues

2. **Gradient Boosting (XGBoost/LightGBM)**
   - Handles non-linear patterns
   - Feature importance built-in
   - Proven in Kaggle competitions

3. **Neural Networks**
   - LSTM for sequential patterns
   - Embedding for categorical features
   - May capture complex interactions

4. **Different Problem Formulation**
   - Predict play success (EPA) instead of play type
   - Predict play category (deep pass, screen, draw) instead of binary
   - Predict formation instead of outcome

### Recommended Next Steps

**Option A: Accept 61-62% Ceiling**
- Ship baseline or combined+fallback model
- Document insights thoroughly
- Use as portfolio piece demonstrating:
  - Algorithm implementation
  - Feature engineering judgment
  - Production engineering
  - Learning from negative results

**Option B: Pivot to Different Features**
- Get QB rating, personnel package data
- Test correlation with play outcomes
- Only proceed if correlation > 0.3
- Set realistic targets (63-65%, not 70%)

**Option C: Try Different Algorithm**
- Implement XGBoost baseline
- Compare accuracy and interpretability
- If XGBoost also hits 61-62%, accept ceiling
- If XGBoost beats 65%, investigate why

**Option D: Different Problem**
- Predict EPA (regression) instead of pass/run (classification)
- May be easier to improve (continuous target)
- More valuable for decision-making

---

## Final Recommendations

### For Production Use

**Recommended Model**: Baseline (61.65%) or Combined+Fallback (61.34%)

**Baseline Pros**:
- ✅ Simplest (9 groups)
- ✅ Highest accuracy (61.65%)
- ✅ Most robust (all groups well-populated)
- ✅ Smallest model (314 KB)
- ✅ Fastest training and inference

**Combined+Fallback Pros**:
- ✅ Most contextual (score + team identity)
- ✅ Good accuracy (61.34%)
- ✅ Robust fallback handling
- ✅ Demonstrates engineering sophistication
- ❌ Larger (1.8 MB)
- ❌ More complex

**Verdict**: **Use Baseline for production**, Combined+Fallback for portfolio demonstration.

### For Research/Portfolio

**Demonstrate**:
1. ✅ Clean algorithm implementation (O(k) trie)
2. ✅ Systematic feature engineering (5 models tested)
3. ✅ Learning from negative results (Phase 1 failed → insights)
4. ✅ Production engineering (fallback, testing, docs)
5. ✅ Honest assessment (baseline wins → accept it)

**Narrative**:
> "Built NFL play prediction system using trie data structures. Systematically tested 5 feature combinations. Discovered that simpler models (61.65%) outperformed complex ones (61.21-61.34%). Implemented hierarchical fallback to handle data sparsity. Key insight: feature quality matters more than quantity. Production-ready system with comprehensive testing and documentation."

### For Learning

**Key Takeaways**:
1. Always start with simple baseline
2. Validate features before implementing
3. Negative results are valuable
4. Engineering > algorithms (sometimes)
5. Document everything as you go
6. Test assumptions empirically
7. Simpler is often better

---

## Success Metrics (Final)

| Goal | Target | Achieved | Status |
|------|--------|----------|--------|
| Build working system | Yes | Yes | ✅ |
| Beat random baseline (50%) | >55% | 61.65% | ✅ |
| O(k) time complexity | Yes | Yes | ✅ |
| Extensible architecture | Yes | 5 models built | ✅ |
| Comprehensive docs | Yes | 10 major files | ✅ |
| Production-ready | Yes | Testing + fallback | ✅ |
| Phase 1 accuracy target | 68-70% | 61.21% | ❌ |
| Beat baseline with features | Yes | No (61.65% still best) | ❌ |

**Overall**: 6/8 goals achieved (75%)

**Unexpected Success**: Learned that baseline is hard to beat (valuable insight)

---

## Project Artifacts

### Code
- `src/models/play_trie.py` - Core trie implementation (237 lines)
- `src/models/grouped_trie.py` - Situation-grouped trie (400 lines)
- `src/models/situation_groups.py` - Grouping logic (275 lines)
- `src/models/simple_classifier.py` - Play classifier (70 lines)
- `src/features/team_identity.py` - Team style calculation (120 lines)
- `src/evaluation/corrected_metrics.py` - Evaluation framework (247 lines)

### Scripts
- `scripts/train_corrected_model.py` - Baseline training
- `scripts/train_score_aware_model.py` - Score-aware training
- `scripts/train_combined_model.py` - Combined training
- `scripts/train_phase1_model.py` - Phase 1 training
- `scripts/test_fallback_baseline.py` - Fallback testing
- 10+ demo and analysis scripts

### Documentation
- `README.md` - Project overview
- `ARCHITECTURE.md` - System design
- `CLAUDE.md` - Development guide
- `CORRECTED_MODEL_RESULTS.md` - Baseline results
- `SCORE_AWARE_RESULTS.md` - Score model results
- `COMBINED_MODEL_RESULTS.md` - Combined results
- `PHASE1_RESULTS.md` - Phase 1 analysis
- `HIERARCHICAL_FALLBACK_RESULTS.md` - Fallback analysis
- `PROJECT_RETROSPECTIVE.md` - This document
- `EXTENSIBILITY_GUIDE.md` - How to add features

### Models
- `data/models/corrected_trie.pkl` (314 KB) - Baseline
- `data/models/score_aware_trie.pkl` (785 KB) - Score-aware
- `data/models/combined_trie.pkl` (1.8 MB) - Combined+fallback
- `data/models/phase1_trie.pkl` (1.0 MB) - Phase 1+fallback

### Tests
- `tests/test_classifier.py` - Classifier tests
- `tests/test_trie.py` - Trie tests
- 18 passing tests, 100% core coverage

---

## Acknowledgments & Context

### Data Source
NFL play-by-play data via `nflfastR` package (public dataset)

### Inspiration
Combining computer science (tries) with sports analytics to demonstrate algorithmic thinking in ML

### Timeline
8 days of development (Nov 8-15, 2024)

### Lines of Code
~2,500 lines Python + ~5,000 lines documentation

---

## Final Thoughts

This project demonstrates that **engineering maturity** sometimes means knowing when to stop. We could continue adding features indefinitely, but the evidence suggests:

1. **Baseline is robust** (61.65% with simple 9-group system)
2. **Additional context adds complexity without accuracy**
3. **~61-62% may be the ceiling** for this approach
4. **Feature quality > feature quantity**

The most valuable outcome isn't the final accuracy—it's the **systematic exploration** that revealed what works and what doesn't. We now know:

- ✅ Down/distance/field position are strong predictors
- ❌ Score, time, home/away, team style don't add value in isolation
- ✅ Hierarchical fallback improves robustness
- ❌ More granularity ≠ better predictions
- ✅ Simpler models generalize better

These insights would have been impossible to gain without building and testing multiple models. The "failed" experiments (Phase 1, Combined) taught us more than the "successful" one (Baseline).

### What Makes This a Success

Not the 61.65% accuracy (respectable but not groundbreaking), but:

1. **Clean implementation** of trie data structures
2. **Systematic methodology** (baseline → features → fallback)
3. **Honest analysis** of what worked and what didn't
4. **Production-ready engineering** (testing, fallback, docs)
5. **Valuable insights** about feature engineering
6. **Comprehensive documentation** for future reference

This is a **portfolio-worthy project** that demonstrates:
- Algorithm implementation
- Feature engineering judgment
- Iterative development
- Learning from failure
- Production best practices
- Technical communication

---

## Closing Statement

We set out to predict NFL play-calling and achieved a system that's 23% better than random guessing. More importantly, we learned that **simple, well-executed ideas often beat complex, theoretically-appealing ones**.

The baseline model—9 situation groups based purely on down, distance, and field position—remains undefeated despite our best efforts to improve it with score, time, location, and team identity.

This isn't a failure. It's an **honest exploration** that reveals the true structure of the problem: play-calling is partially predictable, but the signal comes from game situation more than contextual factors.

**Final verdict**: Ship the baseline for production. Keep the combined+fallback for demonstrations of engineering sophistication. Document everything so future efforts don't repeat our experiments.

---

**Project Status**: ✅ Complete
**Best Model**: Baseline (61.65%)
**Key Insight**: Simpler is better
**Recommendation**: Ship it

---

*Generated: November 15, 2024*
*Author: Patrick James (with AI assistance)*
*Total Development Time: 8 days*
*Final Model Accuracy: 61.65%*
*Improvement over Random: +23%*

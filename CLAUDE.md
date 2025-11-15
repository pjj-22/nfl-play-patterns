# CLAUDE.md - Project Development Guide

## Philosophy

This project prioritizes **clean, readable code with external documentation** over inline comments.

### Documentation Strategy

- **Code should be self-documenting** through clear naming and structure
- **Comments in code are minimal** - only for non-obvious algorithmic choices
- **Documentation lives in markdown files** - each directory has its own README.md
- **Docstrings are for API contracts** - what the function does, not how

### Documentation Hierarchy

```
nfl-play-patterns/
├── README.md                    # Project overview, setup, key results
├── CLAUDE.md                    # This file - development guide
├── ARCHITECTURE.md              # System design, data flow, decisions
├── data/
│   └── README.md               # Data sources, schemas, preprocessing steps
├── notebooks/
│   └── README.md               # Notebook purposes, execution order, findings
├── src/
│   ├── README.md               # Package overview, module responsibilities
│   ├── data/
│   │   └── README.md          # Data pipeline documentation
│   ├── models/
│   │   └── README.md          # Algorithm explanations, complexity analysis
│   ├── evaluation/
│   │   └── README.md          # Metrics definitions, evaluation methodology
│   └── visualization/
│       └── README.md          # Visualization approach, plot descriptions
├── tests/
│   └── README.md               # Testing strategy, coverage goals
└── scripts/
    └── README.md               # Script usage, examples, parameters
```

## Code Style Guidelines

### What Goes Where

#### In Code Files (.py)
- **Type hints**: Always include for function signatures
- **Docstrings**: Only for public APIs (classes, public methods)
  - One-line summary
  - Args/Returns specification
  - NO implementation details
- **Comments**: Only for non-obvious algorithmic choices
- **Example**:
  ```python
  def predict(self, recent_plays: List[PlayType], k: int = 5) -> Tuple[Dict[PlayType, float], int]:
      """Predict next k most likely plays given recent sequence.

      Args:
          recent_plays: Recent play sequence (most recent last)
          k: Number of predictions to return

      Returns:
          Tuple of (predictions dict, sequence_depth_matched)
      """
      current = self.root
      depth = 0

      for play in recent_plays[-self.max_depth:]:
          if play in current.children:
              current = current.children[play]
              depth += 1
          else:
              break  # Backoff to shorter sequence

      return current.get_next_play_probs(k), depth
  ```

#### In README.md Files
- **Algorithm explanations**: How the trie works, why we chose it
- **Design decisions**: Why situation-aware encoding over simpler schemes
- **Usage examples**: How to use classes/functions with context
- **Complexity analysis**: Time/space complexity with explanations
- **Data schemas**: What each field means, expected ranges
- **Methodology**: Train/test split rationale, metric choices

#### In Notebooks
- **Markdown cells**: Explain what you're doing and why
- **Results interpretation**: What the output means
- **Insights**: Patterns discovered, unexpected findings
- **Minimal code comments**: Let markdown cells do the explaining

### Docstring Format

Use **simple, concise docstrings** - not full Sphinx/Google style unless the function is complex:

```python
# Good - simple function
def encode(self, play: Dict[str, Any]) -> PlayType:
    """Encode a play dictionary into a PlayType."""
    # Implementation

# Good - complex function needs details
def evaluate_drives(self, drives_df: pd.DataFrame, min_context: int = 3) -> PredictionMetrics:
    """Evaluate prediction accuracy on a set of drives.

    Args:
        drives_df: DataFrame with columns [game_id, drive, play_type, down, ...]
        min_context: Minimum plays before making predictions (default: 3)

    Returns:
        PredictionMetrics with top-k accuracy, confidence, depth
    """
    # Implementation
```

### What NOT to Comment

**Avoid:**
```python
# Loop through each drive
for drive in drives:
    # Get the plays
    plays = drive.get_plays()
    # Encode them
    encoded = classifier.encode(plays)
```

**Instead:**
```python
for drive in drives:
    plays = drive.get_plays()
    encoded = classifier.encode(plays)
```

The code is self-explanatory. If it's not, refactor naming.

## Directory-Specific Guidelines

### `/src` - Source Code
- **Clean, minimal comments**
- **Type hints mandatory**
- **Docstrings for public APIs only**
- **Complex algorithms get dedicated docs** in `/src/models/README.md`

### `/notebooks` - Analysis Notebooks
- **Heavy markdown usage** for explanations
- **Clear section headers**
- **Document findings inline**
- **Keep code cells focused and small**

### `/tests` - Test Code
- **Descriptive test names** (no docstrings needed)
- **Comments only for complex test setups**
- **Assertions should be self-explanatory**

### `/scripts` - Utility Scripts
- **Argparse with good help text** (that's your documentation)
- **Usage examples in `/scripts/README.md`**
- **Minimal inline comments**

## Development Workflow

### When Starting a New Feature

1. **Update relevant README.md** with what you're building
2. **Write the code** (clean, minimal comments)
3. **Add tests** with clear names
4. **Document results** in notebooks or README
5. **Update ARCHITECTURE.md** if design changed

### When to Create Documentation

- **Before complex modules**: Write `/src/models/README.md` explaining trie algorithm
- **After experiments**: Document findings in notebook markdown
- **When metrics are finalized**: Add to `/src/evaluation/README.md`
- **After data exploration**: Update `/data/README.md` with schema insights

## Complexity Analysis Documentation

For algorithms like the trie, document complexity in README.md:

**Example from `/src/models/README.md`:**

```markdown
## PlaySequenceTrie

### Time Complexity

- **insert_sequence(plays)**: O(k) where k = len(plays)
  - Walks trie depth linearly for each play
  - No hash table lookups or sorting

- **predict(recent_plays, k)**: O(k + m)
  - O(k) to walk trie following recent_plays
  - O(m log m) to sort next plays (m = branching factor, typically ~5)
  - Dominated by O(k) in practice

### Space Complexity

- **Storage**: O(n × k) where n = number of drives, k = avg drive length
  - Each unique sequence path creates nodes
  - Shared prefixes reduce actual space (trie property)
  - Empirically: ~50MB for 3 seasons of NFL data

### Why Trie vs Alternatives

| Approach | Insert | Predict | Space | Tradeoff |
|----------|--------|---------|-------|----------|
| Hash table | O(1) | O(1) | O(n×k) | No partial matching |
| Trie | O(k) | O(k) | O(n×k) | Enables backoff |
| Suffix tree | O(k) | O(k) | O(n²) | Overkill for this use case |

We chose trie for **graceful degradation** - if exact sequence isn't seen, we backoff to shorter match.
```

## Python Package Standards

### Imports
```python
# Standard library
from typing import Dict, List, Tuple
from collections import defaultdict

# Third-party
import pandas as pd
import numpy as np

# Local
from .play_classifier import PlayType
```

### Type Hints
```python
# Always use for function signatures
def predict(self, plays: List[PlayType], k: int = 5) -> Tuple[Dict[PlayType, float], int]:
    ...

# Optional for local variables (only if it aids clarity)
node: TrieNode = self.root
```

### Naming Conventions
- `snake_case` for functions, variables, files
- `PascalCase` for classes
- `UPPER_CASE` for constants
- `_leading_underscore` for private methods (document why it's private in README)

## Testing Strategy

Document in `/tests/README.md`:
- **What we test**: Algorithm correctness, edge cases, complexity validation
- **What we don't test**: Visualization output, notebook execution
- **Coverage goal**: 80%+ for `/src/models` and `/src/evaluation`

## Tools & Environment

Document in main `README.md`:
- Python version
- Key dependencies
- Setup instructions
- How to run tests
- How to reproduce results

## Questions to Answer in Documentation

When writing a README for a module, answer:

1. **What problem does this solve?**
2. **How does it work? (High-level algorithm)**
3. **Why this approach over alternatives?**
4. **What are the time/space constraints?**
5. **How do I use it? (Examples)**
6. **What are the gotchas/limitations?**

## Example README Structure

### `/src/models/README.md`

```markdown
# Models

## Overview
Trie-based play sequence prediction with O(k) lookup time.

## Components

### PlaySequenceTrie
Prefix tree storing NFL play sequences for prediction.

**Algorithm**: [Detailed explanation]
**Complexity**: [Analysis with justification]
**Usage**: [Code example]

### PlayClassifier
Encodes raw play data into discrete types for trie storage.

**Encoding Scheme**: [Explanation of categories]
**Trade-offs**: [Why this scheme vs alternatives]
**Usage**: [Code example]

## Design Decisions

### Why Trie Instead of Markov Chain?
[Explanation]

### Why Situational Encoding?
[Explanation]
```

---

## Summary

**Code**: Clean and minimal
**Docs**: Comprehensive and external
**Comments**: Only when necessary
**Examples**: In README files and notebooks
**Explanations**: In markdown, not comments

This keeps code readable while maintaining thorough documentation for future you (and others).

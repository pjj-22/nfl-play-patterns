# Data Module

## Overview

Handles data acquisition, cleaning, and preprocessing for NFL play prediction.

## Components

### loader.py

**Purpose:** Download and load nflfastR play-by-play data

**Key Functions:**

```python
def load_pbp_data(seasons: List[int], cache_dir: str = 'data/raw') -> pd.DataFrame:
    """Load play-by-play data for specified seasons.

    Args:
        seasons: List of season years (e.g., [2021, 2022, 2023])
        cache_dir: Directory to cache downloaded data

    Returns:
        DataFrame with all plays from specified seasons
    """
```

**Caching Strategy:**
- First call downloads and saves to `data/raw/`
- Subsequent calls load from cache
- Use `force_refresh=True` to re-download

### preprocessor.py

**Purpose:** Clean and filter plays for prediction

**Key Functions:**

```python
def clean_plays(pbp: pd.DataFrame) -> pd.DataFrame:
    """Filter and clean play-by-play data.

    Removes:
    - Special teams plays (punts, field goals, kickoffs)
    - Plays with missing critical fields
    - Penalty plays
    - End-of-half/game scenarios

    Adds:
    - distance_category: categorized ydstogo
    - field_category: categorized field position

    Args:
        pbp: Raw play-by-play DataFrame

    Returns:
        Cleaned DataFrame with only relevant plays
    """
```

**Filtering Logic:**

```python
# Keep only pass/run plays
pbp = pbp[pbp['play_type'].isin(['pass', 'run'])]

# Remove missing critical fields
pbp = pbp.dropna(subset=['down', 'ydstogo', 'yardline_100'])

# Remove penalties
pbp = pbp[pbp['penalty'] == 0]

# Remove end-of-half scenarios (< 2 min in half, not normal play-calling)
# Optional - TBD based on analysis
```

### feature_extractor.py

**Purpose:** Extract and engineer features for play encoding

**Key Functions:**

```python
def categorize_distance(ydstogo: int) -> str:
    """Categorize yards to go.

    Returns:
        'short' (≤3), 'med' (4-7), 'long' (>7)
    """

def categorize_field_position(yardline_100: int) -> str:
    """Categorize field position.

    Returns:
        'own' (>50 yards from goal), 'opp' (≤50 yards from goal)
    """

def extract_game_situation(play: Dict) -> Dict[str, Any]:
    """Extract all situational features for a play.

    Returns:
        Dict with down, distance, field_pos, quarter, score_diff, etc.
    """
```

## Data Schema

### Input (Raw nflfastR)

See `/data/README.md` for full schema.

### Output (Processed)

After cleaning, guaranteed fields:

| Field | Type | Description |
|-------|------|-------------|
| `game_id` | str | Game identifier |
| `play_id` | int | Play identifier |
| `drive` | int | Drive number |
| `play_type` | str | `pass` or `run` |
| `down` | int | 1-4 |
| `ydstogo` | int | Yards to first down |
| `yardline_100` | int | Yards from own goal |
| `distance_category` | str | `short`, `med`, `long` |
| `field_category` | str | `own`, `opp` |
| `epa` | float | Expected Points Added |
| `posteam` | str | Team code |

## Usage Example

```python
from src.data.loader import load_pbp_data
from src.data.preprocessor import clean_plays

# Load data
pbp = load_pbp_data(seasons=[2021, 2022, 2023])
print(f"Loaded {len(pbp):,} raw plays")

# Clean
pbp_clean = clean_plays(pbp)
print(f"Retained {len(pbp_clean):,} plays after cleaning")

# Group by drive for sequence analysis
drives = pbp_clean.groupby(['game_id', 'drive'])
print(f"Total drives: {len(drives):,}")
```

## Design Decisions

### Why Filter Out Penalties?

Penalty plays don't represent actual play-calling decisions - they're often the result of defensive infractions or false starts. Including them would add noise to sequence patterns.

### Why Categorize Distance?

Exact yardage (1 vs 2 yards) is less meaningful than categorical distance:
- **Short** (≤3): Run/play-action heavy
- **Medium** (4-7): Balanced
- **Long** (>7): Pass heavy

This reduces encoding vocabulary while preserving strategic meaning.

### Why Not Include Score Differential?

Initially excluded to keep encoding simple. May add in future iterations if analysis shows it's predictive. Score differential is continuous, so would need discretization.

## Data Quality Checks

Functions should include basic validation:

```python
def clean_plays(pbp: pd.DataFrame) -> pd.DataFrame:
    initial_count = len(pbp)

    # Cleaning steps...
    pbp_clean = ...

    final_count = len(pbp_clean)
    removed_pct = (1 - final_count / initial_count) * 100

    print(f"Removed {removed_pct:.1f}% of plays")
    print(f"  Initial: {initial_count:,}")
    print(f"  Final: {final_count:,}")

    return pbp_clean
```

## Future Enhancements

- [ ] Add personnel grouping features (11 vs 12 personnel)
- [ ] Include formation data (shotgun, under center)
- [ ] Add time remaining in half
- [ ] Include weather conditions for outdoor games
- [ ] Add strength of opponent defense (DVOA)

## Testing

See `tests/test_data.py` for data module tests.

Key tests:
- Data loading caching works correctly
- Cleaning removes expected number of plays
- No null values in critical fields after cleaning
- Categorization functions handle edge cases

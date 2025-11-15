# Data Directory

## Overview

Contains all data used in the NFL play prediction project, organized by processing stage.

## Structure

```
data/
├── raw/              # Unmodified data from nflfastR
├── processed/        # Cleaned and transformed data
└── models/           # Saved trie structures and trained models
```

## Data Sources

### nflfastR Play-by-Play Data

- **Source**: `nfl_data_py.import_pbp_data()`
- **Seasons**: 2021-2024
- **Format**: CSV/Parquet
- **Size**: ~500MB per season

## Key Fields

### Raw Data Schema

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `game_id` | str | Unique game identifier | `2023_01_BUF_NYJ` |
| `play_id` | int | Unique play identifier | `1` |
| `drive` | int | Drive number in game | `1` |
| `play_type` | str | Type of play | `pass`, `run`, `punt` |
| `down` | int | Down (1-4) | `1` |
| `ydstogo` | int | Yards to go for first down | `10` |
| `yardline_100` | int | Yards from own goal line | `75` |
| `qtr` | int | Quarter (1-5, 5=OT) | `1` |
| `score_differential` | int | Point differential | `-7` |
| `posteam` | str | Possession team | `BUF` |
| `defteam` | str | Defensive team | `NYJ` |
| `epa` | float | Expected Points Added | `2.3` |
| `wp` | float | Win Probability | `0.65` |
| `shotgun` | int | Shotgun formation (0/1) | `1` |
| `no_huddle` | int | No huddle offense (0/1) | `0` |

## Data Processing Pipeline

### 1. Raw Data (`/raw`)

Downloaded directly from nflfastR, no modifications.

```python
import nfl_data_py as nfl
pbp = nfl.import_pbp_data([2021, 2022, 2023, 2024])
pbp.to_parquet('data/raw/pbp_2021_2024.parquet')
```

### 2. Processed Data (`/processed`)

Cleaned and filtered for play prediction:

**Filters Applied:**
- Keep only `play_type` in `['pass', 'run']`
- Remove rows with missing `down`, `ydstogo`, `yardline_100`
- Remove penalty plays (where `penalty == 1`)
- Remove end-of-half/game scenarios

**New Features:**
- `distance_category`: `short` (≤3), `med` (4-7), `long` (>7)
- `field_category`: `own` (>50), `opp` (≤50)
- `play_encoding`: Encoded play type for trie

**Output:** `data/processed/pbp_clean.parquet`

### 3. Model Files (`/models`)

Saved trained models and trie structures:

- `trie_2021_2023.pkl`: Trie trained on 2021-2023 seasons
- `trie_full.pkl`: Trie trained on all available data
- `classifier_config.json`: Play encoding configuration

## Data Statistics

_To be populated after Phase 1: Data Exploration_

**Total Plays:**
- Raw:
- Filtered:

**Drives:**
- Total drives:
- Average plays per drive:
- Median plays per drive:

**Play Type Distribution:**
- Pass:
- Run:

## Gitignore Note

Large data files (>100MB) are gitignored. To reproduce:

```bash
python scripts/download_data.py --seasons 2021 2022 2023 2024
python scripts/process_data.py
```

## Data Quality Issues

_Document any data quality issues discovered during exploration_

-
-

## References

- [nflfastR Documentation](https://www.nflfastr.com/)
- [nfl_data_py GitHub](https://github.com/nflverse/nfl_data_py)

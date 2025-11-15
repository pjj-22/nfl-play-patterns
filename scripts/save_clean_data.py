"""
Load and save cleaned NFL play-by-play data.
"""
import nfl_data_py as nfl
import pandas as pd
from pathlib import Path


def main():
    print("=" * 60)
    print("Loading and Cleaning NFL Data")
    print("=" * 60)

    # Load multiple seasons
    seasons = [2021, 2022, 2023, 2024]
    print(f"\n1. Loading play-by-play data for {seasons}...")
    print("   This may take 5-10 minutes on first run...")

    pbp = nfl.import_pbp_data(seasons)
    print(f"   ✓ Loaded {len(pbp):,} total plays")

    # Clean data
    print("\n2. Filtering to pass/run plays with valid data...")
    pbp_clean = pbp[
        (pbp['play_type'].isin(['pass', 'run'])) &
        (pbp['down'].notna()) &
        (pbp['ydstogo'].notna()) &
        (pbp['yardline_100'].notna())
    ].copy()

    print(f"   ✓ Filtered to {len(pbp_clean):,} plays ({len(pbp_clean)/len(pbp):.1%} of total)")
    print(f"   ✓ {pbp_clean['game_id'].nunique()} games")
    print(f"   ✓ {len(pbp_clean.groupby(['game_id', 'drive'])):,} drives")

    # Save
    output_dir = Path(__file__).parent.parent / "data" / "processed"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "pbp_clean.parquet"

    print(f"\n3. Saving to {output_path}...")
    pbp_clean.to_parquet(output_path, index=False)

    file_size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"   ✓ Saved! File size: {file_size_mb:.1f} MB")

    print("\n" + "=" * 60)
    print("✓ Complete! Data ready for model training.")
    print("=" * 60)
    print("\nNext step:")
    print("  python scripts/evaluate_model.py")


if __name__ == "__main__":
    main()

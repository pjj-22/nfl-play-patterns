"""
Train Phase 1 model with time remaining + home/away features.

This creates situation groups (36 total) by combining:
- Base game situation (9 types)
- Time remaining (2 types: normal/two_minute)
- Home/Away (2 types: home/away)
"""
import sys
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.grouped_trie import SituationGroupedTrie
from src.models.simple_classifier import SimplePlayClassifier
from src.evaluation.corrected_metrics import CorrectedTrieEvaluator


def main():
    print("=" * 70)
    print("PHASE 1 MODEL: Time Remaining + Home/Away")
    print("=" * 70)
    print("\nThis model combines TWO contextual features:")
    print("  1. Time remaining (normal vs two_minute drill)")
    print("  2. Home/Away context")
    print("\nExpected: 36 situation groups (9 × 2 × 2)")
    print("Target accuracy: ~68-70% (+7-9 points over baseline)\n")

    # Load data
    print("1. Loading NFL play-by-play data...")
    data_path = Path(__file__).parent.parent / "data" / "processed" / "pbp_clean.parquet"

    if not data_path.exists():
        print(f"❌ Error: Data file not found at {data_path}")
        print("Please run: python scripts/save_clean_data.py")
        return

    pbp = pd.read_parquet(data_path)
    print(f"   ✓ Loaded {len(pbp):,} plays from {pbp['game_id'].nunique()} games")

    # Check for required columns
    required_cols = ['game_seconds_remaining', 'posteam_type']
    missing_cols = [col for col in required_cols if col not in pbp.columns]
    if missing_cols:
        print(f"❌ Error: Missing required columns: {missing_cols}")
        return

    # Show distribution of time contexts
    print("\n2. Analyzing time remaining context...")
    two_minute_plays = pbp[pbp['game_seconds_remaining'] <= 120]
    normal_plays = pbp[pbp['game_seconds_remaining'] > 120]
    print(f"   Two-minute drill: {len(two_minute_plays):,} plays ({len(two_minute_plays)/len(pbp)*100:.1f}%)")
    print(f"   Normal time:      {len(normal_plays):,} plays ({len(normal_plays)/len(pbp)*100:.1f}%)")

    # Show distribution of home/away
    print("\n   Home/Away distribution:")
    home_away_counts = pbp['posteam_type'].value_counts()
    for team_type, count in home_away_counts.items():
        pct = count / len(pbp) * 100
        print(f"     {team_type:6} {count:>7,} plays ({pct:5.1f}%)")

    # Train/test split by GAMES
    print("\n3. Creating train/test split...")
    games = pbp['game_id'].unique()
    train_games, test_games = train_test_split(games, test_size=0.2, random_state=42)

    train_df = pbp[pbp['game_id'].isin(train_games)]
    test_df = pbp[pbp['game_id'].isin(test_games)]

    print(f"   Train: {len(train_games):,} games, {len(train_df):,} plays")
    print(f"   Test:  {len(test_games):,} games, {len(test_df):,} plays")

    # Build Phase 1 model
    print("\n4. Building PHASE 1 situation-grouped trie...")
    print("   Features: ['time_remaining', 'home_away']")
    print("   This will create situation groups like:")
    print("     - 'third_short_two_minute_away'")
    print("     - 'early_down_medium_normal_home'")
    print("     - 'red_zone_two_minute_home'")

    classifier = SimplePlayClassifier()
    trie = SituationGroupedTrie(max_depth=8, features=['time_remaining', 'home_away'])

    train_drives = train_df.groupby(['game_id', 'drive'])
    total_drives = len(train_drives)

    for i, ((game_id, drive_num), drive) in enumerate(train_drives):
        if i % 1000 == 0:
            print(f"   Processing drive {i+1:,}/{total_drives:,}...", end='\r')

        # Encode play types (just P or R)
        play_types = classifier.encode_series(drive)

        # Extract situations (down, ydstogo, yardline)
        situations = [
            (int(row['down']), int(row['ydstogo']), int(row['yardline_100']))
            for _, row in drive.iterrows()
        ]

        # Extract time remaining
        game_seconds_remaining = drive['game_seconds_remaining'].tolist()

        # Extract home/away
        posteam_types = drive['posteam_type'].tolist()

        # EPAs
        epas = drive['epa'].tolist() if 'epa' in drive.columns else None

        # Insert into Phase 1 trie
        trie.insert_drive(
            play_types, situations, epas,
            game_seconds_remaining=game_seconds_remaining,
            posteam_types=posteam_types
        )

    print(f"\n   ✓ Trie built from {total_drives:,} training drives")

    # Statistics
    stats = trie.get_statistics()
    print(f"\n   Model Statistics:")
    print(f"     Max depth: {stats['max_depth']}")
    print(f"     Features: {stats['features']}")
    print(f"     Total situations processed: {stats['total_situations']:,}")
    print(f"     Number of situation groups: {stats['num_situation_groups']}")

    # Show top situation groups by frequency
    print(f"\n     Top 15 situation groups by frequency:")
    sorted_situations = sorted(
        stats['situation_breakdown'].items(),
        key=lambda x: x[1],
        reverse=True
    )[:15]

    for situation_name, count in sorted_situations:
        print(f"       {situation_name:50} {count:>7,} plays")

    # Evaluate on TEST set
    print("\n5. Evaluating on TEST set...")
    evaluator = CorrectedTrieEvaluator(trie, classifier)

    print("   Running predictions on test drives...")
    metrics = evaluator.evaluate_drives(test_df, min_context=3)

    print("\n" + "=" * 70)
    print("OVERALL TEST SET RESULTS (Phase 1 Model)")
    print("=" * 70)
    print(metrics)

    # Comparisons
    print("\n6. Model Comparisons:")
    print("   Random baseline: 50.0%")
    print(f"   Our accuracy: {metrics.overall_accuracy:.2%}")
    improvement = metrics.overall_accuracy / 0.5
    print(f"   Improvement: {improvement:.2f}x better than random")

    print("\n   Previous models:")
    baseline_accuracy = 0.6165  # From corrected model (no features)
    score_accuracy = 0.6164     # From score-aware model
    combined_accuracy = 0.6127  # From combined model (score + team)
    print(f"   Baseline (no features):     {baseline_accuracy:.2%}")
    print(f"   Score-aware only:           {score_accuracy:.2%}")
    print(f"   Combined (score + team):    {combined_accuracy:.2%}")
    print(f"   Phase 1 (time + home/away): {metrics.overall_accuracy:.2%}")

    gain_from_baseline = (metrics.overall_accuracy - baseline_accuracy) * 100
    print(f"\n   Gain from baseline: {gain_from_baseline:+.2f} percentage points")

    # Save model
    print("\n7. Saving model...")
    model_dir = Path(__file__).parent.parent / "data" / "models"
    model_dir.mkdir(parents=True, exist_ok=True)
    model_path = model_dir / "phase1_trie.pkl"

    trie.save(str(model_path))
    file_size_kb = model_path.stat().st_size / 1024
    print(f"   ✓ Model saved to: {model_path}")
    print(f"   ✓ File size: {file_size_kb:.1f} KB")

    print("\n" + "=" * 70)
    print("✓ TRAINING COMPLETE")
    print("=" * 70)

    print("\n📊 Key Takeaways:")
    print(f"  - Phase 1 model accuracy: {metrics.overall_accuracy:.2%}")
    print(f"  - Improvement over baseline: {gain_from_baseline:+.2f} percentage points")
    print(f"  - {improvement:.2f}x better than random guessing")
    print(f"  - Number of situation groups: {stats['num_situation_groups']}")

    print("\n🎯 Phase 1 Feature Impact:")
    print("  - Two-minute drill situations: Different urgency and clock management")
    print("  - Home field advantage: Potential impact on play-calling")
    print("  - Balanced granularity (36 groups vs 81 in combined model)")

    print("\n🔗 Next steps:")
    print("  - Run demo: python scripts/phase1_demo.py")
    print("  - Phase 2: Add QB/RB quality ratings")
    print("  - Phase 3: Add coach tendencies and weather")

    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()

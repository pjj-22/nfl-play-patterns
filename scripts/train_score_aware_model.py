"""
Train the SCORE-AWARE model with score differential.

This extends the corrected architecture by incorporating game score
into situation grouping, improving predictions in trailing/leading situations.
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
    print("SCORE-AWARE NFL PLAY PREDICTION - Training & Evaluation")
    print("=" * 70)
    print("\nThis model incorporates score differential into predictions!")
    print("Expected improvement: +6-8 percentage points\n")

    # Load data
    print("1. Loading NFL data...")
    data_path = Path(__file__).parent.parent / "data" / "processed" / "pbp_clean.parquet"

    if not data_path.exists():
        print(f"❌ Error: Data file not found at {data_path}")
        print("Please run: python scripts/save_clean_data.py")
        return

    pbp = pd.read_parquet(data_path)
    print(f"   ✓ Loaded {len(pbp):,} plays from {pbp['game_id'].nunique()} games")

    # Check for score_differential column
    if 'score_differential' not in pbp.columns:
        print("❌ Error: score_differential column not found in data!")
        return

    # Train/test split by GAMES
    print("\n2. Creating train/test split...")
    games = pbp['game_id'].unique()
    train_games, test_games = train_test_split(games, test_size=0.2, random_state=42)

    train_df = pbp[pbp['game_id'].isin(train_games)]
    test_df = pbp[pbp['game_id'].isin(test_games)]

    print(f"   Train: {len(train_games):,} games, {len(train_df):,} plays")
    print(f"   Test:  {len(test_games):,} games, {len(test_df):,} plays")

    # Build score-aware model
    print("\n3. Building SCORE-AWARE situation-grouped trie...")
    print("   (This uses score differential to create more specific situations)")

    classifier = SimplePlayClassifier()
    trie = SituationGroupedTrie(max_depth=8, use_score=True)  # ← Score-aware!

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

        # Extract score differentials
        score_diffs = drive['score_differential'].tolist()

        # EPAs
        epas = drive['epa'].tolist() if 'epa' in drive.columns else None

        # Insert into score-aware grouped trie
        trie.insert_drive(play_types, situations, epas, score_diffs)

    print(f"\n   ✓ Trie built from {total_drives:,} training drives")

    # Statistics
    stats = trie.get_statistics()
    print(f"\n   Model Statistics:")
    print(f"     Max depth: {stats['max_depth']}")
    print(f"     Score-aware: {stats['use_score']}")
    print(f"     Total situations processed: {stats['total_situations']:,}")
    print(f"     Number of situation groups: {stats['num_situation_groups']}")

    # Show top situation groups by frequency
    print(f"\n     Top 10 situation groups by frequency:")
    sorted_situations = sorted(
        stats['situation_breakdown'].items(),
        key=lambda x: x[1],
        reverse=True
    )[:10]

    for situation_name, count in sorted_situations:
        print(f"       {situation_name:35} {count:>7,} plays")

    # Evaluate on TEST set
    print("\n4. Evaluating on TEST set...")
    evaluator = CorrectedTrieEvaluator(trie, classifier)

    print("   Running predictions on test drives...")
    metrics = evaluator.evaluate_drives(test_df, min_context=3)

    print("\n" + "=" * 70)
    print("OVERALL TEST SET RESULTS (Score-Aware Model)")
    print("=" * 70)
    print(metrics)

    # Baseline comparison
    print("\n5. Baseline Comparison:")
    print("   Random baseline: 50.0%")
    print(f"   Our accuracy: {metrics.overall_accuracy:.2%}")
    improvement = metrics.overall_accuracy / 0.5
    print(f"   Improvement: {improvement:.2f}x better than random")

    # Compare to baseline model
    print("\n6. Comparison to Baseline (without score):")
    baseline_accuracy = 61.65  # From corrected model
    gain = (metrics.overall_accuracy - baseline_accuracy / 100) * 100
    print(f"   Baseline model (no score): {baseline_accuracy}%")
    print(f"   Score-aware model: {metrics.overall_accuracy:.2%}")
    print(f"   Gain: {gain:+.2f} percentage points")

    # Save model
    print("\n7. Saving model...")
    model_dir = Path(__file__).parent.parent / "data" / "models"
    model_dir.mkdir(parents=True, exist_ok=True)
    model_path = model_dir / "score_aware_trie.pkl"

    trie.save(str(model_path))
    file_size_kb = model_path.stat().st_size / 1024
    print(f"   ✓ Model saved to: {model_path}")
    print(f"   ✓ File size: {file_size_kb:.1f} KB")

    print("\n" + "=" * 70)
    print("✓ TRAINING COMPLETE")
    print("=" * 70)

    print("\n📊 Key Takeaways:")
    print(f"  - Score-aware accuracy: {metrics.overall_accuracy:.2%}")
    print(f"  - Improvement over baseline: {gain:+.2f} percentage points")
    print(f"  - {improvement:.2f}x better than random guessing")
    print(f"  - Number of situation groups: {stats['num_situation_groups']}")

    print("\n🎯 Impact of Score Differential:")
    print("  - Trailing teams become MORE predictable (must pass)")
    print("  - Leading teams become MORE predictable (run clock)")
    print("  - Tied games remain similar to baseline")

    print("\n🔗 Next steps:")
    print("  - Run demo: python scripts/score_aware_demo.py")
    print("  - Add time remaining for further improvement")
    print("  - Add QB rating tiers")

    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()

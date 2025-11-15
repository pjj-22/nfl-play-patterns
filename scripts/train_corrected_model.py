"""
Train and evaluate the CORRECTED model architecture.

This version uses SituationGroupedTrie to predict Pass/Run only,
without conflating play-calling decisions with game outcomes.
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
    print("CORRECTED NFL PLAY PREDICTION - Training & Evaluation")
    print("=" * 70)
    print("\nThis model predicts ONLY Pass vs Run, without conflating")
    print("play-calling decisions with game outcomes.")

    # Load data
    print("\n1. Loading NFL data...")
    data_path = Path(__file__).parent.parent / "data" / "processed" / "pbp_clean.parquet"

    if not data_path.exists():
        print(f"❌ Error: Data file not found at {data_path}")
        print("Please run: python scripts/save_clean_data.py")
        return

    pbp = pd.read_parquet(data_path)
    print(f"   ✓ Loaded {len(pbp):,} plays from {pbp['game_id'].nunique()} games")

    # Train/test split by GAMES
    print("\n2. Creating train/test split...")
    games = pbp['game_id'].unique()
    train_games, test_games = train_test_split(games, test_size=0.2, random_state=42)

    train_df = pbp[pbp['game_id'].isin(train_games)]
    test_df = pbp[pbp['game_id'].isin(test_games)]

    print(f"   Train: {len(train_games):,} games, {len(train_df):,} plays")
    print(f"   Test:  {len(test_games):,} games, {len(test_df):,} plays")

    # Build corrected model
    print("\n3. Building corrected situation-grouped trie...")
    classifier = SimplePlayClassifier()
    trie = SituationGroupedTrie(max_depth=8)

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

        # EPAs
        epas = drive['epa'].tolist() if 'epa' in drive.columns else None

        # Insert into grouped trie
        trie.insert_drive(play_types, situations, epas)

    print(f"\n   ✓ Trie built from {total_drives:,} training drives")

    # Statistics
    stats = trie.get_statistics()
    print(f"\n   Model Statistics:")
    print(f"     Max depth: {stats['max_depth']}")
    print(f"     Total situations processed: {stats['total_situations']:,}")
    print(f"\n     Situation breakdown:")

    for situation_name, count in sorted(
        stats['situation_breakdown'].items(),
        key=lambda x: x[1],
        reverse=True
    ):
        print(f"       {situation_name:25} {count:>7,} plays")

    # Evaluate on TEST set
    print("\n4. Evaluating on TEST set...")
    evaluator = CorrectedTrieEvaluator(trie, classifier)

    print("   Running predictions on test drives...")
    metrics = evaluator.evaluate_drives(test_df, min_context=3)

    print("\n" + "=" * 70)
    print("OVERALL TEST SET RESULTS")
    print("=" * 70)
    print(metrics)

    # Baseline comparison
    print("\n5. Baseline Comparison:")
    print("   Random baseline (Pass or Run): 50.0%")
    improvement = metrics.overall_accuracy / 0.5
    print(f"   Our accuracy: {metrics.overall_accuracy:.2%}")
    print(f"   Improvement: {improvement:.2f}x better than random")

    # Evaluate by situation
    print("\n" + "=" * 70)
    print("ACCURACY BY SITUATION")
    print("=" * 70)

    by_situation = evaluator.evaluate_by_situation(test_df)

    for situation_name in sorted(by_situation.keys()):
        metrics_sit = by_situation[situation_name]
        print(f"\n{situation_name}:")
        print(f"  Accuracy: {metrics_sit.overall_accuracy:.2%}")
        print(f"  Pass precision: {metrics_sit.pass_precision:.2%}, recall: {metrics_sit.pass_recall:.2%}")
        print(f"  Run precision: {metrics_sit.run_precision:.2%}, recall: {metrics_sit.run_recall:.2%}")
        print(f"  Predictions: {metrics_sit.total_predictions:,}")

    # Save model
    print("\n6. Saving model...")
    model_dir = Path(__file__).parent.parent / "data" / "models"
    model_dir.mkdir(parents=True, exist_ok=True)
    model_path = model_dir / "corrected_trie.pkl"

    trie.save(str(model_path))
    print(f"   ✓ Model saved to: {model_path}")

    print("\n" + "=" * 70)
    print("✓ TRAINING COMPLETE")
    print("=" * 70)

    print("\n📊 Key Takeaways:")
    print(f"  - Binary Pass/Run accuracy: {metrics.overall_accuracy:.2%}")
    print(f"  - {improvement:.2f}x better than random guessing")
    print(f"  - No conflation of decisions with outcomes")
    print(f"  - Model predicts ONLY play type, not game state")

    print("\n🔗 Next steps:")
    print("  - Run demo: python scripts/corrected_predictions_demo.py")
    print("  - Compare to old model results in PROJECT_SUMMARY.md")
    print("  - Update documentation with corrected architecture")

    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()

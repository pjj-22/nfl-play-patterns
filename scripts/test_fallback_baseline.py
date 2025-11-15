"""
Test hierarchical fallback on the baseline model (no features).
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
    print("BASELINE MODEL WITH HIERARCHICAL FALLBACK")
    print("=" * 70)

    # Load data
    print("\n1. Loading NFL play-by-play data...")
    data_path = Path(__file__).parent.parent / "data" / "processed" / "pbp_clean.parquet"
    pbp = pd.read_parquet(data_path)
    print(f"   ✓ Loaded {len(pbp):,} plays")

    # Train/test split
    print("\n2. Creating train/test split...")
    games = pbp['game_id'].unique()
    train_games, test_games = train_test_split(games, test_size=0.2, random_state=42)
    train_df = pbp[pbp['game_id'].isin(train_games)]
    test_df = pbp[pbp['game_id'].isin(test_games)]
    print(f"   Train: {len(train_df):,} plays")
    print(f"   Test:  {len(test_df):,} plays")

    # Build baseline model WITH fallback
    print("\n3. Building baseline model WITH hierarchical fallback...")
    classifier = SimplePlayClassifier()
    trie_with_fallback = SituationGroupedTrie(
        max_depth=8,
        features=[],  # No features
        use_hierarchical_fallback=True,
        min_examples_threshold=50
    )

    train_drives = train_df.groupby(['game_id', 'drive'])
    for i, ((game_id, drive_num), drive) in enumerate(train_drives):
        if i % 5000 == 0:
            print(f"   Processing drive {i:,}...", end='\r')

        play_types = classifier.encode_series(drive)
        situations = [(int(row['down']), int(row['ydstogo']), int(row['yardline_100']))
                     for _, row in drive.iterrows()]
        epas = drive['epa'].tolist() if 'epa' in drive.columns else None

        trie_with_fallback.insert_drive(play_types, situations, epas)

    print(f"\n   ✓ Trie built from {len(train_drives):,} training drives")

    # Build baseline model WITHOUT fallback (for comparison)
    print("\n4. Building baseline model WITHOUT hierarchical fallback...")
    trie_no_fallback = SituationGroupedTrie(
        max_depth=8,
        features=[],
        use_hierarchical_fallback=False
    )

    for i, ((game_id, drive_num), drive) in enumerate(train_drives):
        if i % 5000 == 0:
            print(f"   Processing drive {i:,}...", end='\r')

        play_types = classifier.encode_series(drive)
        situations = [(int(row['down']), int(row['ydstogo']), int(row['yardline_100']))
                     for _, row in drive.iterrows()]
        epas = drive['epa'].tolist() if 'epa' in drive.columns else None

        trie_no_fallback.insert_drive(play_types, situations, epas)

    print(f"\n   ✓ Trie built from {len(train_drives):,} training drives")

    # Evaluate both
    print("\n5. Evaluating WITH fallback...")
    evaluator_with = CorrectedTrieEvaluator(trie_with_fallback, classifier)
    metrics_with = evaluator_with.evaluate_drives(test_df, min_context=3)

    print("\n6. Evaluating WITHOUT fallback...")
    evaluator_without = CorrectedTrieEvaluator(trie_no_fallback, classifier)
    metrics_without = evaluator_without.evaluate_drives(test_df, min_context=3)

    # Compare
    print("\n" + "=" * 70)
    print("COMPARISON: BASELINE MODEL")
    print("=" * 70)
    print(f"\nWITHOUT Hierarchical Fallback:")
    print(f"  Accuracy: {metrics_without.overall_accuracy:.2%}")
    print(f"  Predictions: {metrics_without.total_predictions:,}")

    print(f"\nWITH Hierarchical Fallback:")
    print(f"  Accuracy: {metrics_with.overall_accuracy:.2%}")
    print(f"  Predictions: {metrics_with.total_predictions:,}")

    improvement = (metrics_with.overall_accuracy - metrics_without.overall_accuracy) * 100
    print(f"\nImprovement: {improvement:+.2f} percentage points")

    # Fallback stats
    stats = trie_with_fallback.get_statistics()
    print(f"\n7. Fallback Statistics:")
    print(f"   Groups with sufficient data (≥50): {stats['groups_with_sufficient_data']}")
    print(f"   Groups with sparse data (<50): {stats['groups_with_sparse_data']}")

    if stats['fallback_stats']:
        total_predictions = sum(stats['fallback_stats'].values())
        print(f"\n   Fallback level usage:")
        for level, count in sorted(stats['fallback_stats'].items()):
            pct = count / total_predictions * 100 if total_predictions > 0 else 0
            print(f"     {level:20} {count:>7,} ({pct:5.1f}%)")

    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()

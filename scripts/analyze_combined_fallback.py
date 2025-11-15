"""
Analyze fallback statistics for Combined model.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.grouped_trie import SituationGroupedTrie


def main():
    print("=" * 70)
    print("COMBINED MODEL - FALLBACK ANALYSIS")
    print("=" * 70)

    # Load model
    model_path = Path(__file__).parent.parent / "data" / "models" / "combined_trie.pkl"
    print(f"\nLoading model from {model_path}...")
    trie = SituationGroupedTrie.load(str(model_path))
    print("✓ Model loaded")

    # Get statistics
    stats = trie.get_statistics()

    print(f"\nModel Configuration:")
    print(f"  Features: {stats['features']}")
    print(f"  Hierarchical fallback: {stats['use_hierarchical_fallback']}")
    print(f"  Min examples threshold: {stats['min_examples_threshold']}")

    print(f"\nSituation Groups:")
    print(f"  Total groups: {stats['num_situation_groups']}")
    print(f"  Groups with sufficient data (≥{stats['min_examples_threshold']}): {stats['groups_with_sufficient_data']}")
    print(f"  Groups with sparse data: {stats['groups_with_sparse_data']}")

    # Show sparse groups
    sparse_groups = {k: v for k, v in stats['situation_breakdown'].items()
                    if v < stats['min_examples_threshold']}
    print(f"\n  Sparse groups (<{stats['min_examples_threshold']} examples): {len(sparse_groups)}")
    print(f"  Showing 20 sparsest:")
    for group, count in sorted(sparse_groups.items(), key=lambda x: x[1])[:20]:
        group_str = group.value if hasattr(group, 'value') else str(group)
        print(f"    {group_str:55} {count:>4} plays")

    print(f"\n  Well-populated groups (≥{stats['min_examples_threshold']} examples):")
    sufficient_groups = {k: v for k, v in stats['situation_breakdown'].items()
                        if v >= stats['min_examples_threshold']}
    for group, count in sorted(sufficient_groups.items(), key=lambda x: x[1], reverse=True)[:15]:
        group_str = group.value if hasattr(group, 'value') else str(group)
        print(f"    {group_str:55} {count:>7,} plays")

    # Fallback usage
    if stats['fallback_stats']:
        total_predictions = sum(stats['fallback_stats'].values())
        print(f"\nFallback Level Usage (during evaluation):")
        print(f"  Total predictions: {total_predictions:,}")
        for level, count in sorted(stats['fallback_stats'].items()):
            pct = count / total_predictions * 100
            bar = '█' * int(pct / 2)  # Scale to fit
            print(f"    {level:20} {count:>7,} ({pct:5.1f}%) {bar}")

        print(f"\n  Interpretation:")
        level_1_pct = stats['fallback_stats'].get('level_1_specific', 0) / total_predictions * 100
        level_2_pct = stats['fallback_stats'].get('level_2_base', 0) / total_predictions * 100
        level_3_pct = stats['fallback_stats'].get('level_3_league', 0) / total_predictions * 100

        print(f"    {level_1_pct:.1f}% of predictions used full context (score + team)")
        print(f"    {level_2_pct:.1f}% fell back to base situation only")
        print(f"    {level_3_pct:.1f}% fell back to league average")
    else:
        print("\n⚠ No fallback statistics (model not yet used for prediction)")

    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()

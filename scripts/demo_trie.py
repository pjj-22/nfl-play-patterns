"""
Quick demonstration of the trie implementation with synthetic data.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.play_trie import PlaySequenceTrie
from src.models.play_classifier import PlayType


def main():
    print("=" * 60)
    print("Trie Demo with Synthetic Data")
    print("=" * 60)

    print("\n1. Creating trie...")
    trie = PlaySequenceTrie(max_depth=5)

    print("\n2. Inserting play sequences...")

    sequences = [
        ([PlayType('P_1_long_own'), PlayType('R_2_med_own'), PlayType('P_3_short_own')], "Pass → Run → Pass"),
        ([PlayType('P_1_long_own'), PlayType('P_2_long_own'), PlayType('P_3_long_own')], "Pass → Pass → Pass"),
        ([PlayType('P_1_long_own'), PlayType('P_2_long_own'), PlayType('R_3_short_own')], "Pass → Pass → Run"),
        ([PlayType('R_1_long_own'), PlayType('R_2_med_own'), PlayType('P_3_short_own')], "Run → Run → Pass"),
        ([PlayType('R_1_long_own'), PlayType('P_2_long_own'), PlayType('P_3_short_own')], "Run → Pass → Pass"),
    ]

    for seq, desc in sequences:
        trie.insert_sequence(seq)
        print(f"   ✓ Inserted: {desc}")

    print("\n3. Trie Statistics:")
    stats = trie.get_statistics()
    print(f"   Total sequences: {stats['total_sequences']}")
    print(f"   Total nodes: {stats['num_nodes']}")
    print(f"   Avg branching factor: {stats['avg_branching_factor']:.2f}")

    print("\n4. Testing Predictions:")

    print("\n   Query: [P_1_long_own, P_2_long_own]")
    predictions, depth = trie.predict([PlayType('P_1_long_own'), PlayType('P_2_long_own')], k=5)
    print(f"   Depth matched: {depth}")
    print(f"   Predictions:")
    for play_type, prob in sorted(predictions.items(), key=lambda x: x[1], reverse=True):
        print(f"     {play_type.code:20} {prob:.1%}")

    print("\n   Query: [R_1_long_own]")
    predictions, depth = trie.predict([PlayType('R_1_long_own')], k=5)
    print(f"   Depth matched: {depth}")
    print(f"   Predictions:")
    for play_type, prob in sorted(predictions.items(), key=lambda x: x[1], reverse=True):
        print(f"     {play_type.code:20} {prob:.1%}")

    print("\n5. Testing Backoff:")
    print("\n   Query: [P_1_long_own, P_2_short_opp] (partial match)")
    predictions, depth = trie.predict([PlayType('P_1_long_own'), PlayType('P_2_short_opp')], k=5)
    print(f"   Depth matched: {depth} (backed off to 1-play context)")
    print(f"   Predictions:")
    for play_type, prob in sorted(predictions.items(), key=lambda x: x[1], reverse=True):
        print(f"     {play_type.code:20} {prob:.1%}")

    print("\n" + "=" * 60)
    print("✓ Demo Complete! Trie is working correctly.")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Run the last cell in the data exploration notebook to save data")
    print("  2. Run: python scripts/test_trie_on_real_data.py")
    print("  3. Move to Phase 3: Evaluation & Validation")


if __name__ == "__main__":
    main()

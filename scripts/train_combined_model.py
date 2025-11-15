"""
Train model with COMBINED features: score differential + team identity.

This creates the most granular situation groups (81 total) by combining:
- Base game situation (9 types)
- Score context (3 types: trailing/tied/leading)
- Team offensive identity (3 types: pass_heavy/balanced/run_heavy)
"""
import sys
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.grouped_trie import SituationGroupedTrie
from src.models.simple_classifier import SimplePlayClassifier
from src.features.team_identity import add_team_identity_to_plays
from src.evaluation.corrected_metrics import CorrectedTrieEvaluator


def main():
    print("=" * 70)
    print("COMBINED MODEL: Score Differential + Team Identity")
    print("=" * 70)
    print("\nThis model combines TWO contextual features:")
    print("  1. Score differential (trailing/tied/leading)")
    print("  2. Team offensive identity (pass_heavy/balanced/run_heavy)")
    print("\nExpected: 81 situation groups (9 × 3 × 3)")
    print("Target accuracy: ~66-68% (+5-6 points over baseline)\n")

    # Load data
    print("1. Loading NFL play-by-play data...")
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
        print("This model requires score differential to be in the dataset.")
        return

    # Calculate team identities
    print("\n2. Calculating team offensive identities...")
    print("   Using 4-game rolling window for team pass rates...")
    pbp = add_team_identity_to_plays(pbp, window_games=4)

    # Show some stats about team identities
    team_identity_counts = pbp['team_identity'].value_counts()
    print(f"\n   Team identity distribution:")
    for identity, count in team_identity_counts.items():
        pct = count / len(pbp) * 100
        print(f"     {identity:12} {count:>7,} plays ({pct:5.1f}%)")

    # Show average pass rates by identity
    print(f"\n   Average pass rates by identity:")
    for identity in ['run_heavy', 'balanced', 'pass_heavy']:
        if identity in pbp['team_identity'].values:
            avg_rate = pbp[pbp['team_identity'] == identity]['team_pass_rate'].mean()
            print(f"     {identity:12} {avg_rate:5.1%}")

    # Train/test split by GAMES
    print("\n3. Creating train/test split...")
    games = pbp['game_id'].unique()
    train_games, test_games = train_test_split(games, test_size=0.2, random_state=42)

    train_df = pbp[pbp['game_id'].isin(train_games)]
    test_df = pbp[pbp['game_id'].isin(test_games)]

    print(f"   Train: {len(train_games):,} games, {len(train_df):,} plays")
    print(f"   Test:  {len(test_games):,} games, {len(test_df):,} plays")

    # Build combined model
    print("\n4. Building COMBINED situation-grouped trie...")
    print("   Features: ['score', 'team_identity']")
    print("   This will create situation groups like:")
    print("     - 'third_short_trailing_pass_heavy'")
    print("     - 'early_down_medium_tied_balanced'")
    print("     - 'red_zone_leading_run_heavy'")

    classifier = SimplePlayClassifier()
    trie = SituationGroupedTrie(max_depth=8, features=['score', 'team_identity'])

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

        # Extract team pass rates
        team_pass_rates = drive['team_pass_rate'].tolist()

        # EPAs
        epas = drive['epa'].tolist() if 'epa' in drive.columns else None

        # Insert into combined trie
        trie.insert_drive(
            play_types, situations, epas,
            score_diffs=score_diffs,
            team_pass_rates=team_pass_rates
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
    print("OVERALL TEST SET RESULTS (Combined Model)")
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
    print(f"   Baseline (no features):     {baseline_accuracy:.2%}")
    print(f"   Score-aware only:           {score_accuracy:.2%}")
    print(f"   Combined (score + team):    {metrics.overall_accuracy:.2%}")

    gain_from_baseline = (metrics.overall_accuracy - baseline_accuracy) * 100
    gain_from_score = (metrics.overall_accuracy - score_accuracy) * 100
    print(f"\n   Gain from baseline: {gain_from_baseline:+.2f} percentage points")
    print(f"   Gain from score-only: {gain_from_score:+.2f} percentage points")

    # Save model
    print("\n7. Saving model...")
    model_dir = Path(__file__).parent.parent / "data" / "models"
    model_dir.mkdir(parents=True, exist_ok=True)
    model_path = model_dir / "combined_trie.pkl"

    trie.save(str(model_path))
    file_size_kb = model_path.stat().st_size / 1024
    print(f"   ✓ Model saved to: {model_path}")
    print(f"   ✓ File size: {file_size_kb:.1f} KB")

    print("\n" + "=" * 70)
    print("✓ TRAINING COMPLETE")
    print("=" * 70)

    print("\n📊 Key Takeaways:")
    print(f"  - Combined model accuracy: {metrics.overall_accuracy:.2%}")
    print(f"  - Improvement over baseline: {gain_from_baseline:+.2f} percentage points")
    print(f"  - Improvement over score-only: {gain_from_score:+.2f} percentage points")
    print(f"  - {improvement:.2f}x better than random guessing")
    print(f"  - Number of situation groups: {stats['num_situation_groups']}")

    print("\n🎯 Combined Feature Impact:")
    print("  - Pass-heavy teams trailing: Maximum pass probability")
    print("  - Run-heavy teams leading: Maximum run probability")
    print("  - Most granular situation modeling yet (81 groups)")

    print("\n🔗 Next steps:")
    print("  - Run demo: python scripts/combined_demo.py")
    print("  - Add time remaining for 4th dimension")
    print("  - Add QB rating for 5th dimension")

    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()

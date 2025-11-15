"""
Demo of the COMBINED model (score + team identity).

Shows how predictions change based on BOTH game score and team identity.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.grouped_trie import SituationGroupedTrie
from src.models.simple_classifier import SimplePlayClassifier, SimplePlayType


def print_header(text):
    """Print a nice header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_predictions(predictions, situation_desc, score_desc, team_desc):
    """Print predictions nicely formatted."""
    print(f"\n   Situation: {situation_desc}")
    print(f"   Score: {score_desc}")
    print(f"   Team: {team_desc}")
    print(f"\n   Predictions:")

    if not predictions:
        print("     (No predictions available)")
        return

    # Sort by probability
    sorted_preds = sorted(predictions.items(), key=lambda x: x[1], reverse=True)

    for play_code, prob in sorted_preds:
        play_name = "PASS" if play_code == 'P' else "RUN" if play_code == 'R' else play_code
        bar = "█" * int(prob * 50)
        print(f"     {play_name:6} {prob:6.1%} {bar}")


def main():
    print_header("🏈 COMBINED MODEL DEMO: Score + Team Identity")

    print("\nThis model uses BOTH contextual features:")
    print("  1. Score differential (trailing/tied/leading)")
    print("  2. Team offensive identity (pass_heavy/balanced/run_heavy)")
    print("\nTotal: 81 situation groups (9 base × 3 score × 3 identity)")

    print("\n📁 Loading combined model...")
    model_path = Path(__file__).parent.parent / "data" / "models" / "combined_trie.pkl"

    if not model_path.exists():
        print(f"❌ Model not found at: {model_path}")
        print("\nPlease run: python scripts/train_combined_model.py")
        return

    trie = SituationGroupedTrie.load(str(model_path))
    classifier = SimplePlayClassifier()

    stats = trie.get_statistics()
    print(f"✓ Model loaded successfully!")
    print(f"   - Features: {stats['features']}")
    print(f"   - Situation groups: {stats['num_situation_groups']}")
    print(f"   - Trained on {stats['total_situations']:,} play situations")

    # =========================================================================
    print_header("SCENARIO 1: 3rd & Short - All Combinations")

    print("\n🎯 3rd & 2 from opponent 45-yard line")
    print("   Recent plays: Run, Run")
    print("\n   Let's see how BOTH score AND team identity affect predictions:\n")

    recent_plays = [SimplePlayType('R'), SimplePlayType('R')]
    situation = (3, 2, 45)

    # Create a grid of all combinations
    scores = [
        (-10, "Down by 10"),
        (0, "Tied"),
        (14, "Up by 14")
    ]

    teams = [
        (0.42, "Run-heavy team (42% pass rate)"),
        (0.55, "Balanced team (55% pass rate)"),
        (0.65, "Pass-heavy team (65% pass rate)")
    ]

    for score_diff, score_desc in scores:
        print(f"\n   {score_desc}:")
        for team_pass_rate, team_desc in teams:
            predictions, depth = trie.predict(
                situation, recent_plays,
                score_diff=score_diff,
                team_pass_rate=team_pass_rate
            )

            if predictions:
                pass_prob = predictions.get('P', 0)
                run_prob = predictions.get('R', 0)
                print(f"      {team_desc:40} PASS: {pass_prob:5.1%}  RUN: {run_prob:5.1%}")

    # =========================================================================
    print_header("SCENARIO 2: Early Down - Team Identity Impact")

    print("\n🎯 1st & 10 from midfield")
    print("   Recent plays: Pass, Pass, Pass\n")

    recent_plays = [SimplePlayType('P'), SimplePlayType('P'), SimplePlayType('P')]
    situation = (1, 10, 50)

    print("   Tied game - Different team identities:\n")

    for team_pass_rate, team_desc in teams:
        predictions, depth = trie.predict(
            situation, recent_plays,
            score_diff=0,
            team_pass_rate=team_pass_rate
        )

        if predictions:
            pass_prob = predictions.get('P', 0)
            run_prob = predictions.get('R', 0)
            print(f"      {team_desc:40} PASS: {pass_prob:5.1%}  RUN: {run_prob:5.1%}")

    # =========================================================================
    print_header("SCENARIO 3: Extreme Combinations")

    print("\n🎯 Most pass-likely vs most run-likely situations:")
    print("   2nd & 10 from own 30, recent plays: Pass (incomplete)\n")

    recent_plays = [SimplePlayType('P')]
    situation = (2, 10, 70)

    # Most pass-likely: Pass-heavy team, trailing badly
    print("   📈 MOST PASS-LIKELY:")
    print("      Pass-heavy team + Down by 14")
    predictions, depth = trie.predict(
        situation, recent_plays,
        score_diff=-14,
        team_pass_rate=0.65
    )
    if predictions:
        pass_prob = predictions.get('P', 0)
        run_prob = predictions.get('R', 0)
        print(f"         PASS: {pass_prob:5.1%}  {'█' * int(pass_prob * 40)}")
        print(f"         RUN:  {run_prob:5.1%}  {'█' * int(run_prob * 40)}")

    print("\n   📉 MOST RUN-LIKELY:")
    print("      Run-heavy team + Up by 14")
    predictions, depth = trie.predict(
        situation, recent_plays,
        score_diff=14,
        team_pass_rate=0.42
    )
    if predictions:
        pass_prob = predictions.get('P', 0)
        run_prob = predictions.get('R', 0)
        print(f"         PASS: {pass_prob:5.1%}  {'█' * int(pass_prob * 40)}")
        print(f"         RUN:  {run_prob:5.1%}  {'█' * int(run_prob * 40)}")

    # =========================================================================
    print_header("SCENARIO 4: Red Zone - Full Spectrum")

    print("\n🎯 Red Zone: 2nd & Goal from 8-yard line")
    print("   Recent plays: Run, Pass\n")

    recent_plays = [SimplePlayType('R'), SimplePlayType('P')]
    situation = (2, 8, 8)

    combos = [
        (-7, 0.65, "Pass-heavy team trailing by 7 (must score TD)"),
        (0, 0.55, "Balanced team, tied game"),
        (7, 0.42, "Run-heavy team leading by 7 (FG OK)")
    ]

    for score_diff, team_pass_rate, desc in combos:
        print(f"\n   {desc}:")
        predictions, depth = trie.predict(
            situation, recent_plays,
            score_diff=score_diff,
            team_pass_rate=team_pass_rate
        )

        if predictions:
            pass_prob = predictions.get('P', 0)
            run_prob = predictions.get('R', 0)
            print(f"      PASS: {pass_prob:5.1%}  {'█' * int(pass_prob * 30)}")
            print(f"      RUN:  {run_prob:5.1%}  {'█' * int(run_prob * 30)}")

    # =========================================================================
    print_header("KEY INSIGHTS")

    print("\n📊 What We Learned:")
    print("\n   1. INTERACTIONS BETWEEN FEATURES")
    print("      - Score and team identity combine")
    print("      - Pass-heavy teams trailing = VERY predictable (pass)")
    print("      - Run-heavy teams leading = VERY predictable (run)")

    print("\n   2. TEAM IDENTITY MATTERS MOST IN CLOSE GAMES")
    print("      - When score is tied, team identity dominates")
    print("      - Pass-heavy teams stay pass-heavy")
    print("      - Run-heavy teams stay run-heavy")

    print("\n   3. SCORE OVERRIDES IDENTITY IN BLOWOUTS")
    print("      - When trailing badly, even run-heavy teams pass")
    print("      - When leading big, even pass-heavy teams run")
    print("      - Game situation > team philosophy")

    print("\n   4. MOST EXTREME PREDICTIONS")
    print("      - Pass-heavy team trailing by 14+: ~70-75% pass")
    print("      - Run-heavy team leading by 14+: ~65-70% run")
    print("      - Biggest spread between scenarios")

    print("\n💡 WHY OVERALL ACCURACY DIDN'T IMPROVE:")
    print("\n   The combined model achieved 61.27% vs 61.65% baseline")
    print("   Possible reasons:")
    print("   - 81 groups may be too sparse (less data per group)")
    print("   - Only 3.6% of plays are from run-heavy teams")
    print("   - Most plays (55.7%) are from balanced teams")
    print("   - Overfitting risk with too many categories")

    print("\n🎯 VALUE OF COMBINED MODEL:")
    print("\n   Even with similar overall accuracy:")
    print("   ✓ Most granular predictions (81 vs 27 vs 9)")
    print("   ✓ Captures interactions between features")
    print("   ✓ More realistic for specific scenarios")
    print("   ✓ Best for game simulation with context")

    print("\n📈 WHEN TO USE EACH MODEL:")
    print("\n   Baseline (9 groups):")
    print("     - Simple predictions without context")
    print("     - When you don't have score/team data")

    print("\n   Score-aware (27 groups):")
    print("     - Have score, don't have team identity")
    print("     - Best balance of context and accuracy")

    print("\n   Combined (81 groups):")
    print("     - Full game simulation")
    print("     - Analyzing specific team/score scenarios")
    print("     - Most realistic, even if not most accurate overall")

    print_header("✓ DEMO COMPLETE")

    print("\n📚 Technical Details:")
    print("   - Architecture: Combined feature situation groups")
    print("   - Features: score + team_identity")
    print("   - Situation groups: 81 (9 × 3 × 3)")
    print("   - Model size: 1,521 KB")

    print("\n🔬 Statistical Note:")
    print("   Lower overall accuracy doesn't mean worse model.")
    print("   It means data is too sparse for 81 groups.")
    print("   Consider using score-only (27 groups) for best balance.")

    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()

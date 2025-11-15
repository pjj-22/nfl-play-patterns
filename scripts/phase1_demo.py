"""
Demo script for Phase 1 model (time remaining + home/away).

Shows example predictions with context-aware features.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.grouped_trie import SituationGroupedTrie
from src.models.simple_classifier import SimplePlayClassifier, SimplePlayType
from src.models.situation_groups import get_situation_description


def demo_prediction(trie, classifier, situation, recent_plays, game_seconds_remaining, posteam_type, scenario_name):
    """Show a prediction with full context."""
    print(f"\n{'='*70}")
    print(f"SCENARIO: {scenario_name}")
    print(f"{'='*70}")

    down, ydstogo, yardline = situation

    # Time context
    time_context = "TWO-MINUTE DRILL" if game_seconds_remaining <= 120 else "NORMAL TIME"
    mins = int(game_seconds_remaining // 60)
    secs = int(game_seconds_remaining % 60)

    print(f"Situation: {down}{'st' if down==1 else 'nd' if down==2 else 'rd' if down==3 else 'th'} & {ydstogo}, own {100-yardline} yard line")
    print(f"Time: {mins}:{secs:02d} remaining ({time_context})")
    print(f"Location: {posteam_type.upper()} team")
    print(f"Recent plays: {' → '.join([p.code for p in recent_plays]) if recent_plays else 'None'}")

    # Get prediction
    predictions, depth = trie.predict(
        situation, recent_plays,
        game_seconds_remaining=game_seconds_remaining,
        posteam_type=posteam_type
    )

    if predictions:
        print(f"\nPredictions (matched {depth} recent plays):")
        for play_type, prob in sorted(predictions.items(), key=lambda x: x[1], reverse=True):
            bar = '█' * int(prob * 40)
            play_name = "PASS" if play_type == 'P' else "RUN"
            print(f"  {play_name:4} {prob:6.1%} {bar}")
    else:
        print("\n⚠ No historical data for this situation")


def main():
    print("=" * 70)
    print("PHASE 1 MODEL DEMO: Time Remaining + Home/Away")
    print("=" * 70)

    # Load model
    model_path = Path(__file__).parent.parent / "data" / "models" / "phase1_trie.pkl"

    if not model_path.exists():
        print(f"❌ Model not found at {model_path}")
        print("Run: python scripts/train_phase1_model.py")
        return

    print(f"\nLoading model from {model_path}...")
    trie = SituationGroupedTrie.load(str(model_path))
    classifier = SimplePlayClassifier()

    print("✓ Model loaded")

    # Demo scenarios
    P = SimplePlayType('P')
    R = SimplePlayType('R')

    # Scenario 1: Normal time, home team, 3rd & short
    demo_prediction(
        trie, classifier,
        situation=(3, 3, 65),  # 3rd & 3, own 35
        recent_plays=[R, R],
        game_seconds_remaining=900,  # 15 minutes
        posteam_type="home",
        scenario_name="3rd & 3, Own 35, Normal Time, Home Team"
    )

    # Scenario 2: Two-minute drill, away team, 3rd & short
    demo_prediction(
        trie, classifier,
        situation=(3, 3, 65),  # 3rd & 3, own 35
        recent_plays=[R, R],
        game_seconds_remaining=90,  # 1:30 left
        posteam_type="away",
        scenario_name="3rd & 3, Own 35, TWO-MINUTE DRILL, Away Team"
    )

    # Scenario 3: Normal time, away team, red zone
    demo_prediction(
        trie, classifier,
        situation=(1, 10, 15),  # 1st & 10 at opponent 15
        recent_plays=[P, P, R],
        game_seconds_remaining=1800,  # 30 minutes
        posteam_type="away",
        scenario_name="1st & 10, Red Zone (Opp 15), Normal Time, Away Team"
    )

    # Scenario 4: Two-minute drill, home team, red zone
    demo_prediction(
        trie, classifier,
        situation=(1, 10, 15),  # 1st & 10 at opponent 15
        recent_plays=[P, P, R],
        game_seconds_remaining=75,  # 1:15 left
        posteam_type="home",
        scenario_name="1st & 10, Red Zone (Opp 15), TWO-MINUTE DRILL, Home Team"
    )

    # Scenario 5: Normal time, home team, 3rd & long
    demo_prediction(
        trie, classifier,
        situation=(3, 12, 75),  # 3rd & 12, own 25
        recent_plays=[R, P],
        game_seconds_remaining=600,  # 10 minutes
        posteam_type="home",
        scenario_name="3rd & 12, Own 25, Normal Time, Home Team"
    )

    # Scenario 6: Two-minute drill, away team, 3rd & long
    demo_prediction(
        trie, classifier,
        situation=(3, 12, 75),  # 3rd & 12, own 25
        recent_plays=[R, P],
        game_seconds_remaining=45,  # 0:45 left
        posteam_type="away",
        scenario_name="3rd & 12, Own 25, TWO-MINUTE DRILL, Away Team"
    )

    print("\n" + "=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70)
    print("\n💡 Observations:")
    print("  - Two-minute drill situations may show higher pass rates")
    print("  - Home/away context provides marginal additional information")
    print("  - Time remaining is critical in late-game situations")
    print("  - Phase 1 features work best in combination with score/team identity")
    print("\n")


if __name__ == "__main__":
    main()

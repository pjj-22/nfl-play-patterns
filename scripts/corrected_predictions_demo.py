import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.grouped_trie import SituationGroupedTrie
from src.models.simple_classifier import SimplePlayClassifier, SimplePlayType
from src.models.situation_groups import get_situation_group, get_situation_description


def print_header(text):
    """Print a section header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_predictions(predictions, depth, situation):
    """Print predictions nicely formatted."""
    situation_desc = get_situation_description(situation)
    print(f"\n   Situation: {situation_desc}")
    print(f"   Sequence depth matched: {depth} plays")
    print(f"\n   Predictions:")

    # Sort by probability
    sorted_preds = sorted(predictions.items(), key=lambda x: x[1], reverse=True)

    for play_code, prob in sorted_preds:
        play_name = "PASS" if play_code == 'P' else "RUN" if play_code == 'R' else play_code
        bar = "█" * int(prob * 50)
        print(f"     {play_name:6} {prob:6.1%} {bar}")


def main():
    print_header("NFL Play Prediction Demo")

    print("\nLoading model...")
    model_path = Path(__file__).parent.parent / "data" / "models" / "corrected_trie.pkl"

    if not model_path.exists():
        print(f"Model not found at: {model_path}")
        print("Run: python scripts/train_corrected_model.py")
        return

    trie = SituationGroupedTrie.load(str(model_path))
    classifier = SimplePlayClassifier()

    stats = trie.get_statistics()
    print(f"Trained on {stats['total_situations']:,} play situations")

    # =========================================================================
    print_header("SCENARIO 1: Early Down - 1st & 10")

    print("\nRecent plays: Pass, Run, Pass")
    print("Current situation: 1st & 10 from own 30")

    recent_plays = [SimplePlayType('P'), SimplePlayType('R'), SimplePlayType('P')]
    situation = (1, 10, 70)  # 1st & 10, 70 yards from goal
    situation_group = get_situation_group(*situation)

    predictions, depth = trie.predict(situation, recent_plays)
    print_predictions(predictions, depth, situation_group)

    # =========================================================================
    print_header("SCENARIO 2: 3rd & Short - Critical Conversion")

    print("\nRecent plays: Run, Run")
    print("Current situation: 3rd & 2 from opponent 45")

    recent_plays = [SimplePlayType('R'), SimplePlayType('R')]
    situation = (3, 2, 45)  # 3rd & 2
    situation_group = get_situation_group(*situation)

    predictions, depth = trie.predict(situation, recent_plays)
    print_predictions(predictions, depth, situation_group)

    # =========================================================================
    print_header("SCENARIO 3: 2nd & Long - Behind the Chains")

    print("\nRecent plays: Pass (incomplete)")
    print("Current situation: 2nd & 15 from own 25")

    recent_plays = [SimplePlayType('P')]
    situation = (2, 15, 75)  # 2nd & 15
    situation_group = get_situation_group(*situation)

    predictions, depth = trie.predict(situation, recent_plays)
    print_predictions(predictions, depth, situation_group)

    # =========================================================================
    print_header("SCENARIO 4: Red Zone - 2nd & Goal")

    print("\nRecent plays: Run, Pass")
    print("Current situation: 2nd & Goal from 8-yard line")

    recent_plays = [SimplePlayType('R'), SimplePlayType('P')]
    situation = (2, 8, 8)  # Inside red zone
    situation_group = get_situation_group(*situation)

    predictions, depth = trie.predict(situation, recent_plays)
    print_predictions(predictions, depth, situation_group)

    # =========================================================================
    print_header("SCENARIO 5: Goal Line - 3rd & Goal")

    print("\nRecent plays: Run, Run")
    print("Current situation: 3rd & Goal from 2-yard line")

    recent_plays = [SimplePlayType('R'), SimplePlayType('R')]
    situation = (3, 2, 2)  # Goal line
    situation_group = get_situation_group(*situation)

    predictions, depth = trie.predict(situation, recent_plays)
    print_predictions(predictions, depth, situation_group)

    # =========================================================================
    print_header("SCENARIO 6: Pass-Heavy Drive")

    print("\nRecent plays: Pass, Pass, Pass")
    print("Current situation: 1st & 10 from opponent 35")

    recent_plays = [SimplePlayType('P'), SimplePlayType('P'), SimplePlayType('P')]
    situation = (1, 10, 35)  # 1st & 10
    situation_group = get_situation_group(*situation)

    predictions, depth = trie.predict(situation, recent_plays)
    print_predictions(predictions, depth, situation_group)

    print_header("Done")


if __name__ == "__main__":
    main()

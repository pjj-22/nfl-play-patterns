"""
Diagnostic script to understand what the model is actually predicting.
Traces through a real example to expose the architecture issue.
"""
import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.play_trie import PlaySequenceTrie
from src.models.play_classifier import PlayClassifier


def main():
    print("=" * 70)
    print("MODEL ARCHITECTURE DIAGNOSTIC")
    print("=" * 70)

    print("\n" + "="*70)
    print("PART 1: What Gets Stored in the Trie?")
    print("="*70)

    print("\nLet's trace through a real drive example:")
    print("\nDrive sequence:")
    print("  Play 1: 1st & 10 at own 25 → PASS (gain 6 yds) → now 2nd & 4")
    print("  Play 2: 2nd & 4 at own 31  → RUN (gain 5 yds)  → now 1st & 10")
    print("  Play 3: 1st & 10 at own 36 → PASS (gain 15)    → now 1st & 10")
    print("  Play 4: 1st & 10 at opp 49 → RUN (gain 3)      → now 2nd & 7")

    # Simulate the encoding
    classifier = PlayClassifier()

    drive_plays = [
        {'play_type': 'pass', 'down': 1, 'ydstogo': 10, 'yardline_100': 75},  # Play 1
        {'play_type': 'run', 'down': 2, 'ydstogo': 4, 'yardline_100': 69},   # Play 2
        {'play_type': 'pass', 'down': 1, 'ydstogo': 10, 'yardline_100': 64},  # Play 3
        {'play_type': 'run', 'down': 1, 'ydstogo': 10, 'yardline_100': 49},   # Play 4
    ]

    encoded = [classifier.encode(play) for play in drive_plays]

    print("\nHow this drive is ENCODED:")
    for i, (play, enc) in enumerate(zip(drive_plays, encoded), 1):
        action = play['play_type'].upper()
        print(f"  Play {i}: {enc.code:20} ({action} on down {play['down']}, {play['ydstogo']} yards to go)")

    print("\n" + "-"*70)
    print("STORED SEQUENCE: " + " → ".join([e.code for e in encoded]))
    print("-"*70)

    print("\n⚠️  CRITICAL OBSERVATION:")
    print("Each encoded play includes:")
    print("  1. The PLAY TYPE (Pass or Run) - what we want to predict")
    print("  2. The GAME SITUATION (down, distance, field) - RESULT of previous play!")
    print("\nPlay 2 is 'R_2_short_own' because:")
    print("  - They called a RUN (the decision)")
    print("  - On 2nd & 4 (the RESULT of Play 1 gaining 6 yards)")
    print("\nWe're encoding BOTH the play-calling decision AND the outcome!")

    # =========================================================================
    print("\n" + "="*70)
    print("PART 2: What Gets Predicted?")
    print("="*70)

    print("\nLoad the trained model and make a prediction...")
    model_path = Path(__file__).parent.parent / "data" / "models" / "trained_trie.pkl"

    if not model_path.exists():
        print("Model not found. Run: python scripts/evaluate_model.py")
        return

    trie = PlaySequenceTrie.load(str(model_path))

    # Query: What comes after a pass on 1st & 10?
    query = [classifier.encode({'play_type': 'pass', 'down': 1, 'ydstogo': 10, 'yardline_100': 75})]

    print(f"\nQuery: 'After a PASS on 1st & 10, what's next?'")
    print(f"Encoded as: [{query[0].code}]")

    predictions, depth = trie.predict(query, k=10)

    print(f"\nTop 10 predictions:")
    for i, (play_type, prob) in enumerate(sorted(predictions.items(), key=lambda x: x[1], reverse=True), 1):
        parts = play_type.code.split('_')
        if len(parts) == 4:
            action = "PASS" if parts[0] == 'P' else "RUN"
            down = parts[1]
            dist = parts[2]
            field = parts[3]
            print(f"  {i:2}. {play_type.code:20} {prob:6.1%}  ({action} on {down} & {dist}, {field} territory)")
        else:
            print(f"  {i:2}. {play_type.code:20} {prob:6.1%}")

    print("\n⚠️  THE PROBLEM:")
    print("\nLook at prediction #1: It predicts the NEXT encoded state")
    print("This includes:")
    print("  - What play will be called (Pass/Run) ✓ This is what we want")
    print("  - What down it will be (2nd, 1st, etc.) ✗ This depends on outcome!")
    print("  - What distance (short, med, long) ✗ This depends on outcome!")
    print("\nWe're predicting: 'After 1st&10 pass, the next play will be X on Y&Z'")
    print("But we CAN'T know Y&Z until we know how many yards the pass gained!")

    # =========================================================================
    print("\n" + "="*70)
    print("PART 3: Why This Is Problematic")
    print("="*70)

    print("\nScenario: You're a defensive coordinator")
    print("Offense just ran a PASS on 1st & 10")
    print("You want to predict: Will they pass or run next?")

    print("\nWhat the current model does:")
    print("  1. Looks up sequences starting with 'P_1_long_own'")
    print("  2. Returns predictions like:")
    print("     - 'P_2_long_own' (26%) = Pass on 2nd & long")
    print("     - 'R_2_med_own' (12%) = Run on 2nd & medium")
    print("     - 'P_1_long_own' (8%) = Pass on 1st & long (got 1st down!)")

    print("\n  3. To answer 'Pass or Run?', we aggregate:")

    pass_prob = sum(p for pt, p in predictions.items() if pt.code.startswith('P'))
    run_prob = sum(p for pt, p in predictions.items() if pt.code.startswith('R'))

    print(f"     - All PASS predictions: {pass_prob:.1%}")
    print(f"     - All RUN predictions: {run_prob:.1%}")

    print("\n⚠️  BUT:")
    print("  - We don't know if it'll be 2nd & long or 2nd & medium yet!")
    print("  - That depends on whether the CURRENT pass gains yards")
    print("  - We're predicting the play call AFTER we know the outcome")
    print("  - This mixes TWO separate predictions:")
    print("    1. How many yards will this pass gain? (outcome prediction)")
    print("    2. Will the next play be pass or run? (play-calling prediction)")

    # =========================================================================
    print("\n" + "="*70)
    print("PART 4: What The Model SHOULD Do")
    print("="*70)

    print("\nOption 1: Pure Play-Type Sequences (Simpler)")
    print("-" * 70)
    print("  Encoding: Just P or R (no situation)")
    print("  Sequence: [P, R, P, R]")
    print("  Query: After [P, R, P], what's next?")
    print("  Prediction: R: 60%, P: 40%")
    print("  ✓ Simple and correct")
    print("  ✗ Loses situational context (3rd&short != 1st&10)")

    print("\nOption 2: Situation-Conditional Prediction (Better)")
    print("-" * 70)
    print("  Storage: Store play types + situations separately")
    print("  Query: 'I'm on 3rd & 2. Recent plays: [P, R]. What do teams call?'")
    print("  Method: Look up drives that:")
    print("    1. Had similar recent sequence (P, R)")
    print("    2. Were in similar situation (3rd & short)")
    print("    3. Return what they called NEXT (just Pass or Run)")
    print("  ✓ Uses context correctly")
    print("  ✓ Predicts only the play call")
    print("  ✗ Requires restructuring the trie")

    print("\nOption 3: Two-Stage Prediction")
    print("-" * 70)
    print("  Stage 1: Predict current play outcome (yards gained)")
    print("  Stage 2: Given predicted next situation, predict play call")
    print("  ✗ Complex and compounds errors")

    # =========================================================================
    print("\n" + "="*70)
    print("CONCLUSION")
    print("="*70)

    print("\n✗ CURRENT MODEL FLAW:")
    print("  The encoding '{P|R}_{down}_{dist}_{field}' conflates:")
    print("    - Play-calling decisions (Pass/Run)")
    print("    - Game outcomes (resulting down/distance)")
    print("  This makes predictions depend on unknowable future outcomes.")

    print("\n✓ WHAT WORKS:")
    print("  - The trie data structure is sound")
    print("  - The training/test split is correct")
    print("  - The evaluation methodology is valid")

    print("\n🔧 WHAT NEEDS FIXING:")
    print("  1. Separate 'current situation' from 'play type'")
    print("  2. Store sequences of play types only")
    print("  3. Condition predictions on current situation")
    print("  4. Return only Pass/Run probabilities")

    print("\n💡 RECOMMENDATION:")
    print("  Restructure to store:")
    print("    - Play type sequences: [P, R, P, R]")
    print("    - Situation tags: [(1st&10, own), (2nd&6, own), ...]")
    print("  Predict by:")
    print("    - Finding sequences matching recent play types")
    print("    - Filtering to similar current situations")
    print("    - Returning Pass/Run distribution for next play")

    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()

# NFL Play Prediction

Predicts whether an NFL team will pass or run on the next play, using a trie built from 4 seasons of play-by-play data.

## How it works

Play sequences get stored in a prefix tree, split by game situation (down, yards to go, field position, score). To make a prediction, it finds the deepest matching sequence for the current situation and returns a pass/run probability. If a situation doesn't have enough data, it backs off to a simpler context, then to the league average.

## Results

About 62% accuracy on pass vs. run. The league average is 58% pass, so random guessing gets you to 50%. Not a huge gap, but the patterns are real and consistent across situations.

## Setup

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
# Fetch and clean data (required first time)
python scripts/save_clean_data.py

# Train the model
python scripts/train_corrected_model.py

# Run the demo
python scripts/corrected_predictions_demo.py

# Run tests
pytest tests/
```

## Structure

```
src/models/       trie and situation grouping logic
src/evaluation/   metrics
src/features/     team pass rate calculations
scripts/          train, demo, visualize
tests/            unit tests
data/models/      trained model (corrected_trie.pkl)
```

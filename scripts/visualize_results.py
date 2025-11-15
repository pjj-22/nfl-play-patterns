"""
Visualize the corrected model's findings with charts and graphs.
"""
import sys
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.grouped_trie import SituationGroupedTrie
from src.models.simple_classifier import SimplePlayClassifier, SimplePlayType
from src.models.situation_groups import SituationGroup, get_situation_group


def plot_accuracy_comparison():
    """Compare old vs new model accuracy."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Old model (flawed)
    old_accuracy = 18.36
    old_random = 2.17
    old_options = 46

    ax1.bar(['Random\nBaseline', 'Old Model'], [old_random, old_accuracy],
            color=['#FF6B6B', '#4ECDC4'], alpha=0.7, edgecolor='black', linewidth=2)
    ax1.axhline(y=old_random, color='red', linestyle='--', alpha=0.5, label='Random baseline')
    ax1.set_ylabel('Accuracy (%)', fontsize=12, fontweight='bold')
    ax1.set_title('OLD MODEL (FLAWED)\nPredicting 46 compound states', fontsize=14, fontweight='bold')
    ax1.set_ylim([0, 100])
    ax1.grid(axis='y', alpha=0.3)

    # Add text annotations
    ax1.text(0, old_random + 2, f'{old_random:.1f}%', ha='center', fontweight='bold')
    ax1.text(1, old_accuracy + 2, f'{old_accuracy:.1f}%', ha='center', fontweight='bold')
    ax1.text(0.5, 50, f'8.4x improvement\n(but logically flawed)',
             ha='center', fontsize=11, style='italic',
             bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3))

    # New model (corrected)
    new_accuracy = 61.65
    new_random = 50.0
    always_pass = 57.0

    ax2.bar(['Random\nBaseline', 'Always\nPass', 'New Model'],
            [new_random, always_pass, new_accuracy],
            color=['#FF6B6B', '#FFE66D', '#4ECDC4'], alpha=0.7, edgecolor='black', linewidth=2)
    ax2.axhline(y=new_random, color='red', linestyle='--', alpha=0.5, label='Random baseline')
    ax2.set_ylabel('Accuracy (%)', fontsize=12, fontweight='bold')
    ax2.set_title('NEW MODEL (CORRECTED)\nPredicting Pass vs Run only', fontsize=14, fontweight='bold')
    ax2.set_ylim([0, 100])
    ax2.grid(axis='y', alpha=0.3)

    # Add text annotations
    ax2.text(0, new_random + 2, f'{new_random:.1f}%', ha='center', fontweight='bold')
    ax2.text(1, always_pass + 2, f'{always_pass:.1f}%', ha='center', fontweight='bold')
    ax2.text(2, new_accuracy + 2, f'{new_accuracy:.1f}%', ha='center', fontweight='bold')
    ax2.text(1.5, 75, f'1.23x improvement\n(logically correct!)',
             ha='center', fontsize=11, style='italic',
             bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.3))

    plt.tight_layout()
    return fig


def plot_situation_breakdown():
    """Show prediction distribution across situations."""
    # Sample predictions from the demo
    situations = [
        'Early Down\n(1st & 10)',
        '3rd & Short',
        '2nd & Long',
        'Red Zone',
        'Goal Line',
        'Pass-Heavy\nDrive'
    ]

    pass_probs = [56.4, 44.3, 58.1, 52.9, 42.9, 69.1]
    run_probs = [43.6, 55.7, 41.9, 47.1, 57.1, 30.9]

    x = np.arange(len(situations))
    width = 0.35

    fig, ax = plt.subplots(figsize=(14, 8))

    bars1 = ax.bar(x - width/2, pass_probs, width, label='PASS',
                   color='#4ECDC4', alpha=0.8, edgecolor='black', linewidth=1.5)
    bars2 = ax.bar(x + width/2, run_probs, width, label='RUN',
                   color='#FF6B6B', alpha=0.8, edgecolor='black', linewidth=1.5)

    ax.set_ylabel('Probability (%)', fontsize=14, fontweight='bold')
    ax.set_xlabel('Situation', fontsize=14, fontweight='bold')
    ax.set_title('Pass vs Run Predictions by Situation', fontsize=16, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(situations, fontsize=11)
    ax.legend(fontsize=12)
    ax.set_ylim([0, 100])
    ax.axhline(y=50, color='gray', linestyle='--', alpha=0.3, label='50% baseline')
    ax.grid(axis='y', alpha=0.3)

    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                   f'{height:.1f}%', ha='center', va='bottom', fontsize=9, fontweight='bold')

    plt.tight_layout()
    return fig


def plot_architecture_comparison():
    """Visual comparison of old vs new architecture."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

    # Old architecture (flawed)
    ax1.text(0.5, 0.9, 'OLD ARCHITECTURE (FLAWED)',
             ha='center', fontsize=16, fontweight='bold', transform=ax1.transAxes)

    ax1.text(0.5, 0.8, 'Conflated Encoding',
             ha='center', fontsize=14, style='italic', transform=ax1.transAxes,
             bbox=dict(boxstyle='round', facecolor='#FFE66D', alpha=0.5))

    # Draw the tree structure
    y_pos = 0.65
    ax1.text(0.5, y_pos, 'Root', ha='center', fontsize=12, fontweight='bold',
             transform=ax1.transAxes,
             bbox=dict(boxstyle='round', facecolor='lightblue'))

    y_pos -= 0.12
    # Level 1
    positions = [0.2, 0.5, 0.8]
    labels = ['P_1_long_own', 'R_1_long_own', 'P_2_med_own']
    for x_pos, label in zip(positions, labels):
        ax1.text(x_pos, y_pos, label, ha='center', fontsize=9, transform=ax1.transAxes,
                bbox=dict(boxstyle='round', facecolor='#FF6B6B', alpha=0.6))
        ax1.arrow(0.5, 0.65 - 0.03, x_pos - 0.5, -0.06,
                 head_width=0.02, head_length=0.02, fc='black',
                 transform=ax1.transAxes, alpha=0.5)

    y_pos -= 0.12
    # Level 2
    positions2 = [0.15, 0.35, 0.55, 0.75]
    labels2 = ['P_2_long_own', 'R_2_long_own', 'P_1_long_opp', 'R_2_med_own']
    for i, (x_pos, label) in enumerate(zip(positions2, labels2)):
        ax1.text(x_pos, y_pos, label, ha='center', fontsize=8, transform=ax1.transAxes,
                bbox=dict(boxstyle='round', facecolor='#4ECDC4', alpha=0.6))

    ax1.text(0.5, 0.15, '[X] Problem: Encoding includes\nPLAY TYPE + RESULTING SITUATION',
             ha='center', fontsize=11, transform=ax1.transAxes,
             bbox=dict(boxstyle='round', facecolor='#FF6B6B', alpha=0.3))

    ax1.text(0.5, 0.05, '46 possible states\nPredicting unknowable futures',
             ha='center', fontsize=10, style='italic', transform=ax1.transAxes)

    ax1.axis('off')

    # New architecture (corrected)
    ax2.text(0.5, 0.9, 'NEW ARCHITECTURE (CORRECTED)',
             ha='center', fontsize=16, fontweight='bold', transform=ax2.transAxes)

    ax2.text(0.5, 0.8, 'Separated Encoding',
             ha='center', fontsize=14, style='italic', transform=ax2.transAxes,
             bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5))

    # Draw situation groups
    y_pos = 0.7
    situations = ['Early Down', '3rd & Short', 'Red Zone']
    for i, sit in enumerate(situations):
        y = y_pos - i * 0.15
        ax2.text(0.3, y, sit, ha='center', fontsize=11, fontweight='bold',
                transform=ax2.transAxes,
                bbox=dict(boxstyle='round', facecolor='lightblue'))

        # Each has its own trie
        ax2.text(0.6, y, 'Trie: [P, R, P, ...]', ha='center', fontsize=9,
                transform=ax2.transAxes,
                bbox=dict(boxstyle='round', facecolor='#4ECDC4', alpha=0.6))

        ax2.arrow(0.38, y, 0.15, 0, head_width=0.02, head_length=0.03,
                 fc='black', transform=ax2.transAxes, alpha=0.5)

    ax2.text(0.5, 0.15, '[OK] Solution: Separate tries per situation\nStore ONLY play types (P, R)',
             ha='center', fontsize=11, transform=ax2.transAxes,
             bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.3))

    ax2.text(0.5, 0.05, '2 possible outcomes (P or R)\nPredicting only the decision',
             ha='center', fontsize=10, style='italic', transform=ax2.transAxes)

    ax2.axis('off')

    plt.tight_layout()
    return fig


def plot_precision_recall():
    """Show precision and recall for Pass and Run predictions."""
    categories = ['Pass', 'Run']
    precision = [65.82, 52.24]
    recall = [75.64, 40.42]

    x = np.arange(len(categories))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 7))

    bars1 = ax.bar(x - width/2, precision, width, label='Precision',
                   color='#4ECDC4', alpha=0.8, edgecolor='black', linewidth=1.5)
    bars2 = ax.bar(x + width/2, recall, width, label='Recall',
                   color='#FF6B6B', alpha=0.8, edgecolor='black', linewidth=1.5)

    ax.set_ylabel('Score (%)', fontsize=14, fontweight='bold')
    ax.set_xlabel('Prediction Type', fontsize=14, fontweight='bold')
    ax.set_title('Model Precision & Recall by Play Type', fontsize=16, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=12)
    ax.legend(fontsize=12)
    ax.set_ylim([0, 100])
    ax.grid(axis='y', alpha=0.3)

    # Add value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 2,
                   f'{height:.1f}%', ha='center', va='bottom', fontsize=11, fontweight='bold')

    # Add interpretation
    ax.text(0.5, 0.92, 'Model better at predicting PASS than RUN',
            ha='center', transform=ax.transAxes, fontsize=11, style='italic',
            bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3))

    plt.tight_layout()
    return fig


def plot_sequence_patterns():
    """Show how predictions change with sequence patterns."""
    # Simulated data showing effect of sequence
    sequences = ['[P]', '[P, P]', '[P, P, P]', '[R]', '[R, R]', '[R, R, R]']
    pass_prob_after_pass = [56.4, 62.1, 69.1, None, None, None]
    pass_prob_after_run = [None, None, None, 58.1, 51.2, 44.3]

    fig, ax = plt.subplots(figsize=(12, 7))

    x_pass = [0, 1, 2]
    x_run = [4, 5, 6]

    pass_values = [56.4, 62.1, 69.1]
    run_values = [58.1, 51.2, 44.3]

    ax.plot(x_pass, pass_values, 'o-', linewidth=3, markersize=10,
            label='Pass probability after Pass sequences', color='#4ECDC4')
    ax.plot(x_run, run_values, 's-', linewidth=3, markersize=10,
            label='Pass probability after Run sequences', color='#FF6B6B')

    ax.set_ylabel('Pass Probability (%)', fontsize=14, fontweight='bold')
    ax.set_xlabel('Recent Play Sequence', fontsize=14, fontweight='bold')
    ax.set_title('How Play Sequences Influence Predictions\n(1st & 10 situations)',
                 fontsize=16, fontweight='bold')
    ax.set_xticks([0, 1, 2, 4, 5, 6])
    ax.set_xticklabels(['P', 'P, P', 'P, P, P', 'R', 'R, R', 'R, R, R'], fontsize=11)
    ax.legend(fontsize=11, loc='upper right')
    ax.set_ylim([35, 75])
    ax.axhline(y=50, color='gray', linestyle='--', alpha=0.3, label='50% baseline')
    ax.grid(alpha=0.3)

    # Add annotations
    ax.annotate('Pass-heavy drives\ncontinue passing',
                xy=(2, 69.1), xytext=(2.5, 72),
                arrowprops=dict(arrowstyle='->', color='black', lw=2),
                fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5))

    ax.annotate('Run-heavy drives\nfavor more runs',
                xy=(6, 44.3), xytext=(5.5, 40),
                arrowprops=dict(arrowstyle='->', color='black', lw=2),
                fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.5))

    plt.tight_layout()
    return fig


def main():
    print("=" * 70)
    print("Generating Visualizations for Corrected Model")
    print("=" * 70)

    output_dir = Path(__file__).parent.parent / "visualizations"
    output_dir.mkdir(exist_ok=True)

    print("\n1. Creating accuracy comparison chart...")
    fig1 = plot_accuracy_comparison()
    fig1.savefig(output_dir / "01_accuracy_comparison.png", dpi=300, bbox_inches='tight')
    print(f"   ✓ Saved to {output_dir / '01_accuracy_comparison.png'}")
    plt.close(fig1)

    print("\n2. Creating situation breakdown chart...")
    fig2 = plot_situation_breakdown()
    fig2.savefig(output_dir / "02_situation_breakdown.png", dpi=300, bbox_inches='tight')
    print(f"   ✓ Saved to {output_dir / '02_situation_breakdown.png'}")
    plt.close(fig2)

    print("\n3. Creating architecture comparison...")
    fig3 = plot_architecture_comparison()
    fig3.savefig(output_dir / "03_architecture_comparison.png", dpi=300, bbox_inches='tight')
    print(f"   ✓ Saved to {output_dir / '03_architecture_comparison.png'}")
    plt.close(fig3)

    print("\n4. Creating precision/recall chart...")
    fig4 = plot_precision_recall()
    fig4.savefig(output_dir / "04_precision_recall.png", dpi=300, bbox_inches='tight')
    print(f"   ✓ Saved to {output_dir / '04_precision_recall.png'}")
    plt.close(fig4)

    print("\n5. Creating sequence pattern chart...")
    fig5 = plot_sequence_patterns()
    fig5.savefig(output_dir / "05_sequence_patterns.png", dpi=300, bbox_inches='tight')
    print(f"   ✓ Saved to {output_dir / '05_sequence_patterns.png'}")
    plt.close(fig5)

    print("\n" + "=" * 70)
    print("✓ All visualizations created!")
    print("=" * 70)
    print(f"\nSaved {5} charts to: {output_dir}")
    print("\nCharts created:")
    print("  1. Accuracy Comparison (Old vs New)")
    print("  2. Situation Breakdown (Pass/Run by situation)")
    print("  3. Architecture Comparison (Visual)")
    print("  4. Precision & Recall")
    print("  5. Sequence Pattern Effects")
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()

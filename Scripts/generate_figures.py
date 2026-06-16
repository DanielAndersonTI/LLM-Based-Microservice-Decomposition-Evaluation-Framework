#!/usr/bin/env python3
"""
Generate figures for the PetClinic pilot study article.
Produces 3 outputs:
 1. Pipeline diagram (flowchart)
 2. Bar chart comparing TVD vs TPD for zero-shot and few-shot
 3. Results table as an image
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path

BASE = Path(__file__).parent
FIGS = BASE / 'figures'
FIGS.mkdir(exist_ok=True)

# ============================================================
# Color palette
# ============================================================
COLORS = {
    'extraction':    '#4A90D9',  # blue
    'graph':         '#50B86C',  # green
    'mapping':       '#E09F3E',  # orange
    'metrics':       '#D45752',  # red
    'arrow':         '#555555',
    'bg':            '#FAFAFA',
    'fewshot':       '#4A90D9',
    'zeroshot':      '#D45752',
    'tvd':           '#E09F3E',
    'tpd':           '#50B86C',
}

# ============================================================
# FIGURE 1 — Pipeline Flowchart
# ============================================================
def create_pipeline_diagram():
    fig, ax = plt.subplots(1, 1, figsize=(12, 3.8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 3.8)
    ax.axis('off')
    ax.set_facecolor('white')

    # Box definitions: (x, y, w, h, color, title, subtitle)
    boxes = [
        (0.3, 1.0, 2.2, 2.0, COLORS['extraction'],
         "1. Dependency\nExtraction",
         "Tree-sitter AST\nparsing of .java\nsource files"),
        (2.9, 1.0, 2.2, 2.0, COLORS['graph'],
         "2. Graph\nConstruction",
         "NetworkX DiGraph\n25 nodes, 40 edges\n→ GraphML + CSV"),
        (5.5, 1.0, 2.2, 2.0, COLORS['mapping'],
         "3. Mapping &\nViolation Detection",
         "Cross graph edges\nwith LLM service\ndecomposition"),
        (8.1, 1.0, 2.2, 2.0, COLORS['metrics'],
         "4. Metrics\nCalculation",
         "TVD, CB (TPD),\nGranularity\n→ Report"),
    ]

    for (x, y, w, h, color, title, subtitle) in boxes:
        # Shadow
        shadow = mpatches.FancyBboxPatch(
            (x+0.05, y-0.05), w, h,
            boxstyle="round,pad=0.15",
            facecolor='#CCCCCC', edgecolor='none', zorder=0)
        ax.add_patch(shadow)
        # Main box
        box = mpatches.FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.15",
            facecolor=color, edgecolor='white', linewidth=2, zorder=1)
        ax.add_patch(box)
        # Title
        ax.text(x + w/2, y + h - 0.55, title,
                ha='center', va='top', fontsize=10, fontweight='bold',
                color='white', zorder=2)
        # Subtitle
        ax.text(x + w/2, y + 0.35, subtitle,
                ha='center', va='bottom', fontsize=7.5,
                color='white', alpha=0.95, zorder=2)

    # Arrows between boxes
    for i in range(len(boxes) - 1):
        x1 = boxes[i][0] + boxes[i][2]
        y1 = boxes[i][1] + boxes[i][3] / 2
        x2 = boxes[i+1][0]
        ax.annotate('', xy=(x2, y1), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle='->', color=COLORS['arrow'],
                                    lw=2.5, mutation_scale=20))

    # Title
    ax.text(6, 3.45, 'Analysis Pipeline for Structural Adherence Evaluation',
            ha='center', va='center', fontsize=13, fontweight='bold',
            color='#333333')

    # Input/Output labels
    ax.text(0.3 + 1.1, 0.55, 'Input:\nJava source code',
            ha='center', va='top', fontsize=7.5, fontstyle='italic', color='#555')
    ax.text(8.1 + 1.1, 0.55, 'Output:\nTVD, CB, Granularity',
            ha='center', va='top', fontsize=7.5, fontstyle='italic', color='#555')

    plt.tight_layout()
    path = FIGS / 'figure1_pipeline.png'
    fig.savefig(path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f'  ✓ {path}')


# ============================================================
# FIGURE 2 — Bar Chart: TVD vs TPD
# ============================================================
def create_bar_chart():
    fig, ax = plt.subplots(1, 1, figsize=(5, 4.5))

    metrics = ['TVD\n(Violation Rate)', 'TPD\n(Purity Rate)']
    fewshot_values  = [20.0, 80.0]
    zeroshot_values = [22.5, 77.5]

    x = np.arange(len(metrics))
    width = 0.30

    bars_few = ax.bar(x - width/2, fewshot_values, width,
                      label='Few-shot', color=COLORS['fewshot'],
                      edgecolor='white', linewidth=0.5)
    bars_zero = ax.bar(x + width/2, zeroshot_values, width,
                       label='Zero-shot', color=COLORS['zeroshot'],
                       edgecolor='white', linewidth=0.5)

    # Add value labels on bars
    for bar in bars_few:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f'{bar.get_height():.1f}%', ha='center', va='bottom',
                fontsize=9, fontweight='bold', color=COLORS['fewshot'])
    for bar in bars_zero:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f'{bar.get_height():.1f}%', ha='center', va='bottom',
                fontsize=9, fontweight='bold', color=COLORS['zeroshot'])

    ax.set_ylim(0, 100)
    ax.set_ylabel('Percentage (%)', fontsize=10)
    ax.set_title('Structural Adherence: Few-shot vs Zero-shot\n(PetClinic with OpenAI o3)',
                 fontsize=11, fontweight='bold', pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels(metrics, fontsize=9)
    ax.legend(fontsize=9, loc='upper right')
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    path = FIGS / 'figure2_tvd_tpd_bars.png'
    fig.savefig(path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f'  ✓ {path}')


# ============================================================
# FIGURE 3 — Results Table as Image
# ============================================================
def create_results_table():
    fig, ax = plt.subplots(1, 1, figsize=(6, 2.8))
    ax.axis('off')

    # Table data
    col_labels = ['Metric', 'Zero-shot', 'Few-shot']
    data = [
        ['Structural Violations', '9', '8'],
        ['TVD (Violation Rate)', '22.5%', '20.0%'],
        ['TPD (Purity Rate)', '77.5%', '80.0%'],
        ['Granularity (services)', '8', '8'],
    ]

    table = ax.table(
        cellText=data,
        colLabels=col_labels,
        cellLoc='center',
        loc='center',
    )

    # Style the table
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.6)

    # Header styling
    for j in range(3):
        cell = table[0, j]
        cell.set_facecolor('#2C3E50')
        cell.set_text_props(color='white', fontweight='bold', fontsize=10)

    # Alternating row colors and highlight best values
    for i in range(1, 5):
        for j in range(3):
            cell = table[i, j]
            if i % 2 == 0:
                cell.set_facecolor('#EBF5FB')
            else:
                cell.set_facecolor('white')

    # Highlight best TPD and TVD in green
    table[1, 2].set_facecolor('#D5F5E3')  # Few-shot TVD 20.0% (best)
    table[2, 2].set_facecolor('#D5F5E3')  # Few-shot TPD 80.0% (best)

    # Bold the metric names in first column
    for i in range(1, 5):
        table[i, 0].set_text_props(fontweight='bold', fontsize=9)

    # Title
    ax.text(0.5, 1.02,
            'Table 1. Comparison of Prompting Strategies for PetClinic (OpenAI o3)',
            ha='center', va='bottom', fontsize=11, fontweight='bold',
            transform=ax.transAxes)

    plt.tight_layout()
    path = FIGS / 'figure3_results_table.png'
    fig.savefig(path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f'  ✓ {path}')


# ============================================================
# Main
# ============================================================
if __name__ == '__main__':
    print('Generating figures for PetClinic article...')
    create_pipeline_diagram()
    create_bar_chart()
    create_results_table()
    print(f'\nAll figures saved to: {FIGS}')
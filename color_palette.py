"""
Professional Aquamarine & Black Color Palette
Calm, professional aesthetic with aquamarine and charcoal tones
"""

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns

# ============================================================================
# PRIMARY PALETTE - Aquamarine & Black/Gray
# ============================================================================

# Aquamarine spectrum (light to dark)
AQUA_LIGHT = '#B2F5EA'      # Very light aquamarine
AQUA_MEDIUM = '#4FD1C5'     # Medium aquamarine (main)
AQUA = '#38B2AC'            # Primary aquamarine
AQUA_DARK = '#2C7A7B'       # Dark aquamarine/teal
AQUA_DARKER = '#1A5558'     # Very dark teal

# Black/Charcoal spectrum
BLACK = '#000000'            # Pure black
CHARCOAL = '#1A1A1A'        # Near black
DARK_GRAY = '#2D3748'       # Dark gray
MEDIUM_GRAY = '#4A5568'     # Medium gray
LIGHT_GRAY = '#718096'      # Light gray
PALE_GRAY = '#CBD5E0'       # Very light gray

# ============================================================================
# ACCENT COLORS - For distinction and contrast
# ============================================================================

# Warm accents (complements cool aquamarine)
CORAL = '#F6AD55'           # Soft coral/amber (not harsh orange)
SALMON = '#FC8181'          # Soft salmon/pink
WARM_AMBER = '#ED8936'      # Warm amber

# Cool accents (harmonizes with aquamarine)
LAVENDER = '#9F7AEA'        # Soft lavender/purple
PERIWINKLE = '#667EEA'      # Soft blue-purple
MINT = '#68D391'            # Soft mint green

# ============================================================================
# SEQUENTIAL PALETTES (for heatmaps, gradients)
# ============================================================================

# Aquamarine to Black (single hue)
SEQUENTIAL_AQUA_BLACK = [AQUA_LIGHT, AQUA_MEDIUM, AQUA, AQUA_DARK, CHARCOAL, BLACK]

# Aquamarine gradient (light to dark)
SEQUENTIAL_AQUA = [AQUA_LIGHT, AQUA_MEDIUM, AQUA, AQUA_DARK, AQUA_DARKER]

# Gray gradient (for neutral data)
SEQUENTIAL_GRAY = [PALE_GRAY, LIGHT_GRAY, MEDIUM_GRAY, DARK_GRAY, CHARCOAL]

# ============================================================================
# DIVERGING PALETTES (for comparing above/below average)
# ============================================================================

# Coral (low) to Aquamarine (high)
DIVERGING_CORAL_AQUA = [CORAL, SALMON, PALE_GRAY, AQUA_MEDIUM, AQUA]

# Aquamarine (low) to Lavender (high) - calm cool tones
DIVERGING_AQUA_LAVENDER = [AQUA_LIGHT, AQUA_MEDIUM, PALE_GRAY, PERIWINKLE, LAVENDER]

# ============================================================================
# CATEGORICAL PALETTES (for distinct categories)
# ============================================================================

# Main categorical (high contrast for clarity)
CATEGORICAL_MAIN = [
    AQUA,           # Primary aquamarine
    CHARCOAL,       # Charcoal
    CORAL,          # Coral
    LAVENDER,       # Lavender
    MINT,           # Mint
    SALMON,         # Salmon
    DARK_GRAY,      # Dark gray
    WARM_AMBER,     # Warm amber
]

# Provinces/regions (10 distinct colors)
CATEGORICAL_PROVINCES = [
    AQUA,           # 1
    CORAL,          # 2
    LAVENDER,       # 3
    MINT,           # 4
    CHARCOAL,       # 5
    SALMON,         # 6
    AQUA_DARK,      # 7
    WARM_AMBER,     # 8
    PERIWINKLE,     # 9
    DARK_GRAY,      # 10
]

# ============================================================================
# SPECIFIC USE CASES
# ============================================================================

# Geographic maps
GEO_BACKGROUND = '#F7FAFC'      # Very light gray-blue (calm water)
GEO_POINT = AQUA                # Patient points
GEO_POINT_HIGHLIGHT = SALMON    # Highlighted points
GEO_LINE = AQUA_DARK            # Flow lines
GEO_BORDER = DARK_GRAY          # Borders

# Density heatmap
HEATMAP_LOW = AQUA_LIGHT
HEATMAP_MID = AQUA
HEATMAP_HIGH = AQUA_DARKER

# Statistical significance
SIG_VERY_HIGH = AQUA_DARKER     # p < 0.001
SIG_HIGH = AQUA                 # p < 0.01
SIG_MODERATE = AQUA_MEDIUM      # p < 0.05
SIG_NOT = LIGHT_GRAY            # p >= 0.05

# Positive/Negative (calm colors, not red/green)
POSITIVE = AQUA                 # Positive outcome
NEGATIVE = CORAL                # Negative outcome
NEUTRAL = LIGHT_GRAY            # Neutral

# Urban/Rural
URBAN_COLOR = AQUA              # Urban areas
RURAL_COLOR = MINT              # Rural areas

# Comparison (published vs our data)
COLOR_PUBLISHED = LAVENDER      # Published paper data
COLOR_OUR_DATA = AQUA           # Our data
COLOR_REFERENCE = CHARCOAL      # Reference line

# ============================================================================
# GRADIENTS FOR DISPARITY VISUALIZATION
# ============================================================================

# Low to High disparity (calm but clear)
DISPARITY_NONE = MINT           # No disparity
DISPARITY_LOW = AQUA_LIGHT      # Low disparity
DISPARITY_MODERATE = AQUA       # Moderate disparity
DISPARITY_HIGH = CORAL          # High disparity
DISPARITY_SEVERE = SALMON       # Severe disparity

# Distance categories
DISTANCE_VERY_SHORT = AQUA_LIGHT    # < 50 km
DISTANCE_SHORT = AQUA_MEDIUM        # 50-100 km
DISTANCE_MEDIUM = AQUA              # 100-200 km
DISTANCE_LONG = CORAL               # 200-500 km
DISTANCE_VERY_LONG = SALMON         # > 500 km

# ============================================================================
# MATPLOTLIB/SEABORN CONFIGURATION
# ============================================================================

def apply_style():
    """Apply the aquamarine-black aesthetic to matplotlib/seaborn"""
    # Set style
    plt.style.use('seaborn-v0_8-whitegrid')

    # Custom parameters
    params = {
        'figure.facecolor': 'white',
        'axes.facecolor': GEO_BACKGROUND,
        'axes.edgecolor': DARK_GRAY,
        'axes.labelcolor': CHARCOAL,
        'axes.grid': True,
        'grid.color': PALE_GRAY,
        'grid.linestyle': '--',
        'grid.alpha': 0.4,
        'xtick.color': CHARCOAL,
        'ytick.color': CHARCOAL,
        'text.color': CHARCOAL,
        'font.size': 11,
        'axes.titlesize': 14,
        'axes.labelsize': 12,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'legend.fontsize': 10,
        'figure.titlesize': 16,
        'axes.spines.top': False,
        'axes.spines.right': False,
        'axes.spines.left': True,
        'axes.spines.bottom': True,
        'axes.linewidth': 1.5,
    }
    plt.rcParams.update(params)

    # Set seaborn palette
    sns.set_palette(CATEGORICAL_MAIN)
    sns.set_context("paper", font_scale=1.2)

def get_cmap_aqua_gradient():
    """Get custom aquamarine gradient colormap"""
    return LinearSegmentedColormap.from_list('aqua_gradient', SEQUENTIAL_AQUA)

def get_cmap_aqua_black():
    """Get custom aquamarine to black colormap"""
    return LinearSegmentedColormap.from_list('aqua_black', SEQUENTIAL_AQUA_BLACK)

def get_cmap_heatmap():
    """Get custom heatmap colormap (light aqua to dark aqua)"""
    colors = [HEATMAP_LOW, HEATMAP_MID, HEATMAP_HIGH]
    return LinearSegmentedColormap.from_list('heatmap', colors)

def get_cmap_diverging():
    """Get custom diverging colormap (coral-aqua)"""
    return LinearSegmentedColormap.from_list('diverging', DIVERGING_CORAL_AQUA)

# ============================================================================
# FOLIUM/HTML MAP COLORS (hex codes for web)
# ============================================================================

FOLIUM_COLORS = {
    'background': GEO_BACKGROUND,
    'point': AQUA,
    'point_highlight': SALMON,
    'line': AQUA_DARK,
    'fill': AQUA_LIGHT,
    'border': DARK_GRAY,
    'text': CHARCOAL,
}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_color_by_value(value, min_val, max_val, reverse=False):
    """
    Get color from aquamarine gradient based on value
    Args:
        value: numeric value
        min_val: minimum value for scaling
        max_val: maximum value for scaling
        reverse: if True, high values get light colors
    """
    normalized = (value - min_val) / (max_val - min_val)
    if reverse:
        normalized = 1 - normalized

    if normalized < 0.25:
        return AQUA_LIGHT
    elif normalized < 0.5:
        return AQUA_MEDIUM
    elif normalized < 0.75:
        return AQUA
    else:
        return AQUA_DARK

def get_disparity_color(disparity_ratio):
    """
    Get color based on disparity ratio (1.0 = no disparity)
    """
    if disparity_ratio < 1.5:
        return DISPARITY_NONE
    elif disparity_ratio < 2.0:
        return DISPARITY_LOW
    elif disparity_ratio < 3.0:
        return DISPARITY_MODERATE
    elif disparity_ratio < 5.0:
        return DISPARITY_HIGH
    else:
        return DISPARITY_SEVERE

def get_distance_color(distance_km):
    """Get color based on distance category"""
    if distance_km < 50:
        return DISTANCE_VERY_SHORT
    elif distance_km < 100:
        return DISTANCE_SHORT
    elif distance_km < 200:
        return DISTANCE_MEDIUM
    elif distance_km < 500:
        return DISTANCE_LONG
    else:
        return DISTANCE_VERY_LONG

def preview_palette():
    """Display all color palettes for visual inspection"""
    fig, axes = plt.subplots(6, 1, figsize=(12, 10))

    # Categorical main
    axes[0].barh(range(len(CATEGORICAL_MAIN)), [1]*len(CATEGORICAL_MAIN),
                 color=CATEGORICAL_MAIN, height=0.8)
    axes[0].set_title('Categorical Main', fontweight='bold', fontsize=12)
    axes[0].set_xlim(0, 1)
    axes[0].axis('off')

    # Sequential aqua
    axes[1].barh(range(len(SEQUENTIAL_AQUA)), [1]*len(SEQUENTIAL_AQUA),
                 color=SEQUENTIAL_AQUA, height=0.8)
    axes[1].set_title('Sequential Aquamarine', fontweight='bold', fontsize=12)
    axes[1].set_xlim(0, 1)
    axes[1].axis('off')

    # Diverging
    axes[2].barh(range(len(DIVERGING_CORAL_AQUA)), [1]*len(DIVERGING_CORAL_AQUA),
                 color=DIVERGING_CORAL_AQUA, height=0.8)
    axes[2].set_title('Diverging Coral-Aqua', fontweight='bold', fontsize=12)
    axes[2].set_xlim(0, 1)
    axes[2].axis('off')

    # Distance categories
    distance_colors = [DISTANCE_VERY_SHORT, DISTANCE_SHORT, DISTANCE_MEDIUM,
                       DISTANCE_LONG, DISTANCE_VERY_LONG]
    distance_labels = ['<50km', '50-100km', '100-200km', '200-500km', '>500km']
    axes[3].barh(range(len(distance_colors)), [1]*len(distance_colors),
                 color=distance_colors, height=0.8)
    axes[3].set_yticks(range(len(distance_labels)))
    axes[3].set_yticklabels(distance_labels)
    axes[3].set_title('Distance Categories', fontweight='bold', fontsize=12)
    axes[3].set_xlim(0, 1)

    # Significance levels
    sig_colors = [SIG_VERY_HIGH, SIG_HIGH, SIG_MODERATE, SIG_NOT]
    sig_labels = ['p<0.001', 'p<0.01', 'p<0.05', 'p≥0.05']
    axes[4].barh(range(len(sig_colors)), [1]*len(sig_colors),
                 color=sig_colors, height=0.8)
    axes[4].set_yticks(range(len(sig_labels)))
    axes[4].set_yticklabels(sig_labels)
    axes[4].set_title('Statistical Significance', fontweight='bold', fontsize=12)
    axes[4].set_xlim(0, 1)

    # Comparison colors
    comp_colors = [COLOR_PUBLISHED, COLOR_OUR_DATA, COLOR_REFERENCE]
    comp_labels = ['Published', 'Our Data', 'Reference']
    axes[5].barh(range(len(comp_colors)), [1]*len(comp_colors),
                 color=comp_colors, height=0.8)
    axes[5].set_yticks(range(len(comp_labels)))
    axes[5].set_yticklabels(comp_labels)
    axes[5].set_title('Comparison Colors', fontweight='bold', fontsize=12)
    axes[5].set_xlim(0, 1)

    plt.suptitle('Aquamarine & Black Professional Color Palette',
                 fontweight='bold', fontsize=16, y=0.995)
    plt.tight_layout()
    plt.savefig('/Users/ramihatoum/Desktop/PPA/maps/final/color_palette_preview.png',
                dpi=300, bbox_inches='tight', facecolor='white')
    print("✓ Color palette preview saved: color_palette_preview.png")
    plt.close()

if __name__ == '__main__':
    apply_style()
    preview_palette()
    print("\n" + "="*70)
    print("PROFESSIONAL AQUAMARINE & BLACK COLOR PALETTE")
    print("="*70)
    print("\nPrimary Colors:")
    print(f"  Aquamarine (main):     {AQUA}")
    print(f"  Charcoal (contrast):   {CHARCOAL}")
    print(f"  Coral (accent):        {CORAL}")
    print(f"  Lavender (accent):     {LAVENDER}")
    print("\nUse: import color_palette as cp")
    print("     cp.apply_style()")
    print("     colors = cp.CATEGORICAL_MAIN")

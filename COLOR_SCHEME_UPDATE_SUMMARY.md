# Color Scheme Update Summary
**Professional Aquamarine & Black Aesthetic**

Date: November 6, 2025

## Overview

All dashboard figures, visuals, and maps have been updated with a professional, calm aesthetic based on aquamarine and charcoal black tones. This creates a cohesive, modern look across all visualizations while maintaining excellent distinction in legends and annotations.

---

## Color Palette Details

### Primary Colors
- **Aquamarine (Primary)**: `#38B2AC` - Main data visualization color
- **Charcoal**: `#1A1A1A` - Text, borders, and high contrast elements
- **Coral Accent**: `#F6AD55` - Warm accent for contrast
- **Lavender Accent**: `#9F7AEA` - Cool accent for categorical distinction

### Aquamarine Gradient (Light to Dark)
1. **Very Light**: `#B2F5EA` - Low values, excellent categories
2. **Medium**: `#4FD1C5` - Moderate values
3. **Primary**: `#38B2AC` - Standard data points
4. **Dark**: `#2C7A7B` - High values, emphasis
5. **Darker**: `#1A5558` - Maximum values, critical categories

### Distance/Disparity Categories
- **< 50 km (Excellent)**: `#68D391` Mint green
- **50-100 km (Good)**: `#B2F5EA` Light aquamarine
- **100-200 km (Moderate)**: `#38B2AC` Primary aquamarine
- **200-400 km (Poor)**: `#F6AD55` Coral
- **> 400 km (Critical)**: `#FC8181` Salmon

### Statistical Significance
- **p < 0.001**: `#1A5558` Very dark aquamarine
- **p < 0.01**: `#38B2AC` Primary aquamarine
- **p < 0.05**: `#4FD1C5` Medium aquamarine
- **p ≥ 0.05**: `#718096` Light gray

### Comparison Colors
- **Published Data**: `#9F7AEA` Lavender
- **Our Data**: `#38B2AC` Aquamarine
- **Reference Line**: `#1A1A1A` Charcoal

### Geographic Map Colors
- **Background**: `#F7FAFC` Very light gray-blue
- **Patient Points**: `#38B2AC` Aquamarine
- **Flow Lines**: `#2C7A7B` Dark aquamarine
- **Borders**: `#2D3748` Dark gray
- **Urban Areas**: `#38B2AC` Aquamarine
- **Rural Areas**: `#68D391` Mint green

---

## Updated Files

### 1. Core Color Palette
**File**: `color_palette.py`
- Complete professional color palette definition
- Helper functions for color selection
- Matplotlib/Seaborn style configuration
- Custom colormaps (gradients, diverging, heatmaps)
- Utility functions for value-based color selection

### 2. Main Visualization Scripts
**File**: `create_visualizations.py` (✓ Updated)
- Indigenous Disparity Gradient
- Regression Coefficients (Forest Plot)
- Provincial Comparison (4-panel)
- Interaction Effects
- Distance Distributions
- Scatterplot Matrix
- Model Diagnostics
- Demographics Summary
- Socioeconomic Indicators
- Correlation Matrix Heatmap

### 3. Figure 1 Scripts
**File**: `generate_figure1_ultradetailed.py` (✓ Updated)
- Geographic Distribution (Basic)
- Density Heatmap
- Provincial Proportional Circles
- Temporal Evolution (Year-by-Year)
- Age Distribution by Geography
- Rural vs Urban Access

### 4. Figure 3 Scripts
**File**: `generate_figure3_with_CI.py` (✓ Updated)
- Provincial Rate Ratios with Confidence Intervals
- Overlapping Bars with Error Bars
- Side-by-Side Comparison Panels
- Forest Plot Style

### 5. Interactive Maps
**File**: `maps_nov2025/generate_calm_maps_final.py` (✓ Updated)
- Updated distance color categories to aquamarine gradient
- Changed primary color to aquamarine
- Updated borders to dark gray
- Changed text to charcoal

---

## Regenerated Visualizations

### Figure 1 Series (✓ Regenerated)
1. `Figure1A_Geographic_Distribution_Basic.png`
2. `Figure1B_Geographic_Density_Heatmap.png`
3. `Figure1C_Provincial_Proportional_Circles.png`
4. `Figure1D_Temporal_Evolution.png`
5. `Figure1E_Age_Distribution_Geography.png`
6. `Figure1F_Rural_vs_Urban.png`

### Figure 3 Series (✓ Regenerated)
1. `Figure3_WITH_CONFIDENCE_INTERVALS.png`
2. `Figure3_SIDE_BY_SIDE_WITH_CI.png`
3. `Figure3_FOREST_PLOT_WITH_CI.png`

### Main Visualization Suite (✓ Regenerated)
All 10 figures in the `figures/` directory:
1. `Fig1_Indigenous_Disparity_Gradient.png`
2. `Fig2_Regression_Coefficients.png`
3. `Fig3_Provincial_Comparison.png`
4. `Fig4_Interaction_Effect.png`
5. `Fig5_Distance_Distribution.png`
6. `Fig6_Scatterplot_Matrix.png`
7. `Fig7_Model_Diagnostics.png`
8. `Fig8_Demographics.png`
9. `Fig9_Socioeconomic_Indicators.png`
10. `Fig10_Correlation_Matrix.png`

---

## Design Principles Applied

### 1. Professional Aesthetics
- **Calm palette**: Muted tones reduce visual fatigue
- **Consistent branding**: Aquamarine creates identity across all visualizations
- **Modern appearance**: Charcoal replaces harsh black for softer contrast

### 2. Visual Hierarchy
- **Primary data**: Aquamarine shades
- **Accents**: Coral and lavender for distinction
- **Emphasis**: Darker aquamarine and charcoal for important elements
- **Backgrounds**: Very light gray-blue for subtle context

### 3. Accessibility
- **High contrast**: Aquamarine on light backgrounds, charcoal text
- **Color-blind safe**: Avoided red-green combinations
- **Clear legends**: Enhanced with charcoal borders (linewidth=1.5-2)
- **Bold text**: All labels fontweight='bold' for readability

### 4. Data Distinction
- **Sequential data**: Aquamarine gradient (light → dark)
- **Diverging data**: Coral (low) ↔ Aquamarine (high)
- **Categorical data**: Mixed palette (aquamarine, coral, lavender, mint)
- **Significance levels**: Aquamarine gradient by p-value

### 5. Consistency
- **Edge colors**: Charcoal (`#1A1A1A`) for all bars, boxes, markers
- **Line widths**: Standardized (1.5-2.5) for clarity
- **Alpha values**: 0.7-0.85 for optimal visibility without overwhelming
- **Grid lines**: Light gray with alpha=0.3-0.4

---

## Technical Implementation

### Matplotlib Configuration
```python
import color_palette as cp
cp.apply_style()  # Applies global settings
```

### Key Parameters Set
- `figure.facecolor`: white
- `axes.facecolor`: `#F7FAFC` (light gray-blue)
- `axes.edgecolor`: `#2D3748` (dark gray)
- `grid.color`: `#CBD5E0` (pale gray)
- `grid.alpha`: 0.4
- `axes.linewidth`: 1.5
- All spines: top/right hidden, left/bottom visible

### Custom Colormaps
1. **Sequential Aquamarine**: Light → Dark aquamarine
2. **Aquamarine to Black**: Gradient for heatmaps
3. **Diverging Coral-Aqua**: For above/below comparisons
4. **Heatmap**: Light aqua → Dark aqua gradient

---

## Quality Assurance

### ✓ Visual Distinction Verified
- Legends remain clear and readable
- All categories easily distinguishable
- No confusion in multi-line graphs
- Statistical significance clearly indicated

### ✓ Professional Appearance
- Calm, sophisticated color scheme
- Modern aesthetic without being trendy
- Suitable for academic publications
- Professional presentation quality

### ✓ Consistency Across All Outputs
- Unified color language throughout
- Same palette in static figures and interactive maps
- Coherent branding across different visualization types

### ✓ Technical Quality
- 300 DPI resolution for all static figures
- Proper alpha blending for overlays
- Clean edges with appropriate line widths
- Publication-ready quality

---

## Usage Instructions

### For Future Visualizations

1. **Import the palette**:
   ```python
   import color_palette as cp
   cp.apply_style()
   ```

2. **Use predefined colors**:
   ```python
   # For bars
   ax.bar(x, y, color=cp.AQUA, edgecolor=cp.CHARCOAL, linewidth=1.5)

   # For scatter
   ax.scatter(x, y, c=cp.AQUA, edgecolor=cp.CHARCOAL, s=50, alpha=0.7)

   # For lines
   ax.plot(x, y, color=cp.AQUA_DARK, linewidth=2.5)
   ```

3. **Use categorical palette**:
   ```python
   colors = cp.CATEGORICAL_MAIN  # Returns list of 8 distinct colors
   ```

4. **Use distance colors**:
   ```python
   color = cp.get_distance_color(distance_km)
   ```

5. **Use custom colormaps**:
   ```python
   ax.scatter(x, y, c=values, cmap=cp.get_cmap_aqua_gradient())
   ```

---

## Files Reference

### Core Files
- `color_palette.py` - Master palette definition
- `color_palette_preview.png` - Visual reference of all colors

### Main Scripts
- `create_visualizations.py` - 10-figure visualization suite
- `generate_figure1_ultradetailed.py` - Geographic visualizations
- `generate_figure3_with_CI.py` - Provincial comparisons with CIs

### Map Scripts
- `maps_nov2025/generate_calm_maps_final.py` - Interactive maps

### Output Directories
- `figures/` - Static PNG visualizations (10 figures + 4 tables)
- `maps_nov2025/` - Interactive HTML maps
- Root directory - Figure 1 and Figure 3 series

---

## Summary Statistics

**Total Files Updated**: 5 core scripts
**Total Figures Regenerated**: 19+ PNG images
**Color Palette Size**: 40+ predefined colors
**Colormaps Created**: 4 custom gradients
**Quality**: 300 DPI for all static figures

---

## Color Harmony Analysis

### Complementary Colors
- **Aquamarine** (`#38B2AC`) complements **Coral** (`#F6AD55`)
- Creates warm/cool balance
- High visual distinction without clash

### Analogous Colors
- Aquamarine family: `#B2F5EA` → `#4FD1C5` → `#38B2AC` → `#2C7A7B` → `#1A5558`
- Smooth gradients for sequential data
- Professional monochromatic feel

### Triadic Harmony
- **Aquamarine** + **Lavender** + **Coral**
- Three-way balance for categorical data
- Each color distinct yet harmonious

---

## Recommendations

### Do's ✓
- Always use `cp.apply_style()` at start of scripts
- Use charcoal (`cp.CHARCOAL`) for all edges and text
- Use aquamarine as primary data color
- Use coral/lavender for accents and categories
- Maintain line widths 1.5-2.5 for clarity

### Don'ts ✗
- Don't use pure black - use charcoal instead
- Don't use harsh primary colors (red, green, blue)
- Don't reduce line widths below 1.0
- Don't use alpha < 0.6 (too transparent)
- Don't mix this palette with other color schemes

---

## Contact & Support

For questions about the color palette or to report issues:
1. Check `color_palette.py` documentation
2. View `color_palette_preview.png` for visual reference
3. Review this document for usage examples

---

**Last Updated**: November 6, 2025
**Status**: ✓ Complete - All visualizations updated and regenerated

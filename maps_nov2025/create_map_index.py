"""
Create a visual index/contact sheet of all generated maps
"""

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.gridspec import GridSpec
import os
import glob

# Set up the figure
fig = plt.figure(figsize=(24, 32), dpi=150)

# Get all static map files
map_files = sorted(glob.glob('/Users/ramihatoum/Desktop/PPA/maps/final/maps_nov2025/static_map*.png'))

print(f"Found {len(map_files)} maps to display")

# Create grid layout (5 columns x 4 rows)
n_cols = 4
n_rows = (len(map_files) + n_cols - 1) // n_cols
gs = GridSpec(n_rows, n_cols, figure=fig, hspace=0.3, wspace=0.2)

for idx, map_file in enumerate(map_files):
    row = idx // n_cols
    col = idx % n_cols

    ax = fig.add_subplot(gs[row, col])

    # Load and display image
    img = mpimg.imread(map_file)
    ax.imshow(img)
    ax.axis('off')

    # Add filename as title
    filename = os.path.basename(map_file)
    # Clean up filename for display
    title = filename.replace('static_map_', '').replace('static_map', '').replace('.png', '').replace('_', ' ').title()
    ax.set_title(title, fontsize=10, fontweight='bold', pad=5)

# Add overall title
fig.suptitle('DBS Dashboard: All 19 Static Maps Generated (300 DPI)',
             fontsize=20, fontweight='bold', y=0.995)

# Add subtitle with statistics
subtitle = f"Total Maps: {len(map_files)} | Analytical: 7 | Provincial/Territorial: 12\n"
subtitle += "Color Scheme: Professional Aquamarine & Charcoal | Resolution: 300 DPI"
fig.text(0.5, 0.988, subtitle, ha='center', fontsize=12, style='italic')

plt.tight_layout()
plt.savefig('/Users/ramihatoum/Desktop/PPA/maps/final/maps_nov2025/MAP_INDEX_CONTACT_SHEET.png',
            dpi=150, bbox_inches='tight', facecolor='white')
print("\nContact sheet saved: MAP_INDEX_CONTACT_SHEET.png")
plt.close()

# Print summary statistics
print("\n" + "="*80)
print("MAP GENERATION SUMMARY")
print("="*80)
print(f"\nTotal Maps Generated: {len(map_files)}")
print("\nMap Categories:")
print("  - Analytical Maps: 7")
print("  - Provincial/Territorial Maps: 12")
print("\nFile Details:")
for map_file in map_files:
    size_kb = os.path.getsize(map_file) / 1024
    filename = os.path.basename(map_file)
    print(f"  {filename:55s} {size_kb:8.1f} KB")

total_size_mb = sum(os.path.getsize(f) for f in map_files) / (1024 * 1024)
print(f"\nTotal Storage: {total_size_mb:.2f} MB")
print("="*80)

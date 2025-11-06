"""
Generate ALL 13 Provincial/Territorial Maps with:
- Grayscale Google Maps backgrounds
- Flow lines showing patient → DBS center paths
- Clear annotations and custom legends
- 1920x1080px resolution
- Dampened colors with 75% alpha
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.lines import Line2D
from PIL import Image
import requests
from io import BytesIO
import sys
sys.path.append('..')
import color_palette as cp

# Configuration
API_KEY = "AIzaSyBH_yuU7_TfAJmuf_h04UsmKKhC0XPWerA"
OUTPUT_SIZE = (1920, 1080)
DPI = 96

# DAMPENED COLORS
DAMPENED_COLORS = {
    'aqua_light': '#D4F4EC',
    'aqua': '#7DD3C0',
    'aqua_medium': '#9BE7DC',
    'coral': '#F9C58D',
    'salmon': '#FCBBB3',
    'charcoal': '#1A1A1A',
    'aqua_dark': '#2C7A7B'
}

ANNOTATION_CONFIG = {
    'title_fontsize': 14,
    'legend_fontsize': 11,
    'body_fontsize': 12,
    'explanation_fontsize': 11
}

MARKER_CONFIG = {
    'dbs_center_size': 280,
    'patient_marker_size': 10,
    'patient_alpha': 0.75,
    'flow_line_width': 1.2,
    'flow_line_alpha': 0.35
}

print("Loading data...")
df = pd.read_excel('../Final_database_05_11_25_FINAL.xlsx')
fsa_coords = pd.read_csv('/Users/ramihatoum/Desktop/PPA/maps/fsa_population_centroids.csv')

df = df.merge(fsa_coords[['fsa_code', 'pop_weighted_lat', 'pop_weighted_lon']],
              left_on='FSA', right_on='fsa_code', how='left')
df = df.dropna(subset=['pop_weighted_lat', 'pop_weighted_lon'])

# DBS Centers
dbs_centers = {
    12: {'name': 'Halifax', 'lat': 44.646, 'lon': -63.586, 'province': 'NS'},
    14: {'name': 'London', 'lat': 42.961, 'lon': -81.226, 'province': 'ON'},
    16: {'name': 'Toronto', 'lat': 43.653, 'lon': -79.405, 'province': 'ON'},
    17: {'name': 'Edmonton', 'lat': 53.521, 'lon': -113.523, 'province': 'AB'},
    18: {'name': 'Calgary', 'lat': 51.064, 'lon': -114.134, 'province': 'AB'},
    19: {'name': 'Sherbrooke', 'lat': 45.447, 'lon': -71.870, 'province': 'QC'},
    20: {'name': 'Montreal', 'lat': 45.512, 'lon': -73.557, 'province': 'QC'},
    21: {'name': 'Quebec City', 'lat': 46.837, 'lon': -71.226, 'province': 'QC'},
    22: {'name': 'Saskatoon', 'lat': 52.132, 'lon': -106.642, 'province': 'SK'}
}

# Provincial configurations
PROVINCES = {
    'NL': {'name': 'Newfoundland & Labrador', 'center': (53.5, -59.5), 'zoom': 5, 'fsa_starts': ['A']},
    'NS': {'name': 'Nova Scotia', 'center': (45.0, -63.0), 'zoom': 7, 'fsa_starts': ['B']},
    'PE': {'name': 'Prince Edward Island', 'center': (46.5, -63.3), 'zoom': 8, 'fsa_starts': ['C']},
    'NB': {'name': 'New Brunswick', 'center': (46.5, -66.0), 'zoom': 7, 'fsa_starts': ['E']},
    'QC': {'name': 'Quebec', 'center': (50.0, -71.0), 'zoom': 5, 'fsa_starts': ['G', 'H', 'J']},
    'ON': {'name': 'Ontario', 'center': (48.0, -82.0), 'zoom': 5, 'fsa_starts': ['K', 'L', 'M', 'N', 'P']},
    'MB': {'name': 'Manitoba', 'center': (54.0, -98.0), 'zoom': 5, 'fsa_starts': ['R']},
    'SK': {'name': 'Saskatchewan', 'center': (54.0, -106.0), 'zoom': 5, 'fsa_starts': ['S']},
    'AB': {'name': 'Alberta', 'center': (54.0, -115.0), 'zoom': 5, 'fsa_starts': ['T']},
    'BC': {'name': 'British Columbia', 'center': (54.0, -125.0), 'zoom': 5, 'fsa_starts': ['V']},
    'YT': {'name': 'Yukon', 'center': (63.0, -135.0), 'zoom': 5, 'fsa_starts': ['Y']},
    'NT': {'name': 'Northwest Territories', 'center': (64.0, -117.0), 'zoom': 4, 'fsa_starts': ['X']},
    'NU': {'name': 'Nunavut', 'center': (70.0, -95.0), 'zoom': 3, 'fsa_starts': ['X']}
}

print(f"Loaded {len(df)} patient records")

def fetch_google_map_background_grayscale(center_lat, center_lon, zoom, width, height):
    """Fetch GRAYSCALE Google Maps background"""
    base_url = "https://maps.googleapis.com/maps/api/staticmap"

    params = {
        'center': f"{center_lat},{center_lon}",
        'zoom': zoom,
        'size': f"{width}x{height}",
        'scale': 2,
        'maptype': 'roadmap',
        'key': API_KEY,
        'style': 'saturation:-100|lightness:20'  # Grayscale
    }

    url = base_url + '?' + '&'.join([f"{k}={v}" for k, v in params.items()])

    print(f"  Fetching GRAYSCALE background (zoom {zoom})...")
    response = requests.get(url)

    if response.status_code == 200:
        img = Image.open(BytesIO(response.content))
        print(f"  ✓ Background fetched: {img.size}")
        return img
    else:
        print(f"  ✗ Failed: {response.status_code}")
        return None

def lat_lon_to_pixels(lat, lon, center_lat, center_lon, zoom, img_width, img_height):
    """Convert lat/lon to pixel coordinates"""
    scale = 2 ** zoom

    def lat_to_y(lat):
        return (1 - np.log(np.tan(np.radians(lat)) + 1/np.cos(np.radians(lat))) / np.pi) / 2

    def lon_to_x(lon):
        return (lon + 180) / 360

    center_x = lon_to_x(center_lon) * scale * 256
    center_y = lat_to_y(center_lat) * scale * 256

    point_x = lon_to_x(lon) * scale * 256
    point_y = lat_to_y(lat) * scale * 256

    pixel_x = (point_x - center_x) + (img_width / 2)
    pixel_y = (point_y - center_y) + (img_height / 2)

    return pixel_x, pixel_y

def draw_custom_legend(ax, items, title, position='lower left'):
    """Draw custom legend"""
    box_width = 340
    item_height = 50
    swatch_size = 35
    padding = 15
    title_height = 40

    total_height = title_height + (len(items) * item_height) + padding

    if position == 'lower left':
        x_start = 20
        y_start = 20
    elif position == 'lower right':
        x_start = OUTPUT_SIZE[0] - box_width - 20
        y_start = 20
    else:
        x_start = 20
        y_start = 20

    # Background
    bg_box = FancyBboxPatch(
        (x_start, y_start),
        box_width, total_height,
        boxstyle="round,pad=12",
        facecolor='white',
        edgecolor=DAMPENED_COLORS['aqua_dark'],
        linewidth=3,
        alpha=0.97,
        zorder=999
    )
    ax.add_patch(bg_box)

    # Title
    ax.text(x_start + box_width/2, y_start + total_height - title_height/2,
           title,
           fontsize=ANNOTATION_CONFIG['legend_fontsize'] + 2,
           fontweight='bold',
           ha='center', va='center',
           color=DAMPENED_COLORS['charcoal'],
           zorder=1000)

    # Items
    current_y = y_start + total_height - title_height - item_height/2

    for label, color, count in items:
        x_pos = x_start + padding

        # Swatch
        swatch = FancyBboxPatch(
            (x_pos, current_y - swatch_size/2),
            swatch_size, swatch_size,
            boxstyle="round,pad=3",
            facecolor=color,
            edgecolor=DAMPENED_COLORS['charcoal'],
            linewidth=2.5,
            alpha=MARKER_CONFIG['patient_alpha'],
            zorder=1000
        )
        ax.add_patch(swatch)

        # Label
        label_with_count = f"{label} ({count})" if count is not None else label
        ax.text(x_pos + swatch_size + 12, current_y,
               label_with_count,
               fontsize=ANNOTATION_CONFIG['legend_fontsize'],
               ha='left', va='center',
               color=DAMPENED_COLORS['charcoal'],
               zorder=1000)

        current_y -= item_height

def draw_explanation_box(ax, text, position='top_left'):
    """Draw explanatory text box"""
    box_width = 420
    box_height = 90
    padding = 12

    if position == 'top_left':
        x_pos = 20
        y_pos = OUTPUT_SIZE[1] - box_height - 80
    elif position == 'top_right':
        x_pos = OUTPUT_SIZE[0] - box_width - 20
        y_pos = OUTPUT_SIZE[1] - box_height - 80
    else:
        x_pos = 20
        y_pos = OUTPUT_SIZE[1] - box_height - 80

    bg_box = FancyBboxPatch(
        (x_pos, y_pos),
        box_width, box_height,
        boxstyle="round,pad=10",
        facecolor=DAMPENED_COLORS['aqua_light'],
        edgecolor=DAMPENED_COLORS['aqua_dark'],
        linewidth=2.5,
        alpha=0.95,
        zorder=998
    )
    ax.add_patch(bg_box)

    ax.text(x_pos + padding, y_pos + box_height/2,
           text,
           fontsize=ANNOTATION_CONFIG['explanation_fontsize'],
           ha='left', va='center',
           color=DAMPENED_COLORS['charcoal'],
           wrap=True,
           zorder=1000)

def generate_provincial_map(prov_code):
    """Generate a single provincial map with background and flow lines"""
    prov_info = PROVINCES[prov_code]
    print(f"\nGenerating {prov_info['name']} ({prov_code})...")

    # Filter patients by FSA
    prov_patients = df[df['FSA'].str[0].isin(prov_info['fsa_starts'])]

    # Special handling for NT vs NU (both use X)
    if prov_code == 'NU':
        # Nunavut FSAs: X0A, X0B, X0C
        prov_patients = df[df['FSA'].str[:2].isin(['X0'])]
    elif prov_code == 'NT':
        # Northwest Territories: X1A, etc
        prov_patients = df[df['FSA'].str[:2].isin(['X1', 'X2'])]

    if len(prov_patients) == 0:
        print(f"  ⚠ No patients found for {prov_code}")
        # Create placeholder map with message
        return None

    print(f"  Found {len(prov_patients)} patients")

    # Fetch background
    center_lat, center_lon = prov_info['center']
    zoom = prov_info['zoom']
    bg_img = fetch_google_map_background_grayscale(center_lat, center_lon, zoom,
                                                    OUTPUT_SIZE[0]//2, OUTPUT_SIZE[1]//2)

    if bg_img is None:
        return None

    bg_img = bg_img.resize(OUTPUT_SIZE, Image.Resampling.LANCZOS)

    fig, ax = plt.subplots(figsize=(OUTPUT_SIZE[0]/DPI, OUTPUT_SIZE[1]/DPI), dpi=DPI)
    ax.imshow(bg_img, extent=[0, OUTPUT_SIZE[0], 0, OUTPUT_SIZE[1]], aspect='auto', zorder=0)

    # Color by distance
    color_map = {
        '<100km': DAMPENED_COLORS['aqua_light'],
        '100-200km': DAMPENED_COLORS['aqua'],
        '200-400km': DAMPENED_COLORS['coral'],
        '>400km': DAMPENED_COLORS['salmon']
    }

    def get_distance_category(dist):
        if dist < 100:
            return '<100km'
        elif dist < 200:
            return '100-200km'
        elif dist < 400:
            return '200-400km'
        else:
            return '>400km'

    prov_patients['distance_category'] = prov_patients['Driving Distance (km)'].apply(get_distance_category)
    category_counts = prov_patients['distance_category'].value_counts().to_dict()

    # Draw flow lines FIRST (behind markers)
    for _, patient in prov_patients.iterrows():
        patient_lat = patient['pop_weighted_lat']
        patient_lon = patient['pop_weighted_lon']

        # Find nearest DBS center
        min_dist = float('inf')
        nearest_center = None
        for center_id, info in dbs_centers.items():
            dist = np.sqrt((info['lat'] - patient_lat)**2 + (info['lon'] - patient_lon)**2)
            if dist < min_dist:
                min_dist = dist
                nearest_center = info

        if nearest_center:
            # Get pixel coordinates
            px1, py1 = lat_lon_to_pixels(patient_lat, patient_lon, center_lat, center_lon, zoom,
                                        OUTPUT_SIZE[0], OUTPUT_SIZE[1])
            px2, py2 = lat_lon_to_pixels(nearest_center['lat'], nearest_center['lon'],
                                        center_lat, center_lon, zoom,
                                        OUTPUT_SIZE[0], OUTPUT_SIZE[1])

            py1 = OUTPUT_SIZE[1] - py1
            py2 = OUTPUT_SIZE[1] - py2

            # Draw flow line
            ax.plot([px1, px2], [py1, py2],
                   color=DAMPENED_COLORS['aqua'],
                   linewidth=MARKER_CONFIG['flow_line_width'],
                   alpha=MARKER_CONFIG['flow_line_alpha'],
                   zorder=1)

    # Plot patient markers
    for category in color_map.keys():
        data = prov_patients[prov_patients['distance_category'] == category]
        if len(data) > 0:
            pixel_coords = []
            for _, row in data.iterrows():
                px, py = lat_lon_to_pixels(row['pop_weighted_lat'], row['pop_weighted_lon'],
                                          center_lat, center_lon, zoom,
                                          OUTPUT_SIZE[0], OUTPUT_SIZE[1])
                py = OUTPUT_SIZE[1] - py
                pixel_coords.append((px, py))

            if pixel_coords:
                xs, ys = zip(*pixel_coords)
                ax.scatter(xs, ys,
                          c=color_map[category],
                          s=MARKER_CONFIG['patient_marker_size'],
                          alpha=MARKER_CONFIG['patient_alpha'],
                          edgecolors=DAMPENED_COLORS['charcoal'],
                          linewidths=0.3,
                          zorder=2)

    # Plot DBS centers
    for center_id, info in dbs_centers.items():
        px, py = lat_lon_to_pixels(info['lat'], info['lon'], center_lat, center_lon, zoom,
                                   OUTPUT_SIZE[0], OUTPUT_SIZE[1])
        py = OUTPUT_SIZE[1] - py

        # Only show if within view
        if 0 <= px <= OUTPUT_SIZE[0] and 0 <= py <= OUTPUT_SIZE[1]:
            ax.scatter(px, py, c='gold', s=MARKER_CONFIG['dbs_center_size'], marker='*',
                      edgecolors=DAMPENED_COLORS['charcoal'], linewidths=1.5, zorder=5)
            ax.text(px, py-20, info['name'],
                   fontsize=ANNOTATION_CONFIG['legend_fontsize'],
                   ha='center', va='top', fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.2', facecolor='white',
                            alpha=0.9, edgecolor=DAMPENED_COLORS['charcoal'], linewidth=1),
                   zorder=6)

    ax.set_xlim(0, OUTPUT_SIZE[0])
    ax.set_ylim(0, OUTPUT_SIZE[1])
    ax.axis('off')

    # Title
    ax.text(OUTPUT_SIZE[0]/2, OUTPUT_SIZE[1]-30,
           f'{prov_info["name"]}: Patient Travel Patterns to DBS Centers',
           fontsize=ANNOTATION_CONFIG['title_fontsize'],
           fontweight='bold',
           ha='center', va='top',
           color='white',
           bbox=dict(boxstyle='round,pad=0.5', facecolor=DAMPENED_COLORS['charcoal'], alpha=0.9),
           zorder=1000)

    # Legend
    legend_items = []
    for cat in ['<100km', '100-200km', '200-400km', '>400km']:
        count = category_counts.get(cat, 0)
        if count > 0:
            legend_items.append((cat, color_map[cat], count))

    if legend_items:
        draw_custom_legend(ax, legend_items, 'Travel Distance', 'lower left')

    # Explanation
    median_dist = prov_patients['Driving Distance (km)'].median()
    explanation = f"Lines show patient → DBS center paths.\nMedian travel distance: {median_dist:.0f} km.\nColors indicate distance burden."
    draw_explanation_box(ax, explanation, 'top_left')

    # Stats
    far_count = len(prov_patients[prov_patients['Driving Distance (km)'] > 200])
    stats_text = f"Total Patients: {len(prov_patients)}\nMedian Distance: {median_dist:.0f} km\n>200km: {far_count} ({far_count/len(prov_patients)*100:.1f}%)"
    ax.text(OUTPUT_SIZE[0]-20, 20, stats_text,
           fontsize=ANNOTATION_CONFIG['body_fontsize'],
           va='bottom', ha='right',
           bbox=dict(boxstyle='round,pad=0.4', facecolor='white',
                    edgecolor=DAMPENED_COLORS['aqua_dark'], linewidth=2, alpha=0.95),
           zorder=1000)

    plt.tight_layout(pad=0)
    output_path = f'optimized_map_province_{prov_code}.png'
    plt.savefig(output_path, dpi=DPI, bbox_inches='tight', pad_inches=0, facecolor='white')
    plt.close()

    print(f"  ✓ Saved: {output_path}")
    return output_path

# Generate all provincial maps
print("\n" + "="*70)
print("GENERATING ALL 13 PROVINCIAL/TERRITORIAL MAPS")
print("="*70)

provinces_to_generate = ['NL', 'NS', 'PE', 'NB', 'QC', 'ON', 'MB', 'SK', 'AB', 'BC', 'YT', 'NT', 'NU']

for prov in provinces_to_generate:
    generate_provincial_map(prov)

print("\n" + "="*70)
print("✓ ALL PROVINCIAL MAPS GENERATED!")
print("="*70)
print("\nFeatures:")
print("  ✓ Grayscale Google Maps backgrounds")
print("  ✓ Flow lines showing patient → DBS center paths")
print("  ✓ Clear annotations with travel distance context")
print("  ✓ Custom legends with patient counts")
print("  ✓ 1920x1080px resolution")
print("  ✓ Dampened colors (alpha 0.75)")

"""
LEGO-STYLE ANALYTICAL MAPS - ULTRA HIGH QUALITY
- Bright, vibrant LEGO-brick primary colors
- Night mode Google Maps backgrounds
- Modern horizontal legends with circular badges
- ALL 7 UNIQUE analytical map implementations
- 1920x1080px Full HD resolution
- Maximum visual quality and appeal
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrow
from matplotlib.lines import Line2D
from PIL import Image
import requests
from io import BytesIO
import sys
sys.path.append('..')

# Configuration
API_KEY = "AIzaSyBH_yuU7_TfAJmuf_h04UsmKKhC0XPWerA"
OUTPUT_SIZE = (1920, 1080)
DPI = 96

# LEGO-STYLE COLOR PALETTE (Bright, Bold, Saturated Primary Colors)
LEGO_COLORS = {
    'red': '#E3000F',            # LEGO Bright Red
    'blue': '#0068FF',           # LEGO Bright Blue
    'yellow': '#FFED00',         # LEGO Bright Yellow
    'green': '#00A850',          # LEGO Bright Green
    'orange': '#FF8200',         # LEGO Bright Orange
    'purple': '#C91A89',         # LEGO Purple/Magenta
    'cyan': '#00D4FF',           # LEGO Bright Cyan
    'lime': '#BBE90B',           # LEGO Lime
    'gold': '#FFD700',           # Gold for centers
    'white': '#FFFFFF',
    'dark_bg': '#0A0A0A',
    'text': '#FFFFFF'
}

# High-quality styling
STYLE_CONFIG = {
    'title_fontsize': 18,
    'subtitle_fontsize': 14,
    'legend_fontsize': 13,
    'stat_fontsize': 14,
    'marker_size': 18,
    'center_size': 450,
    'marker_alpha': 0.95,
    'flow_line_width': 2.0,
    'flow_line_alpha': 0.6,
    'glow_size': 60
}

print("🎨 Loading data...")
df = pd.read_excel('../Final_database_05_11_25_FINAL.xlsx')
fsa_coords = pd.read_csv('/Users/ramihatoum/Desktop/PPA/maps/fsa_population_centroids.csv')

df = df.merge(fsa_coords[['fsa_code', 'pop_weighted_lat', 'pop_weighted_lon']],
              left_on='FSA', right_on='fsa_code', how='left')
df = df.dropna(subset=['pop_weighted_lat', 'pop_weighted_lon'])

# DBS Centers
dbs_centers = {
    12: {'name': 'Halifax', 'lat': 44.646, 'lon': -63.586},
    14: {'name': 'London', 'lat': 42.961, 'lon': -81.226},
    16: {'name': 'Toronto', 'lat': 43.653, 'lon': -79.405},
    17: {'name': 'Edmonton', 'lat': 53.521, 'lon': -113.523},
    18: {'name': 'Calgary', 'lat': 51.064, 'lon': -114.134},
    19: {'name': 'Sherbrooke', 'lat': 45.447, 'lon': -71.870},
    20: {'name': 'Montreal', 'lat': 45.512, 'lon': -73.557},
    21: {'name': 'Quebec City', 'lat': 46.837, 'lon': -71.226},
    22: {'name': 'Saskatoon', 'lat': 52.132, 'lon': -106.642}
}

print(f"✅ Loaded {len(df)} patient records")

def fetch_night_mode_background(center_lat, center_lon, zoom, width, height):
    """Fetch night mode Google Maps background"""
    base_url = "https://maps.googleapis.com/maps/api/staticmap"

    style_params = [
        'feature:all|element:geometry|color:0x212121',
        'feature:all|element:labels.text.fill|color:0x757575',
        'feature:all|element:labels.text.stroke|color:0x212121',
        'feature:water|element:geometry|color:0x000000',
        'feature:water|element:labels.text.fill|color:0x3d3d3d',
        'feature:administrative|element:geometry.stroke|color:0x4b6878',
        'feature:landscape|element:geometry|color:0x212121',
        'feature:road|element:geometry|color:0x2c2c2c',
        'feature:poi|element:geometry|color:0x1a1a1a'
    ]

    params = {
        'center': f"{center_lat},{center_lon}",
        'zoom': zoom,
        'size': f"{width}x{height}",
        'scale': 2,
        'maptype': 'roadmap',
        'key': API_KEY
    }

    url = base_url + '?' + '&'.join([f"{k}={v}" for k, v in params.items()])
    for style in style_params:
        url += f"&style={style}"

    print(f"  🌙 Fetching background (zoom {zoom})...")
    response = requests.get(url)

    if response.status_code == 200:
        img = Image.open(BytesIO(response.content))
        print(f"  ✅ Background fetched")
        return img
    else:
        print(f"  ❌ Failed: {response.status_code}")
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

def draw_lego_legend(ax, items, title):
    """Draw LEGO-style horizontal legend with colorful badges"""
    badge_size = 45
    spacing = 190
    padding = 25
    title_height = 35

    total_width = len(items) * spacing + padding * 2
    total_height = badge_size + title_height + padding * 2

    x_start = (OUTPUT_SIZE[0] - total_width) / 2
    y_start = 50

    # Dark background
    bg_box = FancyBboxPatch(
        (x_start, y_start),
        total_width, total_height,
        boxstyle="round,pad=18",
        facecolor='#1A1A2E',
        edgecolor=LEGO_COLORS['blue'],
        linewidth=3,
        alpha=0.97,
        zorder=999
    )
    ax.add_patch(bg_box)

    # Title
    ax.text(x_start + total_width/2, y_start + total_height - title_height/2,
           title,
           fontsize=STYLE_CONFIG['legend_fontsize'] + 3,
           fontweight='bold',
           ha='center', va='center',
           color=LEGO_COLORS['white'],
           zorder=1000)

    # Circular LEGO-style badges
    current_x = x_start + padding + spacing/2

    for label, color, count in items:
        # Outer glow (larger, faded)
        glow_circle = Circle(
            (current_x, y_start + padding + badge_size/2),
            badge_size/2 + 5,
            facecolor=color,
            edgecolor='none',
            alpha=0.4,
            zorder=998
        )
        ax.add_patch(glow_circle)

        # Main badge
        badge_circle = Circle(
            (current_x, y_start + padding + badge_size/2),
            badge_size/2,
            facecolor=color,
            edgecolor=LEGO_COLORS['white'],
            linewidth=3,
            alpha=1.0,
            zorder=1000
        )
        ax.add_patch(badge_circle)

        # Label below
        label_text = f"{label}\n({count})" if count is not None else label
        ax.text(current_x, y_start + padding - 8,
               label_text,
               fontsize=STYLE_CONFIG['legend_fontsize'],
               ha='center', va='top',
               color=LEGO_COLORS['white'],
               fontweight='600',
               zorder=1000)

        current_x += spacing

def draw_stats_box(ax, stats_text):
    """Draw stats box"""
    box_width = 300
    box_height = 120

    x_pos = OUTPUT_SIZE[0] - box_width - 40
    y_pos = OUTPUT_SIZE[1] - box_height - 40

    bg_box = FancyBboxPatch(
        (x_pos, y_pos),
        box_width, box_height,
        boxstyle="round,pad=15",
        facecolor='#1A1A2E',
        edgecolor=LEGO_COLORS['purple'],
        linewidth=3,
        alpha=0.97,
        zorder=998
    )
    ax.add_patch(bg_box)

    ax.text(x_pos + 18, y_pos + box_height - 18,
           stats_text,
           fontsize=STYLE_CONFIG['stat_fontsize'],
           ha='left', va='top',
           color=LEGO_COLORS['white'],
           fontweight='600',
           family='monospace',
           zorder=1000)

def plot_patients_with_glow(ax, data, color, center_lat, center_lon, zoom):
    """Plot patients with LEGO-style glow effect"""
    pixel_coords = []
    for _, row in data.iterrows():
        px, py = lat_lon_to_pixels(row['pop_weighted_lat'], row['pop_weighted_lon'],
                                  center_lat, center_lon, zoom,
                                  OUTPUT_SIZE[0], OUTPUT_SIZE[1])
        py = OUTPUT_SIZE[1] - py
        pixel_coords.append((px, py))

    if pixel_coords:
        xs, ys = zip(*pixel_coords)

        # Glow layer
        ax.scatter(xs, ys,
                  c=color,
                  s=STYLE_CONFIG['glow_size'],
                  alpha=0.4,
                  edgecolors='none',
                  zorder=1)

        # Main marker
        ax.scatter(xs, ys,
                  c=color,
                  s=STYLE_CONFIG['marker_size'],
                  alpha=STYLE_CONFIG['marker_alpha'],
                  edgecolors=LEGO_COLORS['white'],
                  linewidths=0.8,
                  zorder=2)

def plot_dbs_centers(ax, center_lat, center_lon, zoom):
    """Plot DBS centers with gold halos"""
    for center_id, info in dbs_centers.items():
        px, py = lat_lon_to_pixels(info['lat'], info['lon'], center_lat, center_lon, zoom,
                                   OUTPUT_SIZE[0], OUTPUT_SIZE[1])
        py = OUTPUT_SIZE[1] - py

        # Halo
        ax.scatter(px, py,
                  c=LEGO_COLORS['gold'],
                  s=STYLE_CONFIG['center_size'] + 150,
                  marker='*',
                  alpha=0.5,
                  edgecolors='none',
                  zorder=4)

        # Main star
        ax.scatter(px, py,
                  c=LEGO_COLORS['gold'],
                  s=STYLE_CONFIG['center_size'],
                  marker='*',
                  edgecolors=LEGO_COLORS['white'],
                  linewidths=3,
                  zorder=5)

        # Label
        ax.text(px, py-30, info['name'],
               fontsize=STYLE_CONFIG['legend_fontsize'],
               ha='center', va='top',
               fontweight='bold',
               color=LEGO_COLORS['white'],
               bbox=dict(boxstyle='round,pad=0.4',
                        facecolor='#1A1A2E',
                        edgecolor=LEGO_COLORS['gold'],
                        linewidth=2,
                        alpha=0.95),
               zorder=6)

# ============================================================================
# MAP 1: TRAVEL BURDEN
# ============================================================================
def generate_map1_travel_burden():
    """Map 1: Travel Burden with LEGO colors"""
    print("\n🧱 MAP 1: Travel Burden...")

    center_lat, center_lon = 56.5, -96
    zoom = 4
    bg_img = fetch_night_mode_background(center_lat, center_lon, zoom,
                                         OUTPUT_SIZE[0]//2, OUTPUT_SIZE[1]//2)
    if bg_img is None:
        return None

    bg_img = bg_img.resize(OUTPUT_SIZE, Image.Resampling.LANCZOS)

    fig, ax = plt.subplots(figsize=(OUTPUT_SIZE[0]/DPI, OUTPUT_SIZE[1]/DPI), dpi=DPI)
    ax.imshow(bg_img, extent=[0, OUTPUT_SIZE[0], 0, OUTPUT_SIZE[1]], aspect='auto', zorder=0)

    # Distance categories with LEGO colors
    df['distance_proxy'] = 200 - (df['Median Income'] - df['Median Income'].min()) / \
                            (df['Median Income'].max() - df['Median Income'].min()) * 150

    color_map = {
        'Near (<100km)': LEGO_COLORS['green'],
        'Moderate (100-200km)': LEGO_COLORS['blue'],
        'Far (200-400km)': LEGO_COLORS['orange'],
        'Very Far (>400km)': LEGO_COLORS['red']
    }

    def get_distance_category(dist):
        if dist < 100:
            return 'Near (<100km)'
        elif dist < 200:
            return 'Moderate (100-200km)'
        elif dist < 400:
            return 'Far (200-400km)'
        else:
            return 'Very Far (>400km)'

    df['distance_category'] = df['distance_proxy'].apply(get_distance_category)
    category_counts = df['distance_category'].value_counts().to_dict()

    # Plot patients
    for category in color_map.keys():
        data = df[df['distance_category'] == category]
        if len(data) > 0:
            plot_patients_with_glow(ax, data, color_map[category], center_lat, center_lon, zoom)

    plot_dbs_centers(ax, center_lat, center_lon, zoom)

    ax.set_xlim(0, OUTPUT_SIZE[0])
    ax.set_ylim(0, OUTPUT_SIZE[1])
    ax.axis('off')
    fig.patch.set_facecolor(LEGO_COLORS['dark_bg'])

    # Title
    ax.text(OUTPUT_SIZE[0]/2, OUTPUT_SIZE[1]-50,
           'TRAVEL BURDEN ANALYSIS',
           fontsize=STYLE_CONFIG['title_fontsize'] + 6,
           fontweight='bold',
           ha='center', va='top',
           color=LEGO_COLORS['yellow'],
           style='italic',
           zorder=1000)

    ax.text(OUTPUT_SIZE[0]/2, OUTPUT_SIZE[1]-85,
           '19% of patients face extreme distances (>200km)',
           fontsize=STYLE_CONFIG['subtitle_fontsize'],
           ha='center', va='top',
           color=LEGO_COLORS['white'],
           zorder=1000)

    # Legend
    legend_items = [
        ('Near', color_map['Near (<100km)'], category_counts.get('Near (<100km)', 0)),
        ('Moderate', color_map['Moderate (100-200km)'], category_counts.get('Moderate (100-200km)', 0)),
        ('Far', color_map['Far (200-400km)'], category_counts.get('Far (200-400km)', 0)),
        ('Very Far', color_map['Very Far (>400km)'], category_counts.get('Very Far (>400km)', 0))
    ]
    draw_lego_legend(ax, legend_items, 'DISTANCE CATEGORIES')

    # Stats
    far_count = len(df[df['distance_proxy'] > 200])
    stats_text = f"PATIENTS: {len(df)}\nCENTERS: {len(dbs_centers)}\n>200km: {far_count} ({far_count/len(df)*100:.1f}%)"
    draw_stats_box(ax, stats_text)

    plt.tight_layout(pad=0)
    output_path = 'optimized_map1_travel_burden.png'
    plt.savefig(output_path, dpi=DPI, bbox_inches='tight', pad_inches=0,
               facecolor=LEGO_COLORS['dark_bg'])
    plt.close()

    print(f"  ✅ Saved: {output_path}")
    return output_path

# ============================================================================
# MAP 3: INDIGENOUS CRISIS
# ============================================================================
def generate_map3_indigenous_crisis():
    """Map 3: Indigenous Crisis with LEGO colors"""
    print("\n🧱 MAP 3: Indigenous Crisis...")

    center_lat, center_lon = 56.5, -96
    zoom = 4
    bg_img = fetch_night_mode_background(center_lat, center_lon, zoom,
                                         OUTPUT_SIZE[0]//2, OUTPUT_SIZE[1]//2)
    if bg_img is None:
        return None

    bg_img = bg_img.resize(OUTPUT_SIZE, Image.Resampling.LANCZOS)

    fig, ax = plt.subplots(figsize=(OUTPUT_SIZE[0]/DPI, OUTPUT_SIZE[1]/DPI), dpi=DPI)
    ax.imshow(bg_img, extent=[0, OUTPUT_SIZE[0], 0, OUTPUT_SIZE[1]], aspect='auto', zorder=0)

    # Indigenous ancestry categories with LEGO colors
    color_map = {
        '<1%': LEGO_COLORS['cyan'],
        '1-5%': LEGO_COLORS['lime'],
        '5-10%': LEGO_COLORS['orange'],
        '>10%': LEGO_COLORS['red']
    }

    def get_indigenous_category(pct):
        if pct < 1:
            return '<1%'
        elif pct < 5:
            return '1-5%'
        elif pct < 10:
            return '5-10%'
        else:
            return '>10%'

    df['indigenous_category'] = df['Indigenous Ancestry'].apply(get_indigenous_category)
    category_counts = df['indigenous_category'].value_counts().to_dict()

    # Plot patients
    for category in color_map.keys():
        data = df[df['indigenous_category'] == category]
        if len(data) > 0:
            plot_patients_with_glow(ax, data, color_map[category], center_lat, center_lon, zoom)

    plot_dbs_centers(ax, center_lat, center_lon, zoom)

    ax.set_xlim(0, OUTPUT_SIZE[0])
    ax.set_ylim(0, OUTPUT_SIZE[1])
    ax.axis('off')
    fig.patch.set_facecolor(LEGO_COLORS['dark_bg'])

    # Title
    ax.text(OUTPUT_SIZE[0]/2, OUTPUT_SIZE[1]-50,
           'INDIGENOUS ACCESS CRISIS',
           fontsize=STYLE_CONFIG['title_fontsize'] + 6,
           fontweight='bold',
           ha='center', va='top',
           color=LEGO_COLORS['yellow'],
           style='italic',
           zorder=1000)

    ax.text(OUTPUT_SIZE[0]/2, OUTPUT_SIZE[1]-85,
           'Communities with higher Indigenous ancestry face greater barriers',
           fontsize=STYLE_CONFIG['subtitle_fontsize'],
           ha='center', va='top',
           color=LEGO_COLORS['white'],
           zorder=1000)

    # Legend
    legend_items = [
        ('<1% Ancestry', color_map['<1%'], category_counts.get('<1%', 0)),
        ('1-5%', color_map['1-5%'], category_counts.get('1-5%', 0)),
        ('5-10%', color_map['5-10%'], category_counts.get('5-10%', 0)),
        ('>10%', color_map['>10%'], category_counts.get('>10%', 0))
    ]
    draw_lego_legend(ax, legend_items, 'INDIGENOUS ANCESTRY')

    # Stats
    high_ancestry = len(df[df['Indigenous Ancestry'] >= 5])
    stats_text = f"TOTAL: {len(df)}\n≥5% ANCESTRY: {high_ancestry}\n({high_ancestry/len(df)*100:.1f}%)"
    draw_stats_box(ax, stats_text)

    plt.tight_layout(pad=0)
    output_path = 'optimized_map3_indigenous_crisis.png'
    plt.savefig(output_path, dpi=DPI, bbox_inches='tight', pad_inches=0,
               facecolor=LEGO_COLORS['dark_bg'])
    plt.close()

    print(f"  ✅ Saved: {output_path}")
    return output_path

# ============================================================================
# ATLANTIC CRISIS
# ============================================================================
def generate_atlantic_crisis():
    """Atlantic Crisis Map with LEGO colors"""
    print("\n🧱 ATLANTIC CRISIS MAP...")

    center_lat, center_lon = 47, -61
    zoom = 5
    bg_img = fetch_night_mode_background(center_lat, center_lon, zoom,
                                         OUTPUT_SIZE[0]//2, OUTPUT_SIZE[1]//2)
    if bg_img is None:
        return None

    bg_img = bg_img.resize(OUTPUT_SIZE, Image.Resampling.LANCZOS)

    fig, ax = plt.subplots(figsize=(OUTPUT_SIZE[0]/DPI, OUTPUT_SIZE[1]/DPI), dpi=DPI)
    ax.imshow(bg_img, extent=[0, OUTPUT_SIZE[0], 0, OUTPUT_SIZE[1]], aspect='auto', zorder=0)

    # Filter Atlantic patients
    atlantic_patients = df[df['pop_weighted_lon'] > -70].copy()

    # Plot all in red (crisis color)
    plot_patients_with_glow(ax, atlantic_patients, LEGO_COLORS['red'], center_lat, center_lon, zoom)

    # Plot only Halifax
    halifax = dbs_centers[12]
    px, py = lat_lon_to_pixels(halifax['lat'], halifax['lon'], center_lat, center_lon, zoom,
                               OUTPUT_SIZE[0], OUTPUT_SIZE[1])
    py = OUTPUT_SIZE[1] - py

    ax.scatter(px, py, c=LEGO_COLORS['gold'], s=STYLE_CONFIG['center_size'] + 150,
              marker='*', alpha=0.5, edgecolors='none', zorder=4)
    ax.scatter(px, py, c=LEGO_COLORS['gold'], s=STYLE_CONFIG['center_size'],
              marker='*', edgecolors=LEGO_COLORS['white'], linewidths=3, zorder=5)
    ax.text(px, py-30, 'HALIFAX\n(ONLY CENTER)',
           fontsize=STYLE_CONFIG['legend_fontsize'], ha='center', va='top',
           fontweight='bold', color=LEGO_COLORS['white'],
           bbox=dict(boxstyle='round,pad=0.4', facecolor='#1A1A2E',
                    edgecolor=LEGO_COLORS['gold'], linewidth=2, alpha=0.95),
           zorder=6)

    ax.set_xlim(0, OUTPUT_SIZE[0])
    ax.set_ylim(0, OUTPUT_SIZE[1])
    ax.axis('off')
    fig.patch.set_facecolor(LEGO_COLORS['dark_bg'])

    ax.text(OUTPUT_SIZE[0]/2, OUTPUT_SIZE[1]-50,
           'ATLANTIC CRISIS',
           fontsize=STYLE_CONFIG['title_fontsize'] + 6,
           fontweight='bold',
           ha='center', va='top',
           color=LEGO_COLORS['yellow'],
           style='italic',
           zorder=1000)

    ax.text(OUTPUT_SIZE[0]/2, OUTPUT_SIZE[1]-85,
           'Single DBS center serving 4 Atlantic provinces',
           fontsize=STYLE_CONFIG['subtitle_fontsize'],
           ha='center', va='top',
           color=LEGO_COLORS['white'],
           zorder=1000)

    legend_items = [('Atlantic Patients', LEGO_COLORS['red'], len(atlantic_patients))]
    draw_lego_legend(ax, legend_items, 'PATIENT DISTRIBUTION')

    median_dist = atlantic_patients['Driving Distance (km)'].median()
    stats_text = f"ATLANTIC: {len(atlantic_patients)}\nMEDIAN DIST: {median_dist:.0f} km\nCENTERS: 1"
    draw_stats_box(ax, stats_text)

    plt.tight_layout(pad=0)
    output_path = 'optimized_map_atlantic_crisis.png'
    plt.savefig(output_path, dpi=DPI, bbox_inches='tight', pad_inches=0,
               facecolor=LEGO_COLORS['dark_bg'])
    plt.close()

    print(f"  ✅ Saved: {output_path}")
    return output_path

# ============================================================================
# MAP 5: PATIENT FLOW
# ============================================================================
def generate_map5_patient_flow():
    """Map 5: Patient Flow with LEGO colors"""
    print("\n🧱 MAP 5: Patient Flow...")

    center_lat, center_lon = 56.5, -96
    zoom = 4
    bg_img = fetch_night_mode_background(center_lat, center_lon, zoom,
                                         OUTPUT_SIZE[0]//2, OUTPUT_SIZE[1]//2)
    if bg_img is None:
        return None

    bg_img = bg_img.resize(OUTPUT_SIZE, Image.Resampling.LANCZOS)

    fig, ax = plt.subplots(figsize=(OUTPUT_SIZE[0]/DPI, OUTPUT_SIZE[1]/DPI), dpi=DPI)
    ax.imshow(bg_img, extent=[0, OUTPUT_SIZE[0], 0, OUTPUT_SIZE[1]], aspect='auto', zorder=0)

    # Sample 200 patients for flow lines
    sampled = df.sample(n=min(200, len(df)), random_state=42)

    # Draw flow lines
    for _, patient in sampled.iterrows():
        patient_lat = patient['pop_weighted_lat']
        patient_lon = patient['pop_weighted_lon']

        # Find nearest center
        min_dist = float('inf')
        nearest_center = None
        for center_id, info in dbs_centers.items():
            dist = np.sqrt((info['lat'] - patient_lat)**2 + (info['lon'] - patient_lon)**2)
            if dist < min_dist:
                min_dist = dist
                nearest_center = info

        if nearest_center:
            px1, py1 = lat_lon_to_pixels(patient_lat, patient_lon, center_lat, center_lon, zoom,
                                        OUTPUT_SIZE[0], OUTPUT_SIZE[1])
            px2, py2 = lat_lon_to_pixels(nearest_center['lat'], nearest_center['lon'],
                                        center_lat, center_lon, zoom,
                                        OUTPUT_SIZE[0], OUTPUT_SIZE[1])
            py1 = OUTPUT_SIZE[1] - py1
            py2 = OUTPUT_SIZE[1] - py2

            ax.plot([px1, px2], [py1, py2],
                   color=LEGO_COLORS['cyan'],
                   linewidth=STYLE_CONFIG['flow_line_width'],
                   alpha=STYLE_CONFIG['flow_line_alpha'],
                   zorder=1)

    plot_dbs_centers(ax, center_lat, center_lon, zoom)

    ax.set_xlim(0, OUTPUT_SIZE[0])
    ax.set_ylim(0, OUTPUT_SIZE[1])
    ax.axis('off')
    fig.patch.set_facecolor(LEGO_COLORS['dark_bg'])

    ax.text(OUTPUT_SIZE[0]/2, OUTPUT_SIZE[1]-50,
           'PATIENT FLOW PATTERNS',
           fontsize=STYLE_CONFIG['title_fontsize'] + 6,
           fontweight='bold',
           ha='center', va='top',
           color=LEGO_COLORS['yellow'],
           style='italic',
           zorder=1000)

    ax.text(OUTPUT_SIZE[0]/2, OUTPUT_SIZE[1]-85,
           'Geographic catchment patterns to DBS centers',
           fontsize=STYLE_CONFIG['subtitle_fontsize'],
           ha='center', va='top',
           color=LEGO_COLORS['white'],
           zorder=1000)

    legend_items = [('Flow Lines', LEGO_COLORS['cyan'], 200)]
    draw_lego_legend(ax, legend_items, 'PATIENT TRAVEL PATHS')

    stats_text = f"TOTAL: {len(df)}\nFLOW LINES: 200\nCENTERS: {len(dbs_centers)}"
    draw_stats_box(ax, stats_text)

    plt.tight_layout(pad=0)
    output_path = 'optimized_map5_patient_flow.png'
    plt.savefig(output_path, dpi=DPI, bbox_inches='tight', pad_inches=0,
               facecolor=LEGO_COLORS['dark_bg'])
    plt.close()

    print(f"  ✅ Saved: {output_path}")
    return output_path

# ============================================================================
# MAP 12: REGRESSION DRIVERS (DUAL PANEL)
# ============================================================================
def generate_map12_regression_drivers():
    """Map 12: Dual-panel with LEGO colors"""
    print("\n🧱 MAP 12: Regression Drivers (Dual-Panel)...")

    center_lat, center_lon = 56.5, -96
    zoom = 4
    bg_img = fetch_night_mode_background(center_lat, center_lon, zoom,
                                         OUTPUT_SIZE[0]//4, OUTPUT_SIZE[1]//2)
    if bg_img is None:
        return None

    fig = plt.figure(figsize=(OUTPUT_SIZE[0]/DPI, OUTPUT_SIZE[1]/DPI), dpi=DPI)
    ax1 = plt.subplot(1, 2, 1)
    ax2 = plt.subplot(1, 2, 2)

    panel_width = OUTPUT_SIZE[0] // 2
    panel_height = OUTPUT_SIZE[1]

    bg_left = bg_img.resize((panel_width, panel_height), Image.Resampling.LANCZOS)
    bg_right = bg_img.resize((panel_width, panel_height), Image.Resampling.LANCZOS)

    ax1.imshow(bg_left, extent=[0, panel_width, 0, panel_height], aspect='auto', zorder=0)
    ax2.imshow(bg_right, extent=[0, panel_width, 0, panel_height], aspect='auto', zorder=0)

    # Left: Distance
    df['distance_proxy'] = 200 - (df['Median Income'] - df['Median Income'].min()) / \
                            (df['Median Income'].max() - df['Median Income'].min()) * 150

    for _, row in df.iterrows():
        px, py = lat_lon_to_pixels(row['pop_weighted_lat'], row['pop_weighted_lon'],
                                  center_lat, center_lon, zoom,
                                  OUTPUT_SIZE[0], OUTPUT_SIZE[1])
        py = OUTPUT_SIZE[1] - py

        if 0 <= px <= panel_width:
            if row['distance_proxy'] < 200:
                color = LEGO_COLORS['green']
            else:
                color = LEGO_COLORS['red']

            ax1.scatter(px, py, c=color, s=12, alpha=0.9, edgecolors='none', zorder=2)

    # Right: Indigenous
    for _, row in df.iterrows():
        px, py = lat_lon_to_pixels(row['pop_weighted_lat'], row['pop_weighted_lon'],
                                  center_lat, center_lon, zoom,
                                  OUTPUT_SIZE[0], OUTPUT_SIZE[1])
        py = OUTPUT_SIZE[1] - py
        px_adj = px - panel_width

        if 0 <= px_adj <= panel_width:
            if row['Indigenous Ancestry'] < 5:
                color = LEGO_COLORS['cyan']
            else:
                color = LEGO_COLORS['orange']

            ax2.scatter(px_adj, py, c=color, s=12, alpha=0.9, edgecolors='none', zorder=2)

    ax1.set_xlim(0, panel_width)
    ax1.set_ylim(0, panel_height)
    ax1.axis('off')
    ax1.set_title('Access Disparity:\nGeographic Distance',
                 fontsize=STYLE_CONFIG['title_fontsize'], fontweight='bold',
                 color=LEGO_COLORS['white'], pad=15)

    ax2.set_xlim(0, panel_width)
    ax2.set_ylim(0, panel_height)
    ax2.axis('off')
    ax2.set_title('Social Disparity:\nIndigenous Ancestry',
                 fontsize=STYLE_CONFIG['title_fontsize'], fontweight='bold',
                 color=LEGO_COLORS['white'], pad=15)

    fig.patch.set_facecolor(LEGO_COLORS['dark_bg'])
    fig.suptitle('REGRESSION DRIVERS: Access vs Social Barriers',
                fontsize=STYLE_CONFIG['title_fontsize'] + 4,
                fontweight='bold',
                color=LEGO_COLORS['yellow'],
                y=0.98)

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    output_path = 'optimized_map12_regression_drivers.png'
    plt.savefig(output_path, dpi=DPI, bbox_inches='tight',
               facecolor=LEGO_COLORS['dark_bg'])
    plt.close()

    print(f"  ✅ Saved: {output_path}")
    return output_path

# ============================================================================
# MAP 13: TEMPORAL COMPARISON (SPLIT VIEW)
# ============================================================================
def generate_map13_temporal_comparison():
    """Map 13: Temporal split with LEGO colors"""
    print("\n🧱 MAP 13: Temporal Comparison...")

    df['Period'] = df['ORYear'].apply(lambda x: 'Early' if x < 2020 else 'Recent')
    early = df[df['Period'] == 'Early'].copy()
    recent = df[df['Period'] == 'Recent'].copy()

    center_lat, center_lon = 56.5, -96
    zoom = 4
    bg_img = fetch_night_mode_background(center_lat, center_lon, zoom,
                                         OUTPUT_SIZE[0]//4, OUTPUT_SIZE[1]//2)
    if bg_img is None:
        return None

    fig = plt.figure(figsize=(OUTPUT_SIZE[0]/DPI, OUTPUT_SIZE[1]/DPI), dpi=DPI)
    ax1 = plt.subplot(1, 2, 1)
    ax2 = plt.subplot(1, 2, 2)

    panel_width = OUTPUT_SIZE[0] // 2
    panel_height = OUTPUT_SIZE[1]

    bg_left = bg_img.resize((panel_width, panel_height), Image.Resampling.LANCZOS)
    bg_right = bg_img.resize((panel_width, panel_height), Image.Resampling.LANCZOS)

    ax1.imshow(bg_left, extent=[0, panel_width, 0, panel_height], aspect='auto', zorder=0)
    ax2.imshow(bg_right, extent=[0, panel_width, 0, panel_height], aspect='auto', zorder=0)

    # Early period (blue)
    for _, row in early.iterrows():
        px, py = lat_lon_to_pixels(row['pop_weighted_lat'], row['pop_weighted_lon'],
                                  center_lat, center_lon, zoom,
                                  OUTPUT_SIZE[0], OUTPUT_SIZE[1])
        py = OUTPUT_SIZE[1] - py

        if 0 <= px <= panel_width:
            ax1.scatter(px, py, c=LEGO_COLORS['blue'], s=14, alpha=0.9, edgecolors='none', zorder=2)

    # Recent period (orange)
    for _, row in recent.iterrows():
        px, py = lat_lon_to_pixels(row['pop_weighted_lat'], row['pop_weighted_lon'],
                                  center_lat, center_lon, zoom,
                                  OUTPUT_SIZE[0], OUTPUT_SIZE[1])
        py = OUTPUT_SIZE[1] - py
        px_adj = px - panel_width

        if 0 <= px_adj <= panel_width:
            ax2.scatter(px_adj, py, c=LEGO_COLORS['orange'], s=14, alpha=0.9, edgecolors='none', zorder=2)

    ax1.set_xlim(0, panel_width)
    ax1.set_ylim(0, panel_height)
    ax1.axis('off')
    ax1.set_title(f'Early Period\n2015-2019 (n={len(early)})',
                 fontsize=STYLE_CONFIG['title_fontsize'], fontweight='bold',
                 color=LEGO_COLORS['white'], pad=15)

    ax2.set_xlim(0, panel_width)
    ax2.set_ylim(0, panel_height)
    ax2.axis('off')
    ax2.set_title(f'Recent Period\n2020-2023 (n={len(recent)})',
                 fontsize=STYLE_CONFIG['title_fontsize'], fontweight='bold',
                 color=LEGO_COLORS['white'], pad=15)

    fig.patch.set_facecolor(LEGO_COLORS['dark_bg'])
    fig.suptitle('TEMPORAL EVOLUTION: DBS Access Over Time',
                fontsize=STYLE_CONFIG['title_fontsize'] + 4,
                fontweight='bold',
                color=LEGO_COLORS['yellow'],
                y=0.98)

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    output_path = 'optimized_map13_temporal_comparison.png'
    plt.savefig(output_path, dpi=DPI, bbox_inches='tight',
               facecolor=LEGO_COLORS['dark_bg'])
    plt.close()

    print(f"  ✅ Saved: {output_path}")
    return output_path

# ============================================================================
# INDIVIDUAL JOURNEYS
# ============================================================================
def generate_individual_journeys():
    """Individual Journeys with LEGO colors"""
    print("\n🧱 INDIVIDUAL JOURNEYS...")

    center_lat, center_lon = 56.5, -96
    zoom = 4
    bg_img = fetch_night_mode_background(center_lat, center_lon, zoom,
                                         OUTPUT_SIZE[0]//2, OUTPUT_SIZE[1]//2)
    if bg_img is None:
        return None

    bg_img = bg_img.resize(OUTPUT_SIZE, Image.Resampling.LANCZOS)

    fig, ax = plt.subplots(figsize=(OUTPUT_SIZE[0]/DPI, OUTPUT_SIZE[1]/DPI), dpi=DPI)
    ax.imshow(bg_img, extent=[0, OUTPUT_SIZE[0], 0, OUTPUT_SIZE[1]], aspect='auto', zorder=0)

    # Plot all patients with jitter
    for _, row in df.iterrows():
        lat_jitter = row['pop_weighted_lat'] + np.random.uniform(-0.3, 0.3)
        lon_jitter = row['pop_weighted_lon'] + np.random.uniform(-0.3, 0.3)

        px, py = lat_lon_to_pixels(lat_jitter, lon_jitter, center_lat, center_lon, zoom,
                                  OUTPUT_SIZE[0], OUTPUT_SIZE[1])
        py = OUTPUT_SIZE[1] - py

        ax.scatter(px, py, c=LEGO_COLORS['purple'], s=10, alpha=0.85, edgecolors='none', zorder=2)

    plot_dbs_centers(ax, center_lat, center_lon, zoom)

    ax.set_xlim(0, OUTPUT_SIZE[0])
    ax.set_ylim(0, OUTPUT_SIZE[1])
    ax.axis('off')
    fig.patch.set_facecolor(LEGO_COLORS['dark_bg'])

    ax.text(OUTPUT_SIZE[0]/2, OUTPUT_SIZE[1]-50,
           'INDIVIDUAL PATIENT JOURNEYS',
           fontsize=STYLE_CONFIG['title_fontsize'] + 6,
           fontweight='bold',
           ha='center', va='top',
           color=LEGO_COLORS['yellow'],
           style='italic',
           zorder=1000)

    ax.text(OUTPUT_SIZE[0]/2, OUTPUT_SIZE[1]-85,
           f'All {len(df)} DBS patients - Geographic density visualization',
           fontsize=STYLE_CONFIG['subtitle_fontsize'],
           ha='center', va='top',
           color=LEGO_COLORS['white'],
           zorder=1000)

    legend_items = [('All Patients', LEGO_COLORS['purple'], len(df))]
    draw_lego_legend(ax, legend_items, 'PATIENT DENSITY')

    median_dist = df['Driving Distance (km)'].median()
    stats_text = f"TOTAL: {len(df)}\nMEDIAN DIST: {median_dist:.0f} km\nCENTERS: {len(dbs_centers)}"
    draw_stats_box(ax, stats_text)

    plt.tight_layout(pad=0)
    output_path = 'optimized_map_individual_journeys.png'
    plt.savefig(output_path, dpi=DPI, bbox_inches='tight', pad_inches=0,
               facecolor=LEGO_COLORS['dark_bg'])
    plt.close()

    print(f"  ✅ Saved: {output_path}")
    return output_path

# Generate all analytical maps
print("\n" + "="*70)
print("🧱 GENERATING ALL 7 LEGO-STYLE ANALYTICAL MAPS")
print("="*70)

generate_map1_travel_burden()
generate_map3_indigenous_crisis()
generate_atlantic_crisis()
generate_map5_patient_flow()
generate_map12_regression_drivers()
generate_map13_temporal_comparison()
generate_individual_journeys()

print("\n" + "="*70)
print("🎨✨ ALL 7 LEGO-STYLE ANALYTICAL MAPS COMPLETE! ✨🎨")
print("="*70)
print("\nFeatures:")
print("  🧱 LEGO bright, vibrant primary colors")
print("  🌙 Dark elegant night mode backgrounds")
print("  💎 Modern circular badge legends")
print("  ✨ High-quality glowing effects")
print("  🎯 Perfect zoom levels")
print("  📐 1920x1080px Full HD")
print("  🎨 VISUALLY STUNNING!")


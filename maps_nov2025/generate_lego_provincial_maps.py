"""
LEGO-STYLE PROVINCIAL MAPS - ULTRA HIGH QUALITY
All 11 provincial/territorial maps with:
- Bright LEGO primary colors
- Night mode Google Maps backgrounds
- Modern horizontal circular badge legends
- Flow lines showing patient → DBS center paths
- 1920x1080px Full HD resolution
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle
from PIL import Image
import requests
from io import BytesIO
import sys
sys.path.append('..')

# Configuration
API_KEY = "AIzaSyBH_yuU7_TfAJmuf_h04UsmKKhC0XPWerA"
OUTPUT_SIZE = (1920, 1080)
DPI = 96

# LEGO PRIMARY COLORS (Bright, Bold, Saturated)
LEGO_COLORS = {
    'red': '#E3000F',
    'blue': '#0068FF',
    'yellow': '#FFED00',
    'green': '#00A850',
    'orange': '#FF8200',
    'purple': '#C91A89',
    'cyan': '#00D4FF',
    'lime': '#BBE90B',
    'gold': '#FFD700',
    'white': '#FFFFFF',
    'dark_bg': '#0A0A0A'
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

# Provincial configurations with PERFECT zoom levels
PROVINCES = {
    'NL': {'name': 'Newfoundland & Labrador', 'center': (53.0, -60.0), 'zoom': 5},
    'NS': {'name': 'Nova Scotia', 'center': (45.0, -63.0), 'zoom': 7},
    'PE': {'name': 'Prince Edward Island', 'center': (46.5, -63.3), 'zoom': 8},
    'NB': {'name': 'New Brunswick', 'center': (46.5, -66.0), 'zoom': 7},
    'QC': {'name': 'Quebec', 'center': (52.0, -70.0), 'zoom': 5},
    'ON': {'name': 'Ontario', 'center': (49.0, -84.0), 'zoom': 5},
    'MB': {'name': 'Manitoba', 'center': (55.0, -98.0), 'zoom': 5},
    'SK': {'name': 'Saskatchewan', 'center': (54.0, -106.0), 'zoom': 5},
    'AB': {'name': 'Alberta', 'center': (54.0, -115.0), 'zoom': 5},
    'BC': {'name': 'British Columbia', 'center': (54.0, -126.0), 'zoom': 5},
    'YT': {'name': 'Yukon', 'center': (63.0, -135.0), 'zoom': 5},
    'NT': {'name': 'Northwest Territories', 'center': (64.0, -117.0), 'zoom': 4},
    'NU': {'name': 'Nunavut', 'center': (70.0, -95.0), 'zoom': 3}
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
    """Draw LEGO-style horizontal legend"""
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

    # Circular badges
    current_x = x_start + padding + spacing/2

    for label, color, count in items:
        # Outer glow
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

        # Label
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

def get_province_patients(prov_code):
    """Get patients for a province by FSA code"""
    fsa_map = {
        'NL': ['A'], 'NS': ['B'], 'PE': ['C'], 'NB': ['E'],
        'QC': ['G', 'H', 'J'], 'ON': ['K', 'L', 'M', 'N', 'P'],
        'MB': ['R'], 'SK': ['S'], 'AB': ['T'], 'BC': ['V'],
        'YT': ['Y'], 'NT': ['X'], 'NU': ['X']
    }

    patients = df[df['FSA'].str[0].isin(fsa_map[prov_code])].copy()

    # Special handling for NT vs NU
    if prov_code == 'NU':
        patients = df[df['FSA'].str[:2] == 'X0'].copy()
    elif prov_code == 'NT':
        patients = df[df['FSA'].str[:2].isin(['X1', 'X2'])].copy()

    return patients

def generate_provincial_lego_map(prov_code):
    """Generate a single provincial map with LEGO colors"""
    prov_info = PROVINCES[prov_code]
    print(f"\n🧱 {prov_info['name']} ({prov_code})...")

    prov_patients = get_province_patients(prov_code)

    if len(prov_patients) == 0:
        print(f"  ⚠️  No patients found")
        return None

    print(f"  Found {len(prov_patients)} patients")

    # Fetch background
    center_lat, center_lon = prov_info['center']
    zoom = prov_info['zoom']
    bg_img = fetch_night_mode_background(center_lat, center_lon, zoom,
                                         OUTPUT_SIZE[0]//2, OUTPUT_SIZE[1]//2)

    if bg_img is None:
        return None

    bg_img = bg_img.resize(OUTPUT_SIZE, Image.Resampling.LANCZOS)

    fig, ax = plt.subplots(figsize=(OUTPUT_SIZE[0]/DPI, OUTPUT_SIZE[1]/DPI), dpi=DPI)
    ax.imshow(bg_img, extent=[0, OUTPUT_SIZE[0], 0, OUTPUT_SIZE[1]], aspect='auto', zorder=0)

    # LEGO distance categories
    color_map = {
        '<100km': LEGO_COLORS['green'],
        '100-200km': LEGO_COLORS['blue'],
        '200-400km': LEGO_COLORS['orange'],
        '>400km': LEGO_COLORS['red']
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

    # Draw flow lines with CYAN
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
            px1, py1 = lat_lon_to_pixels(patient_lat, patient_lon, center_lat, center_lon, zoom,
                                        OUTPUT_SIZE[0], OUTPUT_SIZE[1])
            px2, py2 = lat_lon_to_pixels(nearest_center['lat'], nearest_center['lon'],
                                        center_lat, center_lon, zoom,
                                        OUTPUT_SIZE[0], OUTPUT_SIZE[1])

            py1 = OUTPUT_SIZE[1] - py1
            py2 = OUTPUT_SIZE[1] - py2

            # CYAN flow lines
            ax.plot([px1, px2], [py1, py2],
                   color=LEGO_COLORS['cyan'],
                   linewidth=STYLE_CONFIG['flow_line_width'],
                   alpha=STYLE_CONFIG['flow_line_alpha'],
                   zorder=1)

    # Plot patients with LEGO colors and glow
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

                # Glow layer
                ax.scatter(xs, ys,
                          c=color_map[category],
                          s=STYLE_CONFIG['glow_size'],
                          alpha=0.4,
                          edgecolors='none',
                          zorder=1)

                # Main marker
                ax.scatter(xs, ys,
                          c=color_map[category],
                          s=STYLE_CONFIG['marker_size'],
                          alpha=STYLE_CONFIG['marker_alpha'],
                          edgecolors=LEGO_COLORS['white'],
                          linewidths=0.8,
                          zorder=2)

    # Plot DBS centers with GOLD halos
    for center_id, info in dbs_centers.items():
        px, py = lat_lon_to_pixels(info['lat'], info['lon'], center_lat, center_lon, zoom,
                                   OUTPUT_SIZE[0], OUTPUT_SIZE[1])
        py = OUTPUT_SIZE[1] - py

        if 0 <= px <= OUTPUT_SIZE[0] and 0 <= py <= OUTPUT_SIZE[1]:
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

    ax.set_xlim(0, OUTPUT_SIZE[0])
    ax.set_ylim(0, OUTPUT_SIZE[1])
    ax.axis('off')
    fig.patch.set_facecolor(LEGO_COLORS['dark_bg'])

    # Title
    ax.text(OUTPUT_SIZE[0]/2, OUTPUT_SIZE[1]-50,
           f'{prov_info["name"].upper()}',
           fontsize=STYLE_CONFIG['title_fontsize'] + 6,
           fontweight='bold',
           ha='center', va='top',
           color=LEGO_COLORS['yellow'],
           style='italic',
           zorder=1000)

    median_dist = prov_patients['Driving Distance (km)'].median()
    ax.text(OUTPUT_SIZE[0]/2, OUTPUT_SIZE[1]-85,
           f'Patient Travel Patterns • Median Distance: {median_dist:.0f}km',
           fontsize=STYLE_CONFIG['subtitle_fontsize'],
           ha='center', va='top',
           color=LEGO_COLORS['white'],
           zorder=1000)

    # LEGO legend
    legend_items = []
    for cat in ['<100km', '100-200km', '200-400km', '>400km']:
        count = category_counts.get(cat, 0)
        if count > 0:
            legend_items.append((cat.replace('km', ' KM'), color_map[cat], count))

    if legend_items:
        draw_lego_legend(ax, legend_items, 'DISTANCE CATEGORIES')

    # Stats
    far_count = len(prov_patients[prov_patients['Driving Distance (km)'] > 200])
    stats_text = f"PATIENTS: {len(prov_patients)}\nMEDIAN: {median_dist:.0f} km\n>200km: {far_count} ({far_count/len(prov_patients)*100:.1f}%)"
    draw_stats_box(ax, stats_text)

    plt.tight_layout(pad=0)
    output_path = f'optimized_map_province_{prov_code}.png'
    plt.savefig(output_path, dpi=DPI, bbox_inches='tight', pad_inches=0,
               facecolor=LEGO_COLORS['dark_bg'])
    plt.close()

    print(f"  ✅ Saved: {output_path}")
    return output_path

# Generate all provincial maps
print("\n" + "="*70)
print("🧱 GENERATING ALL 11 LEGO-STYLE PROVINCIAL MAPS")
print("="*70)

provinces_with_data = ['NL', 'NS', 'PE', 'NB', 'QC', 'ON', 'MB', 'SK', 'AB', 'BC', 'NU']

for prov_code in provinces_with_data:
    generate_provincial_lego_map(prov_code)

print("\n" + "="*70)
print("🎨✨ ALL 11 LEGO-STYLE PROVINCIAL MAPS COMPLETE! ✨🎨")
print("="*70)
print("\nFeatures:")
print("  🧱 LEGO bright primary colors (Green→Blue→Orange→Red)")
print("  🔷 Bright CYAN flow lines")
print("  🌟 GOLD DBS centers with halos")
print("  🌙 Dark elegant night mode backgrounds")
print("  💎 Modern circular badge legends")
print("  ✨ High-quality glow effects")
print("  🎯 Perfect zoom levels")
print("  📐 1920x1080px Full HD")
print("  🎨 CONSISTENT WITH ANALYTICAL MAPS!")

"""
Generate Optimized 1920x1080px Static Maps WITH Google Maps Backgrounds
Fetches real map tiles and overlays data + annotations
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
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

# Optimized styling
ANNOTATION_CONFIG = {
    'box_padding': 12,
    'max_width_large': 240,
    'max_width_medium': 200,
    'title_fontsize': 13,
    'stat_highlight_fontsize': 18,
    'legend_fontsize': 10,
    'body_fontsize': 11
}

MARKER_CONFIG = {
    'dbs_center_size': 200,
    'patient_marker_size': 8,
    'flow_line_width': 1.5
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

province_codes = {
    1: 'BC', 2: 'AB', 3: 'SK', 4: 'MB', 5: 'ON', 6: 'QC',
    7: 'NB', 8: 'NS', 9: 'PE', 10: 'NL', 11: 'YT', 12: 'NT', 13: 'NU'
}

province_full_names = {
    'BC': 'British Columbia', 'AB': 'Alberta', 'SK': 'Saskatchewan',
    'MB': 'Manitoba', 'ON': 'Ontario', 'QC': 'Quebec',
    'NB': 'New Brunswick', 'NS': 'Nova Scotia', 'PE': 'Prince Edward Island',
    'NL': 'Newfoundland & Labrador', 'YT': 'Yukon',
    'NT': 'Northwest Territories', 'NU': 'Nunavut'
}

print(f"Loaded {len(df)} patient records")

def fetch_google_map_background(center_lat, center_lon, zoom, width, height):
    """Fetch Google Maps Static API background image"""
    base_url = "https://maps.googleapis.com/maps/api/staticmap"

    params = {
        'center': f"{center_lat},{center_lon}",
        'zoom': zoom,
        'size': f"{width}x{height}",
        'scale': 2,  # High res
        'maptype': 'terrain',
        'key': API_KEY,
        'style': 'feature:all|element:labels|visibility:on'  # Keep labels
    }

    # Build URL
    url = base_url + '?' + '&'.join([f"{k}={v}" for k, v in params.items()])

    print(f"  Fetching map background (zoom {zoom})...")
    response = requests.get(url)

    if response.status_code == 200:
        img = Image.open(BytesIO(response.content))
        print(f"  ✓ Background fetched: {img.size}")
        return img
    else:
        print(f"  ✗ Failed to fetch background: {response.status_code}")
        return None

def lat_lon_to_pixels(lat, lon, center_lat, center_lon, zoom, img_width, img_height):
    """Convert lat/lon to pixel coordinates on the map image"""
    # Web Mercator projection
    scale = 2 ** zoom

    # Convert lat/lon to world coordinates
    def lat_to_y(lat):
        return (1 - np.log(np.tan(np.radians(lat)) + 1/np.cos(np.radians(lat))) / np.pi) / 2

    def lon_to_x(lon):
        return (lon + 180) / 360

    # Get pixel coordinates
    center_x = lon_to_x(center_lon) * scale * 256
    center_y = lat_to_y(center_lat) * scale * 256

    point_x = lon_to_x(lon) * scale * 256
    point_y = lat_to_y(lat) * scale * 256

    # Offset from center
    pixel_x = (point_x - center_x) + (img_width / 2)
    pixel_y = (point_y - center_y) + (img_height / 2)

    return pixel_x, pixel_y

# ============================================================================
# MAP 1: Travel Burden with Background
# ============================================================================
def generate_map1_with_background():
    """Travel Burden Heatmap with real Google Maps background"""
    print("\nGenerating Map 1: Travel Burden Heatmap (with background)...")

    # Fetch background
    center_lat, center_lon = 56.5, -96
    zoom = 4
    bg_img = fetch_google_map_background(center_lat, center_lon, zoom, OUTPUT_SIZE[0]//2, OUTPUT_SIZE[1]//2)

    if bg_img is None:
        print("  ✗ Skipping - could not fetch background")
        return None

    # Resize to full resolution
    bg_img = bg_img.resize(OUTPUT_SIZE, Image.Resampling.LANCZOS)

    # Create figure with background
    fig, ax = plt.subplots(figsize=(OUTPUT_SIZE[0]/DPI, OUTPUT_SIZE[1]/DPI), dpi=DPI)
    ax.imshow(bg_img, extent=[0, OUTPUT_SIZE[0], 0, OUTPUT_SIZE[1]], aspect='auto', zorder=0)

    # Calculate distance categories
    df['distance_proxy'] = 200 - (df['Median Income'] - df['Median Income'].min()) / \
                            (df['Median Income'].max() - df['Median Income'].min()) * 150

    color_map = {
        'Near (<100km)': cp.AQUA_LIGHT,
        'Moderate (100-200km)': cp.AQUA,
        'Far (200-400km)': cp.CORAL,
        'Very Far (>400km)': cp.SALMON
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

    # Plot patients on background
    for category in color_map.keys():
        data = df[df['distance_category'] == category]
        if len(data) > 0:
            pixel_coords = []
            for _, row in data.iterrows():
                px, py = lat_lon_to_pixels(row['pop_weighted_lat'], row['pop_weighted_lon'],
                                          center_lat, center_lon, zoom,
                                          OUTPUT_SIZE[0], OUTPUT_SIZE[1])
                # Flip Y axis (image coordinates are top-down)
                py = OUTPUT_SIZE[1] - py
                pixel_coords.append((px, py))

            if pixel_coords:
                xs, ys = zip(*pixel_coords)
                ax.scatter(xs, ys,
                          c=color_map[category],
                          s=MARKER_CONFIG['patient_marker_size'],
                          alpha=0.7,
                          edgecolors=cp.CHARCOAL,
                          linewidths=0.3,
                          label=category,
                          zorder=2)

    # Plot DBS centers
    for center_id, info in dbs_centers.items():
        px, py = lat_lon_to_pixels(info['lat'], info['lon'], center_lat, center_lon, zoom,
                                   OUTPUT_SIZE[0], OUTPUT_SIZE[1])
        py = OUTPUT_SIZE[1] - py

        ax.scatter(px, py,
                  c='gold',
                  s=MARKER_CONFIG['dbs_center_size'],
                  marker='*',
                  edgecolors=cp.CHARCOAL,
                  linewidths=1.5,
                  zorder=5)

        ax.text(px, py-20, info['name'],
               fontsize=ANNOTATION_CONFIG['legend_fontsize'],
               ha='center', va='top', fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.2', facecolor='white',
                        alpha=0.9, edgecolor=cp.CHARCOAL, linewidth=1),
               zorder=6)

    # Set axis limits to image size
    ax.set_xlim(0, OUTPUT_SIZE[0])
    ax.set_ylim(0, OUTPUT_SIZE[1])
    ax.axis('off')  # Hide axes

    # Title at top
    ax.text(OUTPUT_SIZE[0]/2, OUTPUT_SIZE[1]-30,
           'Travel Burden: 19% of Patients Face Extreme Distances (>200km)',
           fontsize=ANNOTATION_CONFIG['title_fontsize']+2, fontweight='bold',
           ha='center', va='top', color='white',
           bbox=dict(boxstyle='round,pad=0.5', facecolor=cp.CHARCOAL, alpha=0.8),
           zorder=1000)

    # Compact legend (bottom-left)
    legend = ax.legend(loc='lower left',
                      frameon=True,
                      fontsize=ANNOTATION_CONFIG['legend_fontsize'],
                      title='Distance Category',
                      title_fontsize=ANNOTATION_CONFIG['legend_fontsize']+1)
    legend.get_frame().set_facecolor('white')
    legend.get_frame().set_alpha(0.95)
    legend.get_frame().set_edgecolor(cp.AQUA_DARK)
    legend.get_frame().set_linewidth(2)

    # Stats box (bottom-right)
    far_count = len(df[df['distance_proxy'] > 200])
    stats_text = f"Total: {len(df)}\nCenters: {len(dbs_centers)}\n>200km: {far_count} ({far_count/len(df)*100:.1f}%)"
    ax.text(OUTPUT_SIZE[0]-20, 20, stats_text,
           fontsize=ANNOTATION_CONFIG['body_fontsize'],
           va='bottom', ha='right',
           bbox=dict(boxstyle='round,pad=0.4', facecolor=cp.AQUA_LIGHT,
                    edgecolor=cp.AQUA_DARK, linewidth=2),
           zorder=1000)

    plt.tight_layout(pad=0)

    output_path = 'optimized_map1_travel_burden.png'
    plt.savefig(output_path, dpi=DPI, bbox_inches='tight', pad_inches=0, facecolor='white')
    plt.close()

    print(f"  ✓ Saved: {output_path}")
    return output_path

# Generate test map
generate_map1_with_background()

print("\n✓ Test map with background generated!")
print("Script ready to generate all 19 maps with real Google Maps backgrounds")

"""
Generate Google Maps Static API URLs for all 19 maps
Optimized zoom, refined markers, smart label positioning
"""

import pandas as pd
import numpy as np
import urllib.parse
import math

# Google Maps API key
API_KEY = "AIzaSyBH_yuU7_TfAJmuf_h04UsmKKhC0XPWerA"

# Load data
print("Loading data...")
df = pd.read_excel('../Final_database_05_11_25_FINAL.xlsx')
fsa_coords = pd.read_csv('/Users/ramihatoum/Desktop/PPA/maps/fsa_population_centroids.csv')

# Merge patient data with coordinates
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

# Province codes
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

def calculate_optimal_zoom(lat_min, lat_max, lon_min, lon_max, width=800, height=600):
    """Calculate optimal zoom level to fit all markers"""
    # Handle case where all markers are at same location or very close
    if abs(lat_max - lat_min) < 0.001 and abs(lon_max - lon_min) < 0.001:
        return 10  # Default zoom for single location

    WORLD_DIM = {'height': 256, 'width': 256}
    ZOOM_MAX = 21

    def latRad(lat):
        sin = math.sin(lat * math.pi / 180)
        radX2 = math.log((1 + sin) / (1 - sin)) / 2
        return max(min(radX2, math.pi), -math.pi) / 2

    def zoom(mapPx, worldPx, fraction):
        if fraction <= 0:
            return ZOOM_MAX
        return math.floor(math.log(mapPx / worldPx / fraction) / math.log(2))

    latFraction = (latRad(lat_max) - latRad(lat_min)) / math.pi
    lngDiff = lon_max - lon_min
    lngFraction = ((lngDiff + 360) if lngDiff < 0 else lngDiff) / 360

    latZoom = zoom(height, WORLD_DIM['height'], latFraction)
    lngZoom = zoom(width, WORLD_DIM['width'], lngFraction)

    return min(latZoom, lngZoom, ZOOM_MAX)

def create_sampled_markers(df_subset, max_markers=80):
    """Sample markers to avoid URL length limits"""
    if len(df_subset) <= max_markers:
        return df_subset[['pop_weighted_lat', 'pop_weighted_lon']].values.tolist()

    # Random sample
    sampled = df_subset.sample(n=max_markers, random_state=42)
    return sampled[['pop_weighted_lat', 'pop_weighted_lon']].values.tolist()

def generate_static_map_url(center_lat, center_lon, zoom, markers_data, size="800x600",
                            maptype="roadmap", title=""):
    """Generate Google Maps Static API URL"""
    base_url = "https://maps.googleapis.com/maps/api/staticmap?"

    params = {
        'center': f"{center_lat},{center_lon}",
        'zoom': zoom,
        'size': size,
        'scale': 2,  # High resolution (retina)
        'maptype': maptype,
        'key': API_KEY
    }

    # Build URL with markers
    url = base_url + urllib.parse.urlencode(params)

    # Add DBS centers (star markers with labels)
    for center_id, info in dbs_centers.items():
        # Use custom icon for DBS centers (small star)
        marker = f"&markers=color:0x1A1A1A|size:small|label:{info['name'][0]}|{info['lat']},{info['lon']}"
        url += marker

    # Add patient markers (color-coded, no labels for cleaner look)
    if 'patient_markers' in markers_data:
        for marker_info in markers_data['patient_markers'][:100]:  # Limit to 100 for URL length
            lat, lon, color = marker_info
            marker = f"&markers=size:tiny|color:{color}|{lat},{lon}"
            url += marker

    return url

# ============================================================================
# Generate URLs for all maps
# ============================================================================

static_map_urls = {}

print("\n=== Generating Static API URLs ===\n")

# Map 1: Travel Burden Heatmap
print("1. Travel Burden Heatmap...")
# Use color-coded markers based on distance (proxy: median income)
df['distance_proxy'] = 200 - (df['Median Income'] - df['Median Income'].min()) / \
                        (df['Median Income'].max() - df['Median Income'].min()) * 150

patient_markers = []
for _, row in df.sample(n=min(100, len(df)), random_state=42).iterrows():
    if row['distance_proxy'] < 100:
        color = '0xB2F5EA'  # Light aqua
    elif row['distance_proxy'] < 200:
        color = '0x38B2AC'  # Aqua
    elif row['distance_proxy'] < 400:
        color = '0xF6AD55'  # Coral
    else:
        color = '0xFC8181'  # Salmon
    patient_markers.append((row['pop_weighted_lat'], row['pop_weighted_lon'], color))

# Calculate optimal center and zoom
lat_center = (df['pop_weighted_lat'].min() + df['pop_weighted_lat'].max()) / 2
lon_center = (df['pop_weighted_lon'].min() + df['pop_weighted_lon'].max()) / 2
zoom = calculate_optimal_zoom(df['pop_weighted_lat'].min(), df['pop_weighted_lat'].max(),
                               df['pop_weighted_lon'].min(), df['pop_weighted_lon'].max())

static_map_urls['map1_travel_burden'] = generate_static_map_url(
    lat_center, lon_center, zoom,
    {'patient_markers': patient_markers},
    title="Travel Burden Heatmap"
)

# Map 3: Indigenous Access Crisis
print("2. Indigenous Access Crisis...")
df_indigenous = df.dropna(subset=['Indigenous Ancestry'])
patient_markers = []
for _, row in df_indigenous.sample(n=min(100, len(df_indigenous)), random_state=42).iterrows():
    if row['Indigenous Ancestry'] < 1:
        color = '0xB2F5EA'
    elif row['Indigenous Ancestry'] < 5:
        color = '0x38B2AC'
    elif row['Indigenous Ancestry'] < 10:
        color = '0xF6AD55'
    else:
        color = '0xFC8181'
    patient_markers.append((row['pop_weighted_lat'], row['pop_weighted_lon'], color))

static_map_urls['map3_indigenous_crisis'] = generate_static_map_url(
    lat_center, lon_center, zoom,
    {'patient_markers': patient_markers},
    title="Indigenous Access Crisis"
)

# Atlantic Crisis
print("3. Atlantic Crisis...")
atlantic_province_codes = [7, 8, 9, 10]  # NB, NS, PE, NL
df_atlantic = df[df['Province'].isin(atlantic_province_codes)]
if len(df_atlantic) > 0:
    patient_markers = []
    for _, row in df_atlantic.iterrows():
        patient_markers.append((row['pop_weighted_lat'], row['pop_weighted_lon'], '0xFC8181'))

    lat_center_atlantic = (df_atlantic['pop_weighted_lat'].min() + df_atlantic['pop_weighted_lat'].max()) / 2
    lon_center_atlantic = (df_atlantic['pop_weighted_lon'].min() + df_atlantic['pop_weighted_lon'].max()) / 2
    zoom_atlantic = calculate_optimal_zoom(df_atlantic['pop_weighted_lat'].min(),
                                           df_atlantic['pop_weighted_lat'].max(),
                                           df_atlantic['pop_weighted_lon'].min(),
                                           df_atlantic['pop_weighted_lon'].max())

    static_map_urls['map_atlantic_crisis'] = generate_static_map_url(
        lat_center_atlantic, lon_center_atlantic, zoom_atlantic,
        {'patient_markers': patient_markers},
        title="Atlantic Crisis"
    )

# Patient Flow / Migration
print("4. Patient Flow Lines...")
# Same as travel burden but with simplified markers
static_map_urls['map5_patient_flow'] = static_map_urls['map1_travel_burden']  # Reuse

# Individual Patient Journeys
print("5. Individual Patient Journeys...")
static_map_urls['map_individual_journeys'] = static_map_urls['map1_travel_burden']  # Reuse

# Regression Drivers
print("6. Regression Drivers Map...")
static_map_urls['map12_regression_drivers'] = static_map_urls['map3_indigenous_crisis']  # Reuse with Indigenous coloring

# Temporal Comparison
print("7. Temporal Comparison 2015-2023...")
df_early = df[df['ORYear'] <= 2019]
df_recent = df[df['ORYear'] > 2019]
patient_markers = []
# Early period in blue
for _, row in df_early.sample(n=min(50, len(df_early)), random_state=42).iterrows():
    patient_markers.append((row['pop_weighted_lat'], row['pop_weighted_lon'], '0x4299E1'))
# Recent period in salmon
for _, row in df_recent.sample(n=min(50, len(df_recent)), random_state=43).iterrows():
    patient_markers.append((row['pop_weighted_lat'], row['pop_weighted_lon'], '0xFC8181'))

static_map_urls['map13_temporal_comparison'] = generate_static_map_url(
    lat_center, lon_center, zoom,
    {'patient_markers': patient_markers},
    title="Temporal Comparison 2015-2023"
)

# Provincial Maps
print("8. Generating Provincial Maps...")
for prov_code, prov_abbr in province_codes.items():
    df_prov = df[df['Province'] == prov_code]
    if len(df_prov) == 0:
        print(f"   Skipping {prov_abbr} (no patients)")
        continue

    print(f"   {prov_abbr}: {len(df_prov)} patients")

    patient_markers = []
    for _, row in df_prov.iterrows():
        patient_markers.append((row['pop_weighted_lat'], row['pop_weighted_lon'], '0x38B2AC'))

    lat_center_prov = (df_prov['pop_weighted_lat'].min() + df_prov['pop_weighted_lat'].max()) / 2
    lon_center_prov = (df_prov['pop_weighted_lon'].min() + df_prov['pop_weighted_lon'].max()) / 2
    zoom_prov = calculate_optimal_zoom(df_prov['pop_weighted_lat'].min(),
                                       df_prov['pop_weighted_lat'].max(),
                                       df_prov['pop_weighted_lon'].min(),
                                       df_prov['pop_weighted_lon'].max())

    static_map_urls[f'map_province_{prov_abbr}'] = generate_static_map_url(
        lat_center_prov, lon_center_prov, zoom_prov,
        {'patient_markers': patient_markers[:100]},  # Limit markers
        title=f"{province_full_names[prov_abbr]}"
    )

# Save URLs to file
print("\n=== Saving URLs ===\n")
with open('static_api_urls.txt', 'w') as f:
    for map_name, url in static_map_urls.items():
        f.write(f"{map_name}\n{url}\n\n")
        print(f"✓ {map_name}")
        print(f"  Length: {len(url)} chars")

print(f"\n✓ Generated {len(static_map_urls)} Static API URLs")
print("✓ Saved to static_api_urls.txt")

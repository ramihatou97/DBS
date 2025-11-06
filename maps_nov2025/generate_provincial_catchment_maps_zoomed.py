#!/usr/bin/env python3
"""
Generate Province-by-Province Catchment Maps
Each map shows ONLY patients who underwent DBS in that province's centers
Properly zoomed to show full province without truncation
"""

import pandas as pd
import json
import numpy as np
from math import radians, cos, sin, asin, sqrt

BASE_DIR = '/Users/ramihatoum/Desktop/PPA/maps/final'
PATIENT_DATA_PATH = f'{BASE_DIR}/Final_database_05_11_25_FINAL.xlsx'
FSA_AGG_PATH = f'{BASE_DIR}/fsa_aggregated_data_current.csv'
OUTPUT_DIR = f'{BASE_DIR}/maps_nov2025'

# Load data
print("Loading patient database and FSA coordinates...")
patients = pd.read_excel(PATIENT_DATA_PATH)
coords = pd.read_csv(FSA_AGG_PATH)
coords = coords[['FSA', 'latitude', 'longitude']]

# Handle Nunavut coordinates
FSA_COORD_OVERRIDES = {
    'X0X': {'latitude': 63.7467, 'longitude': -68.5170},
    'X0A': {'latitude': 66.3200, 'longitude': -73.2822}
}

for fsa, coords_override in FSA_COORD_OVERRIDES.items():
    if fsa in coords['FSA'].values:
        coords.loc[coords['FSA'] == fsa, 'latitude'] = coords_override['latitude']
        coords.loc[coords['FSA'] == fsa, 'longitude'] = coords_override['longitude']
    else:
        new_row = pd.DataFrame([{'FSA': fsa, 'latitude': coords_override['latitude'], 'longitude': coords_override['longitude']}])
        coords = pd.concat([coords, new_row], ignore_index=True)

print(f"  ✓ Loaded {len(patients)} patients")
print(f"  ✓ Loaded {len(coords)} FSA coordinates")

# SiteID to Center mapping
SITE_ID_MAP = {
    12.0: 'Halifax', 13.0: 'Montreal', 14.0: 'Ottawa',
    16.0: 'Toronto', 17.0: 'London', 18.0: 'Winnipeg',
    19.0: 'Saskatoon', 20.0: 'Calgary', 21.0: 'Edmonton', 22.0: 'Vancouver'
}

# DBS Centers with coordinates
DBS_CENTERS = {
    'Halifax': {'lat': 44.6488, 'lon': -63.5752, 'province': 'Nova Scotia', 'site_ids': [12.0]},
    'Montreal': {'lat': 45.5017, 'lon': -73.5673, 'province': 'Quebec', 'site_ids': [13.0]},
    'Ottawa': {'lat': 45.4215, 'lon': -75.6972, 'province': 'Ontario/Quebec', 'site_ids': [14.0]},
    'Toronto': {'lat': 43.6532, 'lon': -79.3832, 'province': 'Ontario', 'site_ids': [16.0]},
    'London': {'lat': 43.0109, 'lon': -81.2733, 'province': 'Ontario', 'site_ids': [17.0]},
    'Winnipeg': {'lat': 49.8951, 'lon': -97.1384, 'province': 'Manitoba', 'site_ids': [18.0]},
    'Saskatoon': {'lat': 52.1332, 'lon': -106.6700, 'province': 'Saskatchewan', 'site_ids': [19.0]},
    'Calgary': {'lat': 51.0447, 'lon': -114.0719, 'province': 'Alberta', 'site_ids': [20.0]},
    'Edmonton': {'lat': 53.5461, 'lon': -113.4938, 'province': 'Alberta', 'site_ids': [21.0]},
    'Vancouver': {'lat': 49.2827, 'lon': -123.1207, 'province': 'British Columbia', 'site_ids': [22.0]}
}

# Provincial groupings with proper zoom/center
PROVINCIAL_GROUPS = {
    'Nova_Scotia': {
        'name': 'Nova Scotia',
        'centers': ['Halifax'],
        'site_ids': [12.0],
        'center_lat': 45.0, 'center_lng': -63.0, 'zoom': 6.5,
        'color': '#3b82f6'  # Blue
    },
    'Quebec': {
        'name': 'Quebec',
        'centers': ['Montreal', 'Ottawa'],  # Ottawa serves Quebec too
        'site_ids': [13.0, 14.0],
        'center_lat': 48.0, 'center_lng': -71.0, 'zoom': 5.5,
        'color': '#8b5cf6'  # Purple
    },
    'Ontario': {
        'name': 'Ontario',
        'centers': ['Ottawa', 'Toronto', 'London'],
        'site_ids': [14.0, 16.0, 17.0],
        'center_lat': 47.0, 'center_lng': -82.0, 'zoom': 5.5,
        'color': '#10b981'  # Emerald
    },
    'Manitoba': {
        'name': 'Manitoba',
        'centers': ['Winnipeg'],
        'site_ids': [18.0],
        'center_lat': 54.0, 'center_lng': -98.0, 'zoom': 5.5,
        'color': '#f59e0b'  # Amber
    },
    'Saskatchewan': {
        'name': 'Saskatchewan',
        'centers': ['Saskatoon'],
        'site_ids': [19.0],
        'center_lat': 54.0, 'center_lng': -106.0, 'zoom': 5.5,
        'color': '#f97316'  # Orange
    },
    'Alberta': {
        'name': 'Alberta',
        'centers': ['Calgary', 'Edmonton'],
        'site_ids': [20.0, 21.0],
        'center_lat': 54.0, 'center_lng': -115.0, 'zoom': 5.8,
        'color': '#ef4444'  # Red
    },
    'British_Columbia': {
        'name': 'British Columbia',
        'centers': ['Vancouver'],
        'site_ids': [22.0],
        'center_lat': 54.0, 'center_lng': -125.0, 'zoom': 5.2,
        'color': '#06b6d4'  # Cyan
    }
}

# Prepare patient data
patients = patients[patients['FSA'].notna()]
patients = patients[patients['SiteID'].notna()]
patients['DBS_Center'] = patients['SiteID'].map(SITE_ID_MAP)
patients = patients[patients['DBS_Center'].notna()]
patients = patients.rename(columns={'Driving Distance (km)': 'Distance_km', 'ORYear': 'Year'})

# Merge with coordinates
patients = patients.merge(coords, left_on='FSA', right_on='FSA', how='left')
patients = patients[patients['latitude'].notna()]

# Add jittered positions
np.random.seed(42)
patients['jitter_lat'] = patients['latitude'] + np.random.uniform(-0.03, 0.03, len(patients))
patients['jitter_lng'] = patients['longitude'] + np.random.uniform(-0.05, 0.05, len(patients))

print(f"  ✓ Prepared {len(patients)} patients with coordinates\n")

# Generate map for each province
for province_key, prov_info in PROVINCIAL_GROUPS.items():
    print(f"Generating map for {prov_info['name']}...")

    # Filter patients who went to THIS province's centers
    prov_patients = patients[patients['SiteID'].isin(prov_info['site_ids'])]

    if len(prov_patients) == 0:
        print(f"  ⚠ No patients found for {prov_info['name']}, skipping...")
        continue

    # Prepare flow data
    flows_data = []
    for _, patient in prov_patients.iterrows():
        center_name = patient['DBS_Center']
        if center_name in DBS_CENTERS:
            center = DBS_CENTERS[center_name]
            distance = patient.get('Distance_km', 0)

            # Calculate distance if missing
            if pd.isna(distance) or distance == 0:
                lat1, lon1 = patient['jitter_lat'], patient['jitter_lng']
                lat2, lon2 = center['lat'], center['lon']
                lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
                dlon = lon2 - lon1
                dlat = lat2 - lat1
                a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
                c = 2 * asin(sqrt(a))
                distance = 6371 * c

            # Line styling
            if distance < 100:
                weight = 1.0
                opacity = 0.35
            elif distance < 200:
                weight = 1.2
                opacity = 0.45
            elif distance < 300:
                weight = 1.5
                opacity = 0.55
            else:
                weight = 2.0
                opacity = 0.7

            flows_data.append({
                'from_lat': float(patient['jitter_lat']),
                'from_lng': float(patient['jitter_lng']),
                'to_lat': center['lat'],
                'to_lng': center['lon'],
                'distance': round(distance, 1),
                'fsa': patient['FSA'],
                'center': center_name,
                'color': prov_info['color'],
                'weight': weight,
                'opacity': opacity
            })

    # Get province centers for this map
    prov_centers = [DBS_CENTERS[c] for c in prov_info['centers']]

    print(f"  ✓ {len(flows_data)} patient flows to {len(prov_centers)} center(s)")

    # Generate HTML
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{prov_info['name']} - DBS Catchment</title>
    <script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyBH_yuU7_TfAJmuf_h04UsmKKhC0XPWerA"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Inter', sans-serif; background: #f8fafc; overflow: hidden; }}
        #map {{ width: 100%; height: 100vh; }}

        .info-panel {{
            position: absolute; top: 16px; left: 16px; background: rgba(255, 255, 255, 0.97);
            padding: 16px 20px; border-radius: 10px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            max-width: 280px; z-index: 1000; border: 1px solid #e2e8f0;
        }}

        .info-title {{
            font-size: 15px; font-weight: 600; color: #1e293b; margin-bottom: 8px;
            letter-spacing: -0.02em;
        }}

        .info-stat {{
            font-size: 11px; color: #64748b; line-height: 1.6;
        }}

        .stat-value {{
            font-weight: 600; color: {prov_info['color']};
        }}
    </style>
</head>
<body>
    <div class="info-panel">
        <div class="info-title">{prov_info['name']} DBS Catchment</div>
        <div class="info-stat">
            <span class="stat-value">{len(flows_data)} patients</span> traveled to {len(prov_centers)} DBS center{'s' if len(prov_centers) > 1 else ''} in this province/region.
        </div>
    </div>

    <div id="map"></div>

    <script>
        const flowsData = {json.dumps(flows_data)};
        const centers = {json.dumps(prov_centers)};

        function initMap() {{
            const map = new google.maps.Map(document.getElementById('map'), {{
                center: {{ lat: {prov_info['center_lat']}, lng: {prov_info['center_lng']} }},
                zoom: {prov_info['zoom']},
                mapTypeId: 'terrain',
                styles: [
                    {{ featureType: 'administrative.province', elementType: 'geometry.stroke',
                       stylers: [{{ color: '#1e293b' }}, {{ weight: 2.5 }}] }},
                    {{ featureType: 'water', elementType: 'geometry', stylers: [{{ color: '#dbeafe' }}] }},
                    {{ featureType: 'landscape', elementType: 'geometry', stylers: [{{ color: '#f8fafc' }}] }},
                    {{ featureType: 'poi', stylers: [{{ visibility: 'off' }}] }},
                    {{ featureType: 'road', elementType: 'labels', stylers: [{{ visibility: 'off' }}] }}
                ],
                zoomControl: true,
                mapTypeControl: false,
                streetViewControl: false,
                fullscreenControl: true
            }});

            // Add DBS centers
            centers.forEach(center => {{
                new google.maps.Marker({{
                    position: {{ lat: center.lat, lng: center.lon }},
                    map: map,
                    icon: {{
                        path: google.maps.SymbolPath.CIRCLE,
                        scale: 8,
                        fillColor: '{prov_info['color']}',
                        fillOpacity: 1,
                        strokeColor: 'white',
                        strokeWeight: 3
                    }},
                    title: 'DBS Center',
                    zIndex: 1000
                }});
            }});

            // Draw patient flows
            flowsData.forEach(flow => {{
                const arrowScale = flow.distance > 300 ? 4.0 : 3.0;

                const lineSymbol = {{
                    path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW,
                    scale: arrowScale,
                    strokeColor: flow.color,
                    fillColor: flow.color,
                    fillOpacity: 1
                }};

                new google.maps.Polyline({{
                    path: [
                        {{ lat: flow.from_lat, lng: flow.from_lng }},
                        {{ lat: flow.to_lat, lng: flow.to_lng }}
                    ],
                    geodesic: true,
                    strokeColor: flow.color,
                    strokeOpacity: flow.opacity,
                    strokeWeight: flow.weight,
                    icons: [{{
                        icon: lineSymbol,
                        offset: '65%'
                    }}],
                    map: map
                }});

                // Patient origin marker
                new google.maps.Marker({{
                    position: {{ lat: flow.from_lat, lng: flow.from_lng }},
                    map: map,
                    icon: {{
                        path: google.maps.SymbolPath.CIRCLE,
                        scale: 2.5,
                        fillColor: flow.color,
                        fillOpacity: 0.7,
                        strokeColor: 'white',
                        strokeWeight: 0.5
                    }},
                    zIndex: 10
                }});
            }});
        }}

        window.onload = initMap;
    </script>
</body>
</html>'''

    # Save
    output_path = f'{OUTPUT_DIR}/map_catchment_{province_key.lower()}.html'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"  ✅ Generated: {output_path}\n")

print("✅ All provincial catchment maps generated!")
print(f"\nFeatures:")
print(f"  ✓ Province-specific zoom (no truncation)")
print(f"  ✓ Only patients who went to centers IN that province")
print(f"  ✓ Clear province borders (weight: 2.5)")
print(f"  ✓ Lighter flow lines (1.0-2.0px)")
print(f"  ✓ Province-specific colors")
print(f"  ✓ Patient origin markers")
print(f"  ✓ Larger arrows (3.0-4.0 scale)")

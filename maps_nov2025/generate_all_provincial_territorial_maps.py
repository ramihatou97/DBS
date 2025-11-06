#!/usr/bin/env python3
"""
Generate Comprehensive Provincial/Territorial Maps - ALL 13 Jurisdictions
Shows patient INFLOW to DBS centers from across Canada
Includes provinces/territories WITHOUT DBS centers (showing OUTFLOW)
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

# DBS Centers
DBS_CENTERS = {
    'Halifax': {'lat': 44.6488, 'lon': -63.5752},
    'Montreal': {'lat': 45.5017, 'lon': -73.5673},
    'Ottawa': {'lat': 45.4215, 'lon': -75.6972},
    'Toronto': {'lat': 43.6532, 'lon': -79.3832},
    'London': {'lat': 43.0109, 'lon': -81.2733},
    'Winnipeg': {'lat': 49.8951, 'lon': -97.1384},
    'Saskatoon': {'lat': 52.1332, 'lon': -106.6700},
    'Calgary': {'lat': 51.0447, 'lon': -114.0719},
    'Edmonton': {'lat': 53.5461, 'lon': -113.4938},
    'Vancouver': {'lat': 49.2827, 'lon': -123.1207}
}

# Province code mapping
PROVINCE_CODE_MAP = {
    1.0: 'NL', 2.0: 'NS', 3.0: 'PE', 4.0: 'NB', 5.0: 'QC',
    6.0: 'ON', 7.0: 'MB', 8.0: 'SK', 9.0: 'AB', 10.0: 'BC',
    11.0: 'YT', 12.0: 'NT', 13.0: 'NU'
}

# ALL 13 Province/Territory Configurations
# For provinces WITH centers: show patients coming IN
# For provinces WITHOUT centers: show patients going OUT
ALL_JURISDICTIONS = {
    'Newfoundland_Labrador': {
        'name': 'Newfoundland and Labrador',
        'code': 1.0,
        'has_center': False,
        'center_lat': 53.0, 'center_lng': -60.0, 'zoom': 5.0,
        'color': '#ef4444',
        'description': 'No DBS center - patients travel to other provinces'
    },
    'Nova_Scotia': {
        'name': 'Nova Scotia',
        'code': 2.0,
        'has_center': True,
        'centers': ['Halifax'],
        'site_ids': [12.0],
        'center_lat': 45.0, 'center_lng': -63.0, 'zoom': 6.5,
        'color': '#3b82f6',
        'description': 'Halifax DBS Center serving Atlantic region'
    },
    'Prince_Edward_Island': {
        'name': 'Prince Edward Island',
        'code': 3.0,
        'has_center': False,
        'center_lat': 46.5, 'center_lng': -63.5, 'zoom': 7.5,
        'color': '#f97316',
        'description': 'No DBS center - patients travel primarily to Halifax'
    },
    'New_Brunswick': {
        'name': 'New Brunswick',
        'code': 4.0,
        'has_center': False,
        'center_lat': 46.5, 'center_lng': -66.0, 'zoom': 6.5,
        'color': '#f59e0b',
        'description': 'No DBS center - patients travel to Halifax and Quebec'
    },
    'Quebec': {
        'name': 'Quebec',
        'code': 5.0,
        'has_center': True,
        'centers': ['Montreal', 'Ottawa'],
        'site_ids': [13.0, 14.0],
        'center_lat': 48.0, 'center_lng': -71.0, 'zoom': 5.5,
        'color': '#8b5cf6',
        'description': 'Montreal and Ottawa DBS Centers'
    },
    'Ontario': {
        'name': 'Ontario',
        'code': 6.0,
        'has_center': True,
        'centers': ['Ottawa', 'Toronto', 'London'],
        'site_ids': [14.0, 16.0, 17.0],
        'center_lat': 47.0, 'center_lng': -82.0, 'zoom': 5.5,
        'color': '#10b981',
        'description': 'Ottawa, Toronto, and London DBS Centers'
    },
    'Manitoba': {
        'name': 'Manitoba',
        'code': 7.0,
        'has_center': True,
        'centers': ['Winnipeg'],
        'site_ids': [18.0],
        'center_lat': 54.0, 'center_lng': -98.0, 'zoom': 5.5,
        'color': '#f59e0b',
        'description': 'Winnipeg DBS Center'
    },
    'Saskatchewan': {
        'name': 'Saskatchewan',
        'code': 8.0,
        'has_center': True,
        'centers': ['Saskatoon'],
        'site_ids': [19.0],
        'center_lat': 54.0, 'center_lng': -106.0, 'zoom': 5.5,
        'color': '#f97316',
        'description': 'Saskatoon DBS Center'
    },
    'Alberta': {
        'name': 'Alberta',
        'code': 9.0,
        'has_center': True,
        'centers': ['Calgary', 'Edmonton'],
        'site_ids': [20.0, 21.0],
        'center_lat': 54.0, 'center_lng': -115.0, 'zoom': 5.8,
        'color': '#ef4444',
        'description': 'Calgary and Edmonton DBS Centers'
    },
    'British_Columbia': {
        'name': 'British Columbia',
        'code': 10.0,
        'has_center': True,
        'centers': ['Vancouver'],
        'site_ids': [22.0],
        'center_lat': 54.0, 'center_lng': -125.0, 'zoom': 5.2,
        'color': '#06b6d4',
        'description': 'Vancouver DBS Center'
    },
    'Yukon': {
        'name': 'Yukon',
        'code': 11.0,
        'has_center': False,
        'center_lat': 62.0, 'center_lng': -135.0, 'zoom': 5.0,
        'color': '#ec4899',
        'description': 'No DBS center - no patients in current dataset'
    },
    'Northwest_Territories': {
        'name': 'Northwest Territories',
        'code': 12.0,
        'has_center': False,
        'center_lat': 64.0, 'center_lng': -115.0, 'zoom': 4.5,
        'color': '#a855f7',
        'description': 'No DBS center - no patients in current dataset'
    },
    'Nunavut': {
        'name': 'Nunavut',
        'code': 13.0,
        'has_center': False,
        'center_lat': 70.0, 'center_lng': -85.0, 'zoom': 3.8,
        'color': '#ec4899',
        'description': 'No DBS center - patients travel extreme distances'
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

# Generate map for each province/territory
for jurisdiction_key, juris_info in ALL_JURISDICTIONS.items():
    print(f"Generating map for {juris_info['name']}...")

    if juris_info['has_center']:
        # INFLOW: Show patients coming TO this province's centers
        prov_patients = patients[patients['SiteID'].isin(juris_info['site_ids'])]
        map_type = 'inflow'
    else:
        # OUTFLOW: Show patients FROM this province going elsewhere
        prov_patients = patients[patients['Province'] == juris_info['code']]
        map_type = 'outflow'

    if len(prov_patients) == 0:
        print(f"  ⚠ No patients found for {juris_info['name']}")
        # Still create map with message
        patient_message = "No patients in current dataset (2019-2023)"
    else:
        patient_message = f"{len(prov_patients)} patient{'s' if len(prov_patients) != 1 else ''}"

    # Prepare flow data
    flows_data = []
    centers_in_map = []

    if len(prov_patients) > 0:
        for _, patient in prov_patients.iterrows():
            center_name = patient['DBS_Center']
            if center_name in DBS_CENTERS:
                center = DBS_CENTERS[center_name]

                # Track which centers to display
                if center not in centers_in_map:
                    centers_in_map.append({'name': center_name, **center})

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

                # Line styling - lighter for long distances to avoid truncation appearance
                if distance < 100:
                    weight = 1.0
                    opacity = 0.4
                elif distance < 300:
                    weight = 1.3
                    opacity = 0.5
                elif distance < 1000:
                    weight = 1.8
                    opacity = 0.6
                else:
                    weight = 2.5  # Very long distances
                    opacity = 0.75

                flows_data.append({
                    'from_lat': float(patient['jitter_lat']),
                    'from_lng': float(patient['jitter_lng']),
                    'to_lat': center['lat'],
                    'to_lng': center['lon'],
                    'distance': round(distance, 1),
                    'fsa': patient['FSA'],
                    'center': center_name,
                    'color': juris_info['color'],
                    'weight': weight,
                    'opacity': opacity
                })

    print(f"  ✓ {len(flows_data)} patient flow{'s' if len(flows_data) != 1 else ''}")
    print(f"  ✓ Type: {map_type.upper()}")

    # Generate HTML
    map_title = f"{juris_info['name']}"
    if juris_info['has_center']:
        subtitle = f"Catchment Area: {patient_message}"
    else:
        subtitle = f"Patient Outflow: {patient_message}"

    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{map_title}</title>
    <script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyBH_yuU7_TfAJmuf_h04UsmKKhC0XPWerA"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Inter', sans-serif; background: #f8fafc; overflow: hidden; }}
        #map {{ width: 100%; height: 100vh; }}

        .info-panel {{
            position: absolute; top: 16px; left: 16px; background: rgba(255, 255, 255, 0.97);
            padding: 16px 20px; border-radius: 10px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            max-width: 320px; z-index: 1000; border: 1px solid #e2e8f0;
            border-left: 4px solid {juris_info['color']};
        }}

        .info-title {{
            font-size: 15px; font-weight: 600; color: #1e293b; margin-bottom: 6px;
            letter-spacing: -0.02em;
        }}

        .info-subtitle {{
            font-size: 12px; color: #64748b; margin-bottom: 8px; font-weight: 500;
        }}

        .info-description {{
            font-size: 11px; color: #64748b; line-height: 1.6;
        }}
    </style>
</head>
<body>
    <div class="info-panel">
        <div class="info-title">{map_title}</div>
        <div class="info-subtitle">{subtitle}</div>
        <div class="info-description">{juris_info['description']}</div>
    </div>

    <div id="map"></div>

    <script>
        const flowsData = {json.dumps(flows_data)};
        const centers = {json.dumps(centers_in_map)};

        function initMap() {{
            const map = new google.maps.Map(document.getElementById('map'), {{
                center: {{ lat: {juris_info['center_lat']}, lng: {juris_info['center_lng']} }},
                zoom: {juris_info['zoom']},
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
                        fillColor: '{juris_info['color']}',
                        fillOpacity: 1,
                        strokeColor: 'white',
                        strokeWeight: 3
                    }},
                    title: center.name,
                    zIndex: 1000
                }});
            }});

            // Draw patient flows
            flowsData.forEach(flow => {{
                const arrowScale = flow.distance > 1000 ? 4.5 : (flow.distance > 500 ? 4.0 : 3.5);

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
    filename_safe = jurisdiction_key.lower()
    output_path = f'{OUTPUT_DIR}/map_province_{filename_safe}.html'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"  ✅ Generated: {output_path}\n")

print("=" * 80)
print("✅ ALL 13 PROVINCIAL/TERRITORIAL MAPS GENERATED!")
print("=" * 80)
print("\nSummary:")
print("  ✓ Provinces WITH DBS centers: 7 maps (INFLOW)")
print("  ✓ Provinces WITHOUT DBS centers: 6 maps (OUTFLOW)")
print("  ✓ All flow lines adjusted to avoid truncation")
print("  ✓ Province borders clearly marked (weight: 2.5)")
print("  ✓ Appropriate zoom for each jurisdiction")

#!/usr/bin/env python3
"""
Generate province-specific catchment area maps
Shows patients from inside AND outside each province flowing to DBS centers in that province
Distance-adjusted flow lines with jittered patient positions
"""

import pandas as pd
import json
import random
import math

BASE_DIR = '/Users/ramihatoum/Desktop/PPA/maps/final'
DB_PATH = f'{BASE_DIR}/Final_database_05_11_25_COMPLETE.xlsx'
FSA_COORD_PATH = f'{BASE_DIR}/fsa_coordinates_canada.csv'
OUTPUT_DIR = f'{BASE_DIR}/maps_nov2025/provincial_catchment'

import os
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load data
print("Loading patient database...")
df = pd.read_excel(DB_PATH)
df = df.dropna(subset=['Province', 'FSA', 'SiteID'])
print(f"  ✓ Loaded {len(df)} patients with complete data")

# Load FSA coordinates
print("Loading FSA coordinates...")
fsa_coords = pd.read_csv(FSA_COORD_PATH)
fsa_coords = fsa_coords.rename(columns={
    'fsa_code': 'FSA',
    'pop_weighted_lat': 'latitude',
    'pop_weighted_lon': 'longitude'
})
print(f"  ✓ Loaded {len(fsa_coords)} FSA coordinates")

# Province mappings
PROVINCE_CODES = {
    1.0: 'Newfoundland and Labrador',
    2.0: 'Nova Scotia',
    3.0: 'Prince Edward Island',
    4.0: 'New Brunswick',
    5.0: 'Quebec',
    6.0: 'Ontario',
    7.0: 'Manitoba',
    8.0: 'Saskatchewan',
    9.0: 'Alberta',
    10.0: 'British Columbia',
    11.0: 'Yukon',
    12.0: 'Northwest Territories',
    13.0: 'Nunavut'
}

# DBS Centers with coordinates
DBS_CENTERS = {
    12: {'name': 'QEII Health Sciences Centre, Halifax', 'lat': 44.6382, 'lon': -63.5793, 'province': 2.0},
    13: {'name': 'Ottawa Hospital', 'lat': 45.4112, 'lon': -75.6981, 'province': 6.0},
    14: {'name': 'London Health Sciences Centre', 'lat': 43.0096, 'lon': -81.2737, 'province': 6.0},
    16: {'name': 'Toronto Western Hospital', 'lat': 43.6532, 'lon': -79.3832, 'province': 6.0},
    17: {'name': 'University of Alberta Hospital', 'lat': 53.5232, 'lon': -113.5263, 'province': 9.0},
    18: {'name': 'Calgary Foothills Medical Centre', 'lat': 51.0643, 'lon': -114.1325, 'province': 9.0},
    19: {'name': 'Centre Hospitalier Universitaire de Sherbrooke', 'lat': 45.3781, 'lon': -71.9242, 'province': 5.0},
    20: {'name': 'Centre Hospitalier de l\'Université de Montréal', 'lat': 45.5089, 'lon': -73.5617, 'province': 5.0},
    21: {'name': 'CHU de Québec', 'lat': 46.7787, 'lon': -71.2854, 'province': 5.0},
    22: {'name': 'Royal University Hospital, Saskatoon', 'lat': 52.1324, 'lon': -106.6344, 'province': 8.0}
}

# Calm colors
CALM = {
    'in_province': '#6ee7b7',     # Soft green - patients from same province
    'out_province': '#fdba74',    # Soft orange - patients from other provinces
    'center': '#3b82f6',          # Blue - DBS center
    'border': '#cbd5e1',
    'text': '#475569'
}

def jitter_coordinate(lat, lng, radius_km=5):
    """Add random offset to coordinates within radius_km"""
    # Convert km to degrees (rough approximation)
    offset_degrees = radius_km / 111.0  # 1 degree ≈ 111 km

    # Random angle and distance
    angle = random.uniform(0, 2 * math.pi)
    distance = random.uniform(0, offset_degrees)

    # Apply offset
    lat_offset = distance * math.cos(angle)
    lng_offset = distance * math.sin(angle)

    return lat + lat_offset, lng + lng_offset

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance in km between two coordinates"""
    from math import radians, cos, sin, asin, sqrt

    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    km = 6371 * c
    return km

# Identify provinces with DBS centers
provinces_with_centers = set([center['province'] for center in DBS_CENTERS.values()])
print(f"\n  ✓ Found {len(provinces_with_centers)} provinces with DBS centers")

# Generate maps for each province with centers
for prov_code in sorted(provinces_with_centers):
    prov_name = PROVINCE_CODES[prov_code]
    print(f"\n{'='*80}")
    print(f"Generating catchment map for {prov_name} (Province {int(prov_code)})")
    print(f"{'='*80}")

    # Get DBS centers in this province
    province_centers = {site_id: info for site_id, info in DBS_CENTERS.items()
                       if info['province'] == prov_code}

    print(f"  Centers in province: {len(province_centers)}")
    for site_id, info in province_centers.items():
        center_patients = len(df[df['SiteID'] == site_id])
        print(f"    - SiteID {site_id}: {info['name']} ({center_patients} patients)")

    # Get all patients going to centers in this province
    site_ids = list(province_centers.keys())
    province_patients = df[df['SiteID'].isin(site_ids)].copy()

    # Classify as in-province or out-of-province
    province_patients['is_in_province'] = province_patients['Province'] == prov_code

    in_province_count = province_patients['is_in_province'].sum()
    out_province_count = (~province_patients['is_in_province']).sum()

    print(f"  Total patients: {len(province_patients)}")
    print(f"    - From within {prov_name}: {in_province_count}")
    print(f"    - From other provinces: {out_province_count}")

    # Merge with coordinates and create jittered positions
    province_patients = province_patients.merge(
        fsa_coords[['FSA', 'latitude', 'longitude']],
        on='FSA',
        how='left'
    )

    # Apply jittering
    jittered_data = []
    for idx, row in province_patients.iterrows():
        if pd.notna(row['latitude']) and pd.notna(row['longitude']):
            # Get destination center
            site_id = int(row['SiteID'])
            if site_id in DBS_CENTERS:
                center_info = DBS_CENTERS[site_id]

                # Jitter patient origin
                jit_lat, jit_lng = jitter_coordinate(
                    row['latitude'],
                    row['longitude'],
                    radius_km=3  # Smaller jitter for cleaner look
                )

                # Calculate distance
                distance = calculate_distance(
                    jit_lat, jit_lng,
                    center_info['lat'], center_info['lon']
                )

                # Determine line styling based on distance
                if distance < 100:
                    line_weight = 0.5
                    line_opacity = 0.3
                elif distance < 300:
                    line_weight = 1.0
                    line_opacity = 0.4
                elif distance < 600:
                    line_weight = 1.5
                    line_opacity = 0.5
                else:
                    line_weight = 2.0
                    line_opacity = 0.6

                jittered_data.append({
                    'from_lat': jit_lat,
                    'from_lng': jit_lng,
                    'to_lat': center_info['lat'],
                    'to_lng': center_info['lon'],
                    'center_name': center_info['name'],
                    'patient_fsa': row['FSA'],
                    'patient_province': PROVINCE_CODES.get(row['Province'], 'Unknown'),
                    'is_in_province': bool(row['is_in_province']),
                    'distance_km': round(distance, 1),
                    'color': CALM['in_province'] if row['is_in_province'] else CALM['out_province'],
                    'line_weight': line_weight,
                    'line_opacity': line_opacity,
                    'marker_size': 5 if row['is_in_province'] else 6
                })

    print(f"  ✓ Prepared {len(jittered_data)} jittered patient flows")

    # Determine map center and zoom
    if prov_code == 6.0:  # Ontario - larger area
        map_center = {'lat': 46.0, 'lng': -81.0}
        map_zoom = 5.5
    elif prov_code == 5.0:  # Quebec - larger area
        map_center = {'lat': 48.0, 'lng': -71.0}
        map_zoom = 5.5
    elif prov_code == 9.0:  # Alberta
        map_center = {'lat': 53.5, 'lng': -114.0}
        map_zoom = 6
    elif prov_code == 2.0:  # Nova Scotia
        map_center = {'lat': 45.0, 'lng': -63.0}
        map_zoom = 7
    elif prov_code == 8.0:  # Saskatchewan
        map_center = {'lat': 52.5, 'lng': -106.5}
        map_zoom = 6
    else:
        map_center = {'lat': 55.0, 'lng': -95.0}
        map_zoom = 5

    # Generate HTML
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{prov_name} - DBS Catchment Area</title>
    <script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyBH_yuU7_TfAJmuf_h04UsmKKhC0XPWerA"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Inter', sans-serif; background: #f8fafc; overflow: hidden; }}
        #map {{ width: 100%; height: 100vh; }}
        .info-panel {{
            position: absolute; top: 16px; left: 16px; background: rgba(255, 255, 255, 0.96);
            padding: 16px 20px; border-radius: 8px; box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
            max-width: 300px; z-index: 1000; border: 1px solid {CALM['border']};
        }}
        .info-title {{ font-size: 15px; font-weight: 600; color: #1e293b; margin-bottom: 8px; }}
        .info-stats {{ font-size: 11px; color: {CALM['text']}; line-height: 1.6; }}
        .stat-row {{ display: flex; justify-content: space-between; margin-bottom: 4px; }}
        .legend {{
            position: absolute; bottom: 20px; right: 20px; background: rgba(255, 255, 255, 0.96);
            padding: 14px 16px; border-radius: 8px; box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
            z-index: 1000; border: 1px solid {CALM['border']};
        }}
        .legend-title {{ font-size: 11px; font-weight: 600; color: #1e293b; margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.03em; }}
        .legend-item {{ display: flex; align-items: center; gap: 7px; margin-bottom: 3px; font-size: 10px; color: {CALM['text']}; }}
        .legend-color {{ width: 14px; height: 14px; border-radius: 50%; border: 1px solid rgba(0,0,0,0.1); }}
    </style>
</head>
<body>
    <div class="info-panel">
        <div class="info-title">{prov_name} DBS Catchment</div>
        <div class="info-stats">
            <div class="stat-row"><span>Total Patients:</span><strong>{len(jittered_data)}</strong></div>
            <div class="stat-row"><span>From {prov_name}:</span><strong>{in_province_count}</strong></div>
            <div class="stat-row"><span>From Other Provinces:</span><strong>{out_province_count}</strong></div>
            <div class="stat-row"><span>DBS Centers:</span><strong>{len(province_centers)}</strong></div>
        </div>
    </div>

    <div id="map"></div>

    <div class="legend">
        <div class="legend-title">Patient Origin</div>
        <div class="legend-item">
            <div class="legend-color" style="background:{CALM['in_province']}"></div>
            <span>Within province</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background:{CALM['out_province']}"></div>
            <span>Other provinces</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background:{CALM['center']}"></div>
            <span>DBS Center</span>
        </div>
    </div>

    <script>
        const flowData = {json.dumps(jittered_data)};
        const centers = {json.dumps([{'name': info['name'], 'lat': info['lat'], 'lon': info['lon']} for info in province_centers.values()])};

        function initMap() {{
            const map = new google.maps.Map(document.getElementById('map'), {{
                center: {{ lat: {map_center['lat']}, lng: {map_center['lng']} }},
                zoom: {map_zoom},
                mapTypeId: 'terrain',
                styles: [
                    {{ featureType: 'administrative.province', elementType: 'geometry.stroke',
                       stylers: [{{ color: '{CALM['border']}' }}, {{ weight: 1.5 }}] }},
                    {{ featureType: 'water', elementType: 'geometry', stylers: [{{ color: '#dbeafe' }}] }},
                    {{ featureType: 'landscape', elementType: 'geometry', stylers: [{{ color: '#f1f5f9' }}] }},
                    {{ featureType: 'poi', stylers: [{{ visibility: 'off' }}] }},
                    {{ featureType: 'road', elementType: 'labels', stylers: [{{ visibility: 'off' }}] }}
                ],
                zoomControl: true, mapTypeControl: false, streetViewControl: false, fullscreenControl: true
            }});

            // Add DBS centers
            centers.forEach(center => {{
                new google.maps.Marker({{
                    position: {{ lat: center.lat, lng: center.lon }},
                    map: map,
                    icon: {{
                        path: google.maps.SymbolPath.CIRCLE,
                        scale: 10,
                        fillColor: '{CALM['center']}',
                        fillOpacity: 0.9,
                        strokeColor: 'white',
                        strokeWeight: 2.5
                    }},
                    title: center.name,
                    zIndex: 1000
                }});
            }});

            // Add patient flows
            flowData.forEach(flow => {{
                // Draw flow line
                new google.maps.Polyline({{
                    path: [
                        {{ lat: flow.from_lat, lng: flow.from_lng }},
                        {{ lat: flow.to_lat, lng: flow.to_lng }}
                    ],
                    geodesic: true,
                    strokeColor: flow.color,
                    strokeOpacity: flow.line_opacity,
                    strokeWeight: flow.line_weight,
                    map: map,
                    zIndex: 50
                }});

                // Draw patient marker
                const marker = new google.maps.Marker({{
                    position: {{ lat: flow.from_lat, lng: flow.from_lng }},
                    map: map,
                    icon: {{
                        path: google.maps.SymbolPath.CIRCLE,
                        scale: flow.marker_size,
                        fillColor: flow.color,
                        fillOpacity: 0.7,
                        strokeColor: 'white',
                        strokeWeight: 1
                    }},
                    zIndex: 100
                }});

                const infoWindow = new google.maps.InfoWindow({{
                    content: `
                        <div style="font-family: Inter, sans-serif; padding: 8px; min-width: 160px;">
                            <div style="font-size: 12px; font-weight: 600; color: #1e293b; margin-bottom: 6px;">
                                Patient from ${{flow.patient_fsa}}
                            </div>
                            <div style="font-size: 10px; color: {CALM['text']}; line-height: 1.6;">
                                <strong>Origin:</strong> ${{flow.patient_province}}<br>
                                <strong>Center:</strong> ${{flow.center_name}}<br>
                                <strong>Distance:</strong> ${{flow.distance_km}} km<br>
                                <strong>Type:</strong> ${{flow.is_in_province ? 'In-province' : 'Out-of-province'}}
                            </div>
                        </div>
                    `
                }});

                marker.addListener('click', () => {{
                    infoWindow.open(map, marker);
                }});
            }});
        }}

        window.onload = initMap;
    </script>
</body>
</html>'''

    # Save file
    filename = f"{prov_name.lower().replace(' ', '_')}_catchment.html"
    output_path = f'{OUTPUT_DIR}/{filename}'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"  ✅ Saved: {filename}")

print("\n" + "="*80)
print("✅ ALL PROVINCIAL CATCHMENT MAPS GENERATED")
print("="*80)
print(f"\nOutput directory: {OUTPUT_DIR}")
print(f"\nGenerated {len(provinces_with_centers)} provincial catchment maps")

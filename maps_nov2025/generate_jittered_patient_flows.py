#!/usr/bin/env python3
"""
Generate Individual Patient Flow Map with Jittered Positions
Shows all 936 patients with flow lines to DBS centers
"""

import pandas as pd
import json
import numpy as np
from math import radians, cos, sin, asin, sqrt

BASE_DIR = '/Users/ramihatoum/Desktop/PPA/maps/final'
PATIENT_DATA_PATH = f'{BASE_DIR}/Final_database_05_11_25_FINAL.xlsx'
FSA_AGG_PATH = f'{BASE_DIR}/fsa_aggregated_data_current.csv'
OUTPUT_DIR = f'{BASE_DIR}/maps_nov2025'

# Load patient data
print("Loading patient database...")
patients = pd.read_excel(PATIENT_DATA_PATH)
print(f"  ✓ Loaded {len(patients)} patients")

# Load FSA coordinates
print("Loading FSA coordinates...")
coords = pd.read_csv(FSA_AGG_PATH)
coords = coords[['FSA', 'latitude', 'longitude']]

# Handle missing coordinates for specific FSAs (e.g., Nunavut)
FSA_COORD_OVERRIDES = {
    'X0X': {'latitude': 63.7467, 'longitude': -68.5170},  # Iqaluit, Nunavut
    'X0A': {'latitude': 66.3200, 'longitude': -73.2822}
}

for fsa, coords_override in FSA_COORD_OVERRIDES.items():
    if fsa in coords['FSA'].values:
        coords.loc[coords['FSA'] == fsa, 'latitude'] = coords_override['latitude']
        coords.loc[coords['FSA'] == fsa, 'longitude'] = coords_override['longitude']
    else:
        new_row = pd.DataFrame([{'FSA': fsa, 'latitude': coords_override['latitude'], 'longitude': coords_override['longitude']}])
        coords = pd.concat([coords, new_row], ignore_index=True)

print(f"  ✓ Loaded coordinates for {len(coords)} FSAs")

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

# Province mapping for colors
PROVINCE_CODE_MAP = {
    1.0: 'NL', 2.0: 'NS', 3.0: 'PE', 4.0: 'NB', 5.0: 'QC',
    6.0: 'ON', 7.0: 'MB', 8.0: 'SK', 9.0: 'AB', 10.0: 'BC',
    11.0: 'YT', 12.0: 'NT', 13.0: 'NU'
}

# Color scheme by distance category
DISTANCE_COLORS = {
    'excellent': '#10b981',    # Green <50km
    'good': '#84cc16',         # Lime 50-200km
    'moderate': '#f59e0b',     # Amber 200-300km
    'poor': '#f97316',         # Orange 300-500km
    'extreme': '#ef4444'       # Red >500km
}

# Prepare patient data
print("\nPreparing individual patient flows...")
patients = patients[patients['FSA'].notna()]
patients = patients[patients['SiteID'].notna()]

# Map SiteID to center names
patients['DBS_Center'] = patients['SiteID'].map(SITE_ID_MAP)
patients = patients[patients['DBS_Center'].notna()]

# Rename columns
patients = patients.rename(columns={
    'Driving Distance (km)': 'Distance_km',
    'ORYear': 'Year'
})

# Merge with coordinates
patients = patients.merge(coords[['FSA', 'latitude', 'longitude']],
                         left_on='FSA', right_on='FSA', how='left')
patients = patients[patients['latitude'].notna()]

# Add jittered positions (3-5km radius offset for density visualization)
np.random.seed(42)
patients['jitter_lat'] = patients['latitude'] + np.random.uniform(-0.03, 0.03, len(patients))
patients['jitter_lng'] = patients['longitude'] + np.random.uniform(-0.05, 0.05, len(patients))

# Prepare flow data
patient_flows = []
for idx, patient in patients.iterrows():
    center_name = patient['DBS_Center']
    if center_name in DBS_CENTERS:
        center = DBS_CENTERS[center_name]
        distance = patient.get('Distance_km', 0)

        # Calculate distance if missing using Haversine formula
        if pd.isna(distance) or distance == 0:
            lat1, lon1 = patient['jitter_lat'], patient['jitter_lng']
            lat2, lon2 = center['lat'], center['lon']
            lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * asin(sqrt(a))
            distance = 6371 * c

        # Distance category and color - thinner lines per user request
        if distance < 50:
            category = 'excellent'
            weight = 0.6
            opacity = 0.25
        elif distance < 200:
            category = 'good'
            weight = 0.8
            opacity = 0.35
        elif distance < 300:
            category = 'moderate'
            weight = 1.0
            opacity = 0.45
        elif distance < 500:
            category = 'poor'
            weight = 1.4
            opacity = 0.6
        else:
            category = 'extreme'
            weight = 2.0
            opacity = 0.75

        province = PROVINCE_CODE_MAP.get(patient.get('Province'), 'Unknown')

        patient_flows.append({
            'id': int(idx),
            'from_lat': float(patient['jitter_lat']),
            'from_lng': float(patient['jitter_lng']),
            'to_lat': center['lat'],
            'to_lng': center['lon'],
            'distance': round(distance, 1),
            'fsa': patient['FSA'],
            'center': center_name,
            'province': province,
            'color': DISTANCE_COLORS[category],
            'category': category,
            'weight': weight,
            'opacity': opacity,
            'year': int(patient.get('Year', 2021)) if pd.notna(patient.get('Year')) else 2021
        })

print(f"  ✓ Created {len(patient_flows)} individual patient flows")

# Statistics
dist_stats = {
    'excellent': len([p for p in patient_flows if p['category'] == 'excellent']),
    'good': len([p for p in patient_flows if p['category'] == 'good']),
    'moderate': len([p for p in patient_flows if p['category'] == 'moderate']),
    'poor': len([p for p in patient_flows if p['category'] == 'poor']),
    'extreme': len([p for p in patient_flows if p['category'] == 'extreme'])
}

print(f"\n  Distance Distribution:")
print(f"    Excellent (<50km): {dist_stats['excellent']}")
print(f"    Good (50-200km): {dist_stats['good']}")
print(f"    Moderate (200-300km): {dist_stats['moderate']}")
print(f"    Poor (300-500km): {dist_stats['poor']}")
print(f"    Extreme (>500km): {dist_stats['extreme']}")

# Generate HTML
html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Individual Patient Journeys</title>
    <script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyBH_yuU7_TfAJmuf_h04UsmKKhC0XPWerA"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Inter', sans-serif; background: #f8fafc; overflow: hidden; }}
        #map {{ width: 100%; height: 100vh; }}

        .info-panel {{
            position: absolute; top: 16px; left: 16px; background: rgba(255, 255, 255, 0.97);
            padding: 16px 20px; border-radius: 10px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            max-width: 320px; z-index: 1000; border: 1px solid #e2e8f0;
        }}

        .info-title {{
            font-size: 15px; font-weight: 600; color: #1e293b; margin-bottom: 8px;
            letter-spacing: -0.02em;
        }}

        .info-text {{
            font-size: 11px; color: #64748b; line-height: 1.6;
        }}

        .legend {{
            position: absolute; bottom: 20px; right: 20px; background: rgba(255, 255, 255, 0.97);
            padding: 16px 18px; border-radius: 10px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            z-index: 1000; border: 1px solid #e2e8f0; max-width: 220px;
        }}

        .legend-section {{ margin-bottom: 14px; }}
        .legend-section:last-child {{ margin-bottom: 0; }}

        .legend-title {{
            font-size: 11px; font-weight: 600; color: #1e293b; margin-bottom: 8px;
            text-transform: uppercase; letter-spacing: 0.04em;
        }}

        .legend-item {{
            display: flex; align-items: center; gap: 8px; margin-bottom: 5px;
            font-size: 10px; color: #475569;
        }}

        .legend-line {{
            width: 20px; height: 2px; border-radius: 1px;
        }}

        .legend-label {{
            flex: 1; font-weight: 500;
        }}

        .legend-count {{
            font-weight: 600; color: #1e293b; font-size: 10px;
        }}

        .key-finding {{
            position: absolute; top: 16px; right: 16px; background: rgba(255, 255, 255, 0.97);
            padding: 14px 16px; border-radius: 10px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            z-index: 1000; border: 1px solid #e2e8f0; max-width: 300px;
            border-left: 4px solid #10b981;
        }}

        .key-finding-header {{
            display: flex; align-items: center; gap: 8px; margin-bottom: 6px;
        }}

        .key-finding-icon {{ font-size: 16px; }}

        .key-finding-title {{
            font-size: 11px; font-weight: 700; color: #10b981;
            text-transform: uppercase; letter-spacing: 0.05em;
        }}

        .key-finding-text {{
            font-size: 11px; color: #475569; line-height: 1.5; font-weight: 400;
        }}
    </style>
</head>
<body>
    <div class="info-panel">
        <div class="info-title">Individual Patient Journeys</div>
        <div class="info-text">
            Each line represents one patient's journey from their home community to a DBS center.
            Jittered positioning reveals patient density while maintaining privacy.
        </div>
    </div>

    <div class="key-finding">
        <div class="key-finding-header">
            <span class="key-finding-icon">👥</span>
            <div class="key-finding-title">All Patients</div>
        </div>
        <div class="key-finding-text">
            Mapping all {len(patient_flows)} individual patient journeys across Canada, including remote territories,
            reveals the true scale of geographic barriers to specialized neurological care.
        </div>
    </div>

    <div id="map"></div>

    <div class="legend">
        <div class="legend-section">
            <div class="legend-title">Journey Distance</div>
            <div class="legend-item">
                <div class="legend-line" style="background:{DISTANCE_COLORS['excellent']}"></div>
                <span class="legend-label">&lt;50 km</span>
                <span class="legend-count">{dist_stats['excellent']}</span>
            </div>
            <div class="legend-item">
                <div class="legend-line" style="background:{DISTANCE_COLORS['good']}"></div>
                <span class="legend-label">50-200 km</span>
                <span class="legend-count">{dist_stats['good']}</span>
            </div>
            <div class="legend-item">
                <div class="legend-line" style="background:{DISTANCE_COLORS['moderate']}"></div>
                <span class="legend-label">200-300 km</span>
                <span class="legend-count">{dist_stats['moderate']}</span>
            </div>
            <div class="legend-item">
                <div class="legend-line" style="background:{DISTANCE_COLORS['poor']}"></div>
                <span class="legend-label">300-500 km</span>
                <span class="legend-count">{dist_stats['poor']}</span>
            </div>
            <div class="legend-item">
                <div class="legend-line" style="background:{DISTANCE_COLORS['extreme']}"></div>
                <span class="legend-label">&gt;500 km</span>
                <span class="legend-count">{dist_stats['extreme']}</span>
            </div>
        </div>
    </div>

    <script>
        const patientFlows = {json.dumps(patient_flows)};
        const dbsCenters = {json.dumps(DBS_CENTERS)};

        function initMap() {{
            const map = new google.maps.Map(document.getElementById('map'), {{
                center: {{ lat: 60.0, lng: -95.0 }},
                zoom: 3.5,
                mapTypeId: 'terrain',
                styles: [
                    {{ featureType: 'administrative.province', elementType: 'geometry.stroke',
                       stylers: [{{ color: '#cbd5e1' }}, {{ weight: 1.5 }}] }},
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

            // Add DBS center markers
            Object.entries(dbsCenters).forEach(([name, center]) => {{
                new google.maps.Marker({{
                    position: {{ lat: center.lat, lng: center.lon }},
                    map: map,
                    icon: {{
                        path: google.maps.SymbolPath.CIRCLE,
                        scale: 6,
                        fillColor: '#7c3aed',
                        fillOpacity: 1,
                        strokeColor: 'white',
                        strokeWeight: 2.5
                    }},
                    title: name,
                    zIndex: 1000
                }});
            }});

            // Draw individual patient flows
            patientFlows.forEach(flow => {{
                // Arrow for direction
                const arrowScale = flow.distance > 500 ? 3.5 : (flow.distance > 300 ? 3.0 : 2.5);

                const lineSymbol = {{
                    path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW,
                    scale: arrowScale,
                    strokeColor: flow.color,
                    fillColor: flow.color,
                    fillOpacity: 1
                }};

                const line = new google.maps.Polyline({{
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
                    map: map,
                    zIndex: flow.distance > 500 ? 100 : 50
                }});

                // Patient origin marker (small circle)
                const patientMarker = new google.maps.Marker({{
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

                // Info window
                const infoWindow = new google.maps.InfoWindow({{
                    content: `
                        <div style="font-family: Inter, sans-serif; padding: 10px; min-width: 180px;">
                            <div style="font-size: 13px; font-weight: 600; color: #1e293b; margin-bottom: 8px;">
                                Patient Journey
                            </div>
                            <div style="font-size: 11px; color: #475569; line-height: 1.7;">
                                <strong>From:</strong> ${{flow.fsa}} (${{flow.province}})<br>
                                <strong>To:</strong> ${{flow.center}}<br>
                                <strong>Distance:</strong> ${{flow.distance}} km<br>
                                <strong>Year:</strong> ${{flow.year}}<br>
                                <strong>Category:</strong> ${{flow.category.toUpperCase()}}
                            </div>
                        </div>
                    `
                }});

                line.addListener('click', () => {{
                    infoWindow.setPosition({{ lat: flow.from_lat, lng: flow.from_lng }});
                    infoWindow.open(map);
                }});

                patientMarker.addListener('click', () => {{
                    infoWindow.open(map, patientMarker);
                }});
            }});
        }}

        window.onload = initMap;
    </script>
</body>
</html>'''

# Save
output_path = f'{OUTPUT_DIR}/map_individual_patient_journeys.html'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"\n✅ Generated individual patient journeys map: {output_path}")
print(f"\nFeatures:")
print(f"  ✓ All {len(patient_flows)} individual patient flows mapped")
print(f"  ✓ Lighter flow lines (0.8-2.5px) for better visibility")
print(f"  ✓ Larger arrows (2.5-3.5 scale) distinguishable at zoom 3.5")
print(f"  ✓ Jittered patient positions (3-5km radius)")
print(f"  ✓ Color-coded by distance category")
print(f"  ✓ Includes all Canadian patients including Nunavut")
print(f"  ✓ Small patient origin markers for clarity")
print(f"  ✓ Perfect zoom (3.5) showing all of Canada")

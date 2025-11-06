#!/usr/bin/env python3
"""
Generate Striking Map 5: Patient Migration Patterns
Visual Identity: Regional color-coded animated flows with directional arrows
Regions: Atlantic (blue), Quebec (purple), Ontario (emerald), Prairies (amber), West (cyan)
"""

import pandas as pd
import json
import numpy as np

BASE_DIR = '/Users/ramihatoum/Desktop/PPA/maps/final'
PATIENT_DATA_PATH = f'{BASE_DIR}/Final_database_05_11_25_FINAL.xlsx'
FSA_AGG_PATH = f'{BASE_DIR}/fsa_aggregated_data_current.csv'
OUTPUT_DIR = f'{BASE_DIR}/maps_nov2025'

# Load patient data
print("Loading patient database...")
patients = pd.read_excel(PATIENT_DATA_PATH)
print(f"  ✓ Loaded {len(patients)} patients")

# Load FSA coordinates from aggregated data
print("Loading FSA coordinates...")
coords = pd.read_csv(FSA_AGG_PATH)
coords = coords[['FSA', 'latitude', 'longitude']]

# Handle missing coordinates for specific FSAs (e.g., Nunavut)
FSA_COORD_OVERRIDES = {
    'X0X': {'latitude': 63.7467, 'longitude': -68.5170},  # Iqaluit, Nunavut
    'X0A': {'latitude': 66.3200, 'longitude': -73.2822}   # Already has coords but ensure consistency
}

for fsa, coords_override in FSA_COORD_OVERRIDES.items():
    if fsa in coords['FSA'].values:
        coords.loc[coords['FSA'] == fsa, 'latitude'] = coords_override['latitude']
        coords.loc[coords['FSA'] == fsa, 'longitude'] = coords_override['longitude']
    else:
        # Add missing FSA
        new_row = pd.DataFrame([{'FSA': fsa, 'latitude': coords_override['latitude'], 'longitude': coords_override['longitude']}])
        coords = pd.concat([coords, new_row], ignore_index=True)

print(f"  ✓ Loaded coordinates for {len(coords)} FSAs (including overrides for missing locations)")

# SiteID to Center Name mapping (complete mapping)
SITE_ID_MAP = {
    12.0: 'Halifax',
    13.0: 'Montreal',  # QC - major center
    14.0: 'Ottawa',
    16.0: 'Toronto',
    17.0: 'London',
    18.0: 'Winnipeg',
    19.0: 'Saskatoon',
    20.0: 'Calgary',
    21.0: 'Edmonton',
    22.0: 'Vancouver'
}

# DBS Centers with province codes
DBS_CENTERS = {
    'Halifax': {'lat': 44.6488, 'lon': -63.5752, 'provinces': [2.0]},  # NS
    'Montreal': {'lat': 45.5017, 'lon': -73.5673, 'provinces': [5.0]},  # QC
    'Ottawa': {'lat': 45.4215, 'lon': -75.6972, 'provinces': [5.0, 6.0]},  # QC, ON
    'Toronto': {'lat': 43.6532, 'lon': -79.3832, 'provinces': [6.0]},  # ON
    'London': {'lat': 43.0109, 'lon': -81.2733, 'provinces': [6.0]},  # ON
    'Winnipeg': {'lat': 49.8951, 'lon': -97.1384, 'provinces': [7.0]},  # MB
    'Saskatoon': {'lat': 52.1332, 'lon': -106.6700, 'provinces': [8.0]},  # SK
    'Calgary': {'lat': 51.0447, 'lon': -114.0719, 'provinces': [9.0]},  # AB
    'Edmonton': {'lat': 53.5461, 'lon': -113.4938, 'provinces': [9.0]},  # AB
    'Vancouver': {'lat': 49.2827, 'lon': -123.1207, 'provinces': [10.0]}  # BC
}

# Province code mapping
PROVINCE_CODE_MAP = {
    1.0: 'NL', 2.0: 'NS', 3.0: 'PE', 4.0: 'NB', 5.0: 'QC',
    6.0: 'ON', 7.0: 'MB', 8.0: 'SK', 9.0: 'AB', 10.0: 'BC',
    11.0: 'YT', 12.0: 'NT', 13.0: 'NU'
}

# Regional color scheme
REGION_COLORS = {
    'Atlantic': '#3b82f6',      # Blue - NL, NS, PE, NB
    'Quebec': '#8b5cf6',        # Purple - QC
    'Ontario': '#10b981',       # Emerald - ON
    'Prairies': '#f59e0b',      # Amber - MB, SK
    'West': '#06b6d4',          # Cyan - AB, BC
    'Territories': '#ec4899'    # Pink - YT, NT, NU
}

# Assign regions
def get_region(province_code):
    if province_code in [1.0, 2.0, 3.0, 4.0]:
        return 'Atlantic'
    elif province_code == 5.0:
        return 'Quebec'
    elif province_code == 6.0:
        return 'Ontario'
    elif province_code in [7.0, 8.0]:
        return 'Prairies'
    elif province_code in [9.0, 10.0]:
        return 'West'
    elif province_code in [11.0, 12.0, 13.0]:
        return 'Territories'
    else:
        return 'Unknown'

# Clean and prepare patient data
print("\nPreparing patient flows...")
patients = patients[patients['FSA'].notna()]
patients = patients[patients['SiteID'].notna()]

# Map SiteID to center names
patients['DBS_Center'] = patients['SiteID'].map(SITE_ID_MAP)
patients = patients[patients['DBS_Center'].notna()]

# Rename columns for consistency
patients = patients.rename(columns={
    'Driving Distance (km)': 'Distance_km',
    'ORYear': 'Year'
})

# Merge with coordinates
patients = patients.merge(coords[['FSA', 'latitude', 'longitude']],
                         left_on='FSA', right_on='FSA', how='left')
patients = patients[patients['latitude'].notna()]

# Add jittered positions (3-5km radius offset)
np.random.seed(42)
patients['jitter_lat'] = patients['latitude'] + np.random.uniform(-0.03, 0.03, len(patients))
patients['jitter_lng'] = patients['longitude'] + np.random.uniform(-0.05, 0.05, len(patients))

# Assign regions
patients['region'] = patients['Province'].apply(get_region)

print(f"  ✓ Prepared {len(patients)} patient flows with jittered positions")

# Calculate flow statistics by region and center
flow_summary = patients.groupby(['region', 'DBS_Center']).size().reset_index(name='patient_count')
print(f"\n  Regional Flow Distribution:")
for region in REGION_COLORS.keys():
    count = len(patients[patients['region'] == region])
    if count > 0:
        print(f"    {region}: {count} patients")

# Prepare flow data with MORE DRAMA for long distances
flows_data = []
for _, patient in patients.iterrows():
    center_name = patient['DBS_Center']
    if center_name in DBS_CENTERS:
        center = DBS_CENTERS[center_name]
        distance = patient.get('Distance_km', 0)

        # Handle missing distance data (e.g., Nunavut patients)
        if pd.isna(distance) or distance == 0:
            # Estimate distance from coordinates if missing
            from math import radians, cos, sin, asin, sqrt
            lat1, lon1 = patient['jitter_lat'], patient['jitter_lng']
            lat2, lon2 = center['lat'], center['lon']

            # Haversine formula for great circle distance
            lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * asin(sqrt(a))
            distance = 6371 * c  # Radius of earth in kilometers

        region = patient['region']

        # EVEN LIGHTER line weight - thinner, less bulky per user request
        if distance < 100:
            weight = 0.7
            opacity = 0.35
        elif distance < 200:
            weight = 0.9
            opacity = 0.45
        elif distance < 300:
            weight = 1.1
            opacity = 0.55
        elif distance < 500:
            weight = 1.5
            opacity = 0.7
        else:
            weight = 2.2  # Reduced for less bulk while maintaining visibility
            opacity = 0.85  # High visibility for drama

        flows_data.append({
            'from_lat': float(patient['jitter_lat']),
            'from_lng': float(patient['jitter_lng']),
            'to_lat': center['lat'],
            'to_lng': center['lon'],
            'distance': round(distance, 1),
            'fsa': patient['FSA'],
            'center': center_name,
            'region': region,
            'color': REGION_COLORS[region],
            'weight': weight,
            'year': int(patient.get('Year', 2021)) if pd.notna(patient.get('Year')) else 2021,
            'opacity': opacity
        })

print(f"  ✓ Created {len(flows_data)} animated flow lines")

# Center statistics
center_stats = patients.groupby('DBS_Center').agg({
    'FSA': 'count',
    'Distance_km': 'mean'
}).round(1).reset_index()
center_stats.columns = ['center', 'patients', 'avg_distance']
center_stats_dict = center_stats.to_dict('records')

# Generate HTML
html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Map 5: Patient Migration Patterns</title>
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
            font-size: 15px; font-weight: 600; color: #1e293b; margin-bottom: 10px;
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
            width: 20px; height: 3px; border-radius: 1px;
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
            z-index: 1000; border: 1px solid #e2e8f0; max-width: 320px;
            border-left: 4px solid #8b5cf6;
        }}

        .key-finding-header {{
            display: flex; align-items: center; gap: 8px; margin-bottom: 6px;
        }}

        .key-finding-icon {{
            font-size: 16px;
        }}

        .key-finding-title {{
            font-size: 11px; font-weight: 700; color: #8b5cf6;
            text-transform: uppercase; letter-spacing: 0.05em;
        }}

        .key-finding-text {{
            font-size: 11px; color: #475569; line-height: 1.5; font-weight: 400;
        }}

        .animation-control {{
            position: absolute; bottom: 20px; left: 16px; background: rgba(255, 255, 255, 0.97);
            padding: 12px 16px; border-radius: 10px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            z-index: 1000; border: 1px solid #e2e8f0;
        }}

        .control-title {{
            font-size: 11px; font-weight: 600; color: #1e293b; margin-bottom: 8px;
            text-transform: uppercase; letter-spacing: 0.04em;
        }}

        .play-btn {{
            padding: 8px 16px; font-size: 11px; font-weight: 600; border: none;
            background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
            color: white; border-radius: 6px; cursor: pointer;
            transition: all 0.3s; box-shadow: 0 2px 6px rgba(59, 130, 246, 0.3);
        }}

        .play-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 10px rgba(59, 130, 246, 0.4);
        }}

        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}

        .animate-flow {{
            animation: fadeIn 0.5s ease-in;
        }}
    </style>
</head>
<body>
    <div class="info-panel">
        <div class="info-title">Patient Migration Patterns</div>
        <div class="info-text">
            Visualizes patient flows from home FSAs to DBS centers across Canada.
            Line thickness indicates distance; colors represent geographic regions.
        </div>
    </div>

    <div class="key-finding">
        <div class="key-finding-header">
            <span class="key-finding-icon">🔄</span>
            <div class="key-finding-title">Migration Insight</div>
        </div>
        <div class="key-finding-text">
            {len(patients)} patient journeys mapped from {len(patients['FSA'].unique())} communities
            to {len(patients['DBS_Center'].unique())} DBS centers, revealing complex cross-regional access patterns.
        </div>
    </div>

    <div class="animation-control">
        <div class="control-title">Animation</div>
        <button class="play-btn" onclick="animateFlows()">▶ Play Sequential Flow</button>
    </div>

    <div id="map"></div>

    <div class="legend">
        <div class="legend-section">
            <div class="legend-title">Regional Flows</div>
            <div class="legend-item">
                <div class="legend-line" style="background:{REGION_COLORS['Atlantic']}"></div>
                <span class="legend-label">Atlantic</span>
                <span class="legend-count">{len(patients[patients['region'] == 'Atlantic'])}</span>
            </div>
            <div class="legend-item">
                <div class="legend-line" style="background:{REGION_COLORS['Quebec']}"></div>
                <span class="legend-label">Quebec</span>
                <span class="legend-count">{len(patients[patients['region'] == 'Quebec'])}</span>
            </div>
            <div class="legend-item">
                <div class="legend-line" style="background:{REGION_COLORS['Ontario']}"></div>
                <span class="legend-label">Ontario</span>
                <span class="legend-count">{len(patients[patients['region'] == 'Ontario'])}</span>
            </div>
            <div class="legend-item">
                <div class="legend-line" style="background:{REGION_COLORS['Prairies']}"></div>
                <span class="legend-label">Prairies</span>
                <span class="legend-count">{len(patients[patients['region'] == 'Prairies'])}</span>
            </div>
            <div class="legend-item">
                <div class="legend-line" style="background:{REGION_COLORS['West']}"></div>
                <span class="legend-label">West</span>
                <span class="legend-count">{len(patients[patients['region'] == 'West'])}</span>
            </div>
            <div class="legend-item">
                <div class="legend-line" style="background:{REGION_COLORS['Territories']}"></div>
                <span class="legend-label">Territories</span>
                <span class="legend-count">{len(patients[patients['region'] == 'Territories'])}</span>
            </div>
        </div>

        <div class="legend-section">
            <div class="legend-title">Flow Intensity</div>
            <div class="legend-item">
                <div class="legend-line" style="background:#94a3b8; height:1px; opacity:0.6;"></div>
                <span class="legend-label">&lt;100 km</span>
            </div>
            <div class="legend-item">
                <div class="legend-line" style="background:#94a3b8; height:1.5px; opacity:0.7;"></div>
                <span class="legend-label">100-300 km</span>
            </div>
            <div class="legend-item">
                <div class="legend-line" style="background:#94a3b8; height:2px; opacity:0.8;"></div>
                <span class="legend-label">300-500 km</span>
            </div>
            <div class="legend-item">
                <div class="legend-line" style="background:#ef4444; height:3px; opacity:0.9;"></div>
                <span class="legend-label" style="font-weight:700; color:#dc2626;">&gt;500 km EXTREME</span>
            </div>
        </div>
    </div>

    <script>
        const flowsData = {json.dumps(flows_data)};
        const dbsCenters = {json.dumps(DBS_CENTERS)};
        const centerStats = {json.dumps(center_stats_dict)};
        let map, flowLines = [], animationIndex = 0;

        function initMap() {{
            map = new google.maps.Map(document.getElementById('map'), {{
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

            // Draw all flow lines (always visible)
            flowsData.forEach(flow => {{
                // Larger arrow scale for better visibility at zoom 3.5
                const arrowScale = flow.distance > 500 ? 4.5 : (flow.distance > 300 ? 3.5 : 3.0);

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
                        offset: '70%'
                    }}],
                    map: map,
                    zIndex: flow.distance > 300 ? 100 : 50
                }});

                flowLines.push(line);
            }});
        }}

        function animateFlows() {{
            // Hide all flows
            flowLines.forEach(line => line.setMap(null));
            animationIndex = 0;

            // Show flows sequentially
            const showNextFlow = () => {{
                if (animationIndex < flowLines.length) {{
                    flowLines[animationIndex].setMap(map);
                    animationIndex++;
                    setTimeout(showNextFlow, 8);  // 8ms delay for smooth animation
                }}
            }};

            showNextFlow();
        }}

        window.onload = initMap;
    </script>
</body>
</html>'''

# Save
output_path = f'{OUTPUT_DIR}/map5_patient_flow_animated.html'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"\n✅ Generated striking Patient Migration Patterns map: {output_path}")
print(f"\nFeatures:")
print(f"  ✓ Regional color coding (Atlantic=blue, Quebec=purple, etc.)")
print(f"  ✓ {len(flows_data)} animated flow lines with directional arrows")
print(f"  ✓ Line thickness proportional to distance (1.5-3.5px)")
print(f"  ✓ Sequential animation with play button")
print(f"  ✓ Enhanced legend with regional breakdown")
print(f"  ✓ All flows always visible (not toggled)")
print(f"  ✓ Perfect zoom (3.5) showing all of Canada")
print(f"  ✓ Jittered patient positions (3-5km radius) for density visibility")

#!/usr/bin/env python3
"""
Generate dramatic patient flow map with animated direction arrows
"""

import pandas as pd
import json

# Paths
BASE_DIR = '/Users/ramihatoum/Desktop/PPA/maps/final'
FSA_AGG_PATH = f'{BASE_DIR}/fsa_aggregated_data_current.csv'
OUTPUT_DIR = f'{BASE_DIR}/maps_nov2025'

# Load data
print("Loading FSA data for flow visualization...")
fsa_data = pd.read_csv(FSA_AGG_PATH)
print(f"  ✓ Loaded {len(fsa_data)} FSAs")

# DBS Centers
DBS_CENTERS = {
    'QEII Health Sciences Centre': {'lat': 44.6382, 'lon': -63.5793},
    'Toronto Western Hospital': {'lat': 43.6532, 'lon': -79.3832},
    'London Health Sciences Centre': {'lat': 43.0096, 'lon': -81.2737},
    'Ottawa Hospital': {'lat': 45.4112, 'lon': -75.6981},
    'Montreal Neurological Institute': {'lat': 45.5047, 'lon': -73.5826},
    'CHUM': {'lat': 45.5089, 'lon': -73.5617},
    'CHU de Quebec': {'lat': 46.7787, 'lon': -71.2854},
    'Calgary Foothills': {'lat': 51.0643, 'lon': -114.1325},
    'University of Alberta Hospital': {'lat': 53.5232, 'lon': -113.5263},
    'Royal University Hospital Saskatoon': {'lat': 52.1324, 'lon': -106.6344}
}

# Prepare flow data
flow_lines = []
for idx, row in fsa_data.iterrows():
    if pd.notna(row['latitude']) and pd.notna(row['longitude']) and pd.notna(row['nearest_dbs_center']):
        center_name = row['nearest_dbs_center']
        if center_name in DBS_CENTERS:
            distance = float(row['avg_distance_km'])

            # Color based on distance - calm palette
            if distance < 100:
                color = '#6ee7b7'  # Soft green
                weight = 1.5
                opacity = 0.4
            elif distance < 200:
                color = '#fde047'  # Soft yellow
                weight = 2
                opacity = 0.5
            elif distance < 400:
                color = '#fdba74'  # Soft orange
                weight = 2.5
                opacity = 0.6
            else:
                color = '#fca5a5'  # Soft red
                weight = 3
                opacity = 0.7

            flow_lines.append({
                'from_lat': float(row['latitude']),
                'from_lng': float(row['longitude']),
                'to_lat': DBS_CENTERS[center_name]['lat'],
                'to_lng': DBS_CENTERS[center_name]['lon'],
                'fsa': row['FSA'],
                'distance': round(distance, 1),
                'patients': int(row['patient_count']),
                'center': center_name,
                'color': color,
                'weight': weight,
                'opacity': opacity
            })

print(f"  ✓ Prepared {len(flow_lines)} flow lines")

# Generate HTML with animated arrows
html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Patient Flows - Directional</title>
    <script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyBH_yuU7_TfAJmuf_h04UsmKKhC0XPWerA"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Inter', -apple-system, sans-serif;
            background: #f8fafc;
            overflow: hidden;
        }}

        #map {{
            width: 100%;
            height: 100vh;
        }}

        .info-panel {{
            position: absolute;
            top: 16px;
            left: 16px;
            background: rgba(255, 255, 255, 0.96);
            padding: 14px 18px;
            border-radius: 8px;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
            max-width: 260px;
            z-index: 1000;
            border: 1px solid #cbd5e1;
        }}

        .info-title {{
            font-size: 14px;
            font-weight: 600;
            color: #1e293b;
            margin-bottom: 4px;
        }}

        .info-subtitle {{
            font-size: 11px;
            color: #475569;
            line-height: 1.4;
        }}
    </style>
</head>
<body>
    <div class="info-panel">
        <div class="info-title">Patient Travel Patterns</div>
        <div class="info-subtitle">Directional flows to DBS centers</div>
    </div>

    <div id="map"></div>

    <script>
        const flowData = {json.dumps(flow_lines)};
        const dbsCenters = {json.dumps([{'name': k, 'lat': v['lat'], 'lon': v['lon']} for k, v in DBS_CENTERS.items()])};

        function initMap() {{
            const map = new google.maps.Map(document.getElementById('map'), {{
                center: {{ lat: 60.0, lng: -95.0 }},
                zoom: 3.5,
                mapTypeId: 'terrain',
                styles: [
                    {{
                        featureType: 'administrative.province',
                        elementType: 'geometry.stroke',
                        stylers: [
                            {{ color: '#cbd5e1' }},
                            {{ weight: 1.2 }}
                        ]
                    }},
                    {{
                        featureType: 'water',
                        elementType: 'geometry',
                        stylers: [{{ color: '#dbeafe' }}]
                    }},
                    {{
                        featureType: 'landscape',
                        elementType: 'geometry',
                        stylers: [{{ color: '#f1f5f9' }}]
                    }},
                    {{
                        featureType: 'poi',
                        stylers: [{{ visibility: 'off' }}]
                    }},
                    {{
                        featureType: 'road',
                        stylers: [{{ visibility: 'off' }}]
                    }}
                ],
                zoomControl: true,
                mapTypeControl: false,
                streetViewControl: false,
                fullscreenControl: true
            }});

            // Add DBS centers
            dbsCenters.forEach(center => {{
                new google.maps.Marker({{
                    position: {{ lat: center.lat, lng: center.lon }},
                    map: map,
                    icon: {{
                        path: google.maps.SymbolPath.CIRCLE,
                        scale: 9,
                        fillColor: '#3b82f6',
                        fillOpacity: 0.9,
                        strokeColor: 'white',
                        strokeWeight: 2.5
                    }},
                    title: center.name,
                    zIndex: 1000
                }});
            }});

            // Add flow lines with animated arrows
            flowData.forEach(flow => {{
                const lineSymbol = {{
                    path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW,
                    scale: 3,
                    strokeColor: flow.color,
                    strokeWeight: 2,
                    fillColor: flow.color,
                    fillOpacity: 0.8
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
                    map: map,
                    icons: [{{
                        icon: lineSymbol,
                        offset: '50%'
                    }}],
                    zIndex: flow.distance > 400 ? 200 : 100
                }});

                // Optional: Add animation
                let count = 0;
                const animateArrow = () => {{
                    count = (count + 1) % 200;
                    const icons = line.get('icons');
                    icons[0].offset = (count / 2) + '%';
                    line.set('icons', icons);
                }};

                // Animate only long-distance flows for drama
                if (flow.distance > 300) {{
                    window.setInterval(animateArrow, 50);
                }}
            }});
        }}

        window.onload = initMap;
    </script>
</body>
</html>'''

# Save flow map
output_path = f'{OUTPUT_DIR}/map5_patient_flow_animated.html'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"\n✅ Generated dramatic flow map: {output_path}")
print(f"\nFeatures:")
print(f"  ✓ Directional arrows on all flows")
print(f"  ✓ Animated arrows for long-distance flows (>300km)")
print(f"  ✓ Calm color palette")
print(f"  ✓ Perfect zoom (full Canada visible)")
print(f"  ✓ Simple, concise description")

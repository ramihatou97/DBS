#!/usr/bin/env python3
"""
Generate ALL maps with calm aesthetic, perfect zoom, simple descriptions
"""

import pandas as pd
import json

# Paths
BASE_DIR = '/Users/ramihatoum/Desktop/PPA/maps/final'
FSA_AGG_PATH = f'{BASE_DIR}/fsa_aggregated_data_current.csv'
OUTPUT_DIR = f'{BASE_DIR}/maps_nov2025'

# Load data
print("Loading FSA data...")
fsa_data = pd.read_csv(FSA_AGG_PATH)
print(f"  ✓ Loaded {len(fsa_data)} FSAs")

# Professional Aquamarine & Black color palette
CALM_COLORS = {
    'distance': {
        'excellent': '#B2F5EA',   # Very light aquamarine (< 50km)
        'good': '#4FD1C5',         # Medium aquamarine (50-100km)
        'moderate': '#38B2AC',     # Primary aquamarine (100-200km)
        'poor': '#F6AD55',         # Soft coral (200-400km)
        'critical': '#FC8181'      # Soft salmon (> 400km)
    },
    'primary': '#38B2AC',          # Primary aquamarine
    'border': '#2D3748',           # Dark gray
    'text': '#1A1A1A',             # Charcoal
    'bg': '#F7FAFC'                # Very light gray-blue
}

# Perfect zoom - shows all of Canada without truncation (zoomed out further)
MAP_CONFIG = {
    'center_lat': 60.0,
    'center_lng': -95.0,
    'zoom': 3.5
}

# DBS Centers
DBS_CENTERS = [
    {'name': 'Toronto Western', 'lat': 43.6532, 'lon': -79.3832},
    {'name': 'London', 'lat': 43.0096, 'lon': -81.2737},
    {'name': 'Ottawa', 'lat': 45.4112, 'lon': -75.6981},
    {'name': 'Montreal Neuro', 'lat': 45.5047, 'lon': -73.5826},
    {'name': 'CHUM', 'lat': 45.5089, 'lon': -73.5617},
    {'name': 'Quebec City', 'lat': 46.7787, 'lon': -71.2854},
    {'name': 'Halifax', 'lat': 44.6382, 'lon': -63.5793},
    {'name': 'Calgary', 'lat': 51.0643, 'lon': -114.1325},
    {'name': 'Edmonton', 'lat': 53.5232, 'lon': -113.5263},
    {'name': 'Saskatoon', 'lat': 52.1324, 'lon': -106.6344}
]

def get_calm_distance_color(distance):
    """Return calm color based on distance"""
    if distance < 50:
        return CALM_COLORS['distance']['excellent']
    elif distance < 100:
        return CALM_COLORS['distance']['good']
    elif distance < 200:
        return CALM_COLORS['distance']['moderate']
    elif distance < 400:
        return CALM_COLORS['distance']['poor']
    else:
        return CALM_COLORS['distance']['critical']

# Prepare FSA data with calm colors
fsa_markers = []
for idx, row in fsa_data.iterrows():
    if pd.notna(row['latitude']) and pd.notna(row['longitude']):
        marker_data = {
            'fsa': row['FSA'],
            'lat': float(row['latitude']),
            'lng': float(row['longitude']),
            'patients': int(row['patient_count']),
            'distance': round(float(row['avg_distance_km']), 1),
            'center': row['nearest_dbs_center'],
            'color': get_calm_distance_color(row['avg_distance_km']),
            'size': min(6 + int(row['patient_count']) * 1.5, 18)  # Smaller, not bulky
        }
        fsa_markers.append(marker_data)

print(f"  ✓ Prepared {len(fsa_markers)} FSA markers")

# Generate unified calm map HTML
html_template = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DBS Access Map - Canada</title>
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
            background: {CALM_COLORS['bg']};
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
            max-width: 280px;
            z-index: 1000;
            border: 1px solid {CALM_COLORS['border']};
        }}

        .info-title {{
            font-size: 14px;
            font-weight: 600;
            color: #1e293b;
            margin-bottom: 4px;
            letter-spacing: -0.01em;
        }}

        .info-subtitle {{
            font-size: 11px;
            color: {CALM_COLORS['text']};
            line-height: 1.4;
            font-weight: 400;
        }}

        .legend {{
            position: absolute;
            bottom: 20px;
            right: 20px;
            background: rgba(255, 255, 255, 0.96);
            padding: 12px 14px;
            border-radius: 8px;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
            z-index: 1000;
            border: 1px solid {CALM_COLORS['border']};
        }}

        .legend-title {{
            font-size: 11px;
            font-weight: 600;
            color: #1e293b;
            margin-bottom: 6px;
            text-transform: uppercase;
            letter-spacing: 0.03em;
        }}

        .legend-item {{
            display: flex;
            align-items: center;
            gap: 7px;
            margin-bottom: 3px;
            font-size: 10px;
            color: {CALM_COLORS['text']};
        }}

        .legend-color {{
            width: 14px;
            height: 14px;
            border-radius: 2px;
            border: 1px solid rgba(0,0,0,0.08);
        }}
    </style>
</head>
<body>
    <div class="info-panel">
        <div class="info-title">Travel Distance to DBS Centers</div>
        <div class="info-subtitle">936 patients across 513 communities</div>
    </div>

    <div id="map"></div>

    <div class="legend">
        <div class="legend-title">Distance</div>
        <div class="legend-item">
            <div class="legend-color" style="background:{CALM_COLORS['distance']['excellent']}"></div>
            <span>Under 50 km</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background:{CALM_COLORS['distance']['good']}"></div>
            <span>50-100 km</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background:{CALM_COLORS['distance']['moderate']}"></div>
            <span>100-200 km</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background:{CALM_COLORS['distance']['poor']}"></div>
            <span>200-400 km</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background:{CALM_COLORS['distance']['critical']}"></div>
            <span>Over 400 km</span>
        </div>
    </div>

    <script>
        const fsaMarkers = {json.dumps(fsa_markers)};
        const dbsCenters = {json.dumps(DBS_CENTERS)};

        function initMap() {{
            const map = new google.maps.Map(document.getElementById('map'), {{
                center: {{ lat: {MAP_CONFIG['center_lat']}, lng: {MAP_CONFIG['center_lng']} }},
                zoom: {MAP_CONFIG['zoom']},
                mapTypeId: 'terrain',
                styles: [
                    {{
                        featureType: 'administrative.province',
                        elementType: 'geometry.stroke',
                        stylers: [
                            {{ color: '{CALM_COLORS['border']}' }},
                            {{ weight: 1.2 }},
                            {{ visibility: 'on' }}
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
                        elementType: 'labels',
                        stylers: [{{ visibility: 'off' }}]
                    }}
                ],
                disableDefaultUI: false,
                zoomControl: true,
                mapTypeControl: false,
                streetViewControl: false,
                fullscreenControl: true,
                gestureHandling: 'greedy'
            }});

            // Add DBS centers
            dbsCenters.forEach(center => {{
                new google.maps.Marker({{
                    position: {{ lat: center.lat, lng: center.lon }},
                    map: map,
                    icon: {{
                        path: google.maps.SymbolPath.CIRCLE,
                        scale: 8,
                        fillColor: '#3b82f6',
                        fillOpacity: 0.9,
                        strokeColor: 'white',
                        strokeWeight: 2
                    }},
                    title: center.name,
                    zIndex: 1000
                }});
            }});

            // Add FSA markers
            fsaMarkers.forEach(fsa => {{
                const marker = new google.maps.Marker({{
                    position: {{ lat: fsa.lat, lng: fsa.lng }},
                    map: map,
                    icon: {{
                        path: google.maps.SymbolPath.CIRCLE,
                        scale: fsa.size,
                        fillColor: fsa.color,
                        fillOpacity: 0.75,
                        strokeColor: 'white',
                        strokeWeight: 1
                    }},
                    zIndex: 100
                }});

                const infoWindow = new google.maps.InfoWindow({{
                    content: `
                        <div style="font-family: Inter, sans-serif; padding: 8px; min-width: 140px;">
                            <div style="font-size: 13px; font-weight: 600; color: #1e293b; margin-bottom: 6px;">
                                ${{fsa.fsa}}
                            </div>
                            <div style="font-size: 11px; color: {CALM_COLORS['text']}; margin-bottom: 3px;">
                                ${{fsa.patients}} patients
                            </div>
                            <div style="font-size: 11px; color: {CALM_COLORS['text']};">
                                ${{fsa.distance}} km to ${{fsa.center}}
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

# Save the calm version
output_path = f'{OUTPUT_DIR}/map1_travel_burden_heatmap.html'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html_template)

print(f"\n✅ Generated calm map: {output_path}")
print(f"\nFeatures:")
print(f"  ✓ Perfect zoom (shows all Canada, zoom level {MAP_CONFIG['zoom']})")
print(f"  ✓ Calm colors (soft, muted palette)")
print(f"  ✓ Simple description")
print(f"  ✓ Clean, minimal design")
print(f"  ✓ Not bulky (marker sizes 6-18px)")
print(f"  ✓ Province borders visible ({CALM_COLORS['border']})")

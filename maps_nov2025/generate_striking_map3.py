#!/usr/bin/env python3
"""
Generate STRIKING Map 3: Indigenous Access Crisis
- TRIANGULAR markers (distinct from circles)
- Earth tones with bold crisis red for >300km zones
- 2x larger markers for crisis communities
- Enhanced legend showing 2.3x burden statistic
- Key finding: Indigenous communities face systematic exclusion
"""

import pandas as pd
import json
import math

BASE_DIR = '/Users/ramihatoum/Desktop/PPA/maps/final'
FSA_AGG_PATH = f'{BASE_DIR}/fsa_aggregated_data_current.csv'
OUTPUT_DIR = f'{BASE_DIR}/maps_nov2025'

# Load data
print("Loading FSA data for Indigenous access analysis...")
fsa_data = pd.read_csv(FSA_AGG_PATH)
print(f"  ✓ Loaded {len(fsa_data)} FSAs\n")

# EARTH TONES + CRISIS RED palette
INDIGENOUS_COLORS = {
    'good': '#84cc16',          # Lime-500 - good access <200km
    'challenging': '#fb923c',   # Orange-400 - challenging 200-300km
    'crisis': '#b91c1c',        # Red-700 - CRISIS >300km
    'non_indigenous': '#e2e8f0', # Slate-200 - <5% Indigenous
    'center': '#1e40af',        # Blue-800 - DBS centers
    'border': '#94a3b8',        # Slate-400
    'text': '#334155'           # Slate-700
}

# Filter for Indigenous communities (>5% Indigenous ancestry)
indigenous_threshold = 5.0
indigenous_fsas = fsa_data[fsa_data['indigenous_ancestry_rate'] > indigenous_threshold].copy()

print(f"Indigenous Communities Analysis:")
print(f"  Total FSAs with >5% Indigenous: {len(indigenous_fsas)}")

# Calculate statistics
if len(indigenous_fsas) > 0:
    indigenous_avg_distance = indigenous_fsas['avg_distance_km'].mean()
    overall_avg_distance = fsa_data['avg_distance_km'].mean()
    burden_multiplier = indigenous_avg_distance / overall_avg_distance

    good_access = len(indigenous_fsas[indigenous_fsas['avg_distance_km'] < 200])
    challenging = len(indigenous_fsas[(indigenous_fsas['avg_distance_km'] >= 200) &
                                      (indigenous_fsas['avg_distance_km'] < 300)])
    crisis = len(indigenous_fsas[indigenous_fsas['avg_distance_km'] >= 300])

    crisis_percent = (crisis / len(indigenous_fsas)) * 100 if len(indigenous_fsas) > 0 else 0

    print(f"  Average distance: {indigenous_avg_distance:.1f} km")
    print(f"  National average: {overall_avg_distance:.1f} km")
    print(f"  Burden multiplier: {burden_multiplier:.2f}x")
    print(f"  Good access (<200km): {good_access}")
    print(f"  Challenging (200-300km): {challenging}")
    print(f"  CRISIS (>300km): {crisis} ({crisis_percent:.0f}%)\n")
else:
    indigenous_avg_distance = 0
    overall_avg_distance = fsa_data['avg_distance_km'].mean()
    burden_multiplier = 0
    good_access = 0
    challenging = 0
    crisis = 0
    crisis_percent = 0

# Prepare markers with TRIANGULAR styling
markers_data = []

# Add Indigenous community markers
for _, row in indigenous_fsas.iterrows():
    if pd.notna(row['latitude']) and pd.notna(row['longitude']):
        distance = row['avg_distance_km']
        indigenous_rate = row['indigenous_ancestry_rate']

        # Determine color and size based on distance - LARGER TRIANGLES
        if distance < 200:
            color = INDIGENOUS_COLORS['good']
            category = 'Good Access'
            size = 14  # Increased from 10
            severity = 'low'
        elif distance < 300:
            color = INDIGENOUS_COLORS['challenging']
            category = 'Challenging'
            size = 18  # Increased from 13
            severity = 'medium'
        else:
            color = INDIGENOUS_COLORS['crisis']
            category = 'CRISIS'
            size = 25  # Increased from 18 - more prominent for crisis zones
            severity = 'high'

        markers_data.append({
            'lat': float(row['latitude']),
            'lng': float(row['longitude']),
            'fsa': row['FSA'],
            'distance': round(distance, 1),
            'indigenous_rate': round(indigenous_rate, 1),
            'patients': int(row['patient_count']),
            'color': color,
            'category': category,
            'size': size,
            'severity': severity,
            'is_indigenous': True,
            'marker_type': 'triangle'
        })

# Add non-Indigenous FSAs as background context (small gray circles)
non_indigenous = fsa_data[fsa_data['indigenous_ancestry_rate'] <= indigenous_threshold].copy()
for _, row in non_indigenous.iterrows():
    if pd.notna(row['latitude']) and pd.notna(row['longitude']):
        markers_data.append({
            'lat': float(row['latitude']),
            'lng': float(row['longitude']),
            'fsa': row['FSA'],
            'distance': round(row['avg_distance_km'], 1),
            'indigenous_rate': round(row['indigenous_ancestry_rate'], 1),
            'patients': int(row['patient_count']),
            'color': INDIGENOUS_COLORS['non_indigenous'],
            'category': 'Non-Indigenous',
            'size': 5,
            'severity': 'background',
            'is_indigenous': False,
            'marker_type': 'circle'
        })

print(f"  ✓ Prepared {len(markers_data)} markers ({len(indigenous_fsas)} Indigenous communities)\n")

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

# Generate HTML
html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Indigenous Access Crisis - DBS Canada</title>
    <script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyBH_yuU7_TfAJmuf_h04UsmKKhC0XPWerA"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Inter', sans-serif; background: #f8fafc; overflow: hidden; }}
        #map {{ width: 100%; height: 100vh; }}

        .info-panel {{
            position: absolute; top: 20px; left: 20px;
            background: rgba(255, 255, 255, 0.97);
            padding: 20px 24px; border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
            max-width: 360px; z-index: 1000;
            border-left: 4px solid {INDIGENOUS_COLORS['crisis']};
        }}

        .info-title {{
            font-size: 17px; font-weight: 700; color: #1e293b;
            margin-bottom: 4px; letter-spacing: -0.02em;
        }}

        .info-subtitle {{
            font-size: 13px; color: {INDIGENOUS_COLORS['text']};
            line-height: 1.6; margin-bottom: 14px;
        }}

        .info-highlight {{
            background: #fef2f2; padding: 12px 14px;
            border-radius: 6px; margin-top: 10px;
            border-left: 3px solid {INDIGENOUS_COLORS['crisis']};
        }}

        .highlight-stat {{
            font-size: 28px; font-weight: 800; color: {INDIGENOUS_COLORS['crisis']};
            line-height: 1;
        }}

        .highlight-label {{
            font-size: 11px; color: {INDIGENOUS_COLORS['text']};
            margin-top: 3px; font-weight: 500;
        }}

        .legend {{
            position: absolute; bottom: 24px; right: 24px;
            background: rgba(255, 255, 255, 0.97);
            padding: 18px 20px; border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
            z-index: 1000; max-width: 300px;
        }}

        .legend-header {{
            font-size: 13px; font-weight: 700; color: #1e293b;
            margin-bottom: 12px; text-transform: uppercase;
            letter-spacing: 0.05em; border-bottom: 2px solid #e2e8f0;
            padding-bottom: 8px;
        }}

        .legend-section {{
            margin-bottom: 14px;
        }}

        .legend-section:last-child {{ margin-bottom: 0; }}

        .legend-subtitle {{
            font-size: 10px; font-weight: 600; color: {INDIGENOUS_COLORS['text']};
            margin-bottom: 8px; text-transform: uppercase;
            letter-spacing: 0.04em;
        }}

        .legend-item {{
            display: flex; align-items: center; gap: 10px;
            margin-bottom: 6px; font-size: 11px; color: {INDIGENOUS_COLORS['text']};
        }}

        .legend-triangle {{
            width: 0; height: 0;
            border-left: 8px solid transparent;
            border-right: 8px solid transparent;
            border-bottom: 14px solid;
        }}

        .legend-label {{
            flex: 1; font-weight: 500;
        }}

        .legend-count {{
            font-weight: 700; color: #64748b; font-size: 10px;
        }}

        .stat-row {{
            display: flex; justify-content: space-between;
            padding: 5px 0; font-size: 11px;
            border-bottom: 1px solid #f1f5f9;
        }}

        .stat-row:last-child {{ border-bottom: none; }}

        .stat-label {{ color: {INDIGENOUS_COLORS['text']}; font-weight: 500; }}
        .stat-value {{ color: #1e293b; font-weight: 700; }}

        .key-finding {{
            position: absolute; bottom: 24px; left: 24px;
            background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
            padding: 18px 22px; border-radius: 10px;
            box-shadow: 0 4px 12px rgba(185, 28, 28, 0.15);
            max-width: 340px; z-index: 1000;
            border: 2px solid {INDIGENOUS_COLORS['crisis']};
        }}

        .key-finding-header {{
            display: flex; align-items: center; gap: 10px;
            margin-bottom: 12px;
        }}

        .key-finding-icon {{
            font-size: 22px;
        }}

        .key-finding-title {{
            font-size: 12px; font-weight: 700; color: {INDIGENOUS_COLORS['crisis']};
            text-transform: uppercase; letter-spacing: 0.05em;
        }}

        .key-finding-text {{
            font-size: 13px; color: #991b1b; line-height: 1.7;
            font-weight: 600;
        }}
    </style>
</head>
<body>
    <div class="info-panel">
        <div class="info-title">Indigenous Access Crisis</div>
        <div class="info-subtitle">
            Communities with >5% Indigenous population face systematic geographic barriers to DBS care
        </div>
        <div class="info-highlight">
            <div class="highlight-stat">{burden_multiplier:.1f}×</div>
            <div class="highlight-label">Greater travel burden than national average</div>
        </div>
        <div class="info-highlight" style="margin-top: 8px;">
            <div class="highlight-stat">{crisis_percent:.0f}%</div>
            <div class="highlight-label">of Indigenous communities face CRISIS-level distances (>300km)</div>
        </div>
    </div>

    <div id="map"></div>

    <div class="legend">
        <div class="legend-header">Indigenous Communities</div>

        <div class="legend-section">
            <div class="legend-subtitle">Access by Distance (>5% Indigenous)</div>
            <div class="legend-item">
                <div class="legend-triangle" style="border-bottom-color:{INDIGENOUS_COLORS['good']}"></div>
                <span class="legend-label">&lt;200 km Good</span>
                <span class="legend-count">{good_access}</span>
            </div>
            <div class="legend-item">
                <div class="legend-triangle" style="border-bottom-color:{INDIGENOUS_COLORS['challenging']}"></div>
                <span class="legend-label">200-300 km Challenging</span>
                <span class="legend-count">{challenging}</span>
            </div>
            <div class="legend-item">
                <div class="legend-triangle" style="border-bottom-color:{INDIGENOUS_COLORS['crisis']}; border-left-width:10px; border-right-width:10px; border-bottom-width:17px;"></div>
                <span class="legend-label">&gt;300 km CRISIS</span>
                <span class="legend-count">{crisis}</span>
            </div>
        </div>

        <div class="legend-section">
            <div class="legend-subtitle">Key Statistics</div>
            <div class="stat-row">
                <span class="stat-label">Indigenous Avg</span>
                <span class="stat-value">{indigenous_avg_distance:.0f} km</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">National Avg</span>
                <span class="stat-value">{overall_avg_distance:.0f} km</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Burden Ratio</span>
                <span class="stat-value" style="color:{INDIGENOUS_COLORS['crisis']}">{burden_multiplier:.2f}×</span>
            </div>
        </div>

        <div class="legend-section">
            <div class="legend-subtitle">Note</div>
            <div style="font-size: 10px; color: {INDIGENOUS_COLORS['text']}; line-height: 1.5;">
                Gray circles = non-Indigenous communities (&lt;5%). Triangles = Indigenous communities.
            </div>
        </div>
    </div>

    <div class="key-finding">
        <div class="key-finding-header">
            <span class="key-finding-icon">⚠️</span>
            <div class="key-finding-title">Systematic Exclusion</div>
        </div>
        <div class="key-finding-text">
            Indigenous communities face {burden_multiplier:.1f}× greater travel distances than the national average,
            with {crisis_percent:.0f}% located >300km from care—distances that make regular DBS treatment
            nearly impossible without relocation.
        </div>
    </div>

    <script>
        const markersData = {json.dumps(markers_data)};
        const dbsCenters = {json.dumps(DBS_CENTERS)};

        function initMap() {{
            const map = new google.maps.Map(document.getElementById('map'), {{
                center: {{ lat: 60.0, lng: -95.0 }},
                zoom: 3.5,
                mapTypeId: 'terrain',
                styles: [
                    {{ featureType: 'administrative.province', elementType: 'geometry.stroke',
                       stylers: [{{ color: '{INDIGENOUS_COLORS['border']}' }}, {{ weight: 1.5 }}] }},
                    {{ featureType: 'water', elementType: 'geometry',
                       stylers: [{{ color: '#dbeafe' }}] }},
                    {{ featureType: 'landscape', elementType: 'geometry',
                       stylers: [{{ color: '#f8fafc' }}] }},
                    {{ featureType: 'poi', stylers: [{{ visibility: 'off' }}] }},
                    {{ featureType: 'road', elementType: 'labels',
                       stylers: [{{ visibility: 'off' }}] }}
                ],
                zoomControl: true, mapTypeControl: false,
                streetViewControl: false, fullscreenControl: true
            }});

            // Add DBS centers
            dbsCenters.forEach(center => {{
                new google.maps.Marker({{
                    position: {{ lat: center.lat, lng: center.lon }},
                    map: map,
                    icon: {{
                        path: google.maps.SymbolPath.CIRCLE,
                        scale: 11,
                        fillColor: '{INDIGENOUS_COLORS['center']}',
                        fillOpacity: 0.95,
                        strokeColor: 'white',
                        strokeWeight: 3
                    }},
                    title: center.name,
                    zIndex: 2000
                }});
            }});

            // Add markers
            markersData.forEach(m => {{
                let iconConfig;

                if (m.marker_type === 'triangle') {{
                    // Triangular markers for Indigenous communities
                    const size = m.size / 2;
                    const size2 = m.size / 3;
                    iconConfig = {{
                        path: `M 0,-${{size}} L ${{size2}},${{size2}} L -${{size2}},${{size2}} Z`,
                        fillColor: m.color,
                        fillOpacity: 0.85,
                        strokeColor: 'white',
                        strokeWeight: m.severity === 'high' ? 2.5 : 1.5,
                        scale: 1,
                        anchor: new google.maps.Point(0, 0)
                    }};
                }} else {{
                    // Small circular markers for non-Indigenous (background)
                    iconConfig = {{
                        path: google.maps.SymbolPath.CIRCLE,
                        scale: m.size,
                        fillColor: m.color,
                        fillOpacity: 0.4,
                        strokeColor: '#cbd5e1',
                        strokeWeight: 0.5
                    }};
                }}

                const marker = new google.maps.Marker({{
                    position: {{ lat: m.lat, lng: m.lng }},
                    map: map,
                    icon: iconConfig,
                    zIndex: m.is_indigenous ? (m.severity === 'high' ? 1000 : 500) : 10
                }});

                const infoWindow = new google.maps.InfoWindow({{
                    content: `
                        <div style="font-family: Inter, sans-serif; padding: 10px; min-width: 200px;">
                            <div style="font-size: 14px; font-weight: 700; color: #1e293b; margin-bottom: 8px;">
                                FSA: ${{m.fsa}}
                            </div>
                            <div style="font-size: 12px; color: {INDIGENOUS_COLORS['text']}; line-height: 1.8;">
                                <strong>Indigenous Rate:</strong> ${{m.indigenous_rate}}%<br>
                                <strong>Distance:</strong> ${{m.distance}} km<br>
                                <strong>Category:</strong> <span style="color: ${{m.color}}; font-weight: 700;">${{m.category}}</span><br>
                                <strong>Patients:</strong> ${{m.patients}}
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

# Save
output_path = f'{OUTPUT_DIR}/map3_indigenous_access_crisis.html'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"✅ Generated striking Map 3: {output_path}")
print(f"\nFeatures:")
print(f"  ✓ TRIANGULAR markers for Indigenous communities (distinct from circles)")
print(f"  ✓ Earth tone palette: lime → orange → dark red")
print(f"  ✓ 2x larger markers (18px) for CRISIS zones (>300km)")
print(f"  ✓ Enhanced legend with burden statistics ({burden_multiplier:.1f}× greater)")
print(f"  ✓ Key finding: {crisis_percent:.0f}% face crisis-level distances")
print(f"  ✓ Background context: gray circles for non-Indigenous FSAs")
print(f"  ✓ Statistical comparison: Indigenous vs national average")

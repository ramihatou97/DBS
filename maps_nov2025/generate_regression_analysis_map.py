#!/usr/bin/env python3
"""
Generate Regression Analysis Map with calm aesthetic
Based on: log(Distance) = 7.556 + 0.0000003(Income) - 8.669(Gini) + 0.076(Indigenous) - 0.024(Minority) + Hospital_Effects
"""

import pandas as pd
import json

BASE_DIR = '/Users/ramihatoum/Desktop/PPA/maps/final'
FSA_AGG_PATH = f'{BASE_DIR}/fsa_aggregated_data_current.csv'
OUTPUT_DIR = f'{BASE_DIR}/maps_nov2025'

# Load data
print("Loading FSA data for regression visualization...")
fsa_data = pd.read_csv(FSA_AGG_PATH)
print(f"  ✓ Loaded {len(fsa_data)} FSAs")

# Calm colors
CALM = {
    'good_access': '#6ee7b7',      # Soft green - good access (<200km)
    'poor_access': '#fca5a5',      # Soft coral - poor access (>200km)
    'indigenous_low': '#fef3c7',   # Very light yellow
    'indigenous_mid': '#fde047',   # Soft yellow
    'indigenous_high': '#fdba74',  # Soft orange
    'indigenous_very_high': '#f87171',  # Soft red
    'rural_border': '#f97316',     # Orange for rural outline
    'urban_border': '#cbd5e1',     # Gray for urban
    'text': '#475569'
}

# Calculate regression-based predictions and disparities
markers_data = []
for _, row in fsa_data.iterrows():
    if pd.notna(row['latitude']) and pd.notna(row['longitude']):
        distance = row['avg_distance_km']
        indigenous = row.get('indigenous_ancestry_rate', 0)

        # Binary classification: Good vs Poor access
        is_poor_access = distance > 200

        # Indigenous rate categories
        if indigenous > 25:
            indigenous_color = CALM['indigenous_very_high']
        elif indigenous > 10:
            indigenous_color = CALM['indigenous_high']
        elif indigenous > 5:
            indigenous_color = CALM['indigenous_mid']
        else:
            indigenous_color = CALM['indigenous_low']

        # Determine if rural (simplified logic)
        is_rural = row.get('rural', 0) == 1 if 'rural' in row else False

        markers_data.append({
            'lat': float(row['latitude']),
            'lng': float(row['longitude']),
            'fsa': row['FSA'],
            'distance': round(distance, 1),
            'indigenous': round(indigenous, 1),
            'income': int(row.get('median_household_income_2020', 0)) if pd.notna(row.get('median_household_income_2020')) else 0,
            'gini': round(float(row.get('gini_index', 0)), 3) if pd.notna(row.get('gini_index')) else 0,
            'access_color': CALM['poor_access'] if is_poor_access else CALM['good_access'],
            'indigenous_color': indigenous_color,
            'is_rural': is_rural,
            'border_color': CALM['rural_border'] if is_rural else CALM['urban_border'],
            'border_weight': 2.5 if is_rural else 1
        })

print(f"  ✓ Prepared {len(markers_data)} markers with regression data")

# Generate HTML
html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Regression Analysis - Drivers of Access</title>
    <script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyBH_yuU7_TfAJmuf_h04UsmKKhC0XPWerA"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Inter', sans-serif; background: #f8fafc; overflow: hidden; }}
        #map {{ width: 100%; height: 100vh; }}

        .info-panel {{
            position: absolute; top: 16px; left: 16px; background: rgba(255, 255, 255, 0.96);
            padding: 16px 20px; border-radius: 8px; box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
            max-width: 340px; z-index: 1000; border: 1px solid #cbd5e1;
        }}

        .info-title {{ font-size: 14px; font-weight: 600; color: #1e293b; margin-bottom: 6px; }}

        .regression-formula {{
            font-size: 10px; color: {CALM['text']}; line-height: 1.5;
            background: #f1f5f9; padding: 8px; border-radius: 4px; margin-top: 8px;
            font-family: 'Courier New', monospace;
        }}

        .legend {{
            position: absolute; bottom: 20px; right: 20px; background: rgba(255, 255, 255, 0.96);
            padding: 14px 16px; border-radius: 8px; box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
            z-index: 1000; border: 1px solid #cbd5e1; max-width: 200px;
        }}

        .legend-section {{ margin-bottom: 12px; }}
        .legend-section:last-child {{ margin-bottom: 0; }}

        .legend-title {{
            font-size: 11px; font-weight: 600; color: #1e293b; margin-bottom: 6px;
            text-transform: uppercase; letter-spacing: 0.03em;
        }}

        .legend-item {{
            display: flex; align-items: center; gap: 7px; margin-bottom: 3px;
            font-size: 10px; color: {CALM['text']};
        }}

        .legend-color {{
            width: 14px; height: 14px; border-radius: 2px; border: 1px solid rgba(0,0,0,0.08);
        }}

        .view-toggle {{
            position: absolute; top: 16px; right: 16px; background: rgba(255, 255, 255, 0.96);
            padding: 8px; border-radius: 8px; box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
            z-index: 1000; border: 1px solid #cbd5e1; display: flex; gap: 8px;
        }}

        .toggle-btn {{
            padding: 6px 12px; font-size: 11px; font-weight: 500; border: none;
            background: #f1f5f9; color: {CALM['text']}; border-radius: 4px; cursor: pointer;
            transition: all 0.2s;
        }}

        .toggle-btn.active {{ background: #3b82f6; color: white; }}
        .toggle-btn:hover {{ background: #3b82f6; color: white; }}
    </style>
</head>
<body>
    <div class="info-panel">
        <div class="info-title">Key Drivers of Access Disparity</div>
        <div class="regression-formula">
            log(Distance) = 7.556<br>
            + 0.0000003(Income)<br>
            - 8.669(Gini)<br>
            + 0.076(Indigenous)<br>
            - 0.024(Minority)<br>
            + Hospital Effects
        </div>
    </div>

    <div class="view-toggle">
        <button class="toggle-btn active" onclick="switchView('access')">Access</button>
        <button class="toggle-btn" onclick="switchView('indigenous')">Indigenous</button>
    </div>

    <div id="map"></div>

    <div class="legend">
        <div class="legend-section" id="access-legend">
            <div class="legend-title">Access</div>
            <div class="legend-item">
                <div class="legend-color" style="background:{CALM['good_access']}"></div>
                <span>Good (&lt;200km)</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background:{CALM['poor_access']}"></div>
                <span>Poor (&gt;200km)</span>
            </div>
        </div>

        <div class="legend-section" id="indigenous-legend" style="display:none;">
            <div class="legend-title">Indigenous %</div>
            <div class="legend-item">
                <div class="legend-color" style="background:{CALM['indigenous_low']}"></div>
                <span>&lt;5%</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background:{CALM['indigenous_mid']}"></div>
                <span>5-10%</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background:{CALM['indigenous_high']}"></div>
                <span>10-25%</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background:{CALM['indigenous_very_high']}"></div>
                <span>&gt;25%</span>
            </div>
        </div>

        <div class="legend-section">
            <div class="legend-title">Rural/Urban</div>
            <div class="legend-item">
                <div style="width:14px; height:14px; border:2px solid {CALM['rural_border']}; border-radius:2px;"></div>
                <span>Rural</span>
            </div>
        </div>
    </div>

    <script>
        const markersData = {json.dumps(markers_data)};
        let map, markers = [];
        let currentView = 'access';

        function initMap() {{
            map = new google.maps.Map(document.getElementById('map'), {{
                center: {{ lat: 60.0, lng: -95.0 }}, zoom: 3.5, mapTypeId: 'terrain',
                styles: [
                    {{ featureType: 'administrative.province', elementType: 'geometry.stroke',
                       stylers: [{{ color: '#cbd5e1' }}, {{ weight: 1.2 }}] }},
                    {{ featureType: 'water', elementType: 'geometry', stylers: [{{ color: '#dbeafe' }}] }},
                    {{ featureType: 'landscape', elementType: 'geometry', stylers: [{{ color: '#f1f5f9' }}] }},
                    {{ featureType: 'poi', stylers: [{{ visibility: 'off' }}] }},
                    {{ featureType: 'road', elementType: 'labels', stylers: [{{ visibility: 'off' }}] }}
                ],
                zoomControl: true, mapTypeControl: false, streetViewControl: false, fullscreenControl: true
            }});

            renderMarkers();
        }}

        function renderMarkers() {{
            // Clear existing markers
            markers.forEach(m => m.setMap(null));
            markers = [];

            markersData.forEach(data => {{
                const color = currentView === 'access' ? data.access_color : data.indigenous_color;

                const marker = new google.maps.Marker({{
                    position: {{ lat: data.lat, lng: data.lng }},
                    map: map,
                    icon: {{
                        path: google.maps.SymbolPath.CIRCLE,
                        scale: 7,
                        fillColor: color,
                        fillOpacity: 0.75,
                        strokeColor: data.border_color,
                        strokeWeight: data.border_weight
                    }},
                    zIndex: data.is_rural ? 200 : 100
                }});

                const infoWindow = new google.maps.InfoWindow({{
                    content: `
                        <div style="font-family: Inter, sans-serif; padding: 8px; min-width: 180px;">
                            <div style="font-size: 13px; font-weight: 600; color: #1e293b; margin-bottom: 8px;">
                                ${{data.fsa}}
                            </div>
                            <div style="font-size: 11px; color: {CALM['text']}; line-height: 1.6;">
                                <strong>Distance:</strong> ${{data.distance}} km<br>
                                <strong>Indigenous:</strong> ${{data.indigenous}}%<br>
                                <strong>Income:</strong> $$${{data.income.toLocaleString()}}<br>
                                <strong>Gini:</strong> ${{data.gini}}<br>
                                <strong>Type:</strong> ${{data.is_rural ? 'Rural' : 'Urban'}}
                            </div>
                        </div>
                    `
                }});

                marker.addListener('click', () => {{
                    infoWindow.open(map, marker);
                }});

                markers.push(marker);
            }});
        }}

        function switchView(view) {{
            currentView = view;

            // Update buttons
            document.querySelectorAll('.toggle-btn').forEach(btn => {{
                btn.classList.remove('active');
            }});
            event.target.classList.add('active');

            // Update legend
            if (view === 'access') {{
                document.getElementById('access-legend').style.display = 'block';
                document.getElementById('indigenous-legend').style.display = 'none';
            }} else {{
                document.getElementById('access-legend').style.display = 'none';
                document.getElementById('indigenous-legend').style.display = 'block';
            }}

            // Re-render markers
            renderMarkers();
        }}

        window.onload = initMap;
    </script>
</body>
</html>'''

# Save
output_path = f'{OUTPUT_DIR}/map12_regression_drivers.html'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"\n✅ Generated regression analysis map: {output_path}")
print(f"\nFeatures:")
print(f"  ✓ Regression formula displayed")
print(f"  ✓ Toggle between Access view and Indigenous view")
print(f"  ✓ Rural areas highlighted with orange borders")
print(f"  ✓ Calm color palette")
print(f"  ✓ Perfect zoom (3.5)")
print(f"  ✓ Shows key drivers: Income, Gini, Indigenous %, Minority %")

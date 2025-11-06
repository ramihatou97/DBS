#!/usr/bin/env python3
"""
Generate Enhanced Regression Analysis Map with clear messaging
Shows what drives DBS access disparities based on regression model
"""

import pandas as pd
import json
import numpy as np

BASE_DIR = '/Users/ramihatoum/Desktop/PPA/maps/final'
FSA_AGG_PATH = f'{BASE_DIR}/fsa_aggregated_data_current.csv'
OUTPUT_DIR = f'{BASE_DIR}/maps_nov2025'

# Load data
print("Loading FSA data for regression visualization...")
fsa_data = pd.read_csv(FSA_AGG_PATH)
print(f"  ✓ Loaded {len(fsa_data)} FSAs")

# Color scheme matching other maps
COLORS = {
    'good_access': '#10b981',      # Emerald-500 - good access (<200km)
    'poor_access': '#ef4444',      # Red-500 - poor access (>200km)
    'indigenous_low': '#fef3c7',   # Amber-100
    'indigenous_mid': '#fde047',   # Yellow-300
    'indigenous_high': '#fdba74',  # Orange-300
    'indigenous_very_high': '#f87171',  # Red-400
    'rural_border': '#f97316',     # Orange-500 for rural outline
    'urban_border': '#cbd5e1',     # Slate-300 for urban
    'text': '#475569'
}

# Calculate statistics for key findings
good_access = len(fsa_data[fsa_data['avg_distance_km'] <= 200])
poor_access = len(fsa_data[fsa_data['avg_distance_km'] > 200])
poor_access_pct = (poor_access / len(fsa_data)) * 100

# Calculate correlation insights
indigenous_high = fsa_data[fsa_data['indigenous_ancestry_rate'] > 10]
indigenous_high_poor_access = len(indigenous_high[indigenous_high['avg_distance_km'] > 200])
indigenous_high_poor_access_pct = (indigenous_high_poor_access / len(indigenous_high)) * 100 if len(indigenous_high) > 0 else 0

# Calculate regression-based predictions and disparities
markers_data = []
for _, row in fsa_data.iterrows():
    if pd.notna(row['latitude']) and pd.notna(row['longitude']):
        distance = row['avg_distance_km']
        indigenous = row.get('indigenous_ancestry_rate', 0)
        income = row.get('median_household_income_2020', 0)
        gini = row.get('gini_index', 0)

        # Binary classification: Good vs Poor access
        is_poor_access = distance > 200

        # Indigenous rate categories
        if indigenous > 25:
            indigenous_color = COLORS['indigenous_very_high']
            indigenous_category = 'Very High (>25%)'
        elif indigenous > 10:
            indigenous_color = COLORS['indigenous_high']
            indigenous_category = 'High (10-25%)'
        elif indigenous > 5:
            indigenous_color = COLORS['indigenous_mid']
            indigenous_category = 'Moderate (5-10%)'
        else:
            indigenous_color = COLORS['indigenous_low']
            indigenous_category = 'Low (<5%)'

        # Determine if rural
        is_rural = row.get('rural', 0) == 1 if 'rural' in row else False

        markers_data.append({
            'lat': float(row['latitude']),
            'lng': float(row['longitude']),
            'fsa': row['FSA'],
            'distance': round(distance, 1),
            'indigenous': round(indigenous, 1),
            'indigenous_category': indigenous_category,
            'income': int(income) if pd.notna(income) else 0,
            'gini': round(float(gini), 3) if pd.notna(gini) else 0,
            'access_color': COLORS['poor_access'] if is_poor_access else COLORS['good_access'],
            'indigenous_color': indigenous_color,
            'is_rural': is_rural,
            'border_color': COLORS['rural_border'] if is_rural else COLORS['urban_border'],
            'border_weight': 2.5 if is_rural else 1.5,
            'size': 9 if is_poor_access else 7
        })

print(f"  ✓ Prepared {len(markers_data)} markers with regression data")
print(f"\n  Key Statistics:")
print(f"    Communities with good access (<200km): {good_access} ({100-poor_access_pct:.1f}%)")
print(f"    Communities with poor access (>200km): {poor_access} ({poor_access_pct:.1f}%)")
print(f"    High Indigenous communities with poor access: {indigenous_high_poor_access}/{len(indigenous_high)} ({indigenous_high_poor_access_pct:.1f}%)")

# Generate HTML
html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>What Drives DBS Access Disparities?</title>
    <script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyBH_yuU7_TfAJmuf_h04UsmKKhC0XPWerA"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Inter', sans-serif; background: #f8fafc; overflow: hidden; }}
        #map {{ width: 100%; height: 100vh; }}

        .info-panel {{
            position: absolute; top: 16px; left: 16px; background: rgba(255, 255, 255, 0.97);
            padding: 16px 20px; border-radius: 10px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            max-width: 360px; z-index: 1000; border: 1px solid #e2e8f0;
        }}

        .info-title {{
            font-size: 15px; font-weight: 600; color: #1e293b; margin-bottom: 10px;
            letter-spacing: -0.02em;
        }}

        .info-text {{
            font-size: 11px; color: #64748b; line-height: 1.6; margin-bottom: 10px;
        }}

        .driver-list {{
            background: #f8fafc; padding: 10px 12px; border-radius: 6px; border-left: 3px solid #3b82f6;
        }}

        .driver-item {{
            font-size: 11px; color: #475569; line-height: 1.7; font-family: 'Inter', sans-serif;
            font-weight: 400;
        }}

        .driver-label {{
            font-weight: 600; color: #1e293b;
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

        .legend-color {{
            width: 14px; height: 14px; border-radius: 2px; border: 1px solid rgba(0,0,0,0.1);
        }}

        .view-toggle {{
            position: absolute; top: 16px; right: 16px; background: rgba(255, 255, 255, 0.97);
            padding: 10px 12px; border-radius: 10px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            z-index: 1000; border: 1px solid #e2e8f0;
        }}

        .toggle-label {{
            font-size: 10px; font-weight: 600; color: #64748b; text-transform: uppercase;
            letter-spacing: 0.04em; margin-bottom: 8px;
        }}

        .toggle-buttons {{
            display: flex; gap: 8px;
        }}

        .toggle-btn {{
            padding: 7px 14px; font-size: 11px; font-weight: 500; border: 1px solid #e2e8f0;
            background: white; color: #64748b; border-radius: 6px; cursor: pointer;
            transition: all 0.2s; font-family: 'Inter', sans-serif;
        }}

        .toggle-btn.active {{
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            color: white; border-color: #3b82f6; font-weight: 600;
        }}

        .toggle-btn:hover {{ background: #f8fafc; }}
        .toggle-btn.active:hover {{ background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); }}

        .key-finding {{
            position: absolute; bottom: 20px; left: 16px; background: rgba(255, 255, 255, 0.97);
            padding: 14px 16px; border-radius: 10px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            z-index: 1000; border: 1px solid #e2e8f0; max-width: 360px;
            border-left: 4px solid #3b82f6;
        }}

        .key-finding-header {{
            display: flex; align-items: center; gap: 8px; margin-bottom: 6px;
        }}

        .key-finding-icon {{
            font-size: 16px;
        }}

        .key-finding-title {{
            font-size: 11px; font-weight: 700; color: #3b82f6;
            text-transform: uppercase; letter-spacing: 0.05em;
        }}

        .key-finding-text {{
            font-size: 11px; color: #475569; line-height: 1.5; font-weight: 400;
        }}
    </style>
</head>
<body>
    <div class="info-panel">
        <div class="info-title">What Drives DBS Access Disparities?</div>
        <div class="info-text">
            Our regression analysis reveals the key factors predicting poor access to DBS centers across Canada.
        </div>
        <div class="driver-list">
            <div class="driver-item"><span class="driver-label">Indigenous Ancestry</span>: Higher rates strongly predict longer distances</div>
            <div class="driver-item" style="margin-top: 5px;"><span class="driver-label">Income Inequality (Gini)</span>: More unequal areas face worse access</div>
            <div class="driver-item" style="margin-top: 5px;"><span class="driver-label">Median Income</span>: Minimal effect on geographic access</div>
            <div class="driver-item" style="margin-top: 5px;"><span class="driver-label">Visible Minority</span>: Small negative association</div>
        </div>
    </div>

    <div class="view-toggle">
        <div class="toggle-label">Map View</div>
        <div class="toggle-buttons">
            <button class="toggle-btn active" onclick="switchView('access')">Access</button>
            <button class="toggle-btn" onclick="switchView('indigenous')">Indigenous</button>
        </div>
    </div>

    <div class="key-finding">
        <div class="key-finding-header">
            <span class="key-finding-icon">📊</span>
            <div class="key-finding-title">Key Insight</div>
        </div>
        <div class="key-finding-text">
            Indigenous ancestry is the strongest predictor of poor access. Communities with >10% Indigenous population
            are {indigenous_high_poor_access_pct:.0f}% likely to be >200km from DBS centers, revealing systematic geographic inequity.
        </div>
    </div>

    <div id="map"></div>

    <div class="legend">
        <div class="legend-section" id="access-legend">
            <div class="legend-title">Distance to Care</div>
            <div class="legend-item">
                <div class="legend-color" style="background:{COLORS['good_access']}"></div>
                <span>&lt;200 km</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background:{COLORS['poor_access']}"></div>
                <span>&gt;200 km</span>
            </div>
        </div>

        <div class="legend-section" id="indigenous-legend" style="display:none;">
            <div class="legend-title">Indigenous Rate</div>
            <div class="legend-item">
                <div class="legend-color" style="background:{COLORS['indigenous_low']}"></div>
                <span>&lt;5%</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background:{COLORS['indigenous_mid']}"></div>
                <span>5-10%</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background:{COLORS['indigenous_high']}"></div>
                <span>10-25%</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background:{COLORS['indigenous_very_high']}"></div>
                <span>&gt;25%</span>
            </div>
        </div>

        <div class="legend-section">
            <div class="legend-title">Geography</div>
            <div class="legend-item">
                <div style="width:14px; height:14px; border:2.5px solid {COLORS['rural_border']}; border-radius:2px;"></div>
                <span>Rural</span>
            </div>
            <div class="legend-item">
                <div style="width:14px; height:14px; border:1.5px solid {COLORS['urban_border']}; border-radius:2px;"></div>
                <span>Urban</span>
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
                       stylers: [{{ color: '#cbd5e1' }}, {{ weight: 1.5 }}] }},
                    {{ featureType: 'water', elementType: 'geometry', stylers: [{{ color: '#dbeafe' }}] }},
                    {{ featureType: 'landscape', elementType: 'geometry', stylers: [{{ color: '#f8fafc' }}] }},
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
                        scale: data.size,
                        fillColor: color,
                        fillOpacity: 0.8,
                        strokeColor: data.border_color,
                        strokeWeight: data.border_weight
                    }},
                    zIndex: data.is_rural ? 200 : 100
                }});

                const infoWindow = new google.maps.InfoWindow({{
                    content: `
                        <div style="font-family: Inter, sans-serif; padding: 10px; min-width: 200px;">
                            <div style="font-size: 14px; font-weight: 600; color: #1e293b; margin-bottom: 10px;">
                                ${{data.fsa}}
                            </div>
                            <div style="font-size: 11px; color: #475569; line-height: 1.7;">
                                <strong>Distance:</strong> ${{data.distance}} km<br>
                                <strong>Indigenous:</strong> ${{data.indigenous}}% (${{data.indigenous_category}})<br>
                                <strong>Median Income:</strong> $$${{data.income.toLocaleString()}}<br>
                                <strong>Gini Index:</strong> ${{data.gini}}<br>
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

print(f"\n✅ Generated enhanced regression analysis map: {output_path}")
print(f"\nFeatures:")
print(f"  ✓ Standardized Inter font throughout")
print(f"  ✓ Clear plain-language explanation of drivers")
print(f"  ✓ Key finding box with insight")
print(f"  ✓ Toggle between Access and Indigenous views")
print(f"  ✓ Rural/Urban differentiation with border styling")
print(f"  ✓ Perfect zoom (3.5) showing all of Canada")
print(f"  ✓ Clean, comprehensible messaging")

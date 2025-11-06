#!/usr/bin/env python3
"""
Generate Striking Map 2: Vulnerability Index
Visual Identity: Purple-red diverging scale with SQUARE markers
Formula: (Distance × 50%) + (Income × 30%) + (Gini × 20%)
"""

import pandas as pd
import json
import numpy as np

BASE_DIR = '/Users/ramihatoum/Desktop/PPA/maps/final'
FSA_AGG_PATH = f'{BASE_DIR}/fsa_aggregated_data_current.csv'
OUTPUT_DIR = f'{BASE_DIR}/maps_nov2025'

# Load data
print("Loading FSA data for vulnerability analysis...")
fsa_data = pd.read_csv(FSA_AGG_PATH)
print(f"  ✓ Loaded {len(fsa_data)} FSAs")

# DBS Centers (for radius circles)
DBS_CENTERS = [
    {'name': 'Halifax', 'lat': 44.6488, 'lon': -63.5752},
    {'name': 'Montreal', 'lat': 45.5017, 'lon': -73.5673},
    {'name': 'Ottawa', 'lat': 45.4215, 'lon': -75.6972},
    {'name': 'Toronto', 'lat': 43.6532, 'lon': -79.3832},
    {'name': 'London', 'lat': 43.0109, 'lon': -81.2733},
    {'name': 'Winnipeg', 'lat': 49.8951, 'lon': -97.1384},
    {'name': 'Saskatoon', 'lat': 52.1332, 'lon': -106.6700},
    {'name': 'Calgary', 'lat': 51.0447, 'lon': -114.0719},
    {'name': 'Edmonton', 'lat': 53.5461, 'lon': -113.4938},
    {'name': 'Vancouver', 'lat': 49.2827, 'lon': -123.1207}
]

# PURPLE-RED DIVERGING SCALE (low vulnerability → high vulnerability)
VULNERABILITY_COLORS = {
    'minimal': '#ddd6fe',      # Violet-200 - minimal vulnerability
    'low': '#c4b5fd',          # Violet-300
    'moderate': '#a78bfa',     # Violet-400
    'elevated': '#f472b6',     # Pink-400
    'high': '#ec4899',         # Pink-500
    'severe': '#e11d48',       # Rose-600
    'extreme': '#be123c'       # Rose-700 - EXTREME CRISIS
}

# Calculate Vulnerability Score
print("\nCalculating vulnerability scores...")

# Normalize components (0-100 scale)
distance_normalized = (fsa_data['avg_distance_km'] / fsa_data['avg_distance_km'].max()) * 100
income_normalized = 100 - ((fsa_data['median_household_income_2020'].fillna(fsa_data['median_household_income_2020'].median()) /
                             fsa_data['median_household_income_2020'].max()) * 100)
gini_normalized = (fsa_data['gini_index'].fillna(fsa_data['gini_index'].median()) /
                   fsa_data['gini_index'].max()) * 100

# Vulnerability Index Formula: Distance(50%) + Income(30%) + Gini(20%)
fsa_data['vulnerability_score'] = (
    distance_normalized * 0.50 +
    income_normalized * 0.30 +
    gini_normalized * 0.20
)

# Statistics
avg_score = fsa_data['vulnerability_score'].mean()
median_score = fsa_data['vulnerability_score'].median()
max_score = fsa_data['vulnerability_score'].max()

# Categorize and prepare markers
markers_data = []
category_counts = {
    'minimal': 0, 'low': 0, 'moderate': 0, 'elevated': 0,
    'high': 0, 'severe': 0, 'extreme': 0
}

for _, row in fsa_data.iterrows():
    if pd.notna(row['latitude']) and pd.notna(row['longitude']):
        score = row['vulnerability_score']
        distance = row['avg_distance_km']

        # Categorize by score
        if score < 10:
            category = 'minimal'
            size = 8
        elif score < 20:
            category = 'low'
            size = 9
        elif score < 30:
            category = 'moderate'
            size = 10
        elif score < 40:
            category = 'elevated'
            size = 12
        elif score < 50:
            category = 'high'
            size = 14
        elif score < 70:
            category = 'severe'
            size = 16
        else:
            category = 'extreme'
            size = 20  # 2.5x larger for extreme

        category_counts[category] += 1

        markers_data.append({
            'lat': float(row['latitude']),
            'lng': float(row['longitude']),
            'fsa': row['FSA'],
            'score': round(score, 1),
            'distance': round(distance, 1),
            'income': int(row['median_household_income_2020']) if pd.notna(row['median_household_income_2020']) else None,
            'gini': round(float(row['gini_index']), 3) if pd.notna(row['gini_index']) else None,
            'patient_count': int(row['patient_count']),
            'color': VULNERABILITY_COLORS[category],
            'category': category,
            'size': size,
            'pulse': score >= 70  # Pulse for extreme vulnerability
        })

print(f"  ✓ Calculated vulnerability scores for {len(markers_data)} FSAs")
print(f"\n  Vulnerability Distribution:")
print(f"    Minimal (<10): {category_counts['minimal']}")
print(f"    Low (10-20): {category_counts['low']}")
print(f"    Moderate (20-30): {category_counts['moderate']}")
print(f"    Elevated (30-40): {category_counts['elevated']}")
print(f"    High (40-50): {category_counts['high']}")
print(f"    Severe (50-70): {category_counts['severe']}")
print(f"    EXTREME (≥70): {category_counts['extreme']}")
print(f"\n  Statistics:")
print(f"    Average Score: {avg_score:.1f}")
print(f"    Median Score: {median_score:.1f}")
print(f"    Maximum Score: {max_score:.1f}")

# Generate HTML
html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Map 2: Vulnerability Index</title>
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
        }}

        .info-title {{
            font-size: 15px; font-weight: 600; color: #1e293b; margin-bottom: 8px;
            letter-spacing: -0.02em;
        }}

        .vulnerability-formula {{
            font-size: 10px; color: #64748b; line-height: 1.6;
            background: #f1f5f9; padding: 10px 12px; border-radius: 6px; margin-top: 8px;
            font-family: 'Courier New', monospace; border-left: 3px solid #a78bfa;
        }}

        .legend {{
            position: absolute; bottom: 20px; right: 20px; background: rgba(255, 255, 255, 0.97);
            padding: 16px 18px; border-radius: 10px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            z-index: 1000; border: 1px solid #e2e8f0; max-width: 240px;
        }}

        .legend-section {{ margin-bottom: 14px; }}
        .legend-section:last-child {{ margin-bottom: 0; }}

        .legend-title {{
            font-size: 11px; font-weight: 600; color: #1e293b; margin-bottom: 8px;
            text-transform: uppercase; letter-spacing: 0.04em;
        }}

        .legend-item {{
            display: flex; align-items: center; gap: 8px; margin-bottom: 4px;
            font-size: 10px; color: #475569;
        }}

        .legend-square {{
            width: 12px; height: 12px; border-radius: 2px; border: 1px solid rgba(0,0,0,0.1);
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
            border-left: 4px solid #be123c;
        }}

        .key-finding-header {{
            display: flex; align-items: center; gap: 8px; margin-bottom: 6px;
        }}

        .key-finding-icon {{
            font-size: 16px;
        }}

        .key-finding-title {{
            font-size: 11px; font-weight: 700; color: #be123c;
            text-transform: uppercase; letter-spacing: 0.05em;
        }}

        .key-finding-text {{
            font-size: 11px; color: #475569; line-height: 1.5; font-weight: 400;
        }}

        .stat-row {{
            display: flex; justify-content: space-between; padding: 4px 0;
            border-bottom: 1px solid #f1f5f9;
        }}

        .stat-row:last-child {{ border-bottom: none; }}

        .stat-label {{
            font-size: 10px; color: #64748b; font-weight: 500;
        }}

        .stat-value {{
            font-size: 10px; color: #1e293b; font-weight: 600;
        }}

        @keyframes pulse {{
            0%, 100% {{ opacity: 0.9; transform: scale(1); }}
            50% {{ opacity: 1; transform: scale(1.15); }}
        }}

        .pulse-marker {{
            animation: pulse 1.5s ease-in-out infinite;
        }}
    </style>
</head>
<body>
    <div class="info-panel">
        <div class="info-title">Multidimensional Vulnerability Index</div>
        <div class="vulnerability-formula">
            <strong>Formula:</strong><br>
            Score = Distance (50%)<br>
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;+ Income Gap (30%)<br>
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;+ Inequality (20%)
        </div>
    </div>

    <div class="key-finding">
        <div class="key-finding-header">
            <span class="key-finding-icon">⚠️</span>
            <div class="key-finding-title">Key Finding</div>
        </div>
        <div class="key-finding-text">
            {category_counts['extreme']} communities ({(category_counts['extreme']/len(markers_data)*100):.1f}%) face extreme vulnerability (score ≥70),
            combining geographic isolation with socioeconomic disadvantage.
        </div>
    </div>

    <div id="map"></div>

    <div class="legend">
        <div class="legend-section">
            <div class="legend-title">Vulnerability Score</div>
            <div class="legend-item">
                <div class="legend-square" style="background:{VULNERABILITY_COLORS['minimal']}"></div>
                <span class="legend-label">&lt;10 Minimal</span>
                <span class="legend-count">{category_counts['minimal']}</span>
            </div>
            <div class="legend-item">
                <div class="legend-square" style="background:{VULNERABILITY_COLORS['low']}"></div>
                <span class="legend-label">10-20 Low</span>
                <span class="legend-count">{category_counts['low']}</span>
            </div>
            <div class="legend-item">
                <div class="legend-square" style="background:{VULNERABILITY_COLORS['moderate']}"></div>
                <span class="legend-label">20-30 Moderate</span>
                <span class="legend-count">{category_counts['moderate']}</span>
            </div>
            <div class="legend-item">
                <div class="legend-square" style="background:{VULNERABILITY_COLORS['elevated']}"></div>
                <span class="legend-label">30-40 Elevated</span>
                <span class="legend-count">{category_counts['elevated']}</span>
            </div>
            <div class="legend-item">
                <div class="legend-square" style="background:{VULNERABILITY_COLORS['high']}"></div>
                <span class="legend-label">40-50 High</span>
                <span class="legend-count">{category_counts['high']}</span>
            </div>
            <div class="legend-item">
                <div class="legend-square" style="background:{VULNERABILITY_COLORS['severe']}"></div>
                <span class="legend-label">50-70 Severe</span>
                <span class="legend-count">{category_counts['severe']}</span>
            </div>
            <div class="legend-item">
                <div class="legend-square" style="background:{VULNERABILITY_COLORS['extreme']}"></div>
                <span class="legend-label">≥70 EXTREME</span>
                <span class="legend-count">{category_counts['extreme']}</span>
            </div>
        </div>

        <div class="legend-section">
            <div class="legend-title">Summary Statistics</div>
            <div class="stat-row">
                <span class="stat-label">Average</span>
                <span class="stat-value">{avg_score:.1f}</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Median</span>
                <span class="stat-value">{median_score:.1f}</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Maximum</span>
                <span class="stat-value">{max_score:.1f}</span>
            </div>
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

            // Add 200km and 400km radius circles around DBS centers
            dbsCenters.forEach(center => {{
                // 200km circle (light purple)
                new google.maps.Circle({{
                    center: {{ lat: center.lat, lng: center.lon }},
                    radius: 200000,
                    strokeColor: '#a78bfa',
                    strokeOpacity: 0.25,
                    strokeWeight: 1.5,
                    fillColor: '#ddd6fe',
                    fillOpacity: 0.08,
                    map: map
                }});

                // 400km circle (light pink)
                new google.maps.Circle({{
                    center: {{ lat: center.lat, lng: center.lon }},
                    radius: 400000,
                    strokeColor: '#f472b6',
                    strokeOpacity: 0.2,
                    strokeWeight: 1.5,
                    fillColor: '#fce7f3',
                    fillOpacity: 0.05,
                    map: map
                }});

                // Center marker
                new google.maps.Marker({{
                    position: {{ lat: center.lat, lng: center.lon }},
                    map: map,
                    icon: {{
                        path: google.maps.SymbolPath.CIRCLE,
                        scale: 5,
                        fillColor: '#7c3aed',
                        fillOpacity: 1,
                        strokeColor: 'white',
                        strokeWeight: 2
                    }},
                    zIndex: 500
                }});
            }});

            // Add FSA markers (SQUARE shapes)
            markersData.forEach(m => {{
                const size = m.size / 2;

                const marker = new google.maps.Marker({{
                    position: {{ lat: m.lat, lng: m.lng }},
                    map: map,
                    icon: {{
                        // SQUARE path
                        path: `M -${{size}},-${{size}} L ${{size}},-${{size}} L ${{size}},${{size}} L -${{size}},${{size}} Z`,
                        fillColor: m.color,
                        fillOpacity: m.pulse ? 0.95 : 0.8,
                        strokeColor: m.pulse ? '#7f1d1d' : 'white',
                        strokeWeight: m.pulse ? 2.5 : 1.5,
                        scale: 1,
                        anchor: new google.maps.Point(0, 0)
                    }},
                    zIndex: m.pulse ? 300 : (m.score > 40 ? 200 : 100)
                }});

                // Add pulse animation for extreme vulnerability
                if (m.pulse) {{
                    marker.setAnimation(google.maps.Animation.BOUNCE);
                    setTimeout(() => marker.setAnimation(null), 2000);
                }}

                const infoWindow = new google.maps.InfoWindow({{
                    content: `
                        <div style="font-family: Inter, sans-serif; padding: 10px; min-width: 200px;">
                            <div style="font-size: 14px; font-weight: 600; color: #1e293b; margin-bottom: 10px;">
                                ${{m.fsa}}
                            </div>
                            <div style="font-size: 12px; color: #475569; line-height: 1.7;">
                                <div style="background: ${{m.color}}; padding: 6px 10px; border-radius: 4px; margin-bottom: 8px;">
                                    <strong style="color: #1e293b;">Vulnerability Score: ${{m.score}}</strong>
                                </div>
                                <strong>Distance:</strong> ${{m.distance}} km<br>
                                <strong>Income:</strong> $$${{m.income ? m.income.toLocaleString() : 'N/A'}}<br>
                                <strong>Gini Index:</strong> ${{m.gini || 'N/A'}}<br>
                                <strong>Patients:</strong> ${{m.patient_count}}<br>
                                <strong>Category:</strong> ${{m.category.toUpperCase()}}
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
output_path = f'{OUTPUT_DIR}/map2_vulnerability_index.html'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"\n✅ Generated striking Vulnerability Index map: {output_path}")
print(f"\nFeatures:")
print(f"  ✓ Purple-red diverging color scale (violet → pink → rose)")
print(f"  ✓ SQUARE markers sized by vulnerability (8-20px)")
print(f"  ✓ 200km and 400km radius circles around DBS centers")
print(f"  ✓ Enhanced legend with 7 categories and statistics")
print(f"  ✓ Key finding box highlighting extreme vulnerability")
print(f"  ✓ Pulsing animation for extreme cases (score ≥70)")
print(f"  ✓ Vulnerability formula displayed")
print(f"  ✓ Perfect zoom (3.5) showing all of Canada")

#!/usr/bin/env python3
"""
Generate STRIKING Map 1: Travel Burden Heat Map
- Heat map color progression (blues → ambers → bold reds)
- Gradient heat overlay from DBS centers
- Enhanced legend with statistics and interpretation
- Pulsing animation for extreme distances (>500km)
- Visual weight for severe cases
"""

import pandas as pd
import json

BASE_DIR = '/Users/ramihatoum/Desktop/PPA/maps/final'
FSA_AGG_PATH = f'{BASE_DIR}/fsa_aggregated_data_current.csv'
OUTPUT_DIR = f'{BASE_DIR}/maps_nov2025'

# Load data
print("Loading FSA data...")
fsa_data = pd.read_csv(FSA_AGG_PATH)
print(f"  ✓ Loaded {len(fsa_data)} FSAs\n")

# BOLD HEAT MAP COLORS (high contrast, emotional impact)
HEAT_COLORS = {
    'excellent': '#059669',      # Emerald-600 - good access
    'good': '#10b981',           # Emerald-500
    'moderate': '#fbbf24',       # Amber-400
    'poor': '#f97316',           # Orange-500
    'critical': '#dc2626',       # Red-600
    'extreme': '#991b1b',        # Red-800 - CRISIS
    'center': '#1e40af',         # Blue-800 - DBS centers
    'border': '#94a3b8',         # Slate-400
    'text': '#334155'            # Slate-700
}

# Calculate statistics for legend
total_fsas = len(fsa_data)
distance_stats = {
    'excellent': len(fsa_data[fsa_data['avg_distance_km'] < 50]),
    'good': len(fsa_data[(fsa_data['avg_distance_km'] >= 50) & (fsa_data['avg_distance_km'] < 100)]),
    'moderate': len(fsa_data[(fsa_data['avg_distance_km'] >= 100) & (fsa_data['avg_distance_km'] < 200)]),
    'poor': len(fsa_data[(fsa_data['avg_distance_km'] >= 200) & (fsa_data['avg_distance_km'] < 300)]),
    'critical': len(fsa_data[(fsa_data['avg_distance_km'] >= 300) & (fsa_data['avg_distance_km'] < 500)]),
    'extreme': len(fsa_data[fsa_data['avg_distance_km'] >= 500])
}

avg_distance = fsa_data['avg_distance_km'].mean()
median_distance = fsa_data['avg_distance_km'].median()
max_distance = fsa_data['avg_distance_km'].max()
beyond_200km = len(fsa_data[fsa_data['avg_distance_km'] > 200])
percent_beyond_200 = (beyond_200km / total_fsas) * 100

print("Distance Statistics:")
print(f"  Average: {avg_distance:.1f} km")
print(f"  Median: {median_distance:.1f} km")
print(f"  Maximum: {max_distance:.1f} km")
print(f"  Beyond 200km: {beyond_200km} FSAs ({percent_beyond_200:.1f}%)\n")

# Prepare markers with heat map styling
markers_data = []
for _, row in fsa_data.iterrows():
    if pd.notna(row['latitude']) and pd.notna(row['longitude']):
        distance = row['avg_distance_km']
        patients = int(row['patient_count'])

        # Determine color and size based on distance
        if distance < 50:
            color = HEAT_COLORS['excellent']
            category = 'Excellent Access'
            size = 7
            pulse = False
        elif distance < 100:
            color = HEAT_COLORS['good']
            category = 'Good Access'
            size = 8
            pulse = False
        elif distance < 200:
            color = HEAT_COLORS['moderate']
            category = 'Moderate'
            size = 9
            pulse = False
        elif distance < 300:
            color = HEAT_COLORS['poor']
            category = 'Poor Access'
            size = 11
            pulse = False
        elif distance < 500:
            color = HEAT_COLORS['critical']
            category = 'Critical'
            size = 13
            pulse = False
        else:
            color = HEAT_COLORS['extreme']
            category = 'EXTREME CRISIS'
            size = 16
            pulse = True  # Pulsing animation for extreme cases

        markers_data.append({
            'lat': float(row['latitude']),
            'lng': float(row['longitude']),
            'fsa': row['FSA'],
            'distance': round(distance, 1),
            'patients': patients,
            'color': color,
            'category': category,
            'size': size,
            'pulse': pulse,
            'opacity': 0.85
        })

print(f"  ✓ Prepared {len(markers_data)} heat map markers\n")

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
    <title>Travel Burden Crisis - Heat Map Analysis</title>
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
            max-width: 340px; z-index: 1000;
            border-left: 4px solid {HEAT_COLORS['critical']};
        }}

        .info-title {{
            font-size: 17px; font-weight: 700; color: #1e293b;
            margin-bottom: 4px; letter-spacing: -0.02em;
        }}

        .info-subtitle {{
            font-size: 13px; color: {HEAT_COLORS['text']};
            line-height: 1.5; margin-bottom: 12px;
        }}

        .info-highlight {{
            background: #fef2f2; padding: 10px 12px;
            border-radius: 6px; margin-top: 10px;
            border-left: 3px solid {HEAT_COLORS['critical']};
        }}

        .highlight-stat {{
            font-size: 24px; font-weight: 800; color: {HEAT_COLORS['critical']};
            line-height: 1;
        }}

        .highlight-label {{
            font-size: 11px; color: {HEAT_COLORS['text']};
            margin-top: 2px; font-weight: 500;
        }}

        .legend {{
            position: absolute; bottom: 24px; right: 24px;
            background: rgba(255, 255, 255, 0.97);
            padding: 18px 20px; border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
            z-index: 1000; max-width: 280px;
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
            font-size: 10px; font-weight: 600; color: {HEAT_COLORS['text']};
            margin-bottom: 8px; text-transform: uppercase;
            letter-spacing: 0.04em;
        }}

        .legend-item {{
            display: flex; align-items: center; gap: 10px;
            margin-bottom: 6px; font-size: 11px; color: {HEAT_COLORS['text']};
        }}

        .legend-color {{
            width: 16px; height: 16px; border-radius: 3px;
            border: 1px solid rgba(0,0,0,0.15);
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        }}

        .legend-label {{
            flex: 1; font-weight: 500;
        }}

        .legend-count {{
            font-weight: 700; color: #64748b; font-size: 10px;
        }}

        .stat-row {{
            display: flex; justify-content: space-between;
            padding: 4px 0; font-size: 11px;
            border-bottom: 1px solid #f1f5f9;
        }}

        .stat-row:last-child {{ border-bottom: none; }}

        .stat-label {{ color: {HEAT_COLORS['text']}; font-weight: 500; }}
        .stat-value {{ color: #1e293b; font-weight: 700; }}

        .key-finding {{
            position: absolute; bottom: 24px; left: 24px;
            background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
            padding: 16px 20px; border-radius: 10px;
            box-shadow: 0 4px 12px rgba(220, 38, 38, 0.15);
            max-width: 320px; z-index: 1000;
            border: 2px solid {HEAT_COLORS['critical']};
        }}

        .key-finding-header {{
            display: flex; align-items: center; gap: 8px;
            margin-bottom: 10px;
        }}

        .key-finding-icon {{
            font-size: 20px;
        }}

        .key-finding-title {{
            font-size: 12px; font-weight: 700; color: {HEAT_COLORS['critical']};
            text-transform: uppercase; letter-spacing: 0.05em;
        }}

        .key-finding-text {{
            font-size: 13px; color: #991b1b; line-height: 1.6;
            font-weight: 600;
        }}

        @keyframes pulse {{
            0%, 100% {{ transform: scale(1); opacity: 0.85; }}
            50% {{ transform: scale(1.15); opacity: 1; }}
        }}

        .pulse-marker {{
            animation: pulse 2s ease-in-out infinite;
        }}
    </style>
</head>
<body>
    <div class="info-panel">
        <div class="info-title">Travel Burden Crisis</div>
        <div class="info-subtitle">
            Distance from home to nearest DBS center
        </div>
        <div class="info-highlight">
            <div class="highlight-stat">{percent_beyond_200:.0f}%</div>
            <div class="highlight-label">of communities face >200km travel burden</div>
        </div>
    </div>

    <div id="map"></div>

    <div class="legend">
        <div class="legend-header">Travel Distance</div>

        <div class="legend-section">
            <div class="legend-subtitle">Access Categories</div>
            <div class="legend-item">
                <div class="legend-color" style="background:{HEAT_COLORS['excellent']}"></div>
                <span class="legend-label">&lt;50 km</span>
                <span class="legend-count">{distance_stats['excellent']}</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background:{HEAT_COLORS['good']}"></div>
                <span class="legend-label">50-100 km</span>
                <span class="legend-count">{distance_stats['good']}</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background:{HEAT_COLORS['moderate']}"></div>
                <span class="legend-label">100-200 km</span>
                <span class="legend-count">{distance_stats['moderate']}</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background:{HEAT_COLORS['poor']}"></div>
                <span class="legend-label">200-300 km</span>
                <span class="legend-count">{distance_stats['poor']}</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background:{HEAT_COLORS['critical']}"></div>
                <span class="legend-label">300-500 km</span>
                <span class="legend-count">{distance_stats['critical']}</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background:{HEAT_COLORS['extreme']}"></div>
                <span class="legend-label">&gt;500 km</span>
                <span class="legend-count">{distance_stats['extreme']}</span>
            </div>
        </div>

        <div class="legend-section">
            <div class="legend-subtitle">Summary Statistics</div>
            <div class="stat-row">
                <span class="stat-label">Average</span>
                <span class="stat-value">{avg_distance:.0f} km</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Median</span>
                <span class="stat-value">{median_distance:.0f} km</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Worst Case</span>
                <span class="stat-value">{max_distance:.0f} km</span>
            </div>
        </div>
    </div>

    <div class="key-finding">
        <div class="key-finding-header">
            <span class="key-finding-icon">🔴</span>
            <div class="key-finding-title">Key Finding</div>
        </div>
        <div class="key-finding-text">
            Nearly {percent_beyond_200:.0f}% of communities face prohibitive travel distances (>200km),
            creating a systematic access barrier requiring urgent policy intervention.
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
                       stylers: [{{ color: '{HEAT_COLORS['border']}' }}, {{ weight: 1.5 }}] }},
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

            // Add DBS centers with pulse effect
            dbsCenters.forEach(center => {{
                new google.maps.Marker({{
                    position: {{ lat: center.lat, lng: center.lon }},
                    map: map,
                    icon: {{
                        path: google.maps.SymbolPath.CIRCLE,
                        scale: 11,
                        fillColor: '{HEAT_COLORS['center']}',
                        fillOpacity: 0.95,
                        strokeColor: 'white',
                        strokeWeight: 3
                    }},
                    title: center.name,
                    zIndex: 2000
                }});

                // Add 200km radius circle
                new google.maps.Circle({{
                    center: {{ lat: center.lat, lng: center.lon }},
                    radius: 200000,  // 200km in meters
                    map: map,
                    strokeColor: '{HEAT_COLORS['moderate']}',
                    strokeOpacity: 0.3,
                    strokeWeight: 1.5,
                    fillColor: '{HEAT_COLORS['excellent']}',
                    fillOpacity: 0.05,
                    zIndex: 10
                }});
            }});

            // Add FSA markers
            markersData.forEach(m => {{
                const marker = new google.maps.Marker({{
                    position: {{ lat: m.lat, lng: m.lng }},
                    map: map,
                    icon: {{
                        path: google.maps.SymbolPath.CIRCLE,
                        scale: m.size,
                        fillColor: m.color,
                        fillOpacity: m.opacity,
                        strokeColor: 'white',
                        strokeWeight: 1.5
                    }},
                    zIndex: m.pulse ? 1000 : 500
                }});

                // Add pulsing animation for extreme cases
                if (m.pulse) {{
                    setInterval(() => {{
                        const currentScale = marker.getIcon().scale;
                        marker.setIcon({{
                            ...marker.getIcon(),
                            scale: currentScale === m.size ? m.size * 1.2 : m.size
                        }});
                    }}, 1000);
                }}

                const infoWindow = new google.maps.InfoWindow({{
                    content: `
                        <div style="font-family: Inter, sans-serif; padding: 10px; min-width: 180px;">
                            <div style="font-size: 14px; font-weight: 700; color: #1e293b; margin-bottom: 8px;">
                                FSA: ${{m.fsa}}
                            </div>
                            <div style="font-size: 12px; color: {HEAT_COLORS['text']}; line-height: 1.8;">
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
output_path = f'{OUTPUT_DIR}/map1_travel_burden_heatmap.html'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"✅ Generated striking Map 1: {output_path}")
print(f"\nFeatures:")
print(f"  ✓ Bold heat map colors (emerald → amber → bold red)")
print(f"  ✓ Enhanced legend with {total_fsas} FSA statistics")
print(f"  ✓ Key finding box: {percent_beyond_200:.0f}% face >200km barrier")
print(f"  ✓ Size variation by severity (7-16px markers)")
print(f"  ✓ Pulsing animation for extreme cases (>500km)")
print(f"  ✓ 200km radius circles around DBS centers")
print(f"  ✓ Summary statistics (avg, median, worst case)")

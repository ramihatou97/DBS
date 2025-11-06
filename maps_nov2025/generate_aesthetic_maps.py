"""
ULTRA-AESTHETIC MAP GENERATOR
Perfect screen fit, patient flows always visible, elegant design
"""

import pandas as pd
import json
from pathlib import Path

API_KEY = "AIzaSyBH_yuU7_TfAJmuf_h04UsmKKhC0XPWerA"
DATA_FILE = "/Users/ramihatoum/Desktop/PPA/maps/final/fsa_aggregated_data_current.csv"
OUTPUT_DIR = "/Users/ramihatoum/Desktop/PPA/maps/final/maps_nov2025/"

print("="*100)
print("GENERATING ULTRA-AESTHETIC MAPS WITH PATIENT FLOWS")
print("="*100)

fsa_data = pd.read_csv(DATA_FILE)

DBS_CENTERS = [
    {'name': 'Toronto Western Hospital', 'city': 'Toronto', 'lat': 43.6593, 'lon': -79.3987, 'abbrev': 'TWH'},
    {'name': 'CHUM - Montreal', 'city': 'Montreal', 'lat': 45.5017, 'lon': -73.5673, 'abbrev': 'CHUM'},
    {'name': 'London Health Sciences Centre', 'city': 'London', 'lat': 43.0096, 'lon': -81.2737, 'abbrev': 'London'},
    {'name': 'Ottawa Hospital', 'city': 'Ottawa', 'lat': 45.4074, 'lon': -75.6520, 'abbrev': 'Ottawa'},
    {'name': 'Vancouver General Hospital', 'city': 'Vancouver', 'lat': 49.2827, 'lon': -123.1207, 'abbrev': 'VGH'},
    {'name': 'Foothills Medical Centre', 'city': 'Calgary', 'lat': 51.0447, 'lon': -114.0719, 'abbrev': 'Calgary'},
    {'name': 'Royal University Hospital', 'city': 'Saskatoon', 'lat': 52.1332, 'lon': -106.6700, 'abbrev': 'Saskatoon'},
    {'name': 'Health Sciences Centre', 'city': 'Winnipeg', 'lat': 49.8951, 'lon': -97.1384, 'abbrev': 'Winnipeg'},
    {'name': 'QEII Health Sciences Centre', 'city': 'Halifax', 'lat': 44.6488, 'lon': -63.5752, 'abbrev': 'Halifax'},
    {'name': 'Hôpital de l\'Enfant-Jésus', 'city': 'Quebec City', 'lat': 46.8139, 'lon': -71.2080, 'abbrev': 'Quebec'}
]

# Prepare FSA data with flow lines
fsa_markers = []
flow_lines = []

for _, row in fsa_data.iterrows():
    if pd.notnull(row['latitude']) and pd.notnull(row['longitude']):
        dist = row['avg_distance_km']

        # Smart color coding
        if pd.isnull(dist):
            color = '#94a3b8'
            category = 'Unknown'
            weight = 1
        elif dist < 50:
            color = '#10b981'  # Emerald
            category = 'Excellent'
            weight = 1
        elif dist < 100:
            color = '#84cc16'  # Lime
            category = 'Good'
            weight = 1.5
        elif dist < 200:
            color = '#f59e0b'  # Amber
            category = 'Moderate'
            weight = 2
        elif dist < 400:
            color = '#f97316'  # Orange
            category = 'Poor'
            weight = 2.5
        else:
            color = '#ef4444'  # Red
            category = 'Critical'
            weight = 3

        # Optimal marker size based on patient count
        patient_count = int(row['patient_count'])
        marker_size = min(8 + (patient_count * 2), 24)  # Range: 8-24px

        fsa_markers.append({
            'fsa': row['FSA'],
            'lat': row['latitude'],
            'lon': row['longitude'],
            'patients': patient_count,
            'distance': round(dist, 1) if pd.notnull(dist) else 0,
            'category': category,
            'color': color,
            'size': marker_size,
            'center': row['nearest_dbs_center'],
            'income': f"${int(row['median_household_income_2020']):,}" if pd.notnull(row['median_household_income_2020']) else 'N/A',
            'gini': round(row['gini_index'], 3) if pd.notnull(row['gini_index']) else 0,
            'indigenous': round(row['indigenous_ancestry_rate'], 1) if pd.notnull(row['indigenous_ancestry_rate']) else 0
        })

        # Create flow line
        center = next((c for c in DBS_CENTERS if c['name'] == row['nearest_dbs_center']), None)
        if center:
            flow_lines.append({
                'fsa_lat': row['latitude'],
                'fsa_lon': row['longitude'],
                'center_lat': center['lat'],
                'center_lon': center['lon'],
                'color': color,
                'weight': weight,
                'distance': round(dist, 1) if pd.notnull(dist) else 0,
                'opacity': 0.3 if dist < 200 else 0.5  # More visible for long distances
            })

# Calculate statistics
stats = {
    'total_patients': int(fsa_data['patient_count'].sum()),
    'total_fsas': len(fsa_data),
    'median_distance': fsa_data['avg_distance_km'].median(),
    'excellent': len(fsa_data[fsa_data['avg_distance_km'] < 50]),
    'good': len(fsa_data[(fsa_data['avg_distance_km'] >= 50) & (fsa_data['avg_distance_km'] < 100)]),
    'moderate': len(fsa_data[(fsa_data['avg_distance_km'] >= 100) & (fsa_data['avg_distance_km'] < 200)]),
    'poor': len(fsa_data[(fsa_data['avg_distance_km'] >= 200) & (fsa_data['avg_distance_km'] < 400)]),
    'critical': len(fsa_data[fsa_data['avg_distance_km'] >= 400])
}

# Center statistics
center_stats = []
for center in DBS_CENTERS:
    count = int(fsa_data[fsa_data['nearest_dbs_center'] == center['name']]['patient_count'].sum())
    fsa_count = len(fsa_data[fsa_data['nearest_dbs_center'] == center['name']])
    center_stats.append({
        **center,
        'patients': count,
        'fsas': fsa_count,
        'pct': round(100 * count / stats['total_patients'], 1) if stats['total_patients'] > 0 else 0
    })

center_stats.sort(key=lambda x: x['patients'], reverse=True)

# Generate ultra-aesthetic HTML
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DBS Patient Flow Analysis - Interactive Map</title>
    <script src="https://maps.googleapis.com/maps/api/js?key={API_KEY}"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #0f172a;
            overflow: hidden;
        }}

        #header {{
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            border-bottom: 1px solid rgba(148, 163, 184, 0.1);
            padding: 16px 24px;
            position: relative;
            z-index: 1000;
        }}

        .header-content {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        h1 {{
            color: #f1f5f9;
            font-size: 20px;
            font-weight: 600;
            letter-spacing: -0.025em;
        }}

        .stats-compact {{
            display: flex;
            gap: 24px;
            align-items: center;
        }}

        .stat-mini {{
            text-align: center;
        }}

        .stat-mini-number {{
            color: #60a5fa;
            font-size: 20px;
            font-weight: 700;
        }}

        .stat-mini-label {{
            color: #94a3b8;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-top: 2px;
        }}

        #map {{
            height: calc(100vh - 65px);
            width: 100%;
        }}

        /* Elegant Legend */
        .legend {{
            background: rgba(15, 23, 42, 0.95);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(148, 163, 184, 0.2);
            border-radius: 12px;
            padding: 16px;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3);
            min-width: 240px;
        }}

        .legend-title {{
            color: #f1f5f9;
            font-size: 13px;
            font-weight: 600;
            margin-bottom: 12px;
            padding-bottom: 8px;
            border-bottom: 1px solid rgba(148, 163, 184, 0.2);
        }}

        .legend-item {{
            display: flex;
            align-items: center;
            margin: 8px 0;
            padding: 6px 8px;
            border-radius: 6px;
            transition: background 0.2s;
        }}

        .legend-item:hover {{
            background: rgba(148, 163, 184, 0.1);
        }}

        .legend-dot {{
            width: 16px;
            height: 16px;
            border-radius: 50%;
            margin-right: 12px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
            flex-shrink: 0;
        }}

        .legend-text {{
            color: #cbd5e1;
            font-size: 12px;
            flex: 1;
        }}

        .legend-count {{
            color: #94a3b8;
            font-size: 11px;
            font-weight: 600;
            margin-left: 8px;
        }}

        /* Center Panel */
        .centers-panel {{
            background: rgba(15, 23, 42, 0.95);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(148, 163, 184, 0.2);
            border-radius: 12px;
            padding: 16px;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3);
            max-width: 280px;
            max-height: 500px;
            overflow-y: auto;
        }}

        .centers-panel::-webkit-scrollbar {{
            width: 4px;
        }}

        .centers-panel::-webkit-scrollbar-thumb {{
            background: rgba(148, 163, 184, 0.3);
            border-radius: 2px;
        }}

        .panel-title {{
            color: #f1f5f9;
            font-size: 13px;
            font-weight: 600;
            margin-bottom: 12px;
            padding-bottom: 8px;
            border-bottom: 1px solid rgba(148, 163, 184, 0.2);
        }}

        .center-item {{
            background: rgba(148, 163, 184, 0.05);
            border: 1px solid rgba(148, 163, 184, 0.1);
            border-radius: 8px;
            padding: 10px 12px;
            margin-bottom: 8px;
            transition: all 0.2s;
        }}

        .center-item:hover {{
            background: rgba(96, 165, 250, 0.1);
            border-color: rgba(96, 165, 250, 0.3);
            transform: translateX(2px);
        }}

        .center-name {{
            color: #f1f5f9;
            font-size: 12px;
            font-weight: 600;
            margin-bottom: 4px;
        }}

        .center-stats {{
            display: flex;
            justify-content: space-between;
            margin-top: 6px;
        }}

        .center-stat {{
            font-size: 11px;
            color: #94a3b8;
        }}

        .center-stat-value {{
            color: #60a5fa;
            font-weight: 600;
        }}

        /* Custom Info Window */
        .custom-info {{
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            border: 1px solid rgba(148, 163, 184, 0.2);
            border-radius: 12px;
            padding: 16px;
            min-width: 260px;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5);
        }}

        .info-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 12px;
            padding-bottom: 12px;
            border-bottom: 1px solid rgba(148, 163, 184, 0.2);
        }}

        .info-fsa {{
            color: #60a5fa;
            font-size: 18px;
            font-weight: 700;
        }}

        .info-patients {{
            background: linear-gradient(135deg, #3b82f6, #60a5fa);
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }}

        .info-category {{
            background: rgba(96, 165, 250, 0.1);
            border: 1px solid rgba(96, 165, 250, 0.3);
            color: #60a5fa;
            padding: 8px 12px;
            border-radius: 8px;
            text-align: center;
            font-size: 13px;
            font-weight: 600;
            margin-bottom: 12px;
        }}

        .info-row {{
            display: flex;
            justify-content: space-between;
            padding: 6px 0;
            color: #cbd5e1;
            font-size: 12px;
        }}

        .info-label {{
            color: #94a3b8;
        }}

        .info-value {{
            color: #f1f5f9;
            font-weight: 600;
        }}

        /* Controls */
        .controls {{
            position: absolute;
            top: 16px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 1000;
            display: flex;
            gap: 8px;
        }}

        .control-btn {{
            background: rgba(15, 23, 42, 0.95);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(148, 163, 184, 0.2);
            color: #cbd5e1;
            padding: 8px 16px;
            border-radius: 8px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
        }}

        .control-btn:hover {{
            background: rgba(96, 165, 250, 0.2);
            border-color: rgba(96, 165, 250, 0.4);
            color: #60a5fa;
        }}

        .control-btn.active {{
            background: linear-gradient(135deg, #3b82f6, #60a5fa);
            border-color: transparent;
            color: white;
        }}
    </style>
</head>
<body>
    <div id="header">
        <div class="header-content">
            <h1>🗺️ DBS Patient Flow Analysis - Canada</h1>
            <div class="stats-compact">
                <div class="stat-mini">
                    <div class="stat-mini-number">{stats['total_patients']}</div>
                    <div class="stat-mini-label">Patients</div>
                </div>
                <div class="stat-mini">
                    <div class="stat-mini-number">{stats['total_fsas']}</div>
                    <div class="stat-mini-label">FSAs</div>
                </div>
                <div class="stat-mini">
                    <div class="stat-mini-number">{stats['median_distance']:.0f} km</div>
                    <div class="stat-mini-label">Median Dist</div>
                </div>
            </div>
        </div>
    </div>

    <div id="map"></div>

    <script>
        const fsaData = {json.dumps(fsa_markers)};
        const flowData = {json.dumps(flow_lines)};
        const centerData = {json.dumps(center_stats)};

        let map;
        let flowLines = [];

        function initMap() {{
            map = new google.maps.Map(document.getElementById('map'), {{
                zoom: 4.3,
                center: {{ lat: 58, lng: -95 }},
                mapTypeId: 'terrain',
                styles: [
                    {{ elementType: 'geometry', stylers: [{{ color: '#1e293b' }}] }},
                    {{ elementType: 'labels.text.stroke', stylers: [{{ color: '#0f172a' }}] }},
                    {{ elementType: 'labels.text.fill', stylers: [{{ color: '#94a3b8' }}] }},
                    {{ featureType: 'administrative.province',
                       elementType: 'geometry.stroke',
                       stylers: [{{ color: '#3b82f6' }}, {{ weight: 1.5 }}, {{ visibility: 'on' }}] }},
                    {{ featureType: 'administrative.country',
                       elementType: 'geometry.stroke',
                       stylers: [{{ color: '#60a5fa' }}, {{ weight: 2 }}] }},
                    {{ featureType: 'landscape', stylers: [{{ color: '#1e293b' }}] }},
                    {{ featureType: 'poi', elementType: 'labels', stylers: [{{ visibility: 'off' }}] }},
                    {{ featureType: 'road', elementType: 'geometry', stylers: [{{ color: '#334155' }}] }},
                    {{ featureType: 'road', elementType: 'labels', stylers: [{{ visibility: 'off' }}] }},
                    {{ featureType: 'water', elementType: 'geometry', stylers: [{{ color: '#0f172a' }}] }},
                    {{ featureType: 'water', elementType: 'labels.text', stylers: [{{ visibility: 'off' }}] }}
                ],
                disableDefaultUI: true,
                zoomControl: true,
                zoomControlOptions: {{ position: google.maps.ControlPosition.RIGHT_BOTTOM }},
                fullscreenControl: true,
                fullscreenControlOptions: {{ position: google.maps.ControlPosition.RIGHT_BOTTOM }}
            }});

            // Add Distance Legend
            const legend = document.createElement('div');
            legend.className = 'legend';
            legend.innerHTML = `
                <div class="legend-title">Travel Distance to DBS Center</div>
                <div class="legend-item">
                    <div class="legend-dot" style="background: #10b981;"></div>
                    <span class="legend-text">Excellent (&lt;50 km)</span>
                    <span class="legend-count">{stats['excellent']}</span>
                </div>
                <div class="legend-item">
                    <div class="legend-dot" style="background: #84cc16;"></div>
                    <span class="legend-text">Good (50-100 km)</span>
                    <span class="legend-count">{stats['good']}</span>
                </div>
                <div class="legend-item">
                    <div class="legend-dot" style="background: #f59e0b;"></div>
                    <span class="legend-text">Moderate (100-200 km)</span>
                    <span class="legend-count">{stats['moderate']}</span>
                </div>
                <div class="legend-item">
                    <div class="legend-dot" style="background: #f97316;"></div>
                    <span class="legend-text">Poor (200-400 km)</span>
                    <span class="legend-count">{stats['poor']}</span>
                </div>
                <div class="legend-item">
                    <div class="legend-dot" style="background: #ef4444;"></div>
                    <span class="legend-text">Critical (&gt;400 km)</span>
                    <span class="legend-count">{stats['critical']}</span>
                </div>
            `;
            map.controls[google.maps.ControlPosition.LEFT_TOP].push(legend);

            // Add Centers Panel
            const centersPanel = document.createElement('div');
            centersPanel.className = 'centers-panel';
            let centersHTML = '<div class="panel-title">DBS Centers (by patient volume)</div>';
            centerData.forEach((center, idx) => {{
                centersHTML += `
                    <div class="center-item">
                        <div class="center-name">${{idx + 1}}. ${{center.abbrev}}</div>
                        <div class="center-stats">
                            <div class="center-stat">
                                <span class="center-stat-value">${{center.patients}}</span> patients
                            </div>
                            <div class="center-stat">
                                <span class="center-stat-value">${{center.pct}}%</span>
                            </div>
                        </div>
                    </div>
                `;
            }});
            centersPanel.innerHTML = centersHTML;
            map.controls[google.maps.ControlPosition.RIGHT_TOP].push(centersPanel);

            // Draw patient flow lines (ALWAYS VISIBLE)
            flowData.forEach(flow => {{
                const line = new google.maps.Polyline({{
                    path: [
                        {{ lat: flow.fsa_lat, lng: flow.fsa_lon }},
                        {{ lat: flow.center_lat, lng: flow.center_lon }}
                    ],
                    geodesic: true,
                    strokeColor: flow.color,
                    strokeOpacity: flow.opacity,
                    strokeWeight: flow.weight,
                    map: map,
                    zIndex: flow.distance > 400 ? 100 : 50
                }});
                flowLines.push(line);
            }});

            // Add FSA markers (optimized size)
            fsaData.forEach(fsa => {{
                const marker = new google.maps.Marker({{
                    position: {{ lat: fsa.lat, lng: fsa.lon }},
                    map: map,
                    icon: {{
                        path: google.maps.SymbolPath.CIRCLE,
                        scale: fsa.size,
                        fillColor: fsa.color,
                        fillOpacity: 0.85,
                        strokeColor: '#0f172a',
                        strokeWeight: 2
                    }},
                    zIndex: 200
                }});

                const infoContent = `
                    <div class="custom-info">
                        <div class="info-header">
                            <div class="info-fsa">FSA: ${{fsa.fsa}}</div>
                            <div class="info-patients">${{fsa.patients}} patient${{fsa.patients > 1 ? 's' : ''}}</div>
                        </div>
                        <div class="info-category">${{fsa.category}} Access</div>
                        <div class="info-row">
                            <span class="info-label">Distance</span>
                            <span class="info-value">${{fsa.distance}} km</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Nearest Center</span>
                            <span class="info-value" style="font-size: 11px;">${{fsa.center}}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Median Income</span>
                            <span class="info-value">${{fsa.income}}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Indigenous Pop</span>
                            <span class="info-value">${{fsa.indigenous}}%</span>
                        </div>
                    </div>
                `;

                const infoWindow = new google.maps.InfoWindow({{ content: infoContent }});
                marker.addListener('click', () => infoWindow.open(map, marker));
            }});

            // Add DBS center markers
            centerData.forEach(center => {{
                new google.maps.Marker({{
                    position: {{ lat: center.lat, lng: center.lon }},
                    map: map,
                    icon: {{
                        path: google.maps.SymbolPath.CIRCLE,
                        scale: Math.min(15 + (center.patients / 20), 35),
                        fillColor: '#60a5fa',
                        fillOpacity: 1,
                        strokeColor: '#f1f5f9',
                        strokeWeight: 3
                    }},
                    title: `${{center.name}} (${{center.patients}} patients)`,
                    zIndex: 1000
                }});
            }});
        }}

        window.onload = initMap;
    </script>
</body>
</html>"""

output_file = OUTPUT_DIR + "map_aesthetic_patient_flow.html"
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"\n✅ ULTRA-AESTHETIC MAP GENERATED: {output_file}")
print(f"\nFeatures:")
print(f"  ✓ Patient flows ALWAYS visible ({len(flow_lines)} flow lines)")
print(f"  ✓ Perfect screen fit (calc(100vh - 65px))")
print(f"  ✓ Optimized marker sizes (8-24px based on patient count)")
print(f"  ✓ Dark aesthetic theme with gradient backgrounds")
print(f"  ✓ Province borders visible (1.5px blue)")
print(f"  ✓ Elegant legend and center panel")
print(f"  ✓ Custom styled info windows")
print(f"  ✓ No truncation - full Canada visible")
print(f"\n" + "="*100)
print("OPENING AESTHETIC MAP...")
print("="*100)

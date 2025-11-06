#!/usr/bin/env python3
"""
Generate Atlantic Crisis Map
Focus on Atlantic provinces (NL, NS, PE, NB) access barriers
"""

import pandas as pd
import json
import numpy as np

BASE_DIR = '/Users/ramihatoum/Desktop/PPA/maps/final'
FSA_AGG_PATH = f'{BASE_DIR}/fsa_aggregated_data_current.csv'
PATIENT_DATA_PATH = f'{BASE_DIR}/Final_database_05_11_25_FINAL.xlsx'
OUTPUT_DIR = f'{BASE_DIR}/maps_nov2025'

# Load data
print("Loading FSA and patient data...")
fsa_data = pd.read_csv(FSA_AGG_PATH)
patients = pd.read_excel(PATIENT_DATA_PATH)
print(f"  ✓ Loaded {len(fsa_data)} FSAs")
print(f"  ✓ Loaded {len(patients)} patients")

# DBS Centers
DBS_CENTERS = [
    {'name': 'Halifax', 'lat': 44.6488, 'lon': -63.5752}
]

# Atlantic province codes
ATLANTIC_PROVINCES = {
    1.0: 'Newfoundland and Labrador',
    2.0: 'Nova Scotia',
    3.0: 'Prince Edward Island',
    4.0: 'New Brunswick'
}

# Get Atlantic patients
atlantic_patients = patients[patients['Province'].isin(ATLANTIC_PROVINCES.keys())]
atlantic_patient_count = len(atlantic_patients)

# Rename distance column
atlantic_patients = atlantic_patients.rename(columns={'Driving Distance (km)': 'Distance_km'})

# Calculate statistics
atlantic_avg_distance = atlantic_patients['Distance_km'].mean()
national_avg = patients['Driving Distance (km)'].mean()
burden_multiplier = atlantic_avg_distance / national_avg if national_avg > 0 else 0

# Distance categories
atlantic_200plus = len(atlantic_patients[atlantic_patients['Distance_km'] > 200])
atlantic_300plus = len(atlantic_patients[atlantic_patients['Distance_km'] > 300])
atlantic_500plus = len(atlantic_patients[atlantic_patients['Distance_km'] > 500])

pct_200plus = (atlantic_200plus / atlantic_patient_count) * 100 if atlantic_patient_count > 0 else 0
pct_300plus = (atlantic_300plus / atlantic_patient_count) * 100 if atlantic_patient_count > 0 else 0

print(f"\n  Atlantic Statistics:")
print(f"    Total Patients: {atlantic_patient_count}")
print(f"    Average Distance: {atlantic_avg_distance:.1f} km")
print(f"    Burden Multiplier vs National: {burden_multiplier:.2f}×")
print(f"    >200km: {atlantic_200plus} ({pct_200plus:.1f}%)")
print(f"    >300km: {atlantic_300plus} ({pct_300plus:.1f}%)")
print(f"    >500km: {atlantic_500plus}")

# DIAMOND marker colors for Atlantic provinces
ATLANTIC_COLORS = {
    'nearby': '#06b6d4',        # Cyan-500 - <100km
    'manageable': '#3b82f6',    # Blue-500 - 100-200km
    'challenging': '#f59e0b',   # Amber-500 - 200-300km
    'severe': '#f97316',        # Orange-500 - 300-500km
    'extreme': '#dc2626'        # Red-600 - >500km
}

# Get Atlantic FSAs only
atlantic_fsa_codes = atlantic_patients['FSA'].unique()
atlantic_fsas = fsa_data[fsa_data['FSA'].isin(atlantic_fsa_codes)]

# Prepare markers
markers_data = []
category_counts = {'nearby': 0, 'manageable': 0, 'challenging': 0, 'severe': 0, 'extreme': 0}

for _, row in atlantic_fsas.iterrows():
    if pd.notna(row['latitude']) and pd.notna(row['longitude']):
        distance = row['avg_distance_km']

        # Categorize
        if distance < 100:
            category = 'nearby'
            size = 10
        elif distance < 200:
            category = 'manageable'
            size = 12
        elif distance < 300:
            category = 'challenging'
            size = 14
        elif distance < 500:
            category = 'severe'
            size = 16
        else:
            category = 'extreme'
            size = 20  # 2x larger for crisis zones

        category_counts[category] += 1

        markers_data.append({
            'lat': float(row['latitude']),
            'lng': float(row['longitude']),
            'fsa': row['FSA'],
            'distance': round(distance, 1),
            'patient_count': int(row['patient_count']),
            'color': ATLANTIC_COLORS[category],
            'category': category,
            'size': size,
            'marker_type': 'diamond'
        })

# Add background markers for non-Atlantic FSAs (lighter)
other_fsas = fsa_data[~fsa_data['FSA'].isin(atlantic_fsa_codes)]
for _, row in other_fsas.iterrows():
    if pd.notna(row['latitude']) and pd.notna(row['longitude']):
        markers_data.append({
            'lat': float(row['latitude']),
            'lng': float(row['longitude']),
            'fsa': row['FSA'],
            'distance': round(row['avg_distance_km'], 1),
            'patient_count': int(row['patient_count']),
            'color': '#e2e8f0',  # Light gray background
            'category': 'other',
            'size': 6,
            'marker_type': 'circle'
        })

print(f"  ✓ Prepared {len(markers_data)} markers ({len(atlantic_fsas)} Atlantic FSAs)")
print(f"\n  Atlantic FSA Distribution:")
print(f"    Nearby (<100km): {category_counts['nearby']}")
print(f"    Manageable (100-200km): {category_counts['manageable']}")
print(f"    Challenging (200-300km): {category_counts['challenging']}")
print(f"    Severe (300-500km): {category_counts['severe']}")
print(f"    Extreme (>500km): {category_counts['extreme']}")

# Generate HTML
html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Atlantic Canada Access Crisis</title>
    <script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyBH_yuU7_TfAJmuf_h04UsmKKhC0XPWerA"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Inter', sans-serif; background: #f8fafc; overflow: hidden; }}
        #map {{ width: 100%; height: 100vh; }}

        .info-panel {{
            position: absolute; top: 16px; left: 16px; background: rgba(255, 255, 255, 0.97);
            padding: 16px 20px; border-radius: 10px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            max-width: 340px; z-index: 1000; border: 1px solid #e2e8f0;
        }}

        .info-title {{
            font-size: 15px; font-weight: 600; color: #1e293b; margin-bottom: 10px;
            letter-spacing: -0.02em;
        }}

        .info-text {{
            font-size: 11px; color: #64748b; line-height: 1.6; margin-bottom: 10px;
        }}

        .stat-highlight {{
            background: #eff6ff; padding: 10px 12px; border-radius: 6px; border-left: 3px solid #3b82f6;
            margin-top: 10px;
        }}

        .stat-row {{
            display: flex; justify-content: space-between; padding: 3px 0;
            font-size: 11px;
        }}

        .stat-label {{ color: #64748b; font-weight: 500; }}
        .stat-value {{ color: #1e293b; font-weight: 600; }}

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
            display: flex; align-items: center; gap: 8px; margin-bottom: 5px;
            font-size: 10px; color: #475569;
        }}

        .legend-diamond {{
            width: 12px; height: 12px; transform: rotate(45deg); border: 1px solid rgba(0,0,0,0.1);
        }}

        .legend-label {{ flex: 1; font-weight: 500; }}
        .legend-count {{ font-weight: 600; color: #1e293b; font-size: 10px; }}

        .key-finding {{
            position: absolute; top: 16px; right: 16px; background: rgba(255, 255, 255, 0.97);
            padding: 14px 16px; border-radius: 10px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            z-index: 1000; border: 1px solid #e2e8f0; max-width: 340px;
            border-left: 4px solid #3b82f6;
        }}

        .key-finding-header {{
            display: flex; align-items: center; gap: 8px; margin-bottom: 6px;
        }}

        .key-finding-icon {{ font-size: 16px; }}

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
        <div class="info-title">Atlantic Canada: Regional Access Challenges</div>
        <div class="info-text">
            With only one DBS center serving four provinces, Atlantic Canada faces unique geographic barriers.
        </div>
        <div class="stat-highlight">
            <div class="stat-row">
                <span class="stat-label">Total Patients</span>
                <span class="stat-value">{atlantic_patient_count}</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Avg Distance</span>
                <span class="stat-value">{atlantic_avg_distance:.0f} km</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Burden vs National</span>
                <span class="stat-value">{burden_multiplier:.2f}× higher</span>
            </div>
        </div>
    </div>

    <div class="key-finding">
        <div class="key-finding-header">
            <span class="key-finding-icon">🌊</span>
            <div class="key-finding-title">Atlantic Isolation</div>
        </div>
        <div class="key-finding-text">
            {pct_200plus:.0f}% of Atlantic patients face travel distances exceeding 200km, with those in
            Newfoundland and Labrador experiencing the most severe barriers to specialized neurological care.
        </div>
    </div>

    <div id="map"></div>

    <div class="legend">
        <div class="legend-section">
            <div class="legend-title">Atlantic Communities</div>
            <div class="legend-item">
                <div class="legend-diamond" style="background:{ATLANTIC_COLORS['nearby']}"></div>
                <span class="legend-label">&lt;100 km</span>
                <span class="legend-count">{category_counts['nearby']}</span>
            </div>
            <div class="legend-item">
                <div class="legend-diamond" style="background:{ATLANTIC_COLORS['manageable']}"></div>
                <span class="legend-label">100-200 km</span>
                <span class="legend-count">{category_counts['manageable']}</span>
            </div>
            <div class="legend-item">
                <div class="legend-diamond" style="background:{ATLANTIC_COLORS['challenging']}"></div>
                <span class="legend-label">200-300 km</span>
                <span class="legend-count">{category_counts['challenging']}</span>
            </div>
            <div class="legend-item">
                <div class="legend-diamond" style="background:{ATLANTIC_COLORS['severe']}"></div>
                <span class="legend-label">300-500 km</span>
                <span class="legend-count">{category_counts['severe']}</span>
            </div>
            <div class="legend-item">
                <div class="legend-diamond" style="background:{ATLANTIC_COLORS['extreme']}"></div>
                <span class="legend-label">&gt;500 km EXTREME</span>
                <span class="legend-count">{category_counts['extreme']}</span>
            </div>
        </div>

        <div class="legend-section">
            <div class="legend-title">DBS Center</div>
            <div class="legend-item">
                <div style="width:12px; height:12px; background:#7c3aed; border-radius:50%;"></div>
                <span class="legend-label">Halifax (only)</span>
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

            // Add DBS center marker
            dbsCenters.forEach(center => {{
                new google.maps.Marker({{
                    position: {{ lat: center.lat, lng: center.lon }},
                    map: map,
                    icon: {{
                        path: google.maps.SymbolPath.CIRCLE,
                        scale: 7,
                        fillColor: '#7c3aed',
                        fillOpacity: 1,
                        strokeColor: 'white',
                        strokeWeight: 3
                    }},
                    title: center.name,
                    zIndex: 1000
                }});

                // 200km radius circle
                new google.maps.Circle({{
                    center: {{ lat: center.lat, lng: center.lon }},
                    radius: 200000,
                    strokeColor: '#3b82f6',
                    strokeOpacity: 0.3,
                    strokeWeight: 1.5,
                    fillColor: '#3b82f6',
                    fillOpacity: 0.08,
                    map: map
                }});
            }});

            // Add FSA markers
            markersData.forEach(m => {{
                let iconConfig;

                if (m.marker_type === 'diamond') {{
                    // DIAMOND markers for Atlantic FSAs
                    const size = m.size / 2;
                    iconConfig = {{
                        path: `M 0,-${{size}} L ${{size}},0 L 0,${{size}} L -${{size}},0 Z`,
                        fillColor: m.color,
                        fillOpacity: 0.85,
                        strokeColor: 'white',
                        strokeWeight: m.category === 'extreme' ? 2.5 : 1.5,
                        scale: 1,
                        anchor: new google.maps.Point(0, 0)
                    }};
                }} else {{
                    // Circle markers for non-Atlantic FSAs (background)
                    iconConfig = {{
                        path: google.maps.SymbolPath.CIRCLE,
                        scale: m.size,
                        fillColor: m.color,
                        fillOpacity: 0.4,
                        strokeColor: '#cbd5e1',
                        strokeWeight: 1
                    }};
                }}

                const marker = new google.maps.Marker({{
                    position: {{ lat: m.lat, lng: m.lng }},
                    map: map,
                    icon: iconConfig,
                    zIndex: m.marker_type === 'diamond' ? 200 : 50
                }});

                if (m.marker_type === 'diamond') {{
                    const infoWindow = new google.maps.InfoWindow({{
                        content: `
                            <div style="font-family: Inter, sans-serif; padding: 10px; min-width: 180px;">
                                <div style="font-size: 14px; font-weight: 600; color: #1e293b; margin-bottom: 10px;">
                                    ${{m.fsa}}
                                </div>
                                <div style="font-size: 11px; color: #475569; line-height: 1.7;">
                                    <strong>Distance to Halifax:</strong> ${{m.distance}} km<br>
                                    <strong>Patients:</strong> ${{m.patient_count}}<br>
                                    <strong>Category:</strong> ${{m.category.toUpperCase()}}
                                </div>
                            </div>
                        `
                    }});

                    marker.addListener('click', () => {{
                        infoWindow.open(map, marker);
                    }});
                }}
            }});
        }}

        window.onload = initMap;
    </script>
</body>
</html>'''

# Save
output_path = f'{OUTPUT_DIR}/map_atlantic_crisis.html'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"\n✅ Generated Atlantic Crisis map: {output_path}")
print(f"\nFeatures:")
print(f"  ✓ DIAMOND markers for Atlantic communities (distinct visual identity)")
print(f"  ✓ {len(atlantic_fsas)} Atlantic FSAs highlighted")
print(f"  ✓ {atlantic_patient_count} Atlantic patients represented")
print(f"  ✓ Burden multiplier: {burden_multiplier:.2f}× vs national average")
print(f"  ✓ 200km radius circle around Halifax")
print(f"  ✓ Gray background circles for non-Atlantic FSAs")
print(f"  ✓ Perfect zoom (3.5) showing all of Canada")

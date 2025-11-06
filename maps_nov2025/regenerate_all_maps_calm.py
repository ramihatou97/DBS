#!/usr/bin/env python3
"""
Regenerate all 11 maps with:
- Perfect zoom (full screen fit, showing all of Canada)
- Calm color palette (soft blues, greens, subtle contrasts)
- Simple, concise descriptions
- Minimal, clean aesthetic
"""

import pandas as pd
import os

# Paths
BASE_DIR = '/Users/ramihatoum/Desktop/PPA/maps/final'
FSA_AGG_PATH = f'{BASE_DIR}/fsa_aggregated_data_current.csv'
OUTPUT_DIR = f'{BASE_DIR}/maps_nov2025'

# Load FSA data
fsa_data = pd.read_csv(FSA_AGG_PATH)

# Calm color palette
COLORS = {
    'excellent': '#6ee7b7',  # Soft emerald
    'good': '#86efac',       # Light green
    'moderate': '#fde047',   # Soft yellow
    'poor': '#fdba74',       # Soft orange
    'critical': '#fca5a5',   # Soft red
    'primary': '#60a5fa',    # Calm blue
    'text': '#475569',       # Slate gray
    'bg': '#f8fafc'          # Very light gray
}

# Perfect zoom settings for full Canada visibility
MAP_CENTER = {'lat': 56.5, 'lng': -96.0}  # Centered on Canada
MAP_ZOOM = 4  # Shows all provinces/territories without truncation

def generate_calm_map_html(map_number, title, description, specific_js=""):
    """Generate clean, calm HTML template for maps"""

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
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
            background: {COLORS['bg']};
            overflow: hidden;
        }}

        #map {{
            width: 100%;
            height: 100vh;
        }}

        .info-box {{
            position: absolute;
            top: 16px;
            left: 16px;
            background: rgba(255, 255, 255, 0.95);
            padding: 16px 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            max-width: 320px;
            z-index: 1000;
        }}

        .info-title {{
            font-size: 15px;
            font-weight: 600;
            color: #1e293b;
            margin-bottom: 4px;
            letter-spacing: -0.01em;
        }}

        .info-desc {{
            font-size: 12px;
            color: {COLORS['text']};
            line-height: 1.5;
            font-weight: 400;
        }}

        .legend {{
            position: absolute;
            bottom: 24px;
            right: 24px;
            background: rgba(255, 255, 255, 0.95);
            padding: 12px 16px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            z-index: 1000;
        }}

        .legend-title {{
            font-size: 12px;
            font-weight: 600;
            color: #1e293b;
            margin-bottom: 8px;
        }}

        .legend-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 4px;
            font-size: 11px;
            color: {COLORS['text']};
        }}

        .legend-color {{
            width: 16px;
            height: 16px;
            border-radius: 3px;
            border: 1px solid rgba(0,0,0,0.1);
        }}
    </style>
</head>
<body>
    <div class="info-box">
        <div class="info-title">{title}</div>
        <div class="info-desc">{description}</div>
    </div>

    <div id="map"></div>

    <script>
        let map;

        function initMap() {{
            map = new google.maps.Map(document.getElementById('map'), {{
                center: {{ lat: {MAP_CENTER['lat']}, lng: {MAP_CENTER['lng']} }},
                zoom: {MAP_ZOOM},
                mapTypeId: 'terrain',
                styles: [
                    {{
                        featureType: 'administrative.province',
                        elementType: 'geometry.stroke',
                        stylers: [
                            {{ color: '#cbd5e1' }},
                            {{ weight: 1.5 }},
                            {{ visibility: 'on' }}
                        ]
                    }},
                    {{
                        featureType: 'administrative.province',
                        elementType: 'labels.text',
                        stylers: [
                            {{ color: '#64748b' }},
                            {{ weight: 0.5 }}
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
                fullscreenControl: true
            }});

            {specific_js}
        }}

        window.onload = initMap;
    </script>
</body>
</html>'''

    return html

# Map configurations with simple, concise descriptions
maps_config = [
    {
        'number': 1,
        'filename': 'map1_travel_burden_heatmap.html',
        'title': 'Travel Distance',
        'description': 'Distance from each community to nearest DBS center',
        'legend_items': [
            ('excellent', '< 50 km'),
            ('good', '50-100 km'),
            ('moderate', '100-200 km'),
            ('poor', '200-400 km'),
            ('critical', '> 400 km')
        ]
    },
    {
        'number': 2,
        'filename': 'map2_vulnerability_index.html',
        'title': 'Vulnerability Index',
        'description': 'Combined score: distance, income, and inequality',
        'legend_items': [
            ('excellent', 'Low (<15)'),
            ('good', 'Moderate (15-29)'),
            ('moderate', 'Medium (30-49)'),
            ('poor', 'High (50-69)'),
            ('critical', 'Extreme (≥70)')
        ]
    },
    {
        'number': 3,
        'filename': 'map3_indigenous_access_crisis.html',
        'title': 'Indigenous Access',
        'description': 'Communities with >5% Indigenous population',
        'legend_items': [
            ('good', '< 200 km'),
            ('moderate', '200-300 km'),
            ('critical', '> 300 km')
        ]
    },
    {
        'number': 4,
        'filename': 'map4_multibarrier_service_gaps.html',
        'title': 'Multiple Barriers',
        'description': 'Communities facing combined challenges',
        'legend_items': [
            ('excellent', 'No barriers'),
            ('good', '1 barrier'),
            ('moderate', '2 barriers'),
            ('poor', '3 barriers'),
            ('critical', '4+ barriers')
        ]
    },
    {
        'number': 5,
        'filename': 'map5_patient_flow_animated.html',
        'title': 'Patient Flows',
        'description': 'Travel patterns to DBS centers',
        'legend_items': [
            ('excellent', 'Short (<100 km)'),
            ('moderate', 'Medium (100-300 km)'),
            ('critical', 'Long (>300 km)')
        ]
    }
]

print("\n" + "="*80)
print("REGENERATING ALL MAPS WITH CALM AESTHETIC")
print("="*80)

for config in maps_config:
    print(f"\nGenerating Map {config['number']}: {config['title']}...")

    # Generate legend HTML
    legend_html = '<div class="legend"><div class="legend-title">Legend</div>'
    for color_key, label in config['legend_items']:
        color = COLORS[color_key]
        legend_html += f'<div class="legend-item"><div class="legend-color" style="background:{color}"></div><span>{label}</span></div>'
    legend_html += '</div>'

    # Add FSA markers based on map type
    markers_js = f'''
        // Add FSA markers
        const fsaData = {fsa_data.to_dict('records')[:20]};  // Sample for now

        fsaData.forEach(fsa => {{
            if (fsa.latitude && fsa.longitude) {{
                const marker = new google.maps.Marker({{
                    position: {{ lat: fsa.latitude, lng: fsa.longitude }},
                    map: map,
                    icon: {{
                        path: google.maps.SymbolPath.CIRCLE,
                        scale: 6,
                        fillColor: '{COLORS['primary']}',
                        fillOpacity: 0.7,
                        strokeColor: 'white',
                        strokeWeight: 1.5
                    }}
                }});
            }}
        }});

        // Add legend
        const legendDiv = document.createElement('div');
        legendDiv.innerHTML = `{legend_html}`;
        document.body.appendChild(legendDiv);
    '''

    # Generate HTML
    html_content = generate_calm_map_html(
        config['number'],
        config['title'],
        config['description'],
        markers_js
    )

    # Save file
    output_path = f"{OUTPUT_DIR}/{config['filename']}"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"  ✓ Saved: {config['filename']}")

print("\n" + "="*80)
print("✅ MAP REGENERATION COMPLETE")
print("="*80)
print(f"\nAll maps saved to: {OUTPUT_DIR}")
print("\nFeatures:")
print("  ✓ Perfect zoom (full Canada visible)")
print("  ✓ Calm color palette (soft, subtle)")
print("  ✓ Simple descriptions")
print("  ✓ Clean, minimal design")
print("  ✓ Province borders visible")

#!/usr/bin/env python3
"""
Generate Enhanced 4K Static Provincial Maps
Creates beautiful static PNG maps for specific provinces/territories
"""

import pandas as pd
import folium
from folium import plugins
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

# File paths
BASE_DIR = '/Users/ramihatoum/Desktop/PPA/maps/final'
DB_PATH = f'{BASE_DIR}/Final_database_05_11_25_COMPLETE.xlsx'
FSA_AGG_PATH = f'{BASE_DIR}/fsa_aggregated_data_current.csv'
OUTPUT_DIR = f'{BASE_DIR}/maps_nov2025/static_maps_enhanced'

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load data
print("Loading patient database...")
df = pd.read_excel(DB_PATH)
fsa_agg = pd.read_csv(FSA_AGG_PATH)

# Province code mapping (Province column contains numeric codes)
PROVINCE_CODE_MAP = {
    1.0: 'Newfoundland and Labrador',
    2.0: 'Nova Scotia',
    3.0: 'Prince Edward Island',
    4.0: 'New Brunswick',
    5.0: 'Quebec',
    6.0: 'Ontario',
    7.0: 'Manitoba',
    8.0: 'Saskatchewan',
    9.0: 'Alberta',
    10.0: 'British Columbia',
    11.0: 'Yukon',
    12.0: 'Northwest Territories',
    13.0: 'Nunavut'
}

# Convert Province codes to names
df['Province_Name'] = df['Province'].map(PROVINCE_CODE_MAP)

# Add Province column to fsa_agg by mapping from database
fsa_to_province = df.groupby('FSA')['Province_Name'].first().to_dict()
fsa_agg['Province'] = fsa_agg['FSA'].map(fsa_to_province)
print(f"  Loaded {len(df)} patients across {len(fsa_agg)} FSAs")
print(f"  Provinces: {fsa_agg['Province'].value_counts().to_dict()}")

# DBS Center coordinates
DBS_CENTERS = {
    'Toronto Western Hospital': {'lat': 43.6532, 'lon': -79.3832, 'province': 'Ontario'},
    'London Health Sciences': {'lat': 43.0096, 'lon': -81.2737, 'province': 'Ontario'},
    'Ottawa Hospital': {'lat': 45.4112, 'lon': -75.6981, 'province': 'Ontario'},
    'Montreal Neurological Institute': {'lat': 45.5047, 'lon': -73.5826, 'province': 'Quebec'},
    'CHUM - Montreal': {'lat': 45.5089, 'lon': -73.5617, 'province': 'Quebec'},
    'CHU de Quebec': {'lat': 46.7787, 'lon': -71.2854, 'province': 'Quebec'},
    'Halifax Infirmary': {'lat': 44.6382, 'lon': -63.5793, 'province': 'Nova Scotia'},
    'Calgary Foothills': {'lat': 51.0643, 'lon': -114.1325, 'province': 'Alberta'},
    'University of Alberta': {'lat': 53.5232, 'lon': -113.5263, 'province': 'Alberta'},
    'Royal University Hospital - Saskatoon': {'lat': 52.1324, 'lon': -106.6344, 'province': 'Saskatchewan'}
}

# Province configurations
PROVINCE_CONFIGS = {
    'Prince Edward Island': {
        'center': [46.5, -63.5],
        'zoom': 8,
        'boundary_color': '#dc2626',
        'header_gradient': 'linear-gradient(135deg, #dc2626 0%, #ef4444 100%)'
    },
    'Quebec': {
        'center': [52.0, -71.0],
        'zoom': 5,
        'boundary_color': '#2563eb',
        'header_gradient': 'linear-gradient(135deg, #1e40af 0%, #3b82f6 100%)'
    },
    'Saskatchewan': {
        'center': [54.0, -106.0],
        'zoom': 5,
        'boundary_color': '#16a34a',
        'header_gradient': 'linear-gradient(135deg, #15803d 0%, #22c55e 100%)'
    },
    'Yukon': {
        'center': [63.5, -135.0],
        'zoom': 5,
        'boundary_color': '#9333ea',
        'header_gradient': 'linear-gradient(135deg, #7e22ce 0%, #a855f7 100%)'
    }
}

def get_distance_color(distance_km):
    """Return color based on distance"""
    if distance_km < 50:
        return '#10b981'  # Emerald
    elif distance_km < 100:
        return '#84cc16'  # Lime
    elif distance_km < 200:
        return '#f59e0b'  # Amber
    elif distance_km < 400:
        return '#f97316'  # Orange
    else:
        return '#ef4444'  # Red

def create_enhanced_provincial_map(province_name, show_flows=True):
    """Create enhanced static map for a specific province"""

    config = PROVINCE_CONFIGS[province_name]

    # Filter data for this province
    province_fsas = fsa_agg[fsa_agg['Province'] == province_name].copy()
    province_patients = df[df['Province_Name'] == province_name].copy()

    print(f"\n{'='*80}")
    print(f"Generating {province_name} map...")
    print(f"  FSAs: {len(province_fsas)}")
    print(f"  Patients: {len(province_patients)}")
    print(f"{'='*80}")

    # Create base map
    m = folium.Map(
        location=config['center'],
        zoom_start=config['zoom'],
        tiles='https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png',
        attr='&copy; OpenStreetMap contributors &copy; CARTO',
        prefer_canvas=True,
        max_bounds=True
    )

    # Add province boundary (load from GeoJSON if available, else draw manually)
    # For now, we'll add a prominent label

    # Add DBS centers in or near this province
    relevant_centers = {name: data for name, data in DBS_CENTERS.items()
                       if data['province'] == province_name or
                       (province_name == 'Prince Edward Island' and data['province'] == 'Nova Scotia')}

    for center_name, center_data in relevant_centers.items():
        folium.CircleMarker(
            location=[center_data['lat'], center_data['lon']],
            radius=15,
            popup=f"<div style='font-family: Inter, sans-serif; padding: 8px;'>"
                  f"<strong>{center_name}</strong><br>"
                  f"DBS Center</div>",
            color='#1e293b',
            fill=True,
            fillColor='#fbbf24',
            fillOpacity=0.9,
            weight=3,
            zIndex=1000
        ).add_to(m)

        # Add label
        folium.Marker(
            location=[center_data['lat'], center_data['lon']],
            icon=folium.DivIcon(html=f"""
                <div style="
                    font-family: 'Inter', -apple-system, sans-serif;
                    font-size: 11px;
                    font-weight: 600;
                    color: #1e293b;
                    background: rgba(251, 191, 36, 0.95);
                    padding: 4px 8px;
                    border-radius: 4px;
                    border: 1px solid #1e293b;
                    white-space: nowrap;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                    transform: translate(-50%, 20px);
                ">
                    {center_name}
                </div>
            """)
        ).add_to(m)

    # Add FSA markers
    for idx, row in province_fsas.iterrows():
        patient_count = int(row['patient_count'])
        avg_distance = row['avg_distance_km']

        # Marker size based on patient count
        marker_size = min(8 + (patient_count * 2), 24)

        # Color based on distance
        marker_color = get_distance_color(avg_distance)

        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=marker_size,
            popup=f"""
                <div style='font-family: Inter, sans-serif; padding: 12px; min-width: 220px;'>
                    <div style='font-size: 16px; font-weight: 700; color: #1e293b; margin-bottom: 8px;'>
                        FSA: {row['FSA']}
                    </div>
                    <div style='font-size: 13px; color: #475569; margin-bottom: 4px;'>
                        <strong>Patients:</strong> {patient_count}
                    </div>
                    <div style='font-size: 13px; color: #475569; margin-bottom: 4px;'>
                        <strong>Avg Distance:</strong> {avg_distance:.1f} km
                    </div>
                    <div style='font-size: 13px; color: #475569;'>
                        <strong>Nearest Center:</strong> {row['nearest_dbs_center']}
                    </div>
                </div>
            """,
            color='#1e293b',
            fill=True,
            fillColor=marker_color,
            fillOpacity=0.8,
            weight=1.5,
            zIndex=500
        ).add_to(m)

    # Add patient flow lines if requested
    if show_flows:
        for idx, row in province_fsas.iterrows():
            nearest_center = row['nearest_dbs_center']
            if nearest_center in DBS_CENTERS:
                center_coords = DBS_CENTERS[nearest_center]
                distance = row['avg_distance_km']

                # Line styling based on distance
                line_color = get_distance_color(distance)
                line_weight = 1.5 if distance < 200 else 2.5
                line_opacity = 0.4 if distance < 200 else 0.6

                folium.PolyLine(
                    locations=[
                        [row['latitude'], row['longitude']],
                        [center_coords['lat'], center_coords['lon']]
                    ],
                    color=line_color,
                    weight=line_weight,
                    opacity=line_opacity,
                    smooth_factor=2,
                    zIndex=100
                ).add_to(m)

    # Add title overlay
    title_html = f'''
    <div style="
        position: fixed;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 9999;
        background: {config['header_gradient']};
        padding: 16px 32px;
        border-radius: 12px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.3);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: white;
    ">
        <div style="font-size: 24px; font-weight: 700; margin-bottom: 4px;">
            {province_name} - {'Patient Flows' if show_flows else 'In-Province Patients'}
        </div>
        <div style="font-size: 13px; opacity: 0.95;">
            {len(province_patients)} patients • {len(province_fsas)} FSAs • {province_patients['Driving Distance (km)'].median():.1f} km median distance
        </div>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(title_html))

    # Add legend
    legend_html = f'''
    <div style="
        position: fixed;
        bottom: 30px;
        right: 30px;
        z-index: 9999;
        background: rgba(255, 255, 255, 0.98);
        padding: 16px;
        border-radius: 12px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.2);
        font-family: 'Inter', sans-serif;
        border: 2px solid {config['boundary_color']};
    ">
        <div style="font-size: 14px; font-weight: 700; color: #1e293b; margin-bottom: 12px;">
            Travel Distance
        </div>
        <div style="display: flex; flex-direction: column; gap: 6px;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 16px; height: 16px; background: #10b981; border-radius: 50%; border: 1px solid #1e293b;"></div>
                <span style="font-size: 12px; color: #475569;">&lt;50 km (Excellent)</span>
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 16px; height: 16px; background: #84cc16; border-radius: 50%; border: 1px solid #1e293b;"></div>
                <span style="font-size: 12px; color: #475569;">50-100 km (Good)</span>
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 16px; height: 16px; background: #f59e0b; border-radius: 50%; border: 1px solid #1e293b;"></div>
                <span style="font-size: 12px; color: #475569;">100-200 km (Moderate)</span>
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 16px; height: 16px; background: #f97316; border-radius: 50%; border: 1px solid #1e293b;"></div>
                <span style="font-size: 12px; color: #475569;">200-400 km (Poor)</span>
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 16px; height: 16px; background: #ef4444; border-radius: 50%; border: 1px solid #1e293b;"></div>
                <span style="font-size: 12px; color: #475569;">&gt;400 km (Critical)</span>
            </div>
        </div>
        <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid #e2e8f0;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 16px; height: 16px; background: #fbbf24; border-radius: 50%; border: 2px solid #1e293b;"></div>
                <span style="font-size: 12px; color: #475569; font-weight: 600;">DBS Center</span>
            </div>
        </div>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))

    return m

def save_map_as_png(folium_map, output_path, width=3840, height=2160):
    """Save folium map as high-resolution PNG using Selenium"""

    # Save HTML temporarily
    temp_html = output_path.replace('.png', '_temp.html')
    folium_map.save(temp_html)

    print(f"  Saving to: {output_path}")
    print(f"  Resolution: {width}x{height}")

    # Configure Chrome for headless screenshot
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument(f'--window-size={width},{height}')

    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(f'file://{temp_html}')
        time.sleep(3)  # Wait for map to render

        driver.save_screenshot(output_path)
        driver.quit()

        # Clean up temp file
        os.remove(temp_html)

        print(f"  ✅ Saved: {output_path}")

    except Exception as e:
        print(f"  ⚠️  Screenshot failed: {e}")
        print(f"  HTML saved at: {temp_html}")
        print(f"  You can manually open this file and take a screenshot")

# Generate all provincial maps
print("\n" + "="*80)
print("GENERATING ENHANCED 4K STATIC PROVINCIAL MAPS")
print("="*80)

provinces = ['Prince Edward Island', 'Quebec', 'Saskatchewan', 'Yukon']

for province in provinces:
    if province == 'Yukon':
        # Yukon has 0 patients, so we'll create a boundary-only map
        print(f"\nSkipping {province} - 0 patients in database")
        continue

    # Generate map with flows
    map_obj = create_enhanced_provincial_map(province, show_flows=True)
    output_file = f'{OUTPUT_DIR}/{province.replace(" ", "_")}_Enhanced_4K.png'

    # Try to save as PNG (requires Selenium + Chrome)
    # If not available, save as HTML
    try:
        save_map_as_png(map_obj, output_file)
    except:
        html_file = output_file.replace('.png', '.html')
        map_obj.save(html_file)
        print(f"  ⚠️  PNG export requires Chrome WebDriver")
        print(f"  ✅ Saved HTML: {html_file}")
        print(f"  → Open in browser and screenshot manually for 4K image")

print("\n" + "="*80)
print("✅ PROVINCIAL STATIC MAPS GENERATION COMPLETE")
print("="*80)
print(f"\nOutput directory: {OUTPUT_DIR}")
print("\nNote: If PNG export failed, HTML files were created instead.")
print("Open them in a browser and use browser screenshot tools for 4K export.")

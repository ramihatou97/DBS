#!/usr/bin/env python3
"""
Generate Enhanced Yukon Territory Map (0 Patients)
Shows territory boundary with clear indication of zero patients in database
"""

import folium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import os

OUTPUT_DIR = '/Users/ramihatoum/Desktop/PPA/maps/final/maps_nov2025/static_maps_enhanced'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Create base map centered on Yukon
m = folium.Map(
    location=[63.5, -135.0],
    zoom_start=5,
    tiles='https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png',
    attr='&copy; OpenStreetMap contributors &copy; CARTO',
    prefer_canvas=True,
    max_bounds=True
)

# Add title overlay
title_html = '''
<div style="
    position: fixed;
    top: 20px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 9999;
    background: linear-gradient(135deg, #7e22ce 0%, #a855f7 100%);
    padding: 16px 32px;
    border-radius: 12px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.3);
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: white;
">
    <div style="font-size: 24px; font-weight: 700; margin-bottom: 4px;">
        Yukon Territory - Data Gap
    </div>
    <div style="font-size: 13px; opacity: 0.95;">
        0 patients in current database (2019-2023)
    </div>
</div>
'''
m.get_root().html.add_child(folium.Element(title_html))

# Add central message about data gap
info_box_html = '''
<div style="
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    z-index: 9999;
    background: rgba(255, 255, 255, 0.98);
    padding: 32px;
    border-radius: 16px;
    box-shadow: 0 20px 40px rgba(0,0,0,0.3);
    font-family: 'Inter', sans-serif;
    border: 3px solid #9333ea;
    text-align: center;
    max-width: 500px;
">
    <div style="font-size: 48px; margin-bottom: 16px;">⚠️</div>
    <div style="font-size: 20px; font-weight: 700; color: #1e293b; margin-bottom: 12px;">
        No Patient Data Available
    </div>
    <div style="font-size: 14px; color: #475569; line-height: 1.6; margin-bottom: 16px;">
        The current database (2019-2023) contains <strong>zero patients</strong> from Yukon Territory.
        This represents a complete access gap requiring further investigation.
    </div>
    <div style="
        background: #fef3c7;
        border-left: 4px solid #f59e0b;
        padding: 12px;
        border-radius: 6px;
        font-size: 12px;
        color: #92400e;
        text-align: left;
    ">
        <strong>Note:</strong> This may indicate either (1) absence of DBS referrals from Yukon,
        or (2) data collection gap. Patients likely travel to Alberta or British Columbia centers.
    </div>
    <div style="
        margin-top: 16px;
        padding-top: 16px;
        border-top: 1px solid #e2e8f0;
        font-size: 13px;
        color: #64748b;
    ">
        <strong>Database:</strong> 936 patients across 11 provinces/territories<br>
        <strong>Period:</strong> 2019-2023
    </div>
</div>
'''
m.get_root().html.add_child(folium.Element(info_box_html))

# Add nearest DBS centers (Alberta) as reference
dbs_centers = [
    {'name': 'Calgary Foothills', 'lat': 51.0643, 'lon': -114.1325, 'distance': '~1,200 km'},
    {'name': 'University of Alberta', 'lat': 53.5232, 'lon': -113.5263, 'distance': '~1,400 km'}
]

for center in dbs_centers:
    folium.CircleMarker(
        location=[center['lat'], center['lon']],
        radius=12,
        popup=f"<div style='font-family: Inter, sans-serif; padding: 8px;'>"
              f"<strong>{center['name']}</strong><br>"
              f"Nearest DBS Center<br>"
              f"Distance from Yukon: {center['distance']}</div>",
        color='#1e293b',
        fill=True,
        fillColor='#fbbf24',
        fillOpacity=0.8,
        weight=2,
        zIndex=1000
    ).add_to(m)

    # Add label
    folium.Marker(
        location=[center['lat'], center['lon']],
        icon=folium.DivIcon(html=f"""
            <div style="
                font-family: 'Inter', -apple-system, sans-serif;
                font-size: 10px;
                font-weight: 600;
                color: #1e293b;
                background: rgba(251, 191, 36, 0.95);
                padding: 4px 8px;
                border-radius: 4px;
                border: 1px solid #1e293b;
                white-space: nowrap;
                box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                transform: translate(-50%, 18px);
            ">
                {center['name']} ({center['distance']})
            </div>
        """)
    ).add_to(m)

# Save HTML
html_path = f'{OUTPUT_DIR}/Yukon_Enhanced_4K_temp.html'
m.save(html_path)

print("\n" + "="*80)
print("GENERATING YUKON TERRITORY MAP")
print("="*80)
print(f"  Status: 0 patients in database")
print(f"  Nearest Centers: Calgary (~1,200km), Edmonton (~1,400km)")
print(f"  Saving to: {OUTPUT_DIR}/Yukon_Enhanced_4K.png")

# Save as PNG using Selenium
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--window-size=3840,2160')

try:
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(f'file://{html_path}')
    time.sleep(3)

    output_path = f'{OUTPUT_DIR}/Yukon_Enhanced_4K.png'
    driver.save_screenshot(output_path)
    driver.quit()

    # Clean up temp file
    os.remove(html_path)

    print(f"  ✅ Saved: {output_path}")

except Exception as e:
    print(f"  ⚠️  Screenshot failed: {e}")
    print(f"  HTML saved at: {html_path}")
    print(f"  You can manually open this file and take a screenshot")

print("="*80)
print("✅ YUKON TERRITORY MAP COMPLETE")
print("="*80)

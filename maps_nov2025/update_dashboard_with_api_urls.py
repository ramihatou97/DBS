"""
Update dashboard index.html to use Google Maps Static API URLs
"""

# Read URLs
urls = {}
with open('static_api_urls.txt', 'r') as f:
    lines = f.readlines()
    i = 0
    while i < len(lines):
        if lines[i].strip() and not lines[i].startswith('http'):
            map_name = lines[i].strip()
            if i+1 < len(lines):
                url = lines[i+1].strip()
                urls[map_name] = url
                i += 2
            else:
                i += 1
        else:
            i += 1

# Map names to their API URLs
map_replacements = {
    'maps_nov2025/static_map1_travel_burden_heatmap.png': urls.get('map1_travel_burden', ''),
    'maps_nov2025/static_map3_indigenous_access_crisis.png': urls.get('map3_indigenous_crisis', ''),
    'maps_nov2025/static_map_atlantic_crisis.png': urls.get('map_atlantic_crisis', ''),
    'maps_nov2025/static_map5_patient_flow_animated.png': urls.get('map5_patient_flow', ''),
    'maps_nov2025/static_map_individual_patient_journeys.png': urls.get('map_individual_journeys', ''),
    'maps_nov2025/static_map12_regression_drivers.png': urls.get('map12_regression_drivers', ''),
    'maps_nov2025/static_map13_comparative_analysis_2015_2023.png': urls.get('map13_temporal_comparison', ''),
    'maps_nov2025/static_map_province_NL.png': urls.get('map_province_NL', ''),
    'maps_nov2025/static_map_province_NS.png': urls.get('map_province_NS', ''),
    'maps_nov2025/static_map_province_PE.png': urls.get('map_province_PE', ''),
    'maps_nov2025/static_map_province_NB.png': urls.get('map_province_NB', ''),
    'maps_nov2025/static_map_province_QC.png': urls.get('map_province_QC', ''),
    'maps_nov2025/static_map_province_ON.png': urls.get('map_province_ON', ''),
    'maps_nov2025/static_map_province_MB.png': urls.get('map_province_MB', ''),
    'maps_nov2025/static_map_province_SK.png': urls.get('map_province_SK', ''),
    'maps_nov2025/static_map_province_AB.png': urls.get('map_province_AB', ''),
    'maps_nov2025/static_map_province_BC.png': urls.get('map_province_BC', ''),
    'maps_nov2025/static_map_province_NT.png': '',  # Not generated (0 patients)
    'maps_nov2025/static_map_province_NU.png': urls.get('map_province_NU', ''),
}

# Read index.html
with open('../index.html', 'r') as f:
    html_content = f.read()

# Replace PNG paths with API URLs
for png_path, api_url in map_replacements.items():
    if api_url:  # Only replace if we have a URL
        html_content = html_content.replace(f'src="{png_path}"', f'src="{api_url}"')
        print(f"✓ Replaced {png_path}")
    else:
        print(f"✗ Skipped {png_path} (no URL available)")

# Write updated HTML
with open('../index.html', 'w') as f:
    f.write(html_content)

print(f"\n✓ Dashboard updated with Google Maps Static API URLs")
print(f"✓ {len([v for v in map_replacements.values() if v])} maps now use Google Maps API")

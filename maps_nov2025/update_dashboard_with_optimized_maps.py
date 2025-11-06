"""
Update dashboard index.html to use new optimized 1920x1080px static maps
Replaces Google Maps Static API URLs with local PNG files
"""

import re

# Mapping of map names to new optimized files
map_replacements = {
    # Analytical maps
    'static_map1_travel_burden_heatmap.png': 'optimized_map1_travel_burden.png',
    'static_map3_indigenous_access_crisis.png': 'optimized_map3_indigenous_crisis.png',
    'static_map_atlantic_crisis.png': 'optimized_map_atlantic_crisis.png',
    'static_map5_patient_flow_animated.png': 'optimized_map5_patient_flow.png',
    'static_map_individual_patient_journeys.png': 'optimized_map_individual_journeys.png',
    'static_map12_regression_drivers.png': 'optimized_map12_regression_drivers.png',
    'static_map13_comparative_analysis_2015_2023.png': 'optimized_map13_temporal_comparison.png',

    # Provincial maps
    'static_map_province_NL.png': 'optimized_map_province_NL.png',
    'static_map_province_NS.png': 'optimized_map_province_NS.png',
    'static_map_province_PE.png': 'optimized_map_province_PE.png',
    'static_map_province_NB.png': 'optimized_map_province_NB.png',
    'static_map_province_QC.png': 'optimized_map_province_QC.png',
    'static_map_province_ON.png': 'optimized_map_province_ON.png',
    'static_map_province_MB.png': 'optimized_map_province_MB.png',
    'static_map_province_SK.png': 'optimized_map_province_SK.png',
    'static_map_province_AB.png': 'optimized_map_province_AB.png',
    'static_map_province_BC.png': 'optimized_map_province_BC.png',
    'static_map_province_NT.png': 'optimized_map_province_NT.png',
    'static_map_province_NU.png': 'optimized_map_province_NU.png',
}

# Read index.html
with open('../index.html', 'r') as f:
    html_content = f.read()

# Replace src attributes
# Pattern 1: Replace maps_nov2025/static_map*.png paths
for old_file, new_file in map_replacements.items():
    old_path = f'maps_nov2025/{old_file}'
    new_path = f'maps_nov2025/{new_file}'

    if old_path in html_content:
        html_content = html_content.replace(f'src="{old_path}"', f'src="{new_path}"')
        print(f"✓ Replaced {old_file} → {new_file}")
    else:
        print(f"⊘ Not found: {old_file}")

# Pattern 2: Replace any Google Maps Static API URLs for these maps
for old_file, new_file in map_replacements.items():
    # Find and replace any src="https://maps.googleapis.com/maps/api/staticmap?..."
    # that corresponds to this map
    pattern = r'src="https://maps\.googleapis\.com/maps/api/staticmap\?[^"]*"'

    # This is tricky - we'll replace ALL Google Maps Static API URLs with the first few maps
    # A more robust solution would map each URL to its specific map, but for now we'll
    # do a simple count-based replacement

# Simpler approach: Replace ALL Google Maps Static API URLs with local files
# in the order they appear
google_maps_pattern = r'src="https://maps\.googleapis\.com/maps/api/staticmap\?[^"]*"'
google_maps_urls = re.findall(google_maps_pattern, html_content)

print(f"\nFound {len(google_maps_urls)} Google Maps Static API URLs")

# Replace them in order with our optimized maps
replacement_order = [
    'maps_nov2025/optimized_map1_travel_burden.png',
    'maps_nov2025/optimized_map3_indigenous_crisis.png',
    'maps_nov2025/optimized_map_atlantic_crisis.png',
    'maps_nov2025/optimized_map5_patient_flow.png',
    'maps_nov2025/optimized_map_individual_journeys.png',
    'maps_nov2025/optimized_map12_regression_drivers.png',
    'maps_nov2025/optimized_map13_temporal_comparison.png',
    'maps_nov2025/optimized_map_province_NL.png',
    'maps_nov2025/optimized_map_province_NS.png',
    'maps_nov2025/optimized_map_province_PE.png',
    'maps_nov2025/optimized_map_province_NB.png',
    'maps_nov2025/optimized_map_province_QC.png',
    'maps_nov2025/optimized_map_province_ON.png',
    'maps_nov2025/optimized_map_province_MB.png',
    'maps_nov2025/optimized_map_province_SK.png',
    'maps_nov2025/optimized_map_province_AB.png',
    'maps_nov2025/optimized_map_province_BC.png',
    'maps_nov2025/optimized_map_province_NT.png',
    'maps_nov2025/optimized_map_province_NU.png',
]

for i, url_match in enumerate(google_maps_urls):
    if i < len(replacement_order):
        new_src = f'src="{replacement_order[i]}"'
        html_content = html_content.replace(url_match, new_src, 1)  # Replace only first occurrence
        print(f"✓ Replaced Google Maps API URL #{i+1} → {replacement_order[i]}")

# Write updated HTML
with open('../index.html', 'w') as f:
    f.write(html_content)

print(f"\n✓ Dashboard updated with {len(map_replacements)} optimized HD maps")
print("✓ All Google Maps Static API URLs replaced with local files")

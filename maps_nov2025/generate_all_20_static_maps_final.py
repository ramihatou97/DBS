"""
Generate All 20 High-Quality Static Maps for DBS Dashboard
Professional aquamarine/charcoal color scheme with optimal zoom levels
300 DPI resolution, clear annotations, appropriate marker sizes
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrow
from matplotlib.lines import Line2D
import warnings
warnings.filterwarnings('ignore')

# Import color palette
import sys
sys.path.append('/Users/ramihatoum/Desktop/PPA/maps/final/')
import color_palette as cp

# Apply professional style
cp.apply_style()

# ============================================================================
# DBS CENTERS (9 locations)
# ============================================================================
DBS_CENTERS = {
    'Halifax NS': (44.646, -63.586),
    'London ON': (42.961, -81.226),
    'Toronto ON': (43.653, -79.405),
    'Edmonton AB': (53.521, -113.523),
    'Calgary AB': (51.064, -114.134),
    'Sherbrooke QC': (45.447, -71.870),
    'Montreal QC': (45.512, -73.557),
    'Quebec City QC': (46.837, -71.226),
    'Saskatoon SK': (52.132, -106.642)
}

# Province codes
PROVINCE_CODES = {
    1: 'NL', 10: 'NL', 2: 'PE', 11: 'PE', 3: 'NS', 12: 'NS',
    4: 'NB', 13: 'NB', 5: 'QC', 24: 'QC', 6: 'ON', 35: 'ON',
    7: 'MB', 46: 'MB', 8: 'SK', 47: 'SK', 9: 'AB', 48: 'AB',
    10: 'BC', 59: 'BC', 11: 'YT', 60: 'YT', 12: 'NT', 61: 'NT',
    13: 'NU', 62: 'NU'
}

# ============================================================================
# LOAD DATA
# ============================================================================
def load_all_data():
    """Load all necessary datasets"""
    print("\nLoading data...")

    # Patient data
    patients = pd.read_excel('/Users/ramihatoum/Desktop/PPA/maps/final/Final_database_05_11_25_FINAL.xlsx')

    # FSA aggregated data
    fsa_data = pd.read_csv('/Users/ramihatoum/Desktop/PPA/maps/final/fsa_aggregated_data_current.csv')

    # FSA centroids
    fsa_centroids = pd.read_csv('/Users/ramihatoum/Desktop/PPA/maps/fsa_population_centroids.csv')

    # Merge patient data with FSA coordinates
    patients = patients.merge(
        fsa_centroids[['fsa_code', 'pop_weighted_lat', 'pop_weighted_lon']],
        left_on='FSA', right_on='fsa_code', how='left'
    )

    print(f"  - Loaded {len(patients)} patients")
    print(f"  - Loaded {len(fsa_data)} FSA records")
    print(f"  - Loaded {len(fsa_centroids)} FSA centroids")

    return patients, fsa_data, fsa_centroids

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================
def add_jitter(lat, lon, amount=0.2):
    """Add random jitter to coordinates to prevent complete overlap"""
    return lat + np.random.uniform(-amount, amount), lon + np.random.uniform(-amount, amount)

def get_province_bounds(province_code):
    """Get optimal bounds for each province"""
    bounds = {
        'NL': {'lon': (-67, -52), 'lat': (46, 55), 'figsize': (12, 12)},
        'NS': {'lon': (-66.5, -59.5), 'lat': (43.3, 47.2), 'figsize': (12, 10)},
        'PE': {'lon': (-64.5, -61.8), 'lat': (45.8, 47.2), 'figsize': (10, 10)},
        'NB': {'lon': (-69, -63.5), 'lat': (44.5, 48.2), 'figsize': (12, 10)},
        'QC': {'lon': (-80, -57), 'lat': (45, 63), 'figsize': (12, 14)},
        'ON': {'lon': (-95, -74), 'lat': (41, 57), 'figsize': (14, 12)},
        'MB': {'lon': (-102, -95), 'lat': (49, 60), 'figsize': (9, 12)},
        'SK': {'lon': (-110, -101), 'lat': (49, 60), 'figsize': (10, 12)},
        'AB': {'lon': (-120, -110), 'lat': (49, 60), 'figsize': (10, 12)},
        'BC': {'lon': (-139, -114), 'lat': (48, 60), 'figsize': (10, 14)},
        'YT': {'lon': (-141, -123), 'lat': (60, 70), 'figsize': (10, 12)},
        'NT': {'lon': (-136, -102), 'lat': (60, 78), 'figsize': (14, 12)},
        'NU': {'lon': (-120, -60), 'lat': (60, 83), 'figsize': (16, 12)},
    }
    return bounds.get(province_code, {'lon': (-142, -52), 'lat': (41, 72), 'figsize': (14, 10)})

def draw_canada_outline(ax, bounds=None):
    """Draw simple Canada outline"""
    if bounds is None:
        bounds = {'lon': (-142, -52), 'lat': (41, 72)}

    # Simple provincial boundaries (approximate)
    provinces = [
        # BC
        [(-139, 60), (-139, 48), (-114, 49), (-114, 60), (-139, 60)],
        # AB
        [(-114, 49), (-114, 60), (-110, 60), (-110, 49), (-114, 49)],
        # SK
        [(-110, 49), (-110, 60), (-101.5, 60), (-101.5, 49), (-110, 49)],
        # MB
        [(-101.5, 49), (-101.5, 60), (-95, 60), (-95, 49), (-101.5, 49)],
        # ON
        [(-95, 41), (-95, 57), (-74, 57), (-74, 41), (-95, 41)],
        # QC
        [(-80, 45), (-80, 63), (-57, 63), (-57, 45), (-80, 45)],
    ]

    for province in provinces:
        lons = [p[0] for p in province]
        lats = [p[1] for p in province]
        ax.plot(lons, lats, color=cp.DARK_GRAY, linewidth=1.5, alpha=0.3, zorder=1)

# ============================================================================
# MAP 1: TRAVEL BURDEN HEATMAP
# ============================================================================
def generate_map1_travel_burden(patients, fsa_data):
    """Map 1: Travel distance heatmap across Canada"""
    print("\nGenerating Map 1: Travel Burden Heatmap...")

    fig, ax = plt.subplots(figsize=(16, 10), dpi=300)

    # Draw Canada outline
    draw_canada_outline(ax)

    # Plot FSA data with distance-based colors
    for _, row in fsa_data.iterrows():
        if pd.notna(row['latitude']) and pd.notna(row['longitude']):
            color = cp.get_distance_color(row['avg_distance_km'])
            size = row['patient_count'] * 40
            ax.scatter(row['longitude'], row['latitude'],
                      c=color, s=size, alpha=0.7, edgecolors='white',
                      linewidths=0.5, zorder=3)

    # Plot DBS centers
    for name, (lat, lon) in DBS_CENTERS.items():
        ax.scatter(lon, lat, c=cp.CHARCOAL, s=300, marker='*',
                  edgecolors='white', linewidths=2, zorder=5, label='DBS Center')
        ax.text(lon, lat-0.5, name.split()[0], fontsize=8, ha='center',
               va='top', fontweight='bold', color=cp.CHARCOAL)

    # Set bounds
    ax.set_xlim(-142, -52)
    ax.set_ylim(41, 72)
    ax.set_xlabel('Longitude', fontsize=12, fontweight='bold')
    ax.set_ylabel('Latitude', fontsize=12, fontweight='bold')
    ax.set_title('Map 1: Travel Burden Heatmap - DBS Access Across Canada',
                fontsize=16, fontweight='bold', pad=20)

    # Legend
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor=cp.DISTANCE_VERY_SHORT,
               markersize=10, label='<50 km'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor=cp.DISTANCE_SHORT,
               markersize=10, label='50-100 km'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor=cp.DISTANCE_MEDIUM,
               markersize=10, label='100-200 km'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor=cp.DISTANCE_LONG,
               markersize=10, label='200-500 km'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor=cp.DISTANCE_VERY_LONG,
               markersize=10, label='>500 km'),
        Line2D([0], [0], marker='*', color='w', markerfacecolor=cp.CHARCOAL,
               markersize=15, label='DBS Center'),
    ]
    ax.legend(handles=legend_elements, loc='lower left', frameon=True,
             fancybox=True, shadow=True, fontsize=10)

    # Statistics box
    stats_text = f"Total Patients: {len(patients)}\n"
    stats_text += f"Median Distance: {patients['Driving Distance (km)'].median():.0f} km\n"
    stats_text += f"Mean Distance: {patients['Driving Distance (km)'].mean():.0f} km"
    ax.text(0.98, 0.98, stats_text, transform=ax.transAxes,
           fontsize=10, verticalalignment='top', horizontalalignment='right',
           bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    plt.tight_layout()
    plt.savefig('/Users/ramihatoum/Desktop/PPA/maps/final/maps_nov2025/static_map1_travel_burden_heatmap.png',
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print("  ✓ Map 1 saved")

# ============================================================================
# MAP 3: INDIGENOUS ACCESS CRISIS
# ============================================================================
def generate_map3_indigenous_crisis(patients, fsa_data):
    """Map 3: Indigenous ancestry patterns"""
    print("\nGenerating Map 3: Indigenous Access Crisis...")

    fig, ax = plt.subplots(figsize=(16, 10), dpi=300)

    draw_canada_outline(ax)

    # Plot FSA data with indigenous ancestry colors
    for _, row in fsa_data.iterrows():
        if pd.notna(row['latitude']) and pd.notna(row['longitude']):
            # Color by indigenous ancestry rate
            ancestry = row['indigenous_ancestry_rate']
            if ancestry < 5:
                color = cp.AQUA_LIGHT
            elif ancestry < 15:
                color = cp.AQUA_MEDIUM
            elif ancestry < 30:
                color = cp.AQUA
            elif ancestry < 50:
                color = cp.CORAL
            else:
                color = cp.SALMON

            size = row['patient_count'] * 40
            ax.scatter(row['longitude'], row['latitude'],
                      c=color, s=size, alpha=0.7, edgecolors='white',
                      linewidths=0.5, zorder=3)

    # Plot DBS centers
    for name, (lat, lon) in DBS_CENTERS.items():
        ax.scatter(lon, lat, c=cp.CHARCOAL, s=300, marker='*',
                  edgecolors='white', linewidths=2, zorder=5)
        ax.text(lon, lat-0.5, name.split()[0], fontsize=8, ha='center',
               va='top', fontweight='bold', color=cp.CHARCOAL)

    ax.set_xlim(-142, -52)
    ax.set_ylim(41, 72)
    ax.set_xlabel('Longitude', fontsize=12, fontweight='bold')
    ax.set_ylabel('Latitude', fontsize=12, fontweight='bold')
    ax.set_title('Map 3: Indigenous Access Crisis - Ancestry Patterns',
                fontsize=16, fontweight='bold', pad=20)

    # Legend
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor=cp.AQUA_LIGHT,
               markersize=10, label='<5% Indigenous'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor=cp.AQUA_MEDIUM,
               markersize=10, label='5-15% Indigenous'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor=cp.AQUA,
               markersize=10, label='15-30% Indigenous'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor=cp.CORAL,
               markersize=10, label='30-50% Indigenous'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor=cp.SALMON,
               markersize=10, label='>50% Indigenous'),
    ]
    ax.legend(handles=legend_elements, loc='lower left', frameon=True,
             fancybox=True, shadow=True, fontsize=10)

    # Statistics
    avg_indigenous = patients['Indigenous Ancestry'].mean()
    stats_text = f"Avg Indigenous Ancestry: {avg_indigenous:.1f}%\n"
    stats_text += f"High Ancestry (>30%): {(patients['Indigenous Ancestry'] > 30).sum()} patients"
    ax.text(0.98, 0.98, stats_text, transform=ax.transAxes,
           fontsize=10, verticalalignment='top', horizontalalignment='right',
           bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    plt.tight_layout()
    plt.savefig('/Users/ramihatoum/Desktop/PPA/maps/final/maps_nov2025/static_map3_indigenous_access_crisis.png',
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print("  ✓ Map 3 saved")

# ============================================================================
# MAP: ATLANTIC CRISIS
# ============================================================================
def generate_map_atlantic_crisis(patients):
    """Atlantic provinces focus (NB, NS, PE, NL)"""
    print("\nGenerating Atlantic Crisis Map...")

    # Filter Atlantic patients
    atlantic_provinces = ['NL', 'NS', 'PE', 'NB']
    atlantic_patients = patients[patients['FSA'].str[0].isin(['A', 'B', 'E'])]

    fig, ax = plt.subplots(figsize=(12, 10), dpi=300)

    # Plot patients with jitter and distance colors
    for _, patient in atlantic_patients.iterrows():
        if pd.notna(patient['pop_weighted_lat']) and pd.notna(patient['pop_weighted_lon']):
            lat_j, lon_j = add_jitter(patient['pop_weighted_lat'],
                                      patient['pop_weighted_lon'], 0.15)
            color = cp.get_distance_color(patient['Driving Distance (km)'])
            ax.scatter(lon_j, lat_j, c=color, s=50, alpha=0.7,
                      edgecolors='white', linewidths=0.5, zorder=3)

    # Plot Halifax DBS center
    ax.scatter(-63.586, 44.646, c=cp.CHARCOAL, s=500, marker='*',
              edgecolors='white', linewidths=2, zorder=5)
    ax.text(-63.586, 44.1, 'Halifax\nDBS Center', fontsize=10, ha='center',
           fontweight='bold', color=cp.CHARCOAL)

    ax.set_xlim(-67, -52)
    ax.set_ylim(43, 55)
    ax.set_xlabel('Longitude', fontsize=12, fontweight='bold')
    ax.set_ylabel('Latitude', fontsize=12, fontweight='bold')
    ax.set_title('Atlantic Crisis: Geographic Isolation and Travel Burden',
                fontsize=16, fontweight='bold', pad=20)

    # Legend
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor=cp.DISTANCE_MEDIUM,
               markersize=10, label='100-200 km'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor=cp.DISTANCE_LONG,
               markersize=10, label='200-500 km'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor=cp.DISTANCE_VERY_LONG,
               markersize=10, label='>500 km'),
    ]
    ax.legend(handles=legend_elements, loc='lower left', frameon=True,
             fancybox=True, shadow=True, fontsize=10)

    # Statistics
    stats_text = f"Atlantic Patients: {len(atlantic_patients)}\n"
    stats_text += f"Median Distance: {atlantic_patients['Driving Distance (km)'].median():.0f} km\n"
    stats_text += f">500 km: {(atlantic_patients['Driving Distance (km)'] > 500).sum()} patients"
    ax.text(0.98, 0.98, stats_text, transform=ax.transAxes,
           fontsize=10, verticalalignment='top', horizontalalignment='right',
           bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    plt.tight_layout()
    plt.savefig('/Users/ramihatoum/Desktop/PPA/maps/final/maps_nov2025/static_map_atlantic_crisis.png',
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print("  ✓ Atlantic Crisis map saved")

# ============================================================================
# MAP 5: PATIENT FLOW ANIMATED
# ============================================================================
def generate_map5_patient_flows(patients):
    """Map 5: Patient flow lines from origin to DBS centers"""
    print("\nGenerating Map 5: Patient Flow Lines...")

    fig, ax = plt.subplots(figsize=(16, 10), dpi=300)

    draw_canada_outline(ax)

    # Sample 200 patients for clarity (not 936 overlapping lines)
    sample_patients = patients.sample(n=min(200, len(patients)), random_state=42)

    # Draw flow lines
    for _, patient in sample_patients.iterrows():
        if pd.notna(patient['pop_weighted_lat']) and pd.notna(patient['pop_weighted_lon']):
            origin_lat = patient['pop_weighted_lat']
            origin_lon = patient['pop_weighted_lon']

            # Find nearest DBS center
            min_dist = float('inf')
            nearest_center = None
            for name, (lat, lon) in DBS_CENTERS.items():
                dist = np.sqrt((lat - origin_lat)**2 + (lon - origin_lon)**2)
                if dist < min_dist:
                    min_dist = dist
                    nearest_center = (lat, lon)

            if nearest_center:
                color = cp.get_distance_color(patient['Driving Distance (km)'])
                ax.plot([origin_lon, nearest_center[1]],
                       [origin_lat, nearest_center[0]],
                       color=color, linewidth=0.5, alpha=0.3, zorder=2)

    # Plot DBS centers
    for name, (lat, lon) in DBS_CENTERS.items():
        ax.scatter(lon, lat, c=cp.CHARCOAL, s=300, marker='*',
                  edgecolors='white', linewidths=2, zorder=5)
        ax.text(lon, lat-0.5, name.split()[0], fontsize=8, ha='center',
               va='top', fontweight='bold', color=cp.CHARCOAL)

    ax.set_xlim(-142, -52)
    ax.set_ylim(41, 72)
    ax.set_xlabel('Longitude', fontsize=12, fontweight='bold')
    ax.set_ylabel('Latitude', fontsize=12, fontweight='bold')
    ax.set_title('Map 5: Patient Flow Patterns - Origins to DBS Centers',
                fontsize=16, fontweight='bold', pad=20)

    # Legend
    legend_elements = [
        Line2D([0], [0], color=cp.DISTANCE_VERY_SHORT, linewidth=2, label='<50 km'),
        Line2D([0], [0], color=cp.DISTANCE_SHORT, linewidth=2, label='50-100 km'),
        Line2D([0], [0], color=cp.DISTANCE_MEDIUM, linewidth=2, label='100-200 km'),
        Line2D([0], [0], color=cp.DISTANCE_LONG, linewidth=2, label='200-500 km'),
        Line2D([0], [0], color=cp.DISTANCE_VERY_LONG, linewidth=2, label='>500 km'),
    ]
    ax.legend(handles=legend_elements, loc='lower left', frameon=True,
             fancybox=True, shadow=True, fontsize=10)

    stats_text = f"Flow Lines Shown: {len(sample_patients)}\n"
    stats_text += f"Total Patients: {len(patients)}\n"
    stats_text += f"DBS Centers: {len(DBS_CENTERS)}"
    ax.text(0.98, 0.98, stats_text, transform=ax.transAxes,
           fontsize=10, verticalalignment='top', horizontalalignment='right',
           bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    plt.tight_layout()
    plt.savefig('/Users/ramihatoum/Desktop/PPA/maps/final/maps_nov2025/static_map5_patient_flow_animated.png',
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print("  ✓ Map 5 saved")

# ============================================================================
# MAP: INDIVIDUAL PATIENT JOURNEYS
# ============================================================================
def generate_map_individual_journeys(patients):
    """Individual patient paths (936 patients with jitter)"""
    print("\nGenerating Individual Patient Journeys Map...")

    fig, ax = plt.subplots(figsize=(16, 10), dpi=300)

    draw_canada_outline(ax)

    # Plot all patients with jitter
    for _, patient in patients.iterrows():
        if pd.notna(patient['pop_weighted_lat']) and pd.notna(patient['pop_weighted_lon']):
            lat_j, lon_j = add_jitter(patient['pop_weighted_lat'],
                                      patient['pop_weighted_lon'], 0.25)
            color = cp.get_distance_color(patient['Driving Distance (km)'])
            ax.scatter(lon_j, lat_j, c=color, s=20, alpha=0.6,
                      edgecolors='none', zorder=3)

    # Plot DBS centers
    for name, (lat, lon) in DBS_CENTERS.items():
        ax.scatter(lon, lat, c=cp.CHARCOAL, s=300, marker='*',
                  edgecolors='white', linewidths=2, zorder=5)
        ax.text(lon, lat-0.5, name.split()[0], fontsize=8, ha='center',
               va='top', fontweight='bold', color=cp.CHARCOAL)

    ax.set_xlim(-142, -52)
    ax.set_ylim(41, 72)
    ax.set_xlabel('Longitude', fontsize=12, fontweight='bold')
    ax.set_ylabel('Latitude', fontsize=12, fontweight='bold')
    ax.set_title('Individual Patient Journeys: All 936 DBS Patients',
                fontsize=16, fontweight='bold', pad=20)

    # Legend
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor=cp.DISTANCE_VERY_SHORT,
               markersize=10, label='<50 km'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor=cp.DISTANCE_SHORT,
               markersize=10, label='50-100 km'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor=cp.DISTANCE_MEDIUM,
               markersize=10, label='100-200 km'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor=cp.DISTANCE_LONG,
               markersize=10, label='200-500 km'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor=cp.DISTANCE_VERY_LONG,
               markersize=10, label='>500 km'),
    ]
    ax.legend(handles=legend_elements, loc='lower left', frameon=True,
             fancybox=True, shadow=True, fontsize=10)

    stats_text = f"Total Patients: {len(patients)}\n"
    stats_text += f"DBS Centers: {len(DBS_CENTERS)}\n"
    stats_text += f"Median Distance: {patients['Driving Distance (km)'].median():.0f} km"
    ax.text(0.98, 0.98, stats_text, transform=ax.transAxes,
           fontsize=10, verticalalignment='top', horizontalalignment='right',
           bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    plt.tight_layout()
    plt.savefig('/Users/ramihatoum/Desktop/PPA/maps/final/maps_nov2025/static_map_individual_patient_journeys.png',
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print("  ✓ Individual Journeys map saved")

# ============================================================================
# MAP 12: REGRESSION DRIVERS
# ============================================================================
def generate_map12_regression_drivers(patients):
    """Map 12: Key disparity drivers visualization"""
    print("\nGenerating Map 12: Regression Drivers...")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 10), dpi=300)

    # Left panel: Distance-based
    draw_canada_outline(ax1)
    for _, patient in patients.iterrows():
        if pd.notna(patient['pop_weighted_lat']) and pd.notna(patient['pop_weighted_lon']):
            lat_j, lon_j = add_jitter(patient['pop_weighted_lat'],
                                      patient['pop_weighted_lon'], 0.25)
            color = cp.get_distance_color(patient['Driving Distance (km)'])
            ax1.scatter(lon_j, lat_j, c=color, s=20, alpha=0.6, zorder=3)

    for name, (lat, lon) in DBS_CENTERS.items():
        ax1.scatter(lon, lat, c=cp.CHARCOAL, s=200, marker='*',
                   edgecolors='white', linewidths=2, zorder=5)

    ax1.set_xlim(-142, -52)
    ax1.set_ylim(41, 72)
    ax1.set_title('Access Disparity: Distance', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Longitude', fontsize=11)
    ax1.set_ylabel('Latitude', fontsize=11)

    # Right panel: Indigenous ancestry
    draw_canada_outline(ax2)
    for _, patient in patients.iterrows():
        if pd.notna(patient['pop_weighted_lat']) and pd.notna(patient['pop_weighted_lon']):
            lat_j, lon_j = add_jitter(patient['pop_weighted_lat'],
                                      patient['pop_weighted_lon'], 0.25)
            ancestry = patient['Indigenous Ancestry']
            if ancestry < 5:
                color = cp.AQUA_LIGHT
            elif ancestry < 15:
                color = cp.AQUA_MEDIUM
            elif ancestry < 30:
                color = cp.AQUA
            else:
                color = cp.CORAL
            ax2.scatter(lon_j, lat_j, c=color, s=20, alpha=0.6, zorder=3)

    for name, (lat, lon) in DBS_CENTERS.items():
        ax2.scatter(lon, lat, c=cp.CHARCOAL, s=200, marker='*',
                   edgecolors='white', linewidths=2, zorder=5)

    ax2.set_xlim(-142, -52)
    ax2.set_ylim(41, 72)
    ax2.set_title('Social Disparity: Indigenous Ancestry', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Longitude', fontsize=11)
    ax2.set_ylabel('Latitude', fontsize=11)

    plt.suptitle('Map 12: Key Disparity Drivers - Access vs Social Factors',
                fontsize=16, fontweight='bold', y=0.98)

    plt.tight_layout()
    plt.savefig('/Users/ramihatoum/Desktop/PPA/maps/final/maps_nov2025/static_map12_regression_drivers.png',
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print("  ✓ Map 12 saved")

# ============================================================================
# MAP 13: TEMPORAL COMPARISON
# ============================================================================
def generate_map13_temporal_comparison(patients):
    """Map 13: Temporal comparison 2015-2023"""
    print("\nGenerating Map 13: Temporal Comparison...")

    # Split by time period
    patients['Period'] = patients['ORYear'].apply(lambda x: 'Early (2015-2019)' if x < 2020 else 'Recent (2020-2023)')
    early = patients[patients['Period'] == 'Early (2015-2019)']
    recent = patients[patients['Period'] == 'Recent (2020-2023)']

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 10), dpi=300)

    # Early period
    draw_canada_outline(ax1)
    for _, patient in early.iterrows():
        if pd.notna(patient['pop_weighted_lat']) and pd.notna(patient['pop_weighted_lon']):
            lat_j, lon_j = add_jitter(patient['pop_weighted_lat'],
                                      patient['pop_weighted_lon'], 0.25)
            color = cp.get_distance_color(patient['Driving Distance (km)'])
            ax1.scatter(lon_j, lat_j, c=color, s=25, alpha=0.6, zorder=3)

    for name, (lat, lon) in DBS_CENTERS.items():
        ax1.scatter(lon, lat, c=cp.CHARCOAL, s=200, marker='*',
                   edgecolors='white', linewidths=2, zorder=5)

    ax1.set_xlim(-142, -52)
    ax1.set_ylim(41, 72)
    ax1.set_title(f'Early Period: 2015-2019 (n={len(early)})', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Longitude', fontsize=11)
    ax1.set_ylabel('Latitude', fontsize=11)

    # Recent period
    draw_canada_outline(ax2)
    for _, patient in recent.iterrows():
        if pd.notna(patient['pop_weighted_lat']) and pd.notna(patient['pop_weighted_lon']):
            lat_j, lon_j = add_jitter(patient['pop_weighted_lat'],
                                      patient['pop_weighted_lon'], 0.25)
            color = cp.get_distance_color(patient['Driving Distance (km)'])
            ax2.scatter(lon_j, lat_j, c=color, s=25, alpha=0.6, zorder=3)

    for name, (lat, lon) in DBS_CENTERS.items():
        ax2.scatter(lon, lat, c=cp.CHARCOAL, s=200, marker='*',
                   edgecolors='white', linewidths=2, zorder=5)

    ax2.set_xlim(-142, -52)
    ax2.set_ylim(41, 72)
    ax2.set_title(f'Recent Period: 2020-2023 (n={len(recent)})', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Longitude', fontsize=11)
    ax2.set_ylabel('Latitude', fontsize=11)

    plt.suptitle('Map 13: Temporal Comparison - DBS Access Evolution',
                fontsize=16, fontweight='bold', y=0.98)

    # Shared legend
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor=cp.DISTANCE_VERY_SHORT,
               markersize=10, label='<50 km'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor=cp.DISTANCE_MEDIUM,
               markersize=10, label='100-200 km'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor=cp.DISTANCE_VERY_LONG,
               markersize=10, label='>500 km'),
    ]
    fig.legend(handles=legend_elements, loc='lower center', ncol=3,
              frameon=True, fancybox=True, fontsize=10)

    plt.tight_layout()
    plt.savefig('/Users/ramihatoum/Desktop/PPA/maps/final/maps_nov2025/static_map13_comparative_analysis_2015_2023.png',
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print("  ✓ Map 13 saved")

# ============================================================================
# PROVINCIAL/TERRITORIAL MAPS (13 maps)
# ============================================================================
def generate_provincial_map(patients, province_code):
    """Generate a single provincial/territorial map"""
    print(f"\nGenerating {province_code} map...")

    # Filter patients for this province
    if province_code == 'NL':
        prov_patients = patients[patients['FSA'].str[0] == 'A']
    elif province_code == 'NS':
        prov_patients = patients[patients['FSA'].str[0] == 'B']
    elif province_code == 'PE':
        prov_patients = patients[patients['FSA'].str[0] == 'C']
    elif province_code == 'NB':
        prov_patients = patients[patients['FSA'].str[0] == 'E']
    elif province_code == 'QC':
        prov_patients = patients[patients['FSA'].str[0].isin(['G', 'H', 'J'])]
    elif province_code == 'ON':
        prov_patients = patients[patients['FSA'].str[0].isin(['K', 'L', 'M', 'N', 'P'])]
    elif province_code == 'MB':
        prov_patients = patients[patients['FSA'].str[0] == 'R']
    elif province_code == 'SK':
        prov_patients = patients[patients['FSA'].str[0] == 'S']
    elif province_code == 'AB':
        prov_patients = patients[patients['FSA'].str[0] == 'T']
    elif province_code == 'BC':
        prov_patients = patients[patients['FSA'].str[0] == 'V']
    elif province_code == 'YT':
        prov_patients = patients[patients['FSA'].str[0] == 'Y']
    elif province_code == 'NT':
        prov_patients = patients[patients['FSA'].str[0] == 'X']
    elif province_code == 'NU':
        prov_patients = patients[patients['FSA'].str[0] == 'X']  # Note: NT and NU share X
    else:
        prov_patients = patients[patients['Province'] == province_code]

    if len(prov_patients) == 0:
        print(f"  ⚠ No patients found for {province_code}")
        return

    # Get bounds
    bounds = get_province_bounds(province_code)

    fig, ax = plt.subplots(figsize=bounds['figsize'], dpi=300)

    # Plot patients
    for _, patient in prov_patients.iterrows():
        if pd.notna(patient['pop_weighted_lat']) and pd.notna(patient['pop_weighted_lon']):
            lat_j, lon_j = add_jitter(patient['pop_weighted_lat'],
                                      patient['pop_weighted_lon'], 0.15)
            color = cp.get_distance_color(patient['Driving Distance (km)'])
            ax.scatter(lon_j, lat_j, c=color, s=40, alpha=0.7,
                      edgecolors='white', linewidths=0.5, zorder=3)

    # Plot relevant DBS centers
    for name, (lat, lon) in DBS_CENTERS.items():
        # Only show DBS centers within or near this province
        if (bounds['lon'][0] - 5 <= lon <= bounds['lon'][1] + 5 and
            bounds['lat'][0] - 2 <= lat <= bounds['lat'][1] + 2):
            ax.scatter(lon, lat, c=cp.CHARCOAL, s=400, marker='*',
                      edgecolors='white', linewidths=2, zorder=5)
            ax.text(lon, lat-0.3, name.split()[0], fontsize=9, ha='center',
                   va='top', fontweight='bold', color=cp.CHARCOAL)

    ax.set_xlim(bounds['lon'])
    ax.set_ylim(bounds['lat'])
    ax.set_xlabel('Longitude', fontsize=12, fontweight='bold')
    ax.set_ylabel('Latitude', fontsize=12, fontweight='bold')
    ax.set_title(f'{province_code}: DBS Access Distribution',
                fontsize=16, fontweight='bold', pad=20)

    # Legend
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor=cp.DISTANCE_VERY_SHORT,
               markersize=10, label='<50 km'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor=cp.DISTANCE_SHORT,
               markersize=10, label='50-100 km'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor=cp.DISTANCE_MEDIUM,
               markersize=10, label='100-200 km'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor=cp.DISTANCE_LONG,
               markersize=10, label='200-500 km'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor=cp.DISTANCE_VERY_LONG,
               markersize=10, label='>500 km'),
    ]
    ax.legend(handles=legend_elements, loc='best', frameon=True,
             fancybox=True, shadow=True, fontsize=9)

    # Statistics
    stats_text = f"Patients: {len(prov_patients)}\n"
    stats_text += f"Median Distance: {prov_patients['Driving Distance (km)'].median():.0f} km\n"
    stats_text += f">200 km: {(prov_patients['Driving Distance (km)'] > 200).sum()}"
    ax.text(0.98, 0.98, stats_text, transform=ax.transAxes,
           fontsize=9, verticalalignment='top', horizontalalignment='right',
           bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    plt.tight_layout()
    plt.savefig(f'/Users/ramihatoum/Desktop/PPA/maps/final/maps_nov2025/static_map_province_{province_code}.png',
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  ✓ {province_code} map saved")

# ============================================================================
# MAIN EXECUTION
# ============================================================================
def main():
    """Generate all 20 static maps"""
    print("="*80)
    print("GENERATING ALL 20 HIGH-QUALITY STATIC MAPS FOR DBS DASHBOARD")
    print("="*80)

    # Load data
    patients, fsa_data, fsa_centroids = load_all_data()

    # Generate analytical maps (7)
    print("\n" + "="*80)
    print("PART 1: ANALYTICAL MAPS (7 maps)")
    print("="*80)

    generate_map1_travel_burden(patients, fsa_data)
    generate_map3_indigenous_crisis(patients, fsa_data)
    generate_map_atlantic_crisis(patients)
    generate_map5_patient_flows(patients)
    generate_map_individual_journeys(patients)
    generate_map12_regression_drivers(patients)
    generate_map13_temporal_comparison(patients)

    # Generate provincial/territorial maps (13)
    print("\n" + "="*80)
    print("PART 2: PROVINCIAL/TERRITORIAL MAPS (13 maps)")
    print("="*80)

    provinces = ['NL', 'NS', 'PE', 'NB', 'QC', 'ON', 'MB', 'SK', 'AB', 'BC', 'YT', 'NT', 'NU']
    for prov in provinces:
        generate_provincial_map(patients, prov)

    print("\n" + "="*80)
    print("ALL 20 MAPS GENERATED SUCCESSFULLY!")
    print("="*80)

    # Summary
    print("\nSUMMARY:")
    print("-" * 80)
    print("Analytical Maps (7):")
    print("  1. Travel Burden Heatmap")
    print("  2. Indigenous Access Crisis")
    print("  3. Atlantic Crisis")
    print("  4. Patient Flow Animated")
    print("  5. Individual Patient Journeys")
    print("  6. Regression Drivers")
    print("  7. Temporal Comparison 2015-2023")
    print("\nProvincial/Territorial Maps (13):")
    print("  8-20. NL, NS, PE, NB, QC, ON, MB, SK, AB, BC, YT, NT, NU")
    print("\nAll maps saved to: /Users/ramihatoum/Desktop/PPA/maps/final/maps_nov2025/")
    print("Resolution: 300 DPI")
    print("Color scheme: Professional Aquamarine & Charcoal")
    print("="*80)

if __name__ == '__main__':
    main()

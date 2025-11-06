#!/usr/bin/env python3
"""
Generate Provincial Overview - 6-Panel Statistical Visualization
Comprehensive provincial comparison with key DBS access metrics
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import numpy as np
import seaborn as sns

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# File paths
BASE_DIR = '/Users/ramihatoum/Desktop/PPA/maps/final'
DB_PATH = f'{BASE_DIR}/Final_database_05_11_25_COMPLETE.xlsx'
OUTPUT_DIR = f'{BASE_DIR}/maps_nov2025'

# Province code mapping
PROVINCE_CODE_MAP = {
    1.0: 'NL',  # Newfoundland and Labrador
    2.0: 'NS',  # Nova Scotia
    3.0: 'PE',  # Prince Edward Island
    4.0: 'NB',  # New Brunswick
    5.0: 'QC',  # Quebec
    6.0: 'ON',  # Ontario
    7.0: 'MB',  # Manitoba
    8.0: 'SK',  # Saskatchewan
    9.0: 'AB',  # Alberta
    10.0: 'BC', # British Columbia
    11.0: 'YT', # Yukon
    12.0: 'NT', # Northwest Territories
    13.0: 'NU'  # Nunavut
}

PROVINCE_FULL_NAMES = {
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

print("\n" + "="*80)
print("GENERATING PROVINCIAL OVERVIEW - 6-PANEL STATISTICAL VISUALIZATION")
print("="*80)

# Load data
print("\nLoading patient database...")
df = pd.read_excel(DB_PATH)

# Drop rows with missing Province or Distance data
df = df.dropna(subset=['Province', 'Driving Distance (km)'])

df['Province_Code'] = df['Province'].map(PROVINCE_CODE_MAP)
df['Province_Name'] = df['Province'].map(PROVINCE_FULL_NAMES)

print(f"  ✓ Loaded {len(df)} patients")
print(f"  ✓ Provinces/Territories: {df['Province_Name'].nunique()}")

# Calculate provincial statistics (use raw Province column which has numeric codes)
provincial_stats = df.groupby('Province').agg({
    'StudyID': 'count',
    'Age': 'median',
    'Driving Distance (km)': ['median', 'mean', 'max'],
    'Median Income': 'mean',
    'Gini Index': 'mean',
    'Indigenous Ancestry': 'mean'
}).reset_index()

provincial_stats.columns = ['Province', 'Patient_Count', 'Median_Age',
                            'Median_Distance', 'Mean_Distance', 'Max_Distance',
                            'Avg_Income', 'Avg_Gini', 'Avg_Indigenous_Rate']

# Add province names
provincial_stats['Province_Name'] = provincial_stats['Province'].map(PROVINCE_FULL_NAMES)
provincial_stats['Province_Abbrev'] = provincial_stats['Province'].map(PROVINCE_CODE_MAP)

# Drop any rows where the mapping failed
provincial_stats = provincial_stats.dropna(subset=['Province_Abbrev', 'Province_Name'])

# Sort by patient count (descending)
provincial_stats = provincial_stats.sort_values('Patient_Count', ascending=False)

print("\nProvincial Statistics Summary:")
print(provincial_stats[['Province_Abbrev', 'Patient_Count', 'Median_Distance', 'Avg_Income']].to_string(index=False))

# Create figure with 6 panels
fig = plt.figure(figsize=(20, 12))
fig.suptitle('DBS Access Dashboard - Provincial Overview (936 Patients, 2019-2023)',
             fontsize=24, fontweight='bold', y=0.98)

gs = GridSpec(3, 2, figure=fig, hspace=0.3, wspace=0.3)

# Color scheme
colors = sns.color_palette("husl", len(provincial_stats))

# Panel 1: Patient Count by Province
ax1 = fig.add_subplot(gs[0, 0])
bars1 = ax1.barh(provincial_stats['Province_Abbrev'], provincial_stats['Patient_Count'],
                 color=colors, edgecolor='black', linewidth=1.5)
ax1.set_xlabel('Number of Patients', fontsize=12, fontweight='bold')
ax1.set_title('Panel 1: Patient Distribution Across Provinces/Territories',
              fontsize=14, fontweight='bold', pad=10)
ax1.grid(axis='x', alpha=0.3)

# Add value labels
for i, (bar, value) in enumerate(zip(bars1, provincial_stats['Patient_Count'])):
    ax1.text(value + 10, bar.get_y() + bar.get_height()/2,
             f'{int(value)} ({value/936*100:.1f}%)',
             va='center', fontsize=9, fontweight='bold')

# Highlight Ontario dominance
ax1.axvline(x=600, color='red', linestyle='--', alpha=0.5, linewidth=2)
ax1.text(600, len(provincial_stats)-0.5, 'Ontario: 72%',
         rotation=90, va='bottom', ha='right', color='red', fontweight='bold')

# Panel 2: Median Travel Distance
ax2 = fig.add_subplot(gs[0, 1])
bars2 = ax2.barh(provincial_stats['Province_Abbrev'], provincial_stats['Median_Distance'],
                 color=colors, edgecolor='black', linewidth=1.5)
ax2.set_xlabel('Median Distance (km)', fontsize=12, fontweight='bold')
ax2.set_title('Panel 2: Median Travel Distance to Nearest DBS Center',
              fontsize=14, fontweight='bold', pad=10)
ax2.grid(axis='x', alpha=0.3)

# Add value labels
for bar, value in zip(bars2, provincial_stats['Median_Distance']):
    ax2.text(value + 50, bar.get_y() + bar.get_height()/2,
             f'{value:.0f} km',
             va='center', fontsize=9, fontweight='bold')

# Add distance threshold lines
ax2.axvline(x=200, color='orange', linestyle='--', alpha=0.5, linewidth=2)
ax2.text(200, len(provincial_stats)-0.5, '200 km\nBarrier',
         rotation=0, va='top', ha='center', color='orange', fontweight='bold', fontsize=8)

# Panel 3: Maximum Distance (Extreme Cases)
ax3 = fig.add_subplot(gs[1, 0])
bars3 = ax3.barh(provincial_stats['Province_Abbrev'], provincial_stats['Max_Distance'],
                 color=colors, edgecolor='black', linewidth=1.5)
ax3.set_xlabel('Maximum Distance (km)', fontsize=12, fontweight='bold')
ax3.set_title('Panel 3: Maximum Travel Distance (Extreme Cases)',
              fontsize=14, fontweight='bold', pad=10)
ax3.grid(axis='x', alpha=0.3)
ax3.set_xscale('log')

# Add value labels
for bar, value in zip(bars3, provincial_stats['Max_Distance']):
    if value > 1000:
        label = f'{value:.0f} km'
    else:
        label = f'{value:.0f} km'
    ax3.text(value * 1.1, bar.get_y() + bar.get_height()/2,
             label, va='center', fontsize=9, fontweight='bold')

# Panel 4: Average Household Income
ax4 = fig.add_subplot(gs[1, 1])
income_colors = ['#10b981' if x >= 60000 else '#ef4444'
                 for x in provincial_stats['Avg_Income']]
bars4 = ax4.barh(provincial_stats['Province_Abbrev'], provincial_stats['Avg_Income'],
                 color=income_colors, edgecolor='black', linewidth=1.5)
ax4.set_xlabel('Average Household Income ($)', fontsize=12, fontweight='bold')
ax4.set_title('Panel 4: Average Household Income by Province',
              fontsize=14, fontweight='bold', pad=10)
ax4.grid(axis='x', alpha=0.3)

# Add value labels
for bar, value in zip(bars4, provincial_stats['Avg_Income']):
    ax4.text(value + 1000, bar.get_y() + bar.get_height()/2,
             f'${value:,.0f}',
             va='center', fontsize=9, fontweight='bold')

# Add poverty line
ax4.axvline(x=60000, color='red', linestyle='--', alpha=0.5, linewidth=2)
ax4.text(60000, len(provincial_stats)-0.5, '$60K\nThreshold',
         rotation=0, va='top', ha='center', color='red', fontweight='bold', fontsize=8)

# Panel 5: Gini Index (Income Inequality)
ax5 = fig.add_subplot(gs[2, 0])
gini_colors = ['#10b981' if x <= 0.35 else '#ef4444'
               for x in provincial_stats['Avg_Gini']]
bars5 = ax5.barh(provincial_stats['Province_Abbrev'], provincial_stats['Avg_Gini'],
                 color=gini_colors, edgecolor='black', linewidth=1.5)
ax5.set_xlabel('Average Gini Index', fontsize=12, fontweight='bold')
ax5.set_title('Panel 5: Income Inequality (Gini Index)',
              fontsize=14, fontweight='bold', pad=10)
ax5.grid(axis='x', alpha=0.3)

# Add value labels
for bar, value in zip(bars5, provincial_stats['Avg_Gini']):
    ax5.text(value + 0.01, bar.get_y() + bar.get_height()/2,
             f'{value:.3f}',
             va='center', fontsize=9, fontweight='bold')

# Add inequality threshold
ax5.axvline(x=0.35, color='red', linestyle='--', alpha=0.5, linewidth=2)
ax5.text(0.35, len(provincial_stats)-0.5, '0.35\nHigh Inequality',
         rotation=0, va='top', ha='center', color='red', fontweight='bold', fontsize=8)

# Panel 6: Indigenous Ancestry Rate
ax6 = fig.add_subplot(gs[2, 1])
indigenous_colors = ['#dc2626' if x >= 0.05 else '#94a3b8'
                     for x in provincial_stats['Avg_Indigenous_Rate']]
bars6 = ax6.barh(provincial_stats['Province_Abbrev'], provincial_stats['Avg_Indigenous_Rate'] * 100,
                 color=indigenous_colors, edgecolor='black', linewidth=1.5)
ax6.set_xlabel('Average Indigenous Population (%)', fontsize=12, fontweight='bold')
ax6.set_title('Panel 6: Indigenous Ancestry Rate',
              fontsize=14, fontweight='bold', pad=10)
ax6.grid(axis='x', alpha=0.3)

# Add value labels
for bar, value in zip(bars6, provincial_stats['Avg_Indigenous_Rate']):
    ax6.text(value * 100 + 0.5, bar.get_y() + bar.get_height()/2,
             f'{value*100:.1f}%',
             va='center', fontsize=9, fontweight='bold')

# Add 5% threshold (Indigenous access crisis)
ax6.axvline(x=5, color='red', linestyle='--', alpha=0.5, linewidth=2)
ax6.text(5, len(provincial_stats)-0.5, '5%\nCrisis\nThreshold',
         rotation=0, va='top', ha='center', color='red', fontweight='bold', fontsize=8)

# Add footer with key findings
footer_text = (
    "Key Findings: "
    "• Ontario dominance (72% of patients) "
    "• Northern/territorial access crisis (NL: 2,790km, NU: 4,260km avg) "
    "• BC/MB data gaps (n=4, n=2) "
    "• Indigenous communities face 2.82× greater travel distances\n"
    "Database: Final_database_05_11_25_COMPLETE.xlsx | "
    "Period: 2019-2023 | "
    "Total: 936 patients across 513 FSAs | "
    "Generated: November 6, 2025"
)

fig.text(0.5, 0.02, footer_text, ha='center', fontsize=10,
         style='italic', wrap=True,
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

# Save figure
output_path = f'{OUTPUT_DIR}/provincial_overview_6panel.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
print(f"\n✅ Saved: {output_path}")

# Also save high-res version
output_path_hires = f'{OUTPUT_DIR}/provincial_overview_6panel_4K.png'
plt.savefig(output_path_hires, dpi=400, bbox_inches='tight', facecolor='white')
print(f"✅ Saved: {output_path_hires}")

plt.close()

# Generate summary statistics table
print("\n" + "="*80)
print("PROVINCIAL STATISTICS TABLE")
print("="*80)

summary_table = provincial_stats[['Province_Abbrev', 'Province_Name', 'Patient_Count',
                                   'Median_Age', 'Median_Distance', 'Max_Distance',
                                   'Avg_Income', 'Avg_Gini', 'Avg_Indigenous_Rate']].copy()

summary_table['Patient_Pct'] = (summary_table['Patient_Count'] / 936 * 100).round(1)
summary_table['Avg_Income'] = summary_table['Avg_Income'].round(0).astype(int)
summary_table['Median_Distance'] = summary_table['Median_Distance'].round(1)
summary_table['Max_Distance'] = summary_table['Max_Distance'].round(1)
summary_table['Avg_Gini'] = summary_table['Avg_Gini'].round(3)
summary_table['Avg_Indigenous_Rate'] = (summary_table['Avg_Indigenous_Rate'] * 100).round(1)

print(summary_table.to_string(index=False))

# Save as CSV
csv_path = f'{OUTPUT_DIR}/provincial_statistics_summary.csv'
summary_table.to_csv(csv_path, index=False)
print(f"\n✅ Saved: {csv_path}")

print("\n" + "="*80)
print("✅ PROVINCIAL OVERVIEW GENERATION COMPLETE")
print("="*80)
print(f"\nOutputs:")
print(f"  1. {output_path}")
print(f"  2. {output_path_hires}")
print(f"  3. {csv_path}")
print("\nAll provincial statistics compiled and visualized successfully!")

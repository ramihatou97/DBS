# COMPREHENSIVE METHODOLOGY SUMMARY: DBS ACCESS DISPARITY PROJECT

## EXECUTIVE SUMMARY

This report documents the complete methodology for a multi-phase research project analyzing geographic and socioeconomic disparities in Deep Brain Stimulation (DBS) access across Canada. The project integrates data from 936 DBS procedures (2019-2023) with Statistics Canada Census 2021 data and Google Maps distance calculations to produce:

- A complete analytical database (20 variables, 936 patients)
- Advanced statistical regression models (R² = 0.65)
- 40+ publication-quality visualizations  
- Interactive web dashboard deployed on GitHub Pages
- **Key finding: 10.09× disparity** in access for high-Indigenous areas

---

**📊 Data Sources:**
1. **DBS Patient Data**: 936 procedures, 10 centers, 2019-2023
2. **Statistics Canada Census 2021**: 615MB, 4.3M records, 1,643 FSAs
3. **Google Maps Distance Matrix API**: ~1,000 driving distance calculations
4. **FSA Geographic Data**: Population-weighted centroids for accuracy

**🔬 Analysis Pipeline:**
1. Census data extraction (Characteristics: 1, 243, 379, 1501, 1684)
2. Google Maps API distance calculations  
3. Variable derivation (rural indicator, vulnerability scores)
4. OLS regression modeling (3 specifications tested)
5. Interaction effect testing (Indigenous×Rural, Indigenous×Income)
6. Provincial rate ratio calculations (Poisson regression with Garwood CI)
7. Stratified analysis (Indigenous ancestry quartiles)
8. Sensitivity analysis (5 model specifications)

**📈 Key Results:**
- **Indigenous disparity**: +7.9% distance per 1% Indigenous ancestry (p<0.001)
- **Clinical impact**: 537km average for highest-disparity areas
- **Provincial inequity**: BC (0.03×) and MB (0.06×) vs Ontario (1.88×)
- **Robust finding**: Stable across all model specifications (β=0.057-0.080)

**🎨 Visualizations:**
- 19 static figures (300 DPI, aquamarine/charcoal theme)
- 20+ interactive HTML maps (Google Maps integration)
- Complete statistical diagnostic suite
- Responsive web dashboard

**🌐 Public Access:**
- **Repository**: https://github.com/ramihatou97/DBS
- **Dashboard**: https://ramihatou97.github.io/DBS/
- **Maps**: https://ramihatou97.github.io/DBS/maps_nov2025/

---

For complete details, see full report in:
`/Users/ramihatoum/Desktop/DBS/COMPREHENSIVE_METHODOLOGY_SUMMARY.md`

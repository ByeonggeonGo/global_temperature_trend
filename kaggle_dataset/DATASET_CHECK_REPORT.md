# Global Temperature Dataset Check

Checked on 2026-06-21. The script `check_temperature_datasets.py` downloaded and parsed small global mean time-series products from the four suggested datasets.

## Result

All four suggested datasets are usable from this repo.

| Dataset | Status | Coverage in tested file | Saved file | Notes |
| --- | --- | --- | --- | --- |
| NASA GISTEMP v4 global LOTI | OK | 1880-2026 | `temperature_dataset_samples/nasa_gistemp_global_loti.csv` | Annual table includes a partial 2026 row, so annual `J-D` is `***` until the year is complete. |
| NOAA GlobalTemp v6.1 land-ocean | OK | 1850-01 to 2026-05 | `temperature_dataset_samples/noaa_globaltemp_v6_1_land_ocean_global.asc` | Script discovers the latest monthly global file from the NOAA directory. |
| HadCRUT5 analysis global monthly | OK | 1850-01 to 2026-03 | `temperature_dataset_samples/hadcrut5_5_1_global_monthly.csv` | Search results may show older `5.0.2.0`, but current tested file is `HadCRUT.5.1.0.0`. Includes 95% confidence limits. |
| Berkeley Earth high-resolution global monthly | OK | 1850-01 to 2026-05 | `temperature_dataset_samples/berkeley_earth_hr_global_monthly.txt` | The current high-resolution product is marked preliminary by Berkeley Earth. The older 1 degree product is no longer updated after Q2 2025. |

Machine-readable results are in `temperature_dataset_check_results.json`.

## Recommended Use

For a first global warming trend analysis, start with NASA GISTEMP or HadCRUT5.

NASA GISTEMP is the easiest for a clean global annual/monthly trend chart. HadCRUT5 is best if you want uncertainty intervals in the same file. NOAA GlobalTemp is a strong independent comparison and has land, ocean, and zonal breakdowns. Berkeley Earth is useful as an independent reconstruction, but for the current high-resolution global product, note the preliminary status.

## Good Additional Datasets

ERA5 is worth adding if you want a physically consistent reanalysis product rather than only instrument-based global indices. It starts in 1940 and is available through the Copernicus Climate Data Store, but bulk download usually needs CDS API setup and is heavier than these CSV/TXT files.

JRA-3Q is another strong reanalysis comparison, produced by JMA. It covers September 1947 onward. Access can be less convenient than ERA5 and may have usage restrictions depending on the archive, so I would treat it as a secondary validation source rather than the first dataset to wire into this repo.

NOAA Climate at a Glance is also useful when you want quick global, hemispheric, land, and ocean chart-ready products from NOAA without handling the full directory structure.

## Source Pages

- NASA GISTEMP data downloads: https://data.giss.nasa.gov/gistemp/data_v4.html
- NOAA GlobalTemp: https://www.ncei.noaa.gov/products/land-based-station/noaa-global-temp
- HadCRUT5: https://www.metoffice.gov.uk/hadobs/hadcrut5/
- Berkeley Earth data: https://berkeleyearth.org/data/
- ERA5: https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels
- JRA-3Q: https://www.data.jma.go.jp/jra/html/JRA-3Q/index_en.html

# Renewable Energy Mapping of Romania (Wind and Solar, by County)

A small spatial analysis project that maps wind and solar generation sites across Romania's counties using OpenStreetMap data. Built as a first hands-on exploration of geospatial analysis in Python, alongside my energy consumption forecasting work.

**Interactive maps:**
- Wind: [harta_eolian_ro.html](https://olteanualexandra.github.io/romania-renewables-map/harta_eolian_ro.html)
- Solar: [harta_solar_ro.html](https://olteanualexandra.github.io/romania-renewables-map/harta_solar_ro.html)

[Wind map](images/eolian.png) 
[Solar map](images/solar.png) 

## What it does

1. Reads a local OpenStreetMap extract of Romania (Geofabrik) and keeps elements tagged as `power=generator` or `power=plant` with wind or solar as the source.
2. Reduces each element to a point (polygons such as solar parks are collapsed to their centroid).
3. Assigns each point to a county with a spatial join against GADM 4.1 county boundaries.
4. Computes counts and density per 1000 km² (areas calculated in the Romanian projected CRS, EPSG:3844).
5. Exports two interactive choropleth maps (Folium) and a CSV with per-county results.

## Tech stack

Python, GeoPandas, Shapely, PyOsmium, Folium, Pandas

## Run it yourself

```bash
pip install osmium geopandas folium mapclassify pandas
# Download https://download.geofabrik.de/europe/romania-latest.osm.pbf into this folder
python harta_regenerabile_local.py
```

Outputs: `harta_eolian_ro.html`, `harta_solar_ro.html`, `centrale_pe_judet.csv`.

## Findings

- **Wind** generation is strongly concentrated in Dobrogea (Constanța and Tulcea), with a secondary cluster around Galați.
- **Solar** is far more dispersed across the country, with the highest densities in Satu Mare, Olt, Prahova and the Timiș–Arad area.

## Limitations

- **Counts are not capacity.** The maps count OSM elements, not installed MW. One wind turbine is one point, but a solar park can be mapped as one polygon or as many separate elements.
- **OSM coverage is uneven.** Some counties are mapped far more thoroughly than others, so density partly reflects mapping effort (for example, Satu Mare's solar points are spread across the county, which suggests many small installations mapped individually rather than large parks).
- Wind and solar are therefore shown on separate maps and should not be compared directly.

## Possible next steps

- Use the `generator:output:electricity` tag, where available, to estimate capacity instead of counts.
- Cross-check against official sources (e.g. Transelectrica / ANRE) for validation.
- Publish the results as a web map in ArcGIS Online.

## Data sources

- © OpenStreetMap contributors (via Geofabrik extract, November 2026), ODbL license
- GADM 4.1 administrative boundaries (Romania, level 1)

"""
Harta centralelor eoliene si solare din Romania, pe judete
Date: extras OSM local (romania-261105.osm.pbf, de la Geofabrik) + limite judete GADM 4.1.
"""
import geopandas as gpd
import pandas as pd
import folium
import osmium
from shapely.geometry import Point

PBF = "romania-261105.osm.pbf"
GADM_URL = "https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_ROU_1.json.zip"

# 1. Limitele judetelor (GADM nivel 1 = judete + Bucuresti)
judete = gpd.read_file(GADM_URL)[["NAME_1", "geometry"]].rename(columns={"NAME_1": "judet"})

# 2. Citim centralele din fisierul local 
randuri = []
print("Citesc fisierul OSM... (3-10 minute)")
for obj in osmium.FileProcessor(PBF).with_locations():
    if not (obj.is_node() or obj.is_way()):
        continue
    tags = obj.tags
    if tags.get("power") not in ("generator", "plant"):
        continue
    sursa = tags.get("generator:source") or tags.get("plant:source")
    if sursa not in ("wind", "solar"):
        continue
    try:
        if obj.is_node():
            lon, lat = obj.location.lon, obj.location.lat
        else:  # drum inchis (parc solar): luam media colturilor
            pcte = [(n.location.lon, n.location.lat) for n in obj.nodes]
            lon = sum(p[0] for p in pcte) / len(pcte)
            lat = sum(p[1] for p in pcte) / len(pcte)
    except Exception:
        continue  # locatie lipsa, sarim peste
    randuri.append({"sursa": sursa, "geometry": Point(lon, lat)})

gdf = gpd.GeoDataFrame(randuri, crs=4326)
print(gdf["sursa"].value_counts())

# 3. Spatial join: in ce judet se afla fiecare centrala
joined = gpd.sjoin(gdf, judete, how="inner", predicate="within")
numar = (
    joined.groupby(["judet", "sursa"]).size().unstack(fill_value=0)
    .reindex(columns=["wind", "solar"], fill_value=0)
    .rename(columns={"wind": "nr_eolian", "solar": "nr_solar"})
)

# 4. Densitate pe km2, separat pe tip de sursa
judete_m = judete.to_crs(3844)  # Stereo 70, proiectie metrica pentru Romania
judete["km2"] = judete_m.area / 1e6
judete = judete.merge(numar, on="judet", how="left").fillna({"nr_eolian": 0, "nr_solar": 0})
judete["nr_centrale"] = judete["nr_eolian"] + judete["nr_solar"]
for tip in ("eolian", "solar"):
    judete[f"densitate_{tip}"] = judete[f"nr_{tip}"] / judete["km2"] * 1000  # per 1000 km2

# 5. Doua harti interactive, cate una pentru fiecare tip de sursa
def harta(tip, cod_osm, paleta, nume, culoare_punct):
    m = folium.Map(location=[45.9, 24.9], zoom_start=7, tiles="OpenStreetMap")
    folium.Choropleth(
        geo_data=judete,
        data=judete,
        columns=["judet", f"densitate_{tip}"],
        key_on="feature.properties.judet",
        fill_color=paleta,
        fill_opacity=0.6,
        line_opacity=0.4,
        legend_name=f"{nume}: elemente OSM per 1000 km2",
        name=f"{nume} - densitate pe judet",
    ).add_to(m)

    # Tooltip cu numele judetului si numarul de elemente
    folium.GeoJson(
        judete,
        name=f"{nume} - info judet",
        style_function=lambda f: {"fillOpacity": 0, "weight": 0},
        tooltip=folium.GeoJsonTooltip(
            fields=["judet", f"nr_{tip}"], aliases=["Judet:", f"Nr. {nume.lower()}:"]
        ),
    ).add_to(m)

    # Punctele individuale, ascunse implicit (se bifeaza din meniu)
    grup = folium.FeatureGroup(name=f"{nume} - puncte", show=False)
    for _, r in gdf[gdf["sursa"] == cod_osm].iterrows():
        folium.CircleMarker(
            [r.geometry.y, r.geometry.x], radius=2, color=culoare_punct, fill=True,
        ).add_to(grup)
    grup.add_to(m)
    folium.LayerControl(collapsed=False).add_to(m)
    m.save(f"harta_{tip}_ro.html")


harta("eolian", "wind", "Blues", "Eolian", "navy")
harta("solar", "solar", "YlOrRd", "Solar", "darkred")
judete.drop(columns="geometry").sort_values("nr_centrale", ascending=False).to_csv(
    "centrale_pe_judet.csv", index=False
)
print("Gata: harta_eolian_ro.html, harta_solar_ro.html, centrale_pe_judet.csv")
import os
from typing import Dict, List, Tuple, Any
import numpy as np
import polars as pl
import geopandas as gpd


def load_wiki_dataset(file_path: str) -> pl.DataFrame:
    """Load the Wikipedia dataset with proper null value handling."""
    return pl.read_csv(
        file_path,
        separator="\t",
        null_values=["Null", "Wikidata|getValue|P1082|FETCH_WIKIDATA"],
        infer_schema_length=10000,
    )


def load_name_mapping(file_path: str) -> Dict[str, str]:
    """Load the name mapping between Wikipedia and SAL place names."""
    matchdf = pl.read_csv(
        file_path,
        separator=";",
        has_header=False,
        new_columns=["wiki_name", "sal_name"],
    )
    return dict(zip(matchdf["wiki_name"], matchdf["sal_name"]))


def extract_sal_coordinates(shapefile_path: str) -> Dict[str, Dict[str, float]]:
    """Extract coordinates for all SAL places from the shapefile."""
    gdf = gpd.read_file(shapefile_path)
    gdf_projected = gdf.to_crs(epsg=7845)
    gdf_projected["centroid"] = gdf_projected["geometry"].centroid
    gdf["centroid"] = gdf_projected["centroid"].to_crs(gdf.crs)
    gdf["longitude"] = gdf["centroid"].x
    gdf["latitude"] = gdf["centroid"].y
    return gdf.set_index("SAL_NAME21")[["latitude", "longitude"]].to_dict("index")


def create_valid_name_mapping(
    wiki_names: List[str],
    match_dict: Dict[str, str],
    sal_coord: Dict[str, Dict[str, float]],
) -> Dict[str, str]:
    """Create a mapping of valid Wikipedia to SAL place names."""
    sal_names = [match_dict.get(w, None) for w in wiki_names]
    return {w: s for w, s in zip(wiki_names, sal_names) if s in sal_coord}


def calculate_direction(lat1: float, lon1: float, lat2: float, lon2: float) -> str:
    """Calculate the directional relationship between two coordinate points."""
    dy = lat2 - lat1
    dx = lon2 - lon1
    angle = (np.degrees(np.arctan2(dy, dx)) + 360) % 360

    if 337.5 <= angle or angle < 22.5:
        return "E"
    elif 22.5 <= angle < 67.5:
        return "NE"
    elif 67.5 <= angle < 112.5:
        return "N"
    elif 112.5 <= angle < 157.5:
        return "NW"
    elif 157.5 <= angle < 202.5:
        return "W"
    elif 202.5 <= angle < 247.5:
        return "SW"
    elif 247.5 <= angle < 292.5:
        return "S"
    else:
        return "SE"


def extract_direction_relations(
    wikidf: pl.DataFrame,
    name_map: Dict[str, str],
    sal_coord: Dict[str, Dict[str, float]],
) -> List[Dict[str, Any]]:
    """Extract all directional relations from the Wikipedia dataset."""
    directions = [
        "relation_nearE",
        "relation_nearN",
        "relation_nearNe",
        "relation_nearNw",
        "relation_nearS",
        "relation_nearSe",
        "relation_nearSw",
        "relation_nearW",
    ]
    direction_map = {
        "relation_nearE": "E",
        "relation_nearN": "N",
        "relation_nearNe": "NE",
        "relation_nearNw": "NW",
        "relation_nearS": "S",
        "relation_nearSe": "SE",
        "relation_nearSw": "SW",
        "relation_nearW": "W",
    }

    rows = []
    for row in wikidf.iter_rows(named=True):
        src_wiki = row["nameID"]
        src_sal = name_map.get(src_wiki)
        if not src_sal:
            continue
        src_coord = sal_coord[src_sal]

        for d in directions:
            tgt_wiki = row[d]
            if tgt_wiki is None or tgt_wiki == "Null":
                continue
            tgt_sal = name_map.get(tgt_wiki)
            if not tgt_sal:
                continue
            tgt_coord = sal_coord[tgt_sal]
            wiki_dir = direction_map[d]

            rows.append(
                {
                    "place1": src_sal,
                    "place1_latitude": src_coord["latitude"],
                    "place1_longitude": src_coord["longitude"],
                    "place2": tgt_sal,
                    "place2_latitude": tgt_coord["latitude"],
                    "place2_longitude": tgt_coord["longitude"],
                    "wiki_direction": wiki_dir,
                }
            )
    return rows


def combine_direction_datasets() -> None:
    """Main function to combine Wikipedia and algorithmic directional datasets."""
    # Load Wikipedia dataset
    wikidf = load_wiki_dataset("data/df_wiki_extend.csv")

    # Load name mapping
    match_dict = load_name_mapping("data/match_extend.csv")

    # Extract SAL coordinates
    shp_path = os.path.join("SAL_2021_AUST_GDA2020_SHP", "SAL_2021_AUST_GDA2020.shp")
    sal_coord = extract_sal_coordinates(shp_path)

    # Create valid name mapping
    wiki_names = wikidf["nameID"].to_list()
    name_map = create_valid_name_mapping(wiki_names, match_dict, sal_coord)

    # Extract all directional relations
    rows = extract_direction_relations(wikidf, name_map, sal_coord)

    # Create DataFrame and calculate algorithmic directions
    result_df = pl.DataFrame(rows)
    if len(result_df) == 0:
        raise ValueError("No valid direction pairs found.")

    result_df = result_df.with_columns(
        [
            pl.struct(
                [
                    "place1_latitude",
                    "place1_longitude",
                    "place2_latitude",
                    "place2_longitude",
                ]
            )
            .map_elements(
                lambda s: calculate_direction(
                    s["place1_latitude"],
                    s["place1_longitude"],
                    s["place2_latitude"],
                    s["place2_longitude"],
                ),
                return_dtype=pl.String,
            )
            .alias("algo_direction")
        ]
    )

    # Select final columns and save
    result_df = result_df.select(
        [
            "place1",
            "place1_latitude",
            "place1_longitude",
            "place2",
            "place2_latitude",
            "place2_longitude",
            "algo_direction",
            "wiki_direction",
        ]
    )

    # Generate output with more descriptive filename
    output_file = "data/australia_suburb_directional_relations_wiki_vs_calculated.csv"
    result_df.write_csv(output_file)
    print(f"Successfully generated {output_file}")
    print(
        f"Dataset contains {len(result_df)} directional relationships between Australian suburbs."
    )


if __name__ == "__main__":
    combine_direction_datasets()

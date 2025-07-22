# Australian Locality Coordinate Extraction and Directional Relationship Analysis

This project extracts suburb and locality (SAL) data from Australian government shapefiles, calculates the centroid coordinates for each locality, and determines directional relationships between localities. It provides two main functionalities:

1. **Calculate all city-pair directional relations** from the SAL shapefile data
2. **Combine Wikipedia directional relations with calculated relations** to create a comparative dataset for validation and analysis

## Environment Setup and Usage

This project uses [Pixi](https://pixi.sh/) to manage dependencies and tasks.

### 1. Install Pixi

If you don't have Pixi installed, follow the instructions on the [official Pixi website](https://pixi.sh/latest/#installation).

### 2. Install Project Dependencies

Once Pixi is installed, navigate to the project root directory and run the following command to install all required libraries as defined in the `pixi.toml` file:

```bash
pixi install
```

### 3. Available Tasks

#### Calculate All City-Pair Relations

To generate directional relationships for all possible city pairs from the shapefile:

```bash
pixi run calculate-relations
```

This task will:

- Read the source shapefile from the `SAL_2021_AUST_GDA2020_SHP/` directory.
- Calculate the centroid for each locality.
- Perform a highly optimized, vectorized calculation for over 235 million city pairs.
- Save the results into 20 separate CSV files in the `data/` directory.

#### Combine Wikipedia and Calculated Relations

To create a comparative dataset combining Wikipedia directional information with calculated relations:

```bash
pixi run combine-datasets
```

This task will:

- Read Wikipedia directional relations from `data/df_wiki_extend.csv`
- Load place name mappings from `data/match_extend.csv`
- Extract coordinates from the SAL shapefile
- Generate a unified dataset comparing Wikipedia vs. calculated directions
- Save the result as `data/australia_suburb_directional_relations_wiki_vs_calculated.csv`

### **Important: Data Setup**
The source shapefile data is not included in this Git repository due to its large size. Before running the task, you must download it manually.

1. **Download** the "ESRI Shapefile" format via the [Direct Download Link](https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs-edition-3/jul2021-jun2026/access-and-downloads/digital-boundary-files/SAL_2021_AUST_GDA2020_SHP.zip).
2. **Unzip** the downloaded file.
3. **Place** the resulting `SAL_2021_AUST_GDA2020_SHP` directory into the root of this project.

## Datasets

### Australian Suburbs and Localities (SAL) 2021 Dataset

| Dataset Name | Download Link | Original Literature | Original Link | Sample Count | Feature Count | Class Count | Dataset Introduction |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Suburbs and Localities (SAL) 2021 GDA2020 | [Direct Download Link](https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs-edition-3/jul2021-jun2026/access-and-downloads/digital-boundary-files/SAL_2021_AUST_GDA2020_SHP.zip) | Long Z, Li Q, Meng H, et al. A machine learning based approach for generating point sketch maps from qualitative directional information[J]. International Journal of Geographical Information Science, 2024, 38(9): 1881-1911. | [ABS Official Website](https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs-edition-3/jul2021-jun2026) | 15,353 | 11 | — | This dataset contains Australian Suburbs and Localities (SAL) geographic boundary data, based on the Australian Statistical Geography Standard (ASGS) Edition 3. Features include SAL_CODE21, SAL_NAME21, STE_CODE21, STE_NAME21, coordinates, and geometric information. |

### Australian City-Pair Directional Relations Dataset

| Dataset Name | Download Link | Original Literature | Original Link | Sample Count | Feature Count | Class Count | Dataset Introduction |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Australian City-Pair Directional Relations | Generated locally in the `data/` directory | Long Z, Li Q, Meng H, et al. A machine learning based approach for generating point sketch maps from qualitative directional information[J]. International Journal of Geographical Information Science, 2024, 38(9): 1881-1911. | [GitHub Repository](https://github.com/renyumeng1/extract-coordinates-aus-direction) | ~235,116,222 | 7 | 8 | Contains directional relationships for every city pair calculated from SAL coordinates. Features: city1_name, city1_latitude, city1_longitude, city2_name, city2_latitude, city2_longitude, direction. Classes: N, NE, E, SE, S, SW, W, NW. |

### Australia Suburb Directional Relations (Wiki vs Calculated)

| Dataset Name | Download Link | Original Literature | Original Link | Sample Count | Feature Count | Class Count | Dataset Introduction |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Australia Suburb Directional Relations (Wiki vs Calculated) | Generated locally as `australia_suburb_directional_relations_wiki_vs_calculated.csv` | Long Z, Li Q, Meng H, et al. A machine learning based approach for generating point sketch maps from qualitative directional information[J]. International Journal of Geographical Information Science, 2024, 38(9): 1881-1911. | [GitHub Repository](https://github.com/renyumeng1/extract-coordinates-aus-direction) | 11,138 | 8 | 8 | Comparative dataset combining Wikipedia directional relations with algorithm-calculated directions for Australian suburbs. Features: place1, place1_latitude, place1_longitude, place2, place2_latitude, place2_longitude, algo_direction, wiki_direction. Useful for validation and spatial relationship analysis. |

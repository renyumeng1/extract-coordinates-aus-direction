# Australian Locality Coordinate Extraction and Directional Relationship Analysis

This project extracts suburb and locality (SAL) data from Australian government shapefiles, calculates the centroid coordinates for each locality, and then determines the directional relationship (e.g., North, South-West) for every pair of localities. The final output is a series of CSV files detailing these relationships.

## Environment Setup and Usage

This project uses [Pixi](https://pixi.sh/) to manage dependencies and tasks.

### 1. Install Pixi

If you don't have Pixi installed, follow the instructions on the [official Pixi website](https://pixi.sh/latest/#installation).

### 2. Install Project Dependencies

Once Pixi is installed, navigate to the project root directory and run the following command to install all required libraries as defined in the `pixi.toml` file:

```bash
pixi install
```

### 3. Run the Calculation Task

To perform the entire data processing pipeline—from reading the shapefile to generating the final partitioned CSV files—run the pre-configured task:

```bash
pixi run calculate-relations
```

This task will:
- Read the source shapefile from the `SAL_2021_AUST_GDA2020_SHP/` directory.
- Calculate the centroid for each locality.
- Perform a highly optimized, vectorized calculation for over 235 million city pairs.
- Save the results into 20 separate CSV files in the `data/` directory.

### **Important: Data Setup**
The source shapefile data is not included in this Git repository due to its large size. Before running the task, you must download it manually.

1.  **Download** the "ESRI Shapefile" format from the [Australian Bureau of Statistics website](https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs-edition-3/jul2021-jun2026/access-and-downloads/digital-boundary-files/SAL_2021_AUST_GDA2020_SHP.zip).
2.  **Unzip** the downloaded file.
3.  **Place** the resulting `SAL_2021_AUST_GDA2020_SHP` directory into the root of this project.

## Datasets

### **Australian Suburbs and Localities (SAL) 2021 Dataset**

| Dataset Name | Download Link | Original Literature | Original Link | Sample Count | Feature Count | Class Count | Dataset Introduction |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Suburbs and Localities (SAL) 2021 GDA2020 | [ABS Website](https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs-edition-3/jul2021-jun2026/access-and-downloads/digital-boundary-files/SAL_2021_AUST_GDA2020_SHP.zip | | [ABS Website](https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs-edition-3/jul2021-jun2026) | 15,334 | ~11 | N/A | Suburbs and Localities (SALs) are an ABS approximation of gazetted localities, created for statistical purposes. They cover most of Australia and are based on the Australian Statistical Geography Standard (ASGS). |

### **Australian City-Pair Directional Relations Dataset**

| Dataset Name | Download Link | Original Literature | Original Link | Sample Count | Feature Count | Class Count | Dataset Introduction |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Australian City-Pair Directional Relations | Generated locally in the `data/` directory. | | N/A | ~235,116,222 | 7 | 8 | Contains the directional relationship for every city pair. The 7 features are: `city1_name`, `city1_latitude`, `city1_longitude`, `city2_name`, `city2_latitude`, `city2_longitude`, and `direction`. The 8 classes for the 'direction' feature are N, NE, E, SE, S, SW, W, and NW. |
# Augmentus Assignment

## Core Idea

This project explores two complementary strategies for 3D point cloud segmentation and clustering:

1. **Density-based approach**  
   - Perform *density-preserving sampling* so that dense regions remain dense and sparse regions remain sparse.  
   - Then apply a *density-based clustering* algorithm such as DBSCAN.

2. **Distance-based approach**  
   - Perform *density-equalizing sampling* (e.g., voxel downsampling) so that all regions have roughly uniform point density.  
   - Then apply a *distance-based clustering* algorithm such as Euclidean clustering.

Through experimentation, I found that using approximately **one-third of the original points** achieves the best balance between performance and visual quality.

The primary algorithm used for segmentation is **DBSCAN**, applied on a feature vector that combines:
- 3D position (`x, y, z`)
- Color (`l, a, b`)
- Surface normal (`nx, ny, nz`)

K-Means was tested but proved unsuitable due to its sensitivity to non-spherical clusters.

### Tunable Parameters
- **Epsilon:**  
  Defines the maximum distance between two points for them to be considered neighbors. Smaller values yield finer segmentation; larger values merge nearby clusters.

- **Minimum number of points:**  
  Sets the minimum cluster size. Clusters smaller than this threshold are labeled as noise (`-1`).

- **Feature weights:**  
  Controls the contribution of position, color, and normal vectors in the combined feature space.  
  For example, `(0.6, 0.3, 0.1)` means position contributes 60%, color 30%, and normal 10% to the clustering distance metric.

## Experiment Results



## Architecture

This project uses a **src-layout** structure and defines a namespace package `augmentus`.  
The main package `pointcloudprocessor` contains the following modules:

| Module | Purpose |
|---------|----------|
| **cluster** | Implements DBSCAN for point cloud segmentation. |
| **resample** | Provides sampling algorithms. |
| **estimate_normal** | Estimates and orients point cloud normals using local neighborhoods. |
| **render** | Handles offscreen rendering and visualization of point clouds as static images. |
| **process_eagle** | The main entry point that loads the Eagle dataset, runs the full pipeline, and generates results. |


## How to Run

### 1. Install the package
```bash
python3.10 -m venv venv_augmentus
source venv_augmentus/bin/activate
python3 -m pip install .
```
This command install a Python package **pointcloud_processor**.

### 2. Run the main command
```bash
process-eagle -o output
```
This command generates an `output/` folder containing the rendered point cloud segmentation results.

## Development Setup

To install development and testing dependencies:
```bash
python3 -m pip install -e .[dev,test,interactive]
```

Run the provided unit tests with:
```bash
pytest
```

Three unit tests are included to verify core functionality:
1. Point cloud downsampling reduces point count.
2. DBSCAN segmentation detects multiple clusters.

"""
This script does the following:
1. Loads the eagle point cloud
2. Downsamples the point cloud
3. Estimates the normals
4. Builds the feature vector
5. Segments the point cloud
6. Colors the clusters
7. Renders the point cloud as an image
"""

import argparse
import itertools
from pathlib import Path

import numpy as np
import open3d as o3d
from skimage.color import rgb2lab
from sklearn.preprocessing import MinMaxScaler, StandardScaler

from augmentus.pointcloudprocessor.cluster import dbscan_segment_point_cloud
from augmentus.pointcloudprocessor.estimate_normal import NormalEstimator
from augmentus.pointcloudprocessor.render import colorize_clusters, render_point_cloud_as_image
from augmentus.pointcloudprocessor.resample import PointCloudDownsampler


def build_feature_vector(pcd, weight):
    w_xyz, w_lab, w_norm = weight

    # xyz: standardize to unit variance
    xyz = np.asarray(pcd.points)
    xyz_scaled = StandardScaler().fit_transform(xyz) * np.sqrt(w_xyz)

    # Color: convert to Lab, then normalize to [0,1]
    # Do I need to normalize the LAB space to calculate the euclidean distance?
    rgb = np.asarray(pcd.colors)
    lab = rgb2lab(rgb)  # (L: 0–100, a/b: –128–127)
    lab_norm = MinMaxScaler(feature_range=(0, 1)).fit_transform(lab) * np.sqrt(w_lab)

    # Normal: already unit-length, keep as-is
    nrm = np.asarray(pcd.normals) * np.sqrt(w_norm)

    return np.hstack([xyz_scaled, lab_norm, nrm])


def run(output_dir: Path):
    # load eagle point cloud
    epc = o3d.data.EaglePointCloud()  # open3d.cuda.pybind.data.EaglePointCloud
    pcd = o3d.io.read_point_cloud(epc.path)  # open3d.cuda.pybind.geometry.PointCloud
    print(f"Number of pcd points: {len(pcd.points)}")  # 796825
    min_x, min_y, min_z = pcd.get_min_bound().tolist()
    max_x, max_y, max_z = pcd.get_max_bound().tolist()
    print(f"Point cloud extents: {min_x, min_y, min_z} to {max_x, max_y, max_z}")
    render_point_cloud_as_image(pcd, output_path=output_dir / "original_eagle.png")

    # uniform_down_sample. keeps the original density of the point cloud
    # voxel_down_sample. keeps the geometric structure of the point cloud
    # Do not use less than 1/3 of the original number of points
    algorithms = [
        ("uniform_down_sample", 3),  # 265609 points
        ("voxel_down_sample", 0.023),  # 266159 points
    ]
    epsilons = [0.07, 0.1, 0.13]  # Do not use "<0.07" and ">0.13"
    min_points = [10, 30, 50]  # Do not use "<10" and ">50"
    weights = [
        (1, 0, 0),
        (0.5, 0.5, 0),
        (0.5, 0, 0.5),
        (0.333, 0.333, 0.333),
    ]  # (xyz, LAB, normal)

    for algo in algorithms:
        print(f"Algorithm: {algo[0]}, {algo[1]}")

        d = PointCloudDownsampler(pcd)
        pcd_down = d.downsample(method=algo[0], value=algo[1])
        render_point_cloud_as_image(pcd_down, output_path=output_dir / f"{algo[0]}_{algo[1]}.png")

        print(f"Number of pcd_down points: {len(pcd_down.points)}")

        # Estimate unit normals
        diagonal = ((max_x - min_x) ** 2 + (max_y - min_y) ** 2 + (max_z - min_z) ** 2) ** 0.5
        voxel_size = max(diagonal / 200.0, 1e-3)  # ~0.5% diag, 0.058
        radius = 2.5 * voxel_size  # 0.145
        max_nn = k = 30
        ne = NormalEstimator(pcd_down)
        ne.estimate(radius=radius, max_nn=max_nn, k=k)
        render_point_cloud_as_image(
            pcd_down, output_path=output_dir / f"{algo[0]}_{algo[1]}_normals.png", show_normals=True
        )

        for eps, min_point, weight in itertools.product(epsilons, min_points, weights):
            print(f"Epsilon: {eps}, Min points: {min_point}, Weight: {weight}")

            feature_vector = build_feature_vector(pcd_down, weight)
            assert feature_vector.shape[0] == len(pcd_down.points)
            assert feature_vector.shape[1] == 9

            labels = dbscan_segment_point_cloud(feature_vector, eps, min_point)  # (N,)
            n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
            print(f"Clusters found: {n_clusters}, noise: {(labels == -1).sum()}")

            pcd_colored = colorize_clusters(pcd_down, labels)
            out_filename = (
                f"{algo[0]}_{algo[1]}_"
                + f"eps{eps}_"
                + f"min{min_point}_"
                + f"Wxyz{weight[0]}lab{weight[1]}norm{weight[2]}_"
                + f"clusters{n_clusters}.png"
            )
            render_point_cloud_as_image(pcd_colored, output_dir / out_filename)

            print("--------------------------------")


def main() -> int:
    parser = argparse.ArgumentParser(description="Process the Eagle point cloud and export images.")
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=Path("output"),
        help="Directory to write output images (default: ./output)",
    )

    args = parser.parse_args()
    output_dir: Path = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    run(output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

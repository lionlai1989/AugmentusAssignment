import numpy as np
import open3d as o3d
import pytest


@pytest.fixture
def colored_point_cloud(num_points: int = 200):
    rng = np.random.default_rng(0)
    pts = rng.random((num_points, 3))
    cols = rng.random((num_points, 3))
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(pts)
    pcd.colors = o3d.utility.Vector3dVector(cols)
    return pcd

@pytest.fixture
def two_gaussian_blobs_point_cloud(n_per: int = 50):
    rng = np.random.default_rng(0)
    blob_a = rng.normal(loc=[-2.0, 0.0, 0.0], scale=0.2, size=(n_per, 3))
    blob_b = rng.normal(loc=[+2.0, 0.0, 0.0], scale=0.2, size=(n_per, 3))

    return np.vstack([blob_a, blob_b])  # shape (100, 3)

"""
NormalEstimator estimates normals for a point cloud.
"""

import open3d as o3d


class NormalEstimator:
    def __init__(self, pcd):
        self.pcd = pcd

    def estimate(self, radius, max_nn, k, skip_normals_orientation=False):
        self.pcd.estimate_normals(
            search_param=o3d.geometry.KDTreeSearchParamHybrid(
                radius=radius,  # search radius, tune based on point density
                max_nn=max_nn,  # number of neighbors to use
            )
        )
        # Orient the normals with respect to consistent tangent planes
        if not skip_normals_orientation:
           self.pcd.orient_normals_consistent_tangent_plane(k=k)  # Number of k nearest neighbors used

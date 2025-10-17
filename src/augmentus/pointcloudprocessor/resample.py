"""
PointCloudDownsampler downsamples a point cloud.
"""


class PointCloudDownsampler:
    def __init__(self, pcd):
        self.pcd = pcd

    def downsample(self, method, value):
        if method == "voxel_down_sample":
            return self.pcd.voxel_down_sample(voxel_size=value)
        elif method == "uniform_down_sample":
            return self.pcd.uniform_down_sample(every_k_points=value)
        else:
            raise ValueError(f"Unsupported downsampling method: {method}")

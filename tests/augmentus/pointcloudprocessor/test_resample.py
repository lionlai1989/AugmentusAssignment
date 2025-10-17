from augmentus.pointcloudprocessor.resample import PointCloudDownsampler

def test_PointCloudDownsampler(colored_point_cloud):
    ds = PointCloudDownsampler(colored_point_cloud)

    down = ds.downsample(method="voxel_down_sample", value=0.1)
    assert len(down.points) < len(colored_point_cloud.points)

    down = ds.downsample(method="uniform_down_sample", value=10)
    assert len(down.points) < len(colored_point_cloud.points)

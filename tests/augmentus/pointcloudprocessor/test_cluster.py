import numpy as np

from augmentus.pointcloudprocessor.cluster import dbscan_segment_point_cloud

def test_dbscan_segment_point_cloud(two_gaussian_blobs_point_cloud):
    labels = dbscan_segment_point_cloud(two_gaussian_blobs_point_cloud, eps=0.5, min_points=3)

    assert len(set(labels)) == 2
    assert np.sum(labels == -1) == 0

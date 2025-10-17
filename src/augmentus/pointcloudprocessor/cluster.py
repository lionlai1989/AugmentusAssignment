"""
Cluster features using DBSCAN and return labels.
"""

from sklearn.cluster import DBSCAN


def dbscan_segment_point_cloud(feature_vector, eps, min_points):
    """Cluster features using DBSCAN and return labels."""
    assert feature_vector.shape[1] == 9

    # Do I need to adjust eps based on the weight?
    db = DBSCAN(eps=eps, min_samples=min_points, metric="euclidean")

    # Noisy samples are given the label -1
    labels = db.fit_predict(feature_vector)
    return labels

"""
Render a point cloud as an image.
"""

import numpy as np
import open3d as o3d


def colorize_clusters(pcd, labels):
    """Assign random colors to clusters."""
    unique_labels = np.unique(labels)
    colors = np.zeros((len(labels), 3))
    rng = np.random.default_rng(0)
    palette = rng.random((len(unique_labels), 3))
    for i, lbl in enumerate(unique_labels):
        if lbl == -1:  # noise
            colors[labels == lbl] = [0.1, 0.1, 0.1]
        else:
            colors[labels == lbl] = palette[i]
    pcd.colors = o3d.utility.Vector3dVector(colors)
    return pcd


def render_point_cloud_as_image(
    pcd,
    output_path,
    width=960,
    height=960,
    point_size=2.0,
    rotate_camera_180_z=True,
    show_normals=False,
):
    """Render the point cloud offscreen using the default Open3D view and save to an image."""

    vis = o3d.visualization.Visualizer()
    vis.create_window(visible=False, width=width, height=height)
    vis.add_geometry(pcd)
    ro = vis.get_render_option()
    ro.point_size = float(point_size)
    ro.point_show_normal = show_normals

    vis.poll_events()
    vis.update_renderer()

    # Optionally rotate the camera 180 degrees about Z-axis of the current view
    if rotate_camera_180_z:
        ctr = vis.get_view_control()
        params = ctr.convert_to_pinhole_camera_parameters()
        E = params.extrinsic.copy()
        # Roll camera by 180 deg about its optical axis: Rc = diag(-1,-1,1)
        Rc = np.array([[-1.0, 0.0, 0.0], [0.0, -1.0, 0.0], [0.0, 0.0, 1.0]])
        R = E[:3, :3]
        t = E[:3, 3]
        E[:3, :3] = Rc @ R
        E[:3, 3] = Rc @ t
        params.extrinsic = E
        ctr.convert_from_pinhole_camera_parameters(params)
        vis.poll_events()
        vis.update_renderer()

    vis.capture_screen_image(str(output_path), do_render=True)
    vis.destroy_window()

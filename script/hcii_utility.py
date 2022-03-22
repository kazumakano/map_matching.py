import os.path as path
from typing import Optional
import cv2
import numpy as np
import particle_filter.script.parameter as pf_param
from matplotlib import collections
from matplotlib import pyplot as plt
from .map import Map


def create_network_figure(result_file_name: Optional[str] = None) -> None:
    map = Map(np.empty(0, dtype=str))
    map.set_all_beacons()
    link_segs = np.empty((0, 2, 2), dtype=np.int16)
    for i, js in enumerate(map.link_nodes):
        for j in js:
            link_segs = np.vstack((link_segs, np.vstack(((map.node_poses[i, 0], map.node_poses[i, 1]), (map.node_poses[j, 0], map.node_poses[j, 1])))[np.newaxis, :]))

    plt.rcParams["axes.edgecolor"] = "gray"
    plt.rcParams["axes.linewidth"] = 0.8

    ax = plt.subplots(figsize=(6, 4), dpi=1200)[1]
    ax.set_xlim(left=1425, right=300)
    ax.set_ylim(bottom=800, top=1550)
    ax.imshow(cv2.cvtColor(map.img, cv2.COLOR_BGR2RGB))
    ax.scatter(map.node_poses[:, 0], map.node_poses[:, 1], s=8, c="tab:green", label="Node")
    ax.add_collection(collections.LineCollection(link_segs, colors="tab:green", label="Link", linewidth=0.8))
    ax.legend(fontsize=8, frameon=False, loc="upper left")
    ax.tick_params(color="gray", length=2, width=0.8)
    ax.set_xlabel("Location [m]")
    ax.set_xticks(ticks=range(0, 1126, 125), labels=range(0, 91, 10), fontsize=8)
    ax.set_xticks(ticks=np.arange(0, 1126, 62.5))
    ax.set_ylabel("Location [m]")
    ax.set_yticks(ticks=range(0, 751, 125), labels=range(0, 61, 10), fontsize=8)
    ax.set_yticks(ticks=np.arange(0, 751, 62.5))

    if result_file_name is not None:
        plt.savefig(path.join(pf_param.ROOT_DIR, "result/", result_file_name + ".eps"))
        plt.savefig(path.join(pf_param.ROOT_DIR, "result/", result_file_name + ".png"))
    plt.show()
    plt.close()

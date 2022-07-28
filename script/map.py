import csv
import os.path as path
import pickle
from itertools import combinations_with_replacement
from typing import Any, Optional
import cv2
import numpy as np
import particle_filter.script.parameter as pf_param
import particle_filter.script.utility as pf_util
import yaml
from line_iterator.script.line_iterator import LineIterator
from particle_filter.script.map import Map as PfMap
from . import parameter as param


class Map(PfMap):
    def __init__(self, mac_list: np.ndarray, result_dir: Optional[str] = None) -> None:
        super().__init__(mac_list, result_dir)

        self._set_nodes()
        self._set_links()

    def _set_nodes(self) -> None:
        with open(path.join(param.ROOT_DIR, "map/node.yaml")) as f:
            node_conf: dict[Any, list[int]] = yaml.safe_load(f)
        self.node_poses = np.empty((len(node_conf), 2), dtype=np.int16)
        self.node_names = np.empty(len(node_conf), dtype=np.object_)    # any length string
        for i, (k, v) in enumerate(node_conf.items()):
            self.node_poses[i] = v
            self.node_names[i] = str(k)

        print(f"map.py: {len(self.node_poses)} nodes were found")

    def _init_links(self) -> None:
        self.link_nodes = np.empty((len(self.node_poses)), dtype=np.ndarray)    # another node
        self.link_costs = np.empty((len(self.node_poses)), dtype=np.ndarray)    # length [px]
        for i in range(len(self.node_poses)):
            self.link_nodes[i] = np.empty(0, dtype=np.int16)
            self.link_costs[i] = np.empty(0, dtype=np.float32)

    def _set_link_nodes_and_costs(self, i: np.int16, j: np.int16, cost: np.float32) -> None:
        self.link_nodes[i] = np.hstack((self.link_nodes[i], j))
        self.link_costs[i] = np.hstack((self.link_costs[i], cost))
        if i != j:
            self.link_nodes[j] = np.hstack((self.link_nodes[j], i))
            self.link_costs[j] = np.hstack((self.link_costs[j], cost))

    def _load_links_from_csv(self, file: str) -> None:
        with open(path.join(param.ROOT_DIR, "map/", file)) as f:
            for row in csv.reader(f):
                try:
                    i = np.where(row[0] == self.node_names)[0][0]
                    j = np.where(row[1] == self.node_names)[0][0]
                    cost = np.float32(row[2])
                except:
                    raise Warning(f"map.py: error occurred when loading {row}")
                else:
                    if j not in self.link_nodes[i] and cost <= param.MAX_LINK_LEN:    # not to deplicate
                        self._set_link_nodes_and_costs(i, j, cost)

        print(f"map.py: {file} has been loaded")

    def _search_direct_links_from_img(self) -> None:
        for (i, p), (j, q) in combinations_with_replacement(enumerate(self.node_poses), 2):
            if j not in self.link_nodes[i]:
                cost = pf_util.calc_dist_by_pos(p, q)
                if cost <= param.MAX_LINK_LEN and LineIterator(self.plain_img, p, q).min() > 250:    # link is on white region
                    self._set_link_nodes_and_costs(i, j, cost)

    def _update_link_nodes_and_costs(self, i: np.int16, j: np.int16, cost: np.float16) -> None:
        if j not in self.link_nodes[i]:
            self._set_link_nodes_and_costs(i, j, cost)    # set nodes and costs
        else:
            idx_ij = np.where(j == self.link_nodes[i])[0][0]
            if cost < self.link_costs[i][idx_ij]:
                self.link_costs[i][idx_ij] = cost    # update cost
                self.link_costs[j][np.where(i == self.link_nodes[j])[0][0]] = cost

    def _search_links_recursively(self, node_idxes: list[int], cost: np.float32) -> None:
        i = node_idxes[0]     # root
        j = node_idxes[-1]    # leaf

        for idx_jk, k in enumerate(self.link_nodes[j]):
            if k in node_idxes:
                continue

            cost_sum = cost + self.link_costs[j][idx_jk]
            if cost_sum <= param.MAX_LINK_LEN:
                self._update_link_nodes_and_costs(i, k, cost_sum)
                node_idxes.append(k)
                self._search_links_recursively(node_idxes, cost_sum)

    def _search_indirect_links(self) -> None:
        for i in range(len(self.node_poses)):
            self._search_links_recursively([i], 0)

    def _load_links_from_pkl(self, file: str) -> None:
        with open(path.join(param.ROOT_DIR, "map/", file), mode="rb") as f:
            self.link_nodes, self.link_costs = pickle.load(f)

        print(f"map.py: {file} has been loaded")

    def _check_link_costs(self) -> None:
        for i in range(len(self.link_nodes)):
            del_idxes = []
            for idx_ij, c in enumerate(self.link_costs[i]):
                if c > param.MAX_LINK_LEN:
                    del_idxes.append(idx_ij)
            self.link_nodes[i] = np.delete(self.link_nodes[i], del_idxes)
            self.link_costs[i] = np.delete(self.link_costs[i], del_idxes)

    # prepare lookup table of links
    def _set_links(self) -> None:
        self._init_links()

        match param.SET_NODES_LINKS_POLICY:
            case 1:    # load some irregular and search regular
                self._load_links_from_csv("additional_link.csv")
                self._search_direct_links_from_img()
                self._search_indirect_links()
            case 2:    # load all from CSV file
                self._load_links_from_csv("link.csv")
            case 3:    # load all from pickle file
                self._load_links_from_pkl("link.pkl")
                self._check_link_costs()

    def _draw_line(self, color: tuple[int, int, int], i: int, j: int, is_never_cleared: bool) -> None:
        if is_never_cleared:
            cv2.line(self.plain_img, self.node_poses[i], self.node_poses[j], color, thickness=2)
        cv2.line(self.img, self.node_poses[i], self.node_poses[j], color, thickness=2)

    def draw_links(self, is_never_cleared: bool = False) -> None:
        if not param.ENABLE_DRAW_LINKS:
            raise Warning("map.py: drawing links is not enabled but draw_links() was called")

        for i, js in enumerate(self.link_nodes):
            for j in js:
                self._draw_line((128, 128, 128), i, j, is_never_cleared)

    def draw_nodes(self, is_never_cleared: bool = False) -> None:
        if not param.ENABLE_DRAW_NODES:
            raise Warning("map.py: drawing nodes is not enabled but draw_nodes() was called")

        match param.NODES_SHOW_POLICY:
            case 1:    # circle
                for i, p in enumerate(self.node_poses):
                    self._safe_draw_pos((128, 128, 128), is_never_cleared, p)
            case 2:    # node name
                for i, p in enumerate(self.node_poses):
                    if is_never_cleared:
                        cv2.putText(self.plain_img, self.node_names[i], p, cv2.FONT_HERSHEY_PLAIN, 0.5, (128, 128, 128), lineType=cv2.LINE_AA)
                    cv2.putText(self.img, self.node_names[i], p, cv2.FONT_HERSHEY_PLAIN, 0.5, (128, 128, 128), lineType=cv2.LINE_AA)

    def get_nearest_node(self, pos: np.ndarray) -> int:
        min_dist = np.inf
        min_idx = -1
        for i, p in enumerate(self.node_poses):
            dist = pf_util.calc_dist_by_pos(p, pos)
            if dist < min_dist:
                min_dist = dist
                min_idx = i

        return min_idx

    def draw_particles(self, last_pos: np.ndarray, particles: np.ndarray) -> None:
        super().draw_particles(particles)

        match pf_param.SHOW_POLICY:
            case 6:
                self._draw_line((0, 0, 255), self.get_nearest_node(last_pos), self.get_nearest_node(pf_util.get_likeliest_particle(particles).pos))
            case 7:
                self._draw_line((0, 0, 255), self.get_nearest_node(last_pos), self.get_nearest_node(pf_util.get_center_of_gravity(particles)))

    def export_links_to_csv(self) -> None:
        with open(path.join(param.ROOT_DIR, "map/link.csv"), mode="w", newline="") as f:
            writer = csv.writer(f)
            for i, js in enumerate(self.link_nodes):
                for idx_ij, j in enumerate(js):
                    writer.writerow((self.node_names[i], self.node_names[j], self.link_costs[i][idx_ij]))

        print("map.py: links have been exported to link.csv")

    def export_links_to_pkl(self) -> None:
        with open(path.join(param.ROOT_DIR, "map/link.pkl"), mode="wb") as f:
            pickle.dump((self.link_nodes, self.link_costs), f)

        print("map.py: links have been exported to link.pkl")

    def get_cost(self, i: int, j: int) -> np.float32:
        return self.link_costs[i][np.where(j == self.link_nodes[i])[0][0]] if j in self.link_nodes[i] else np.float32(np.inf)

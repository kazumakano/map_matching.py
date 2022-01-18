import csv
import os.path as path
import pickle
from itertools import combinations_with_replacement
from typing import Any
import cv2
import numpy as np
import particle_filter.script.parameter as pf_param
import particle_filter.script.utility as pf_util
import yaml
from line_iterator.script.line_iterator import LineIterator
from particle_filter.script.map import Map as PfMap
from . import parameter as param


class Map(PfMap):
    def __init__(self, mac_list: np.ndarray, result_file_name: str) -> None:
        super().__init__(mac_list, result_file_name)

        self._set_nodes()
        self._set_links()

    def _set_nodes(self) -> None:
        with open(path.join(param.ROOT_DIR, "map/node.yaml")) as f:
            node_conf: dict[Any, list[int]] = yaml.safe_load(f)
        self.node_poses = np.empty((len(node_conf), 2), dtype=np.int16)
        self.node_names = np.empty(len(node_conf), dtype=object)    # any length string
        i = 0
        for k, v in node_conf.items():
            self.node_poses[i] = v
            self.node_names[i] = str(k)
            i += 1

        print(f"map.py: {len(self.node_poses)} nodes found")

    def _init_links(self) -> None:
        self.link_nodes = np.empty((len(self.node_poses)), dtype=np.ndarray)    # another node
        self.link_costs = np.empty((len(self.node_poses)), dtype=np.ndarray)    # length of the link
        for i in range(len(self.node_poses)):
            self.link_nodes[i] = np.empty(0, dtype=np.int16)
            self.link_costs[i] = np.empty(0, dtype=np.float16)

    def _set_link_nodes_and_costs(self, i: np.int16, j: np.int16, cost: np.float16) -> None:
        self.link_nodes[i] = np.hstack((self.link_nodes[i], j))
        self.link_costs[i] = np.hstack((self.link_costs[i], cost))
        if i != j:
            self.link_nodes[j] = np.hstack((self.link_nodes[j], i))
            self.link_costs[j] = np.hstack((self.link_costs[j], cost))

    # load links from link file
    def _load_links(self, link_file: str) -> None:
        with open(path.join(param.ROOT_DIR, "map/", link_file)) as f:
            reader = csv.reader(f)
            for row in reader:
                try:
                    i = np.int16(np.where(row[0] == self.node_names)[0][0])
                    j = np.int16(np.where(row[1] == self.node_names)[0][0])
                    cost = np.float16(row[2])
                except:
                    raise Warning(f"map.py: error occurred when loading {row}")
                else:
                    if j not in self.link_nodes[i] and cost < param.MAX_LINK_LEN:    # not to deplicate
                        self._set_link_nodes_and_costs(i, j, cost)

        print(f"map.py: {link_file} has been loaded")

    def _get_direct_links_from_img(self) -> None:
        for (i, p), (j, q) in combinations_with_replacement(enumerate(self.node_poses), 2):
            if j not in self.link_nodes[i]:
                cost = pf_util.calc_dist_by_pos(p, q)

                if cost < param.MAX_LINK_LEN:
                    line_iterator = LineIterator(self.plain_img, p, q)

                    if line_iterator.min() > 250:    # if link is on white region
                        self._set_link_nodes_and_costs(i, j, cost)

    def _update_link_nodes_and_costs(self, i: np.int16, j: np.int16, cost: np.float16) -> None:
        if j not in self.link_nodes[i]:
            self._set_link_nodes_and_costs(i, j, cost)    # set nodes and costs
        else:
            index_ij: int = np.where(j == self.link_nodes[i])[0][0]
            if cost < self.link_costs[i][index_ij]:
                self.link_costs[i][index_ij] = cost    # update cost
                self.link_costs[j][np.where(i == self.link_nodes[j])[0][0]] = cost

    def _search_links_recursively(self, node_indexes: np.ndarray, cost: np.float16) -> None:
        i: np.int16 = node_indexes[0]     # root
        j: np.int16 = node_indexes[-1]    # leaf

        for index_jk, k in enumerate(self.link_nodes[j]):
            if k in node_indexes:
                continue

            cost_sum: np.float16 = cost + self.link_costs[j][index_jk]
            if cost_sum < param.MAX_LINK_LEN:
                self._update_link_nodes_and_costs(i, k, cost_sum)
                self._search_links_recursively(np.hstack((node_indexes, k)), cost_sum)

    def _search_indirect_links(self) -> None:
        for i in range(len(self.node_poses)):
            self._search_links_recursively(np.array((i,), dtype=np.int16), 0)

    # prepare lookup table of links
    def _set_links(self) -> None:
        self._init_links()

        if param.SET_LINKS_POLICY == 1:      # load some irregular and search regular
            self._load_links("additional_link.csv")
            self._get_direct_links_from_img()
            self._search_indirect_links()
        elif param.SET_LINKS_POLICY == 2:    # load all from CSV file
            self._load_links("link.csv")
        elif param.SET_LINKS_POLICY == 3:    # load all from pickle file
            with open(path.join(param.ROOT_DIR, "map/link.pkl"), "rb") as f:
                self.link_nodes, self.link_costs = pickle.load(f)

            print("map.py: link.pkl has been loaded")

    def _draw_link(self, color: tuple[int, int, int], i: int, j: int) -> None:
        cv2.line(self.img, self.node_poses[i], self.node_poses[j], color, 2)

    def draw_links(self) -> None:
        if not param.ENABLE_DRAW_LINKS:
            raise Warning("map.py: drawing links is not enabled but draw_links() was called")

        for i, js in enumerate(self.link_nodes):
            for j in js:
                self._draw_link((128, 128, 128), i, j)

    def draw_nodes(self, is_never_cleared: bool = False) -> None:
        if not param.ENABLE_DRAW_NODES:
            raise Warning("map.py: drawing nodes is not enabled but draw_nodes() was called")

        for i, p in enumerate(self.node_poses):
            if param.NODES_SHOW_POLICY == 1:      # circle
                self._draw_pos((128, 128, 128), is_never_cleared, p)
            elif param.NODES_SHOW_POLICY == 2:    # node name
                if is_never_cleared:
                    cv2.putText(self.plain_img, self.node_names[i], p, cv2.FONT_HERSHEY_PLAIN, 1, (128, 128, 128), 2, cv2.LINE_AA)
                cv2.putText(self.img, self.node_names[i], p, cv2.FONT_HERSHEY_PLAIN, 1, (128, 128, 128), 2, cv2.LINE_AA)

    def get_nearest_node(self, pos: np.ndarray) -> int:
        min_dist = np.inf
        min_index = -1
        for i, p in enumerate(self.node_poses):
            dist = pf_util.calc_dist_by_pos(p, pos)
            if dist < min_dist:
                min_dist = dist
                min_index = i

        return min_index

    def draw_particles(self, last_pos: np.ndarray, particles: np.ndarray) -> None:
        super().draw_particles(particles)

        if pf_param.SHOW_POLICY == 6:
            self._draw_link((0, 0, 255), self.get_nearest_node(last_pos), self.get_nearest_node(pf_util.get_likeliest_particle(particles).pos))
        elif pf_param.SHOW_POLICY == 7:
            self._draw_link((0, 0, 255), self.get_nearest_node(last_pos), self.get_nearest_node(pf_util.get_center_of_gravity(particles)))

    def export_links_to_csv(self) -> None:
        with open(path.join(param.ROOT_DIR, "map/link.csv"), "w") as f:
            writer = csv.writer(f)
            for i in range(len(self.node_poses)):
                for index_ij, j in enumerate(self.link_nodes[i]):
                    writer.writerow((self.node_names[i], self.node_names[j], self.link_costs[i][index_ij]))

        print("map.py: links have been exported to link.csv")

    def export_links_to_pkl(self) -> None:
        with open(path.join(param.ROOT_DIR, "map/link.pkl"), "wb") as f:
            pickle.dump((self.link_nodes, self.link_costs), f)

        print("map.py: links have been exported to link.pkl")

    def get_cost(self, i: int, j: int) -> np.float64:
        return self.link_costs[i][np.where(j == self.link_nodes[i])[0][0]] if j in self.link_nodes[i] else np.inf

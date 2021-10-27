from typing import Union
import cv2
import numpy as np
import particle_filter.script.utility as pf_util
import yaml
from particle_filter.script.log import Log
from particle_filter.script.map import Map as PfMap
from line_iterator.script.line_iterator import LineIterator
from . import parameter as param
import particle_filter.script.parameter as pf_param
from . import utility as util
import csv


class Map(PfMap):
    def __init__(self, log: Log) -> None:
        super().__init__(log)

        with open(param.ROOT_DIR + "map/node.yaml") as f:
            node_conf: dict = yaml.safe_load(f)
        self.node_poses = np.empty((len(node_conf), 2), dtype=int)
        self.node_names = np.empty(len(node_conf), dtype=object)
        i: int = 0
        for k, v in node_conf.items():
            self.node_poses[i] = v
            self.node_names[i] = str(k)
            i += 1

        print(f"map.py: {len(node_conf)} nodes found")

        self._set_links()

    def _set_node_and_cost(self, i: int, j: int, cost: np.float16):
        self.link_nodes[i] = np.hstack((self.link_nodes[i], j))       # another node of the link extend from each node
        self.link_costs[i] = np.hstack((self.link_costs[i], cost))    # length of the link extend from each node

    def _load_links(self, link_file: str) -> None:
        self.link_nodes = np.empty((len(self.node_poses)), dtype=np.ndarray)
        self.link_costs = np.empty((len(self.node_poses)), dtype=np.ndarray)
        for i in range(len(self.node_poses)):
            self.link_nodes[i] = np.empty(0, dtype=np.uint16)
            self.link_costs[i] = np.empty(0, dtype=np.float16)

        with open(param.ROOT_DIR + "/map/" + link_file) as f:
            reader = csv.reader(f)
            for row in reader:
                try:
                    i = np.where(row[0] == self.node_names)[0][0]
                    j = np.where(row[1] == self.node_names)[0][0]
                    cost = np.float16(row[2])
                except:
                    raise Warning(f"map.py: error occurred when loading {row}")
                if cost < param.MAX_LINK_LEN:
                    self._set_node_and_cost(i, j, cost)
                    self._set_node_and_cost(j, i, cost)

    def _search_links(self) -> None:
        # construct link connected directly
        for i, p in enumerate(self.node_poses):
            for j, q in enumerate(self.node_poses):
                dist = pf_util.calc_dist_by_pos(p, q)

                if dist < param.MAX_LINK_LEN:
                    line_iterator = LineIterator(self.plain_img, p, q)

                    if line_iterator.min() > 250:    # if line of link is on white region
                        self._set_node_and_cost(i, j, dist)
        
        # construct link connected indirectly
        # now only 2 layer (to be updated to recursive)
        for i in range(len(self.node_poses)):
            for index_ij, j in enumerate(self.link_nodes[i]):
                if j == i:
                    continue
                for index_jk, k in enumerate(self.link_nodes[j]):
                    if k == j or k == i:
                        continue
                    dist_sum: np.float16 = self.link_costs[i][index_ij] + self.link_costs[j][index_jk]
                    if (dist_sum < param.MAX_LINK_LEN) and (k not in self.link_nodes[i]):
                        self._set_node_and_cost(i, k, dist_sum)

    def _set_links(self) -> None:
        if param.SET_LINKS_POLICY == 1:
            self._load_links("additional_link.csv")
            self._search_links()
        elif param.SET_LINKS_POLICY == 2:
            self._load_links("link.csv")

    def export_links(self) -> None:
        pass

    def get_nearest_node(self, pos: np.ndarray) -> int:
        min_dist = np.inf
        min_index: int = -1
        for i, p in enumerate(self.node_poses):
            dist = pf_util.calc_dist_by_pos(pos, p)
            if dist < min_dist:
                min_dist = dist
                min_index = i
    
        return min_index

    def draw_nodes(self) -> None:
        for i, p in enumerate(self.node_poses):
            if param.NODES_SHOW_POLICY == 1:
                cv2.circle(self.img, p, 3, (100, 100, 100), 6)
            elif param.NODES_SHOW_POLICY == 2:
                cv2.putText(self.img, self.node_names[i], p, cv2.FONT_HERSHEY_PLAIN, 1, (100, 100, 100), 2, cv2.LINE_AA)

    def _draw_link_by_index(self, i: int, j: int) -> None:
        cv2.line(self.img, self.node_poses[i], self.node_poses[j], (100, 100, 100), 2)

    def draw_links(self) -> None:
        for i, js in enumerate(self.link_nodes):
            for j in js:
                self._draw_link_by_index(i, j)
    
    def draw_particles(self, particles: np.ndarray, last_pos: np.ndarray) -> None:
        super().draw_particles(particles)

        if pf_param.SHOW_POLOCY == 4:
            self._draw_link_by_index(self.get_nearest_node(last_pos), self.get_nearest_node(pf_util.get_likeliest_particle(particles).pos))
    
    # def zoom(self, mag: float = 1):
    #     cv2.imshow("zoom", cv2.resize(self.img, None, fx=mag, fy=mag))
    #     cv2.waitKey(0)

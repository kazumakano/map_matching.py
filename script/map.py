import csv
from itertools import combinations_with_replacement
from typing import Union
import cv2
import numpy as np
import particle_filter.script.parameter as pf_param
import particle_filter.script.utility as pf_util
import yaml
from line_iterator.script.line_iterator import LineIterator
from particle_filter.script.log import Log
from particle_filter.script.map import Map as PfMap
from . import parameter as param
from . import utility as util


class Map(PfMap):
    def __init__(self, log: Log) -> None:
        super().__init__(log)

        with open(param.ROOT_DIR + "map/node.yaml") as f:
            node_conf: dict = yaml.safe_load(f)
        self.node_poses = np.empty((len(node_conf), 2), dtype=int)
        self.node_names = np.empty(len(node_conf), dtype=object)    # any length string
        i: int = 0
        for k, v in node_conf.items():
            self.node_poses[i] = v
            self.node_names[i] = str(k)
            i += 1

        print(f"map.py: {len(self.node_poses)} nodes found")

        self._set_links()

        self.export_links()

    def _init_links(self) -> None:
        self.link_nodes = np.empty((len(self.node_poses)), dtype=np.ndarray)
        self.link_costs = np.empty((len(self.node_poses)), dtype=np.ndarray)
        for i in range(len(self.node_poses)):
            self.link_nodes[i] = np.empty(0, dtype=np.uint16)
            self.link_costs[i] = np.empty(0, dtype=np.float16)

    def _set_nodes_and_costs(self, i: int, j: int, cost: np.float16) -> None:
        self.link_nodes[i] = np.hstack((self.link_nodes[i], j))       # another node
        self.link_costs[i] = np.hstack((self.link_costs[i], cost))    # length of the link
        if i != j:
            self.link_nodes[j] = np.hstack((self.link_nodes[j], i))
            self.link_costs[j] = np.hstack((self.link_costs[j], cost))

    # load links from link file
    def _load_links(self, link_file: str) -> None:
        with open(param.ROOT_DIR + "/map/" + link_file) as f:
            reader = csv.reader(f)
            for row in reader:
                try:
                    i = np.where(row[0] == self.node_names)[0][0]
                    j = np.where(row[1] == self.node_names)[0][0]
                    cost = np.float16(row[2])
                except:
                    raise Warning(f"map.py: error occurred when loading {row}")

                if j not in self.link_nodes[i] and cost < param.MAX_LINK_LEN:    # not to deplicate
                    self._set_nodes_and_costs(i, j, cost)

    def _get_direct_links_from_img(self) -> None:
        for c in combinations_with_replacement(enumerate(self.node_poses), 2):    # c is ((i, node_poses[i]), (j, node_poses[j]))
            if c[1][0] not in self.link_nodes[c[0][0]]:
                cost = pf_util.calc_dist_by_pos(c[0][1], c[1][1])

                if cost < param.MAX_LINK_LEN:
                    line_iterator = LineIterator(self.plain_img, c[0][1], c[1][1])

                    if line_iterator.min() > 250:    # if link is on white region
                        self._set_nodes_and_costs(c[0][0], c[1][0], cost)

    def _update_nodes_and_costs(self, i: int, j: int, cost: np.float16) -> None:
        if j not in self.link_nodes[i]:
            self._set_nodes_and_costs(i, j, cost)    # set nodes and costs if new
        else:
            index_ij = np.where(j == self.link_nodes[i])[0][0]
            if cost < self.link_costs[i][index_ij]:
                self.link_costs[i][index_ij] = cost    # update costs if lower
                self.link_costs[j][np.where(i == self.link_nodes[j])[0][0]] = cost

    def _search_links_recursively(self, node_indexes: np.ndarray, cost: np.float16) -> None:
        i = node_indexes[0]
        j = node_indexes[-1]

        for index_jk, k in enumerate(self.link_nodes[j]):
            if k in node_indexes:
                continue

            cost_sum = cost + self.link_costs[j][index_jk]
            if cost_sum < param.MAX_LINK_LEN:
                self._update_nodes_and_costs(i, k, cost_sum)
                self._search_links_recursively(np.hstack((node_indexes, k)), cost_sum)

    def _search_indirect_links(self) -> None:
        for i in range(len(self.node_poses)):
            self._search_links_recursively(np.array((i,), dtype=np.uint16), 0)

    def _search_indirect_links_2(self) -> None:
        for i in range(len(self.node_poses)):
            for index_ij, j in enumerate(self.link_nodes[i]):
                if j == i:
                    continue
                for index_jk, k in enumerate(self.link_nodes[j]):
                    if k == j or k == i:
                        continue
                    dist_sum: np.float16 = self.link_costs[i][index_ij] + self.link_costs[j][index_jk]
                    if (dist_sum < param.MAX_LINK_LEN) and (k not in self.link_nodes[i]):
                        self._set_nodes_and_costs(i, k, dist_sum)

    def _set_links(self) -> None:
        self._init_links()
        if param.SET_LINKS_POLICY == 1:      # load some irregular and search
            self._load_links("additional_link.csv")
            self._get_direct_links_from_img()
            self._search_indirect_links()
        elif param.SET_LINKS_POLICY == 2:    # load all
            self._load_links("link.csv")

    def export_links(self) -> None:
        with open(param.ROOT_DIR + "map/link.csv", "w") as f:
            writer = csv.writer(f)
            for i in range(len(self.node_poses)):
                for index_ij, j in enumerate(self.link_nodes[i]):
                    writer.writerow((self.node_names[i], self.node_names[j], self.link_costs[i][index_ij]))

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
                cv2.circle(self.img, p, 3, (128, 128, 128), 6)
            elif param.NODES_SHOW_POLICY == 2:
                cv2.putText(self.img, self.node_names[i], p, cv2.FONT_HERSHEY_PLAIN, 1, (128, 128, 128), 2, cv2.LINE_AA)

    def _draw_link(self, i: int, j: int) -> None:
        cv2.line(self.img, self.node_poses[i], self.node_poses[j], (0, 128, 0), 2)

    def draw_links(self) -> None:
        for i, js in enumerate(self.link_nodes):
            for j in js:
                self._draw_link(i, j)

    def draw_particles(self, particles: np.ndarray, last_pos: np.ndarray) -> None:
        super().draw_particles(particles)

        if pf_param.SHOW_POLOCY == 6:
            self._draw_link(self.get_nearest_node(last_pos), self.get_nearest_node(pf_util.get_likeliest_particle(particles).pos))

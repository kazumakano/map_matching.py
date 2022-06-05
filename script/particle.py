import numpy as np
import particle_filter.script.parameter as pf_param
import particle_filter.script.utility as pf_util
from particle_filter.script.particle import Particle as PfParticle
from . import parameter as param
from .map import Map


class Particle(PfParticle):
    def set_likelihood(self, last_pos: np.ndarray, map: Map, strength_weight_list: np.ndarray, subject_dist_list: np.ndarray) -> None:
        super().set_likelihood(map.beacon_pos_list, strength_weight_list, subject_dist_list)

        if not pf_param.IS_LOST:    # don't consider match weight with old position
            match param.MATCH_WEIGHT_POLICY:
                case 1:    # multiply maximum match weight between nearest node and nodes linked with last node
                    min_cost = np.inf
                    near_node_idx = map.get_nearest_node(self.pos)
                    for i in map.link_nodes[map.get_nearest_node(last_pos)]:
                        cost = map.get_cost(i, near_node_idx)
                        if cost < min_cost:
                            min_cost = cost

                    self.likelihood *= pf_util.calc_prob_weight(min_cost, 0)

                case 2:    # multiply match weight between nearest node and last node
                    self.likelihood *= pf_util.calc_prob_weight(map.get_cost(map.get_nearest_node(self.pos), map.get_nearest_node(last_pos)), 0)

                case 3:    # pass or cut off
                    self.likelihood *= map.get_nearest_node(self.pos) in map.link_nodes[map.get_nearest_node(last_pos)]

                case 4:    # half reduction
                    if map.get_nearest_node(self.pos) not in map.link_nodes[map.get_nearest_node(last_pos)]:
                        self.likelihood *= 0.5

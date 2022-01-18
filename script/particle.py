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
            if param.MATCH_WEIGHT_POLICY == 1:      # multiply maximum match weight between self nearest node and nodes linked with last node
                max_match_weight = 0
                for i in map.link_nodes[map.get_nearest_node(last_pos)]:
                    match_weight = pf_util.calc_prob_weight(map.get_cost(i, map.get_nearest_node(self.pos)), 0)
                    if match_weight > max_match_weight:
                        max_match_weight = match_weight

                self.likelihood *= max_match_weight

            elif param.MATCH_WEIGHT_POLICY == 2:    # multiply match weight between self nearest node and last node
                self.likelihood *= pf_util.calc_prob_weight(map.get_cost(map.get_nearest_node(last_pos), map.get_nearest_node(self.pos)), 0)

            elif param.MATCH_WEIGHT_POLICY == 3:    # pass or cut off
                self.likelihood *= map.get_nearest_node(self.pos) in map.link_nodes[map.get_nearest_node(last_pos)]

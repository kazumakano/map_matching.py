import numpy as np
import particle_filter.script.utility as pf_util
from particle_filter.script.particle import Particle as PfParticle
from particle_filter.script.window import Window
from . import parameter as param
from .map import Map


class Particle(PfParticle):
    def set_likelihood(self, map: Map, win: Window, last_pos: np.ndarray):
        super().set_likelihood(map, win)

        if param.MATCH_WEIGHT_POLICY == 1:      # add match weight
            if self.likelihood > param.MIN_VANILLA_LH:
                # max_match_weight = 0
                # for i in map.link_nodes[map.get_nearest_node(last_pos)]:
                #     match_weight = pf_util.calc_prob_weight(map.get_cost(i, map.get_nearest_node(self.pos)), 0)
                #     if match_weight > max_match_weight:
                #         max_match_weight = match_weight

                # self.likelihood += max_match_weight

                self.likelihood += pf_util.calc_prob_weight(map.get_cost(map.get_nearest_node(last_pos), map.get_nearest_node(self.pos)), 0)
            
            else:
                self.likelihood = 0    # dump perticle if unreliable

        elif param.MATCH_WEIGHT_POLICY == 2:    # pass or cut off
            if self.likelihood > param.MIN_VANILLA_LH:
                self.likelihood *= map.get_nearest_node(self.pos) in map.link_nodes[map.get_nearest_node(last_pos)]    # pass if particle is connected to last position
            else:
                self.likelihood = 0

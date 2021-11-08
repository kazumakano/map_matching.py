import numpy as np
from particle_filter.script.particle import Particle as PfParticle
from particle_filter.script.window import Window
from . import parameter as param
from . import utility as util
from .map import Map


class Particle(PfParticle):
    def set_likelihood(self, map: Map, win: Window, last_pos: np.ndarray):
        super().set_likelihood(map, win)

        if param.MATCH_WEIGHT_POLICY == 1:
            if self.likelihood > param.MIN_VANILLA_LH:
                max_match_weight = 0
                for i in map.link_nodes[map.get_nearest_node(last_pos)]:
                    match_weight = util.calc_match_weight(self.pos, map.node_poses[i])
                    if match_weight > max_match_weight:
                        max_match_weight = match_weight

                self.likelihood = self.likelihood + max_match_weight
            
            else:
                self.likelihood = 0    # dump unreliable data

        elif param.MATCH_WEIGHT_POLICY == 2:
            self.likelihood *= map.get_nearest_node(self.pos) in map.link_nodes[map.get_nearest_node(last_pos)]    # pass if particle is connected to last position

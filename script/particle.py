import numpy as np
import particle_filter.script.parameter as pf_param
import particle_filter.script.utility as pf_util
from particle_filter.script.particle import Particle as PfParticle
from . import parameter as param
from .map import Map


class Particle(PfParticle):
    def __init__(self, map_img_shape: tuple[int, int], last_pos: np.ndarray = np.full(2, np.nan, dtype=np.float16), init_pos: np.ndarray = np.full(2, np.nan, dtype=np.float16), init_direct: np.float16 = np.float16(np.nan)) -> None:
        if np.isnan(init_pos[0]):
            if param.RAND_POS_RANGE == 0 or np.isnan(last_pos[0]):
                self.pos: np.ndarray = (map_img_shape * np.random.rand(2)).astype(np.float16)    # uniform distribution in map
            else:
                self.pos: np.ndarray = (last_pos - param.RAND_POS_RANGE / 2 + param.RAND_POS_RANGE * np.random.rand(2)).astype(np.float16)    # uniform distribution around last position
        else:
            self.pos = init_pos

        if np.isnan(init_direct):
            self.direct = np.float16(360 * np.random.rand())    # uniform distribution in (0, 360)
        else:
            self.direct = init_direct

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

import numpy as np
import particle_filter.script.utility as pf_util
from . import parameter as param

def calc_match_weight(particle_pos: np.ndarray, node_pos: np.ndarray) -> np.float64:
    return pf_util.calc_prob_weight(pf_util.calc_dist_by_pos(particle_pos, node_pos), 0)
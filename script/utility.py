import numpy as np
import particle_filter.script.utility as pf_util
from . import parameter as param


def estim_pos(particles: np.ndarray) -> np.ndarray:
    if param.ESTIM_POS_POLICY == 1:      # position of likeliest particle
        return pf_util.get_likeliest_particle(particles).pos
    elif param.ESTIM_POS_POLICY == 2:    # center of gravity of particles
        return pf_util.get_center_of_gravity(particles)

import os.path as path
from typing import Union
import numpy as np
from particle_filter.script.parameter import set_params as set_pf_params


def _set_map_params(conf: dict) -> None:
    global ENABLE_DRAW_LINKS, ENABLE_DRAW_NODES, MAX_LINK_LEN, NODES_SHOW_POLICY, SET_LINKS_POLICY
    
    ENABLE_DRAW_LINKS = bool(conf["enable_draw_links"])
    ENABLE_DRAW_NODES = bool(conf["enable_draw_nodes"])
    MAX_LINK_LEN = np.float16(conf["max_link_len"])
    NODES_SHOW_POLICY = np.int8(conf["nodes_show_policy"])
    SET_LINKS_POLICY = np.int8(conf["set_links_policy"])

def _set_particle_params(conf: dict) -> None:
    global MATCH_WEIGHT_POLICY, RAND_POS_RANGE

    MATCH_WEIGHT_POLICY = np.int8(conf["match_weight_policy"])
    RAND_POS_RANGE = np.float16(conf["rand_pos_range"])

def set_params(conf_file: Union[str, None] = None) -> dict:
    global ROOT_DIR

    ROOT_DIR = path.join(path.dirname(__file__), "../")

    if conf_file is None:
        conf_file = path.join(ROOT_DIR, "config/default.yaml")

    conf = set_pf_params(conf_file)
    _set_map_params(conf)
    _set_particle_params(conf)

    return conf

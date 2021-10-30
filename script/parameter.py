import os.path as path
from typing import Union
import numpy as np
from particle_filter.script.parameter import set_params as set_pf_params

def _set_particle_params(conf: dict) -> None:
    global MATCH_WEIGHT_POLICY, MIN_VANILLA_LH

    MATCH_WEIGHT_POLICY = conf["match_weight_policy"]          # 1: probability, 2: binary
    MIN_VANILLA_LH = np.float64(conf["min_vanilla_lh"])        # minimum likelihood without match weight

def _set_map_params(conf: dict) -> None:
    global ENABLE_DRAW_NODES, NODES_SHOW_POLICY, MAX_LINK_LEN, ENABLE_DRAW_LINKS, SET_LINKS_POLICY
    
    ENABLE_DRAW_NODES = conf["enable_draw_nodes"]
    NODES_SHOW_POLICY = np.int8(conf["nodes_show_policy"])     # 1: circle, 2: node name
    MAX_LINK_LEN = np.float16(conf["max_link_len"])            # max length of link
    ENABLE_DRAW_LINKS = conf["enable_draw_links"]              # draw links or not
    SET_LINKS_POLICY = conf["set_links_policy"]                # 1: load some irregular links from additional_link.csv and search regular links automatically 
                                                               # 2: load all links from link.csv


def set_params(conf_file: Union[str, None] = None) -> dict:
    global ROOT_DIR

    ROOT_DIR = path.dirname(__file__) + "/../"              # project root directory

    if conf_file is None:
        conf_file = ROOT_DIR + "config/default.yaml"    # load default file if not specified
    else:
        conf_file = conf_file

    conf = set_pf_params(conf_file)
    _set_particle_params(conf)
    _set_map_params(conf)

    return conf

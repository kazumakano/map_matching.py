import os.path as path
from typing import Union
import numpy as np
from particle_filter.script.parameter import set_params as set_pf_params


def _set_map_params(conf: dict) -> None:
    global MAX_LINK_LEN, SET_LINKS_POLICY, ENABLE_DRAW_NODES, NODES_SHOW_POLICY, ENABLE_DRAW_LINKS
    
    MAX_LINK_LEN = np.float16(conf["max_link_len"])           # maximum cost of link
    SET_LINKS_POLICY = conf["set_links_policy"]               # 1: load some irregular links from additional_link.csv and search regular links automatically 
                                                              # 2: load all links from link.csv
                                                              # 3: load all links from link.pkl
    ENABLE_DRAW_NODES = conf["enable_draw_nodes"]             # draw nodes or not
    NODES_SHOW_POLICY = np.int8(conf["nodes_show_policy"])    # 1: circle, 2: node name
    ENABLE_DRAW_LINKS = conf["enable_draw_links"]             # draw links or not

def _set_particle_params(conf: dict) -> None:
    global RAND_POS_RANGE, MATCH_WEIGHT_POLICY, MIN_VANILLA_LH

    RAND_POS_RANGE = conf["rand_pos_range"]                   # range from last estimated position at random initialization of particle position (0 means all map)
    MATCH_WEIGHT_POLICY = conf["match_weight_policy"]         # 1, 2: multi match weight, 3: pass or cut off
    MIN_VANILLA_LH = np.float64(conf["min_vanilla_lh"])       # minimum likelihood without match weight

def set_params(conf_file: Union[str, None] = None) -> dict:
    global ROOT_DIR

    ROOT_DIR = path.dirname(__file__) + "/../"                # project root directory

    if conf_file is None:
        conf_file = ROOT_DIR + "config/default.yaml"    # load default file if not specified
    else:
        conf_file = conf_file

    conf = set_pf_params(conf_file)
    _set_map_params(conf)
    _set_particle_params(conf)

    return conf

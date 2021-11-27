import os.path as path
from typing import Union
import numpy as np
from particle_filter.script.parameter import set_params as set_pf_params


def _set_map_params(conf: dict) -> None:
    global MAX_LINK_LEN, SET_LINKS_POLICY, ENABLE_DRAW_NODES, NODES_SHOW_POLICY, ENABLE_DRAW_LINKS
    
    MAX_LINK_LEN = np.float16(conf["max_link_len"])               # maximum cost of link [pixel]
    SET_LINKS_POLICY = np.int8(conf["set_links_policy"])          # 1: load some irregular links from additional_link.csv and search regular links automatically 
                                                                  # 2: load all links from link.csv
                                                                  # 3: load all links from link.pkl
    ENABLE_DRAW_NODES = bool(conf["enable_draw_nodes"])           # draw nodes or not
    NODES_SHOW_POLICY = np.int8(conf["nodes_show_policy"])        # 1: circle, 2: node name
    ENABLE_DRAW_LINKS = bool(conf["enable_draw_links"])           # draw links or not

def _set_particle_params(conf: dict) -> None:
    global RAND_POS_RANGE, MATCH_WEIGHT_POLICY

    RAND_POS_RANGE = np.float16(conf["rand_pos_range"])           # range from last estimated position at random initialization of particle position [pixel] (all map if 0)
    MATCH_WEIGHT_POLICY = np.int8(conf["match_weight_policy"])    # 1, 2: multi match weight, 3: pass or cut off

def set_params(conf_file: Union[str, None] = None) -> dict:
    global ROOT_DIR

    ROOT_DIR = path.join(path.dirname(__file__), "../")           # project root directory

    if conf_file is None:
        conf_file = path.join(ROOT_DIR, "config/default.yaml")    # load default file

    conf = set_pf_params(conf_file)
    _set_map_params(conf)
    _set_particle_params(conf)

    return conf

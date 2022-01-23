import os.path as path
from datetime import datetime
from glob import glob, iglob
from typing import Union
import numpy as np
import yaml
import particle_filter.script.parameter as pf_param
import script.parameter as param
from particle_filter.script.log import Log
from script.map import Map


def _set_beacons(map: Map) -> None:
    for beacon_file in iglob(path.join(pf_param.ROOT_DIR, "map/beacon/*.yaml")):
        with open(beacon_file) as f:
            beacon_conf: dict = yaml.safe_load(f)
        map.beacon_pos_list = np.vstack((map.beacon_pos_list, beacon_conf["rotated_position"][0:2]))

    print(f"visualize_nodes_and_links.py: {len(map.beacon_pos_list)} beacons found")

def vis_map(result_dir: Union[str, None]) -> None:
    map = Map(Log(datetime(2000, 1, 1), datetime(2000, 1, 1), glob(path.join(pf_param.ROOT_DIR, "log/observed/*.csv"))[0]).mac_list, result_dir)    # whatever is fine
    if pf_param.ENABLE_DRAW_BEACONS:
        _set_beacons(map)
        map.draw_beacons()
    if param.ENABLE_DRAW_NODES:
        map.draw_nodes()
    if param.ENABLE_DRAW_LINKS:
        map.draw_links()
    if pf_param.ENABLE_SAVE_IMG:
        map.save_img()

    map.show(0)

if __name__ == "__main__":
    import argparse
    import particle_filter.script.utility as pf_util
    from script.parameter import set_params

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--conf_file", help="specify config file", metavar="PATH_TO_CONF_FILE")
    parser.add_argument("-b", "--beacon", action="store_true", help="enable draw beacons")
    parser.add_argument("-n", "--node", action="store_true", help="enable draw nodes")
    parser.add_argument("-l", "--link", action="store_true", help="enable draw links")
    parser.add_argument("-s", "--save", action="store_true", help="enable save image")
    args = parser.parse_args()

    if (not args.beacon) and (not args.node) and (not args.link):
        raise Warning("visualize_map.py: set flags in order to visualize")

    conf = set_params(args.conf_file)
    pf_param.ENABLE_DRAW_BEACONS = args.beacon
    param.ENABLE_DRAW_NODES = args.node
    param.ENABLE_DRAW_LINKS = args.link
    pf_param.ENABLE_SAVE_IMG = args.save

    vis_map(pf_util.make_result_dir(None if conf["result_dir_name"] is None else str(conf["result_dir_name"])))

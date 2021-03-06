from typing import Optional
import numpy as np
import particle_filter.script.parameter as pf_param
import script.parameter as param
from script.map import Map


def vis_map(enable_show: bool = True, result_dir: Optional[str] = None) -> None:
    map = Map(np.empty(0, dtype=str), result_dir)
    if pf_param.ENABLE_DRAW_BEACONS:
        map.set_all_beacons()
        map.draw_beacons()
    if param.ENABLE_DRAW_NODES:
        map.draw_nodes()
    if param.ENABLE_DRAW_LINKS:
        map.draw_links()
    if pf_param.ENABLE_SAVE_IMG:
        map.save_img()
    if enable_show:
        map.show(0)

if __name__ == "__main__":
    import argparse
    import particle_filter.script.utility as pf_util
    from script.parameter import set_params

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--conf_file", help="specify config file", metavar="PATH_TO_CONF_FILE")
    parser.add_argument("--no_display", action="store_true", help="run without display")
    parser.add_argument("-b", "--beacon", action="store_true", help="enable draw beacons")
    parser.add_argument("-l", "--link", action="store_true", help="enable draw links")
    parser.add_argument("-n", "--node", type=int, choices=(1, 2), help="enable draw nodes", metavar="NODES_SHOW_POLICY")
    parser.add_argument("-s", "--save", action="store_true", help="enable save image")
    args = parser.parse_args()

    if (not args.beacon) and (not args.link) and (args.node is None):
        raise Warning("visualize_map.py: set flags in order to visualize")

    conf = set_params(args.conf_file)
    pf_param.ENABLE_DRAW_BEACONS = bool(args.beacon)
    param.ENABLE_DRAW_LINKS = bool(args.link)
    param.ENABLE_DRAW_NODES = bool(args.node is not None)
    if param.ENABLE_DRAW_NODES:
        param.NODES_SHOW_POLICY = int(args.node)
    pf_param.ENABLE_SAVE_IMG = bool(args.save)

    vis_map(not args.no_display, pf_util.make_result_dir(None if conf["result_dir_name"] is None else str(conf["result_dir_name"])))

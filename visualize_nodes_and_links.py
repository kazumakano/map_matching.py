import argparse
from datetime import datetime
from particle_filter.script.log import Log
from script.map import Map
from script.parameter import set_params
import script.parameter as param

def vis_nodes_and_links() -> None:
    map = Map(Log(datetime(2000, 1, 1), datetime(2000, 1, 1)))    # whenever is fine

    if param.ENABLE_DRAW_NODES:
        map.draw_nodes()
    if param.ENABLE_DRAW_LINKS:
        map.draw_links()

    map.show(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="specify your config file", metavar="PATH_TO_CONFIG_FILE")
    parser.add_argument("-n", "--node", action="store_true", help="enable draw node")
    parser.add_argument("-l", "--link", action="store_true", help="enable draw link")
    args = parser.parse_args()

    if (not args.node) and (not args.link):
        raise Warning("visualize_nodes_and_links.py: set flags in order to visualize")

    set_params(args.config)
    param.ENABLE_DRAW_NODES = args.node
    param.ENABLE_DRAW_LINKS = args.link

    vis_nodes_and_links()

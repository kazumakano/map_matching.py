import argparse
from datetime import datetime
import script.parameter as param
from particle_filter.script.log import Log
from script.map import Map
from script.parameter import set_params


def prepare_links(enable_csv: bool = False, enable_pkl: bool = False) -> None:
    map = Map(Log(datetime(2000, 1, 1), datetime(2000, 1, 1)))    # whenever is fine

    if enable_csv:
        map.export_links_as_csv()
    if enable_pkl:
        map.export_links_as_pkl()

    map.draw_links()
    map.show(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="specify your config file", metavar="PATH_TO_CONFIG_FILE")
    parser.add_argument("--csv", action="store_true", help="export as CSV file")
    parser.add_argument("--pkl", action="store_true", help="export as pickle file")
    args = parser.parse_args()

    if (not args.csv) and (not args.pkl):
        raise Warning("prepare_links.py: set flags in order to export")

    set_params(args.config)
    param.SET_LINKS_POLICY = 1
    param.ENABLE_DRAW_LINKS = True

    prepare_links(args.csv, args.pkl)

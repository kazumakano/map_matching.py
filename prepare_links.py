import numpy as np
from script.map import Map


def prepare_links(enable_show: bool = True, enable_csv: bool = False, enable_pkl: bool = False) -> None:
    map = Map(np.empty(0, dtype=str))

    if enable_csv:
        map.export_links_to_csv()
    if enable_pkl:
        map.export_links_to_pkl()

    map.draw_links()
    map.draw_nodes()
    if enable_show:
        map.show(0)

if __name__ == "__main__":
    import argparse
    import script.parameter as param
    from script.parameter import set_params

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--conf_file", help="specify config file", metavar="PATH_TO_CONF_FILE")
    parser.add_argument("--no_display", action="store_true", help="run without display")
    parser.add_argument("--csv", action="store_true", help="export to CSV file")
    parser.add_argument("--pkl", action="store_true", help="export to pickle file")
    args = parser.parse_args()

    if (not args.csv) and (not args.pkl):
        raise Warning("prepare_links.py: set flags in order to export")

    conf = set_params(args.conf_file)
    param.ENABLE_DRAW_LINKS = True
    param.ENABLE_DRAW_NODES = True
    param.SET_NODES_LINKS_POLICY = 1

    prepare_links(not args.no_display, args.csv, args.pkl)

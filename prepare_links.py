import argparse
from datetime import datetime
import script.parameter as param
from particle_filter.script.log import Log
from script.map import Map
from script.parameter import set_params


def prepare_links() -> None:
    map = Map(Log(datetime(2000, 1, 1), datetime(2000, 1, 1)))    # whenever is fine

    map.export_links()

    map.draw_links()
    map.show(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="specify your config file", metavar="PATH_TO_CONFIG_FILE")

    set_params(parser.parse_args().config)
    param.SET_LINKS_POLICY = 1
    param.ENABLE_DRAW_LINKS = True

    prepare_links()

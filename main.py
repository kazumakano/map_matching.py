import argparse
from datetime import datetime, timedelta
from typing import Union
import numpy as np
import particle_filter.script.parameter as pf_param
import script.parameter as param
from particle_filter.script.log import Log
from particle_filter.script.resample import resample
from particle_filter.script.window import Window
from script.map import Map
from script.parameter import set_params
from script.particle import Particle
import particle_filter.script.utility as pf_util


def _set_main_params(conf: dict):
    global BEGIN, END, PARTICLE_NUM, INIT_POS, INIT_POS_SD, INIT_DIRECT, INIT_DIRECT_SD

    # particle filter
    BEGIN = datetime.strptime(conf["begin"], "%Y-%m-%d %H:%M:%S")
    END = datetime.strptime(conf["end"], "%Y-%m-%d %H:%M:%S")
    PARTICLE_NUM = conf["particle_num"]        # the number of particles
    INIT_POS = conf["init_pos"]                # initial position [pixel]
    INIT_POS_SD = conf["init_pos_sd"]          # standard deviation of position at initialization
    INIT_DIRECT = conf["init_direct"]          # initial direction [degree]
    INIT_DIRECT_SD = conf["init_direct_sd"]    # standard deviation of direction at initialization

    # map matching

def map_matching():
    log = Log(BEGIN, END)
    map = Map(log)

    if pf_param.ENABLE_DRAW_BEACONS:
        map.draw_beacons(True)
    if pf_param.ENABLE_SAVE_VIDEO:
        map.init_recorder()
    if param.ENABLE_DRAW_NODES:
        map.draw_nodes(True)

    particles = np.empty(PARTICLE_NUM, dtype=Particle)
    poses = np.empty((PARTICLE_NUM, 2), dtype=np.float16)    # positions
    directs = np.empty(PARTICLE_NUM, dtype=np.float16)       # directions
    for i in range(PARTICLE_NUM):
        poses[i] = np.random.normal(loc=INIT_POS, scale=INIT_POS_SD, size=2)
        directs[i] = np.random.normal(loc=INIT_DIRECT, scale=INIT_DIRECT_SD) % 360
    estim_pos = np.array(INIT_POS, dtype=np.float16)

    t = BEGIN
    while t <= END:
        print("main.py:", t.time())
        win = Window(log, map, t)

        for i in range(PARTICLE_NUM):
            particles[i] = Particle(map, poses[i], directs[i])
            particles[i].random_walk()
            particles[i].set_likelihood(map, win, estim_pos)

        poses, directs = resample(particles)

        if not pf_param.IS_LOST:
            map.draw_particles(particles, estim_pos)
            map.show()
            estim_pos = pf_util.get_likeliest_particle(particles).pos
        if pf_param.ENABLE_SAVE_VIDEO:
            map.record()

        t += timedelta(seconds=pf_param.WIN_STRIDE)

    print("main.py: reached end of log")
    map.show(0)
    if pf_param.ENABLE_SAVE_VIDEO:
        map.save_video()
    if pf_param.ENABLE_SAVE_IMG:
        map.save_img()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="specify your config file", metavar="PATH_TO_CONFIG_FILE")

    conf = set_params(parser.parse_args().config)
    _set_main_params(conf)
    map_matching()

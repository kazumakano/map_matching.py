import os.path as path
from datetime import datetime, timedelta
from typing import Any
import numpy as np
import particle_filter.script.parameter as pf_param
import script.parameter as param
import script.utility as util
from particle_filter.script.log import Log
from particle_filter.script.resample import resample
from particle_filter.script.window import Window
from script.map import Map
from script.particle import Particle


def _set_main_params(conf: dict[str, Any]) -> None:
    global BEGIN, END, LOG_FILE, INIT_DIRECT, INIT_DIRECT_SD, INIT_POS, INIT_POS_SD, PARTICLE_NUM

    BEGIN = datetime.strptime(conf["begin"], "%Y-%m-%d %H:%M:%S")
    END = datetime.strptime(conf["end"], "%Y-%m-%d %H:%M:%S")
    LOG_FILE = str(conf["log_file"])
    INIT_DIRECT = np.float16(conf["init_direct"])
    INIT_DIRECT_SD = np.float16(conf["init_direct_sd"])
    INIT_POS = np.array(conf["init_pos"], dtype=np.float16)
    INIT_POS_SD = np.float16(conf["init_pos_sd"])
    PARTICLE_NUM = np.int16(conf["particle_num"])

def map_matching() -> None:
    log = Log(BEGIN, END, path.join(pf_param.ROOT_DIR, "log/observed/", LOG_FILE))
    map = Map(log.mac_list)

    if pf_param.ENABLE_DRAW_BEACONS:
        map.draw_beacons(True)
    if param.ENABLE_DRAW_NODES:
        map.draw_nodes(True)
    if pf_param.ENABLE_SAVE_VIDEO:
        map.init_recorder()

    particles = np.empty(PARTICLE_NUM, dtype=Particle)
    poses = np.empty((PARTICLE_NUM, 2), dtype=np.float16)
    directs = np.empty(PARTICLE_NUM, dtype=np.float16)
    for i in range(PARTICLE_NUM):
        poses[i] = np.random.normal(loc=INIT_POS, scale=INIT_POS_SD, size=2).astype(np.float16)
        directs[i] = np.float16(np.random.normal(loc=INIT_DIRECT, scale=INIT_DIRECT_SD) % 360)
    estim_pos = np.array(INIT_POS, dtype=np.float16)

    t = BEGIN
    while t <= END:
        print("main.py:", t.time())
        win = Window(t, log, map.resolution)

        for i in range(PARTICLE_NUM):
            particles[i] = Particle(map.img.shape[:2], estim_pos, poses[i], directs[i])
            particles[i].random_walk()
            particles[i].set_likelihood(estim_pos, map, win.strength_weight_list, win.subject_dist_list)

        poses, directs = resample(particles)

        if not pf_param.IS_LOST:
            map.draw_particles(estim_pos, particles)
            map.show()
            estim_pos = util.estim_pos(particles)
        if pf_param.ENABLE_SAVE_VIDEO:
            map.record()

        t += timedelta(seconds=pf_param.WIN_STRIDE)

    print("main.py: reached end of log")
    if pf_param.ENABLE_SAVE_IMG:
        map.save_img()
    if pf_param.ENABLE_SAVE_VIDEO:
        map.save_video()
    map.show(0)

if __name__ == "__main__":
    import argparse
    from script.parameter import set_params

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--conf_file", help="specify config file", metavar="PATH_TO_CONF_FILE")

    _set_main_params(set_params(parser.parse_args().conf_file))

    map_matching()

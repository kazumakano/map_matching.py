import os.path as path
from datetime import datetime, timedelta
from typing import Any
import numpy as np
import particle_filter.script.parameter as pf_param
import particle_filter.script.utility as pf_util
import script.parameter as param
from particle_filter.script.log import Log
from particle_filter.script.resample import resample
from particle_filter.script.truth import Truth
from particle_filter.script.window import Window
from script.map import Map
from script.particle import Particle


def _set_main_params(conf: dict[str, Any]) -> None:
    global BEGIN, END, LOG_FILE, INIT_DIRECT, INIT_DIRECT_SD, INIT_POS, INIT_POS_SD, LOST_TJ_POLICY, PARTICLE_NUM, RESULT_DIR_NAME

    BEGIN = datetime.strptime(conf["begin"], "%Y-%m-%d %H:%M:%S")
    END = datetime.strptime(conf["end"], "%Y-%m-%d %H:%M:%S")
    LOG_FILE = str(conf["log_file"])
    INIT_DIRECT = np.float32(conf["init_direct"])
    INIT_DIRECT_SD = np.float32(conf["init_direct_sd"])
    INIT_POS = np.array(conf["init_pos"], dtype=np.float32)
    INIT_POS_SD = np.float32(conf["init_pos_sd"])
    LOST_TJ_POLICY = np.int8(conf["lost_tj_policy"])
    PARTICLE_NUM = np.int16(conf["particle_num"])
    RESULT_DIR_NAME = None if conf["result_dir_name"] is None else str(conf["result_dir_name"])

def map_matching(conf: dict[str, Any], enable_show: bool = True) -> None:
    log = Log(BEGIN, END, path.join(pf_param.ROOT_DIR, "log/observed/", LOG_FILE))
    result_dir = pf_util.make_result_dir(RESULT_DIR_NAME)
    map = Map(log.mac_list, result_dir)
    if pf_param.TRUTH_LOG_FILE is not None:
        truth = Truth(BEGIN, END, result_dir)

    if pf_param.ENABLE_DRAW_BEACONS:
        map.draw_beacons(True)
    if param.ENABLE_DRAW_LINKS:
        map.draw_links(True)
    if param.ENABLE_DRAW_NODES:
        map.draw_nodes(True)
    if pf_param.ENABLE_SAVE_VIDEO:
        map.init_recorder()

    particles = np.empty(PARTICLE_NUM, dtype=Particle)
    poses = np.empty((PARTICLE_NUM, 2), dtype=np.float32)
    directs = np.empty(PARTICLE_NUM, dtype=np.float32)
    for i in range(PARTICLE_NUM):
        poses[i] = np.random.normal(loc=INIT_POS, scale=INIT_POS_SD, size=2)
        directs[i] = np.random.normal(loc=INIT_DIRECT, scale=INIT_DIRECT_SD) % 360
    
    estim_pos = np.array(INIT_POS, dtype=np.float32)
    lost_ts_buf = []
    t = BEGIN
    while t <= END:
        print(f"main.py: {t.time()}")
        win = Window(t, log, map.resolution)

        for i in range(PARTICLE_NUM):
            particles[i] = Particle(map, poses[i], directs[i], estim_pos)
            particles[i].random_walk()
            particles[i].set_likelihood(estim_pos, map, win.strength_weight_list, win.subject_dist_list)

        poses, directs = resample(particles)

        match LOST_TJ_POLICY:
            case 1:
                if not pf_param.IS_LOST:
                    estim_pos = pf_util.estim_pos(particles)
                    map.draw_particles(estim_pos, particles)
                if pf_param.TRUTH_LOG_FILE is not None:
                    map.draw_truth(truth.update_err(t, estim_pos, map.resolution, pf_param.IS_LOST), True)

            case 2:
                if pf_param.TRUTH_LOG_FILE is not None and pf_param.IS_LOST:
                    last_estim_pos = estim_pos
                    lost_ts_buf.append(t)
                elif not pf_param.IS_LOST:
                    estim_pos = pf_util.estim_pos(particles)
                    map.draw_particles(estim_pos, particles)

                    if pf_param.TRUTH_LOG_FILE is not None:
                        buf_len = len(lost_ts_buf)
                        for i, lt in enumerate(lost_ts_buf):
                            lerped_pos = pf_util.get_lerped_pos(estim_pos, last_estim_pos, i, buf_len)
                            map.draw_lerped_pos(lerped_pos, True)
                            map.draw_truth(truth.update_err(lt, lerped_pos, map.resolution, True), True)
                        lost_ts_buf.clear()
                        map.draw_truth(truth.update_err(t, estim_pos, map.resolution, False), True)

        if pf_param.ENABLE_SAVE_VIDEO:
            map.record()
        if enable_show:
            map.show()

        t += timedelta(seconds=pf_param.WIN_STRIDE)

    print("main.py: reached end of log")
    if pf_param.ENABLE_SAVE_IMG:
        map.save_img()
    if pf_param.ENABLE_SAVE_VIDEO:
        map.save_video()
    if pf_param.ENABLE_WRITE_CONF:
        pf_util.write_conf(conf, result_dir)
    if pf_param.TRUTH_LOG_FILE is not None:
        truth.export_err()
    if enable_show:
        map.show(0)

if __name__ == "__main__":
    import argparse
    from script.parameter import set_params

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--conf_file", help="specify config file", metavar="PATH_TO_CONF_FILE")
    parser.add_argument("--no_display", action="store_true", help="run without display")
    args = parser.parse_args()

    conf = set_params(args.conf_file)
    _set_main_params(conf)

    map_matching(conf, not args.no_display)

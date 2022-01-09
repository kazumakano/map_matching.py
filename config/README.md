# config

This is directory for config files.
Put your config files here.
You can customize following parameters:
| Key                  | Description                                          | Notes                                                                                                   | Type          |
| ---                  | ---                                                  | ---                                                                                                     | ---           |
| begin                | begin datetime of RSSI log                           | must be like 'yyyy-mm-dd hh:mm:ss'                                                                      | `str`         |
| end                  | end datetime of RSSI log                             | must be like 'yyyy-mm-dd hh:mm:ss'                                                                      | `str`         |
| log_file             | RSSI log file                                        |                                                                                                         | `str`         |
| init_direct          | initial direction [degree]                           |                                                                                                         | `float`       |
| init_direct_sd       | standard deviation of direction at initialization    |                                                                                                         | `float`       |
| init_pos             | initial position [pixel]                             |                                                                                                         | `list[float]` |
| init_pos_sd          | standard deviation of position at initialization     |                                                                                                         | `float`       |
| particle_num         | number of particles                                  |                                                                                                         | `int`         |
|                      |                                                      |                                                                                                         |               |
| win_size             | size of sliding window [second]                      |                                                                                                         | `float`       |
|                      |                                                      |                                                                                                         |               |
| enable_clear_map     | clear map image at each step or not                  |                                                                                                         | `bool`        |
| enable_draw_beacons  | draw beacon positions or not                         |                                                                                                         | `bool`        |
| enable_save_img      | capture image or not                                 |                                                                                                         | `bool`        |
| enable_save_video    | record video or not                                  |                                                                                                         | `bool`        |
| frame_rate           | frame rate of video [FPS]                            | synchronized with real speed if 0                                                                       | `float`       |
| map_conf_file        | map config file                                      |                                                                                                         | `str`         |
| map_img_file         | map image file                                       |                                                                                                         | `str`         |
| map_show_policy      | policy to show particles and trajectory              | 1: all, 2: all & likeliest, 3: all & center, 4: likeliest, 5: center, 6: likeliest link, 7: center link | `int`         |
| result_file_name     | file name of image and video                         | auto generated if unspecified                                                                           | `str \| None` |
| win_stride           | stride width of sliding window [second]              |                                                                                                         | `float`       |
|                      |                                                      |                                                                                                         |               |
| direct_sd            | standard deviation of direction at walk              |                                                                                                         | `float`       |
| max_particle_stride  | maximum stride width of particles in a step [pixel]  |                                                                                                         | `float`       |
|                      |                                                      |                                                                                                         |               |
| lost_resample_policy | policy to resample particles when lost               | 1: reset, 2: use last particles                                                                         | `int`         |
|                      |                                                      |                                                                                                         |               |
| enable_truth         | enable ground truth or not                           |                                                                                                         | `bool`        |
|                      |                                                      |                                                                                                         |               |
| dist_sd              | standard deviation of distance gap                   |                                                                                                         | `float`       |
| el_correction        | correction term for difference in elevation          |                                                                                                         | `float`       |
| neg_weight_coef      | coefficient for negative weight                      | not consider undetected beacons if 0                                                                    | `float`       |
| propag_coef          | propagation coefficient                              | takes 2 in ideal environment                                                                            | `float`       |
|                      |                                                      |                                                                                                         |               |
| win_policy           | policy to get representative RSSI value in window    | 1: maximum, 2: latest                                                                                   | `int`         |
|                      |                                                      |                                                                                                         |               |
| estim_pos_policy     | policy to estimate subject's position                | 1: position of likeliest particle, 2: center of gravity of perticles                                    | `int`         |
|                      |                                                      |                                                                                                         |               |
| enable_draw_links    | draw links or not                                    |                                                                                                         | `bool`        |
| enable_draw_nodes    | draw nodes or not                                    |                                                                                                         | `bool`        |
| max_link_len         | maximum cost between 2 nodes to be linked            |                                                                                                         | `float`       |
| nodes_show_policy    | policy to show nodes                                 | 1: circle, 2: node name                                                                                 | `int`         |
| set_links_policy     | policy to set links                                  | 1: load irregular from csv and search regular, 2: load all from CSV, 3: load all from pickle            | `int`         |
|                      |                                                      |                                                                                                         |               |
| match_weight_policy  | policy to calculate likelihood with map match weight | 1, 2: multiply match weight between nearest node and last linked node, last node 3: pass or cut off     | `int`         |
| rand_pos_range       | range from last position at initialization [pixel]   | whole map if 0                                                                                          | `float`       |

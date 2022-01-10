# map_matching.py
This is Python module to estimate subject's position with particle filter and map matching.

## Usage
### main.py
You can run with following command.
You can specify config file with `--conf_file` flag.
`config/default.yaml` will be used if unspecified.
```sh
python main.py [--conf_file PATH_TO_CONF_FILE]
```

### prepare_links.py
You can prepare link file in advance.
Then, you can reuse it when creating instance of `Map` class instead of constructing it.
CSV and pickle are supported.

You can run link preparer with following command.
You can specify config file with `--conf_file` flag.
`config/default.yaml` will be used if unspecified.
Set `--csv` flag and `--pkl` flag to set format.
```sh
python prepare_links.py [--conf_file PATH_TO_CONF_FILE] [--csv] [--pkl]
```

### visualize_map.py
You can visualize map with following command.
You can specify config file with `--conf_file` flag.
`config/default.yaml` will be used if unspecified.
Set `--beacon` flag, `--node` flag, and `--link` flag to visualize them.
Set `--save` flag to save image.
```sh
python visualize_map.py [--conf_file PATH_TO_CONF_FILE] [--beacon] [--node] [--link] [--save]
```

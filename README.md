# map_matching.py
This is Python module to estimate subject position with particle filter and map matching.

## Usage
### main.py
You can run with following command.
You can specify config file with `--config` flag.
`config/default.yaml` will be used if no config file is specified.
```sh
python main.py [--config PATH_TO_CONFIG_FILE]
```

### prepare_links.py
You can prepare link file in advance.
Then, you can reuse it when creating instance of Map class instead of constructing it.
CSV and pickle are supported.

You can run preparer with following command.
You can specify config file with `--config` flag.
`config/default.yaml` will be used if no config file is specified.
Set `--csv` flag and `--pkl` flag to specify format.
```sh
python main.py [--config PATH_TO_CONFIG_FILE] [--csv] [--pkl]
```

### visualize_map.py
You can visualize map with following command.

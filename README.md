# Nanome - Align Tool

Override the 3D local coordinate space of a complex to be relative to a reference complex

## Dependencies

[Docker](https://docs.docker.com/get-docker/)


## Usage

To run Align Tool in a Docker container:

```sh
$ cd docker
$ ./build.sh
$ ./deploy.sh -a <plugin_server_address> [optional args]
```

## Development

To run Align Tool with autoreload:

```sh
$ python -m pip install -r requirements.txt
$ python run.py -r -a <plugin_server_address> [optional args]
```

## License

MIT

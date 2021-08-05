# Nanome - Local Align

Align complex's position to be relative to another complex

## Dependencies

[Docker](https://docs.docker.com/get-docker/)

## Usage

To run Local Align in a Docker container:

```sh
$ cd docker
$ ./build.sh
$ ./deploy.sh -a <plugin_server_address> [optional args]
```

## Development

To run Local Align with autoreload:

```sh
$ python3 -m pip install -r requirements.txt
$ python3 run.py -r -a <plugin_server_address> [optional args]
```

## License

MIT

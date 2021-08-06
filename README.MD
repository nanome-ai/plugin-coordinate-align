# Nanome - Align Tool

Align complex's position to be relative to another complex.

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

To run Align Tool with autoreload:

```sh
$ python3 -m pip install -r requirements.txt
$ python3 run.py -r -a <plugin_server_address> [optional args]
```

### Devcontainer Environment Variables.
To connect your vscode devcontainer to NTS, populate NTS_HOST and NTS_PORT in `.devcontainer/devcontainer.env`
This will allow the launch configs to quickly connect your plugin to the right environment

## License

MIT

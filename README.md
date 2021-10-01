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

### Using VSCode.
By default we provide a devcontainer with launch configs for easily debugging the plugin.

#### Setting devcontainer environment variables
Create a file .devcontainer/devcontainer.env using the sample, and set your NTS variables

These values will then set the environment variables for your devcontainer, and allow launch configs to work
```sh
cp .devcontainer/devcontainer.env.sample .devcontainer/devcontainer.env
```

## License

MIT

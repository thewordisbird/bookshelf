#! /usr/bin/env python

import os
import json
import signal
import subprocess
import click


def setenv(variable, default):
    # check if an enviornmental variable exists.
    # If not set the variable to the default.
    os.environ[variable] = os.getenv(variable, default)


# Use development config as default
setenv("APPLICATION_CONFIG", "development")

# Set globals
APPLICATION_CONFIG_PATH = "config"
DOCKER_PATH = "docker"


def app_config_file(config):
    return os.path.join(APPLICATION_CONFIG_PATH, f"{config}.json")


def docker_compose_file(config):
    return os.path.join(DOCKER_PATH, f"{config}.yml")


def dockerfile_file(config):
    return os.path.join(DOCKER_PATH, f"web/Dockerfile.{config}")


def configure_app(config):
    # Set configuration variables as enviornmental variables to be used
    # for image construction, and container injection.
    with open(app_config_file(config)) as f:
        config_data = json.load(f)

    config_data = dict((i["name"], i["value"]) for i in config_data)

    for key, value in config_data.items():
        setenv(key, value)


@click.group()
def cli():
    pass


@cli.command(context_settings={"ignore_unknown_options": True})
@click.argument("subcommand", nargs=-1, type=click.Path())
def flask(subcommand):
    """Use flask cmd to run flask server or flask shell.

    Args:
        subcommand (str): flask command line option. Valid options:
            [run]: runs local development server.
            [shell]: runs flask shell.

    Example:
        Run the local flask server:
            ./manage.py flask run

    For more information on flask command line options:
        https://flask.palletsprojects.com/en/1.1.x/cli/

    """
    configure_app(os.getenv("APPLICATION_CONFIG"))

    cmdline = ["flask"] + list(subcommand)

    try:
        p = subprocess.Popen(cmdline)
        p.wait()
    except KeyboardInterrupt:
        p.send_signal(signal.SIGINT)
        p.wait()


def docker_compose_cmdline(commands_string=None):
    # Generates docker-compose command line command formatted as list
    # to be consumed by subprocess call.
    config = os.getenv("APPLICATION_CONFIG")
    configure_app(config)

    compose_file = docker_compose_file(config)

    if not os.path.isfile(compose_file):
        raise ValueError(f"The file {compose_file} does not exist")

    command_line = [
        "docker-compose",
        "-p",
        config,
        "-f",
        compose_file,
    ]

    if commands_string:
        command_line.extend(commands_string.split(" "))

    return command_line


@cli.command(context_settings={"ignore_unknown_options": True})
@click.argument("subcommand", nargs=-1, type=click.Path())
def compose(subcommand):
    """Run docker-compose command line commands.

    Args:
        subcommand (str): Valid docker-compose sub commands. Common usage:
            ['build']: Builds docker image from docker-compose file.
            ['up']: Run container. If image doesn't exist, build image first.
            ['down']: Stop container.

    Example:
        Run container in detached mode:
            ./manage.py compose up -d

    For more information on docker-compose options:
        https://docs.docker.com/compose/

    """
    cmdline = docker_compose_cmdline() + list(subcommand)

    try:
        p = subprocess.Popen(cmdline)
        p.wait()
    except KeyboardInterrupt:
        p.send_signal(signal.SIGINT)
        p.wait()


@cli.command()
@click.argument("filenames", nargs=-1)
def test(filenames):
    """Run pytests on application.

    Builds a docker image if not already built based on the testing
    configuration. Spins up a container from the testing image. The container
    must contain the pytest run command. When the tests are complete the
    container is torn down.

    Args:
        filename (str): Specific file to test. Not implemented

    TODO:
        Accept pytest commands to control testing. Currently the pytest
        command is set in the testing.yml file.

    """
    os.environ["APPLICATION_CONFIG"] = "testing"

    cmdline = docker_compose_cmdline("up")
    subprocess.call(cmdline)

    cmdline = docker_compose_cmdline("down")
    subprocess.call(cmdline)


def get_build_args(config):
    with open(app_config_file(config)) as f:
        config_data = json.load(f)

    return dict((i["name"], i["value"]) for i in config_data)


def docker_build_cmdline():
    # Generates docker build command line command formatted as list
    # to be consumed by subprocess call.
    config = os.getenv("APPLICATION_CONFIG")
    build_args = get_build_args(config)

    dockerfile = dockerfile_file(config)

    if not os.path.isfile(dockerfile):
        raise ValueError(f"The file {dockerfile} does not exist")

    command_line = ["docker", "build"]

    # Add build-args to image build
    for key, value in build_args.items():
        command_line.extend(["--build-arg", f"{key}={value}"])

    # Point to docker file:
    command_line.extend(["-f", dockerfile])

    # Tag file with container registry url
    command_line.extend(
        ["-t", f"gcr.io/{os.environ.get('PROJECT_ID')}/{os.environ.get('PROJECT_ID')}"]
    )

    # Path to working directory,
    command_line.append(".")

    return command_line


@cli.command()
def pushimage():
    """Build and push production image to GCP container registry.

    Image is built and tagged 'gcr.io/<PROJECT_ID>/<PROJECT_ID>'. Once
    built it is pushed to GCP container registry.

    Example:
        ./manage.py pushimage

    Deployment is not yet automated.
    To deploy on GCP console:
        Container Registry -> Select Image -> Deploy

    To depoly using GCP CLI:
        $ gcloud run deploy --image gcr.io/<PROJECT_ID>/<PROJECT_ID> \
            --platform managed

    """
    # Set enviornment variables to be pushed to the image
    os.environ["APPLICATION_CONFIG"] = "production"
    configure_app(os.getenv("APPLICATION_CONFIG"))

    # Build a docker image with the data
    cmdline = docker_build_cmdline()
    subprocess.call(cmdline)

    # Push to gcp container registry
    cmdline = [
        "docker",
        "push",
        f"gcr.io/{os.environ.get('PROJECT_ID')}/{os.environ.get('PROJECT_ID')}",
    ]
    subprocess.call(cmdline)

    click.echo(
        "Container Pushed to GCP Container Registry. Ready to deploy to Cloud Run!"
    )


if __name__ == "__main__":
    cli()

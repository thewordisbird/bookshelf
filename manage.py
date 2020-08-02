#! /usr/bin/env python

import os
import json
import signal
import subprocess
import time

import click

# Ensure an environment variable exists and has a value
def setenv(variable, default):
    os.environ[variable] = os.getenv(variable, default)

setenv("APPLICATION_CONFIG", "development")

APPLICATION_CONFIG_PATH = "config"
DOCKER_PATH = "docker"

def app_config_file(config):
    return os.path.join(APPLICATION_CONFIG_PATH, f"{config}.json")

def docker_compose_file(config):
    return os.path.join(DOCKER_PATH, f"{config}.yml")

def dockerfile_file(config):
    return os.path.join(DOCKER_PATH, f"web/Dockerfile.{config}")

def configure_app(config):
    # Read configuration from the relative JSON file
    with open(app_config_file(config)) as f:
        config_data = json.load(f)

    # Convert config to python dict
    config_data = dict((i["name"], i["value"]) for i in config_data)

    for key, value in config_data.items():
        #print(f'setting env var: {k} = {v}')
        setenv(key, value)


@click.group()
def cli():
    pass


@cli.command(context_settings={"ignore_unknown_options": True})
@click.argument("subcommand", nargs=-1, type=click.Path())
def flask(subcommand):
    configure_app(os.getenv("APPLICATION_CONFIG"))

    cmdline = ["flask"] + list(subcommand)


    try:
        p = subprocess.Popen(cmdline)
        p.wait()
    except KeyboardInterrupt:
        p.send_signal(signal.SIGINT)
        p.wait()


def docker_compose_cmdline(commands_string=None):
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
    os.environ["APPLICATION_CONFIG"] = "testing"
    #configure_app(os.getenv("APPLICATION_CONFIG"))
    
    cmdline = docker_compose_cmdline("up")
    subprocess.call(cmdline)

    cmdline = docker_compose_cmdline("down")
    subprocess.call(cmdline)

def get_build_args(config):
    with open(app_config_file(config)) as f:
        config_data = json.load(f)

    return dict((i["name"], i["value"]) for i in config_data)

def docker_build_cmdline():
    """Build a docker image to be pushed to gcp"""
    config = os.getenv("APPLICATION_CONFIG")
    build_args = get_build_args(config)

    dockerfile = dockerfile_file(config)

    if not os.path.isfile(dockerfile):
        raise ValueError(f"The file {compose_file} does not exist")

    command_line = ['docker', 'build']

    # Add build-args to image build
    for key, value in build_args.items():
        command_line.extend(["--build-arg", f"{key}={value}"])

    # Point to docker file:
    command_line.extend(["-f", dockerfile])

    # Tag file with container registry url
    command_line.extend(["-t", f"gcr.io/{os.environ.get('PROJECT_ID')}/{os.environ.get('PROJECT_ID')}"])

    # Path to working directory,
    command_line.append('.')

    # if commands_string:
    #     command_line.extend(commands_string.split(" "))

    return command_line



@cli.command()
def pushimage():
    """Build and push production image to GCP container registry."""
    # Set enviornment variables to be pushed to the image
    os.environ["APPLICATION_CONFIG"] = 'production'
    configure_app(os.getenv("APPLICATION_CONFIG"))
    
    # Build a docker image with the data
    cmdline = docker_build_cmdline()
    #print(cmdline)
    subprocess.call(cmdline)

    # push to gcp container registry
    cmdline = ['docker', 'push', f"gcr.io/{os.environ.get('PROJECT_ID')}/{os.environ.get('PROJECT_ID')}"] 
    subprocess.call(cmdline)

    click.echo('Container Pushed to GCP Container Registry. Ready to deploy to Cloud Run!')
if __name__ == "__main__":
    cli()

"""
docker build -f ./docker/web/Dockerfile.production -t gcr.io/<PROJECT_ID>/<PROJECT_ID> .

docker build --build-arg FLASK_ENV=${FLASK_ENV} --build-arg FLASK_CONFIG=${FLASK_CONFIG} --build-arg GOOGLE_APPLICATION_CREDENTIALS=${GOOGLE_APPLICATION_CREDENTIALS} --build-argPROJECT_ID=${PROJECT_ID}  -f ./docker/web/Dockerfile.production -t gcr.io/<PROJECT_ID>/<PROJECT_ID> .

docker build --build-arg FLASK_ENV=production --build-arg FLASK_CONFIG=production --build-arg GOOGLE_APPLICATION_CREDENTIALS=./.keys/bookshelf-firebase-api.json --build-arg PROJECT_ID="bookshelf-89de1"  -f ./docker/web/Dockerfile.production -t gcr.io/<PROJECT_ID>/<PROJECT_ID> .

# This works. Need to look at port passthru
docker build --build-arg FLASK_ENV=production --build-arg FLASK_CONFIG=production --build-arg GOOGLE_APPLICATION_CREDENTIALS=./.keys/bookshelf-firebase-api.json --build-arg PROJECT_ID="bookshelf-89de1"  -f ./docker/web/Dockerfile.production -t bookshelf .
"""
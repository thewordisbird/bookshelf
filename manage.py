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
    #print(os.getenv('APPLICATION_CONFIG'))

setenv("APPLICATION_CONFIG", "development")

APPLICATION_CONFIG_PATH = "config"
DOCKER_PATH = "docker"

def app_config_file(config):
    return os.path.join(APPLICATION_CONFIG_PATH, f"{config}.json")

def docker_compose_file(config):
    return os.path.join(DOCKER_PATH, f"{config}.yml")

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
    configure_app(os.getenv("APPLICATION_CONFIG"))

    cmdline = docker_compose_cmdline("up")
    subprocess.call(cmdline)

    # TODO: DB Logging for firestore
    # cmdline = docker_compose_cmdline(os.getenv("APPLICATION_CONFIG")) + ["logs", "db"]
    # logs = subprocess.check_output(cmdline)
    # while "ready to accept connections" not in logs.decode("utf-8"):
    #     time.sleep(0.1)
    #     logs = subprocess.check_output(cmdline)

    # cmdline = ["pytest", "-svv", "--cov=application", "--cov-report=term-missing"]
    # cmdline.extend(filenames)
    # subprocess.call(cmdline)

    # cmdline = docker_compose_cmdline("down")
    # subprocess.call(cmdline)


if __name__ == "__main__":
    cli()
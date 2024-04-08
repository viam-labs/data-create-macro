import asyncio
import random
from viam.app.viam_client import ViamClient, AppClient
from viam.rpc.dial import DialOptions
from random_word import RandomWords
from viam.proto.app import SharedSecret
import json
import os
from applescript import tell
import subprocess
from typing import Tuple
import webbrowser
from time import sleep
import argparse
import requests
from config import Config
from threading import Thread

VIAM_PATH = "~/.viam/capture"


async def connect(api_key_id: str, api_key: str, is_staging: bool) -> ViamClient:
    dial_options = DialOptions.with_api_key(api_key, api_key_id)
    if is_staging:
        client = await ViamClient.create_from_dial_options(
            dial_options, app_url="app.viam.dev"
        )
    else:
        client = await ViamClient.create_from_dial_options(dial_options)

    return client


# if needed, pick a random location from all in the org
async def pick_location_id(fleet: AppClient) -> Tuple[str, str]:
    locations = await fleet.list_locations()
    selected_location = random.choice(locations)
    return (selected_location.id, selected_location.name)


async def get_location_name(fleet: AppClient, location_id) -> str:
    locations = await fleet.list_locations()
    for location in locations:
        if location.id == location_id:
            return location.name
    raise ValueError(f"Could not find location matching id {location_id}")


def generate_machine_name() -> str:
    r = RandomWords()
    return f"{r.get_random_word()}{r.get_random_word()}"


def generate_robot_config(robot_id: str, num_binary:int, num_tabular:int, frequency:int) -> map:
        config = Config(robot_id)
        for i in range(num_binary):
            config.add_camera(frequency=frequency)

        methods = [
            config.add_arm,
            config.add_encoder,
            config.add_gantry,
            config.add_motor,
            config.add_movement_sensor,
            config.add_power_sensor,
            config.add_sensor,
            config.add_servo,
        ]
        for i in range(num_tabular):
            method = random.choice(methods)
            method(frequency=frequency)

        return config.config


def get_corresponding_secret_id(secrets: list[SharedSecret], target_secret: str) -> str:
    for secret in secrets:
        if secret.secret == target_secret:
            return secret.id


def generate_viam_json(secert_id: str, secert: str, url: str, robot_name: str):
    config = {
        "cloud": {
            "app_address": f"{url}:443",
            "id": secert_id,
            "secret": secert,
        }
    }
    filename = f"configs/viam-{robot_name}-main.json"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as f:
        f.write(json.dumps(config))
        print(f"Config written to: {os.path.abspath(filename)}")
        return os.path.abspath(filename)


def start_robot(filepath: str):
    command = f"viam-server -config {filepath}"
    print(f"Command to start robot: \n{command}\n")
    tell.app("Terminal", 'do script "' + command + '"')


def log_in_cli(is_staging: bool):
    login_command = (
        f"viam --base-url '{'app.viam.dev' if is_staging else 'app.viam.com'}' login"
    )
    output = subprocess.getoutput(login_command)
    if "error" in output.lower():
        process = subprocess.Popen("viam logout", shell=True, stdout=subprocess.PIPE)
        process.wait()
        output = subprocess.getoutput(login_command)
    if "logged in" not in output.lower():
        print("failed to log into CLI, exiting")
        exit()


def get_org_id_from_cli(org_name: str, orglist: str) -> str:
    org_name_cleaned = org_name.replace(" ", "").lower()
    lines = orglist.splitlines()
    del lines[0:2]
    for line in lines:
        name = line.split("(")[0][1:].replace(" ", "").lower()
        if name == org_name_cleaned:
            return (
                line.replace("/t", "")
                .replace("/", " ")
                .split("(")[1][4:-1]
                .replace(")", "")
            )
    raise ValueError(f"Could not find org matching name {org_name}")


def get_apikey_and_id_from_cli(input: str) -> Tuple[str, str]:
    lines = input.splitlines()
    id_raw = lines[3]
    value_raw = lines[4]
    return (id_raw[8:], value_raw[11:])


def generate_api_key(org_name: str) -> Tuple[str, str]:
    output = subprocess.getoutput("viam organizations list")
    org_id = get_org_id_from_cli(org_name, output)
    api_key_raw = subprocess.getoutput(
        f"viam organizations api-key create --org-id {org_id}"
    )
    return get_apikey_and_id_from_cli(api_key_raw)


# Add http to url if not provided
def validate_url(url: str) -> str:
    if "https://" not in url:
        return f"https://{url}"
    return url


def ping_temp_env(url: str) -> Thread:
    thread = Thread(target=ping_temp_env_helper, args=(url,))
    thread.start()
    return thread


def ping_temp_env_helper(url: str):
    requests.get(url)
    sleep(7)


async def main():
    parser = argparse.ArgumentParser(description="Big Data Macro")
    parser.add_argument("-url", type=str, help="viam url", required=True)
    parser.add_argument("-org", type=str, help="org to add robot to", required=True)
    parser.add_argument("-l", "--location_id", type=str, help="location id")
    parser.add_argument("-m", "--machine_name", type=str, help="robot name")
    parser.add_argument(
        "-f", "--frequency", type=int, help="capture frequency", default=1
    )
    parser.add_argument(
        "-b", "--binary_count", type=int, help="number of binary sources", default=1
    )
    parser.add_argument(
        "-t", "--tabular_count", type=int, help="number of tabular sources", default=1
    )

    args = parser.parse_args()
    url = validate_url(args.url)
    org_name = args.org
    location_id = args.location_id
    machine_name = args.machine_name
    frequency = args.frequency
    num_binary = args.binary_count
    num_tabular = args.tabular_count

    is_staging = ".com" not in url
    is_temp_env = "appmain" in url
    ping_thread = None
    if is_temp_env:
        ping_thread = ping_temp_env(url)

    log_in_cli(is_staging)
    api_key_id, api_key = generate_api_key(org_name)

    viam_client = await connect(f"{api_key_id.strip()}", api_key, is_staging)
    fleet = viam_client.app_client
    location_name = ""
    if not location_id:
        location_id, location_name = await pick_location_id(fleet)
    else:
        # This is slow
        location_name = await get_location_name(fleet, location_id)
    print(f"Adding robot to location: {location_name}")

    if not machine_name:
        machine_name = generate_machine_name()
    print(f"Generated machine name: {machine_name}")
    robot_id = await fleet.new_robot(name=machine_name, location_id=location_id)

    robot_parts = await fleet.get_robot_parts(robot_id=robot_id)
    robot_part = robot_parts[0]
    secret = robot_part.secret

    # create config with data and update robot part
    config = generate_robot_config(robot_id, num_binary, num_tabular, frequency)
    await fleet.update_robot_part(robot_part.id, robot_part.name, config)
    # generate viam-{robot}-main.json to run on terminal
    filepath = generate_viam_json(robot_part.id, secret, url, robot_name=machine_name)

    webbrowser.open(f"{url}/robot?id={robot_id}&tab=config", new=2, autoraise=True)
    viam_client.close()

    # Delay on temp envs since it might take some time for them to be ready to serve robot traffic
    if is_temp_env and ping_thread:
        ping_thread.join()
    start_robot(filepath)


if __name__ == "__main__":
    asyncio.run(main())

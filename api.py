import asyncio
import random
from viam.app.viam_client import ViamClient, AppClient
from viam.rpc.dial import Credentials, DialOptions
from random_word import RandomWords
from viam.app.app_client import RobotPart
from viam.proto.app import SharedSecret
import json
import os
from applescript import tell
from dotenv import load_dotenv
import subprocess
from typing import Tuple
import webbrowser

VIAM_PATH = "~/.viam/capture"


async def connect(api_key_id:str, api_key:str, is_staging:bool) -> ViamClient:
    dial_options = DialOptions.with_api_key(
        api_key, api_key_id
    )
    if is_staging:
        client = await ViamClient.create_from_dial_options(dial_options, app_url='app.viam.dev')
    else:
        client = await ViamClient.create_from_dial_options(dial_options)

    return client


# if needed, pick a random location from all in the org
async def pick_location_id(fleet: AppClient) -> str:
    locations = await fleet.list_locations()
    return random.choice(locations).id


def generate_machine_name() -> str:
    r = RandomWords()
    return f"{r.get_random_word()}{r.get_random_word()}"


def generate_robot_config(robot_id: str) -> map:
    with open("template_config.json") as f:
        data = json.load(f)
        data["services"][0]["attributes"]["capture_dir"] = f"{VIAM_PATH}/{robot_id}"
        return data


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
        print(os.path.abspath(filename))
        return os.path.abspath(filename)


def start_robot(filepath: str):
    tell.app("Terminal", 'do script "' + f"viam-server -config {filepath}" + '"')

def log_in_cli(is_staging:bool):
    login_command = f"viam --base-url '{'app.viam.dev' if is_staging else 'app.viam.com'}' login"
    output = subprocess.getoutput(login_command)
    if 'error' in output.lower():
        process = subprocess.Popen('viam logout', shell=True, stdout=subprocess.PIPE)
        process.wait()
        output = subprocess.getoutput(login_command)
    if 'logged in' not in output.lower():
        print("failed to log into CLI, exiting")
        exit()

def get_org_id_from_cli(org_name:str, orglist:str) -> str:
    org_name_cleaned = org_name.replace(' ','').lower()
    lines = orglist.splitlines()
    del lines[0:2]
    for line in lines:
        name = line.split('(')[0][1:].replace(' ','').lower()
        if name == org_name_cleaned:
            return line.replace('/t', '').replace('/', ' ').split('(')[1][4:-1]
    raise ValueError('Could not find org matching name')
   
def get_apikey_and_id_from_cli(input: str) -> Tuple[str, str]:
    lines = input.splitlines()
    id_raw = lines[3]
    value_raw = lines[4]
    return (id_raw[8:], value_raw[11:])

def generate_api_key(org_name:str) -> Tuple[str, str]:
    output = subprocess.getoutput("viam organizations list")
    org_id = get_org_id_from_cli(org_name, output)
    api_key_raw = subprocess.getoutput(f"viam organizations api-key create --org-id {org_id}")
    return get_apikey_and_id_from_cli(api_key_raw)
            


async def main():
    load_dotenv()
    url = os.getenv('URL')
    org_name = os.getenv('ORG_NAME')
    is_staging = '.com' not in url
    print(is_staging)
    log_in_cli(is_staging)
    api_key_id, api_key = generate_api_key(org_name)

    viam_client = await connect(f'{api_key_id.strip()}', api_key, is_staging)
    fleet = viam_client.app_client
    location_id = await pick_location_id(fleet)

    machine_name = generate_machine_name()
    print(machine_name)
    robot_id = await fleet.new_robot(name=machine_name, location_id=location_id)

    robot_parts = await fleet.get_robot_parts(robot_id=robot_id)
    robot_part = robot_parts[0]
    secret = robot_part.secret
    

    # create config with data and update robot part
    config = generate_robot_config(robot_id=robot_id)
    await fleet.update_robot_part(robot_part.id, robot_part.name, config)
    # generate viam-{robot}-main.json to run on terminal
    filepath = generate_viam_json(
        secert_id=robot_part.id, secert=secret, url=url, robot_name=machine_name
    )
    start_robot(filepath)
    webbrowser.open(f"{url}/robot?id={robot_id}&tab=config", new = 2, autoraise = True)
    # clean up
    viam_client.close()


if __name__ == "__main__":
    asyncio.run(main())

# TODO: start sessions and end them.
import podman
from podman import PodmanClient

IMAGE="ubuntu:24.04"
sessions={}

def start_session(user_id: str):
    client= PodmanClient.from_env()
    container = client.containers.create(IMAGE, detach=True)
    container.start()
    sessions[user_id] = container

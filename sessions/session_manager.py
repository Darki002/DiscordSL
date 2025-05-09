# TODO: start sessions and end them.
from podman import PodmanClient

from sessions.Session import Session

IMAGE="ubuntu:24.04"

sessions={}


def start_session(user_id: str, username: str):
    client= PodmanClient.from_env()
    container = client.containers.create(IMAGE, detach=True, name=username)
    container.start()

    sessions[user_id] = Session(user_id, container)
    return container.name


def get_session(user_id: str):
    return sessions[user_id]
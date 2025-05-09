from podman import PodmanClient

from sessions.Session import Session
from sessions.SessionError import MaxSessionsError, UserHasSessionError, SessionError

IMAGE="ubuntu:24.04"
MAX_SESSIONS=5

sessions={}


def start_session(user_id: str, username: str) -> str | SessionError:
    if len(sessions) >= MAX_SESSIONS:
        return MaxSessionsError()

    if sessions.get(user_id) is not None:
        return UserHasSessionError()

    client= PodmanClient.from_env()
    container = client.containers.create(IMAGE, detach=True, name=username)
    container.start()

    sessions[user_id] = Session(user_id, container, _remove_container)
    return container.short_id

def stop_session(user_id: str):
    get_session(user_id).stop()

def get_session(user_id: str) -> Session :
    return sessions.get(user_id)


def _remove_container(user_id: str):
    sessions.pop(user_id)
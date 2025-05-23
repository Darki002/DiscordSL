from podman import PodmanClient
from podman.errors import ImageNotFound, APIError

from sessions.Session import Session
from sessions.SessionError import MaxSessionsError, UserHasSessionError, SessionError

IMAGE="ubuntu:24.04"
MAX_SESSIONS=5

sessions={}


def start_session(user_id: str, username: str) -> Session | SessionError:
    if len(sessions) >= MAX_SESSIONS:
        return MaxSessionsError()

    if sessions.get(user_id) is not None:
        return UserHasSessionError()

    try:
        client = PodmanClient.from_env()
        container = client.containers.create(IMAGE, detach=True, name=username)
        container.start()

        sessions[user_id] = Session(user_id, container, _remove_container)
        return sessions[user_id]
    except ImageNotFound:
        return SessionError()
    except APIError:
        return SessionError()


def stop_session(user_id: str):
    get_session(user_id).stop()


def get_session(user_id: str) -> Session :
    return sessions.get(user_id)


def get_container_status(user_id: str) -> str:
    session = get_session(user_id)
    if session:
        return session.status()
    return "unknown"


def _remove_container(user_id: str):
    sessions.pop(user_id)

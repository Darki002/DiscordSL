# TODO: class for Session that manages connection to podman
import threading

from podman.domain.containers import Container

SHUTDOWN_TIME_IN_HOURS=1
SHUTDOWN_TIME=SHUTDOWN_TIME_IN_HOURS*60*60


class Session:
    def __init__(self, user_id: str, container: Container):
        self.user_id: str = user_id
        self.container: Container = container
        self.timer = threading.Timer(SHUTDOWN_TIME, self.stop)


    def stop(self):
        self.timer.cancel()
        self.container.stop()
        self.container.remove(v=True)
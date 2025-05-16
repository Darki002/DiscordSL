import threading

from podman.domain.containers import Container

SHUTDOWN_TIME_IN_HOURS=1
SHUTDOWN_TIME=SHUTDOWN_TIME_IN_HOURS*60*60


class Session:
    def __init__(self, user_id: str, container: Container, on_stop) -> None:
        self.user_id: str = user_id
        self.container: Container = container
        self.on_stop = on_stop
        self.timer = threading.Timer(SHUTDOWN_TIME, self.stop)


    def stop(self):
        self.timer.cancel()
        self.container.stop()
        self.container.remove(v=True)
        self.on_stop(self.user_id)

    def status(self):
        self.container.reload()  # Refresh container state
        return self.container.status

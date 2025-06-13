import logging
import threading

from podman.domain.containers import Container
from podman.errors import APIError

logger = logging.getLogger("session")

SHUTDOWN_TIME_IN_HOURS=1
SHUTDOWN_TIME=SHUTDOWN_TIME_IN_HOURS*60*60


class Session:
    def __init__(self, user_id: str | int, container: Container, on_stop) -> None:
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
        self.container.reload()
        return self.container.status

    def exec_bash(self, command: str) -> tuple[str, str] | str:

        if(isPermissibleCommand(command)):
            return "You don't have enough privileges to execute this command. Check out https://github.com/Darki002/DiscordSL for more info!"

        try:
            exit_code, output = self.container.exec_run(command)

            stdout = b''
            stderr = b''

            if hasattr(output, '__iter__') and not isinstance(output, tuple):
                for item in output:
                    if isinstance(item, tuple):
                        out, err = item
                        stdout += out
                        stderr += err
                    else:
                        stdout += item
            else:
                stdout, stderr = output if isinstance(output, tuple) else (output, b'')

            return stdout.decode(errors="replace").strip(), stderr.decode(errors="replace").strip()
        except APIError as e:
            logger.error(f"Error while executing bash: {e}")
            return "There was an unexpected error, while executing the command!"

    def isPermissibleCommand(self, command: str) -> bool:
        if("sudo" in command):
            return false
        return true
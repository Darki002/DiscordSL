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
        self.container.reload()
        return self.container.status

    def exec_bash(self, command: str):
        exit_code, output = self.container.exec_run(command)

        stdout = b''
        stderr = b''

        # Handle streamed or tuple output
        if hasattr(output, '__iter__') and not isinstance(output, tuple):
            for item in output:
                if isinstance(item, tuple):
                    out, err = item
                    stdout += out
                    stderr += err
                else:
                    stdout += item
        else:
            # Tuple (stdout, stderr)
            stdout, stderr = output if isinstance(output, tuple) else (output, b'')

        return stdout.decode(errors="replace").strip(), stderr.decode(errors="replace").strip()

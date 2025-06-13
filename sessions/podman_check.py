import os
import stat
import sys
from urllib.parse import urlparse

def check_podman_socket():
    # Pull socket path from env (fall back to default)
    host = os.environ.get("DOCKER_HOST", "unix:///run/podman/podman.sock")
    parsed = urlparse(host)
    if parsed.scheme != "unix":
        print(f"⚠️  Unsupported scheme {parsed.scheme} in DOCKER_HOST", file=sys.stderr)
        return False

    sock_path = parsed.path
    # 1) Does it exist?
    if not os.path.exists(sock_path):
        print(f"❌  Socket not found at {sock_path}", file=sys.stderr)
        return False

    # 2) Is it actually a socket?
    mode = os.stat(sock_path).st_mode
    if not stat.S_ISSOCK(mode):
        print(f"❌  {sock_path} exists but isn’t a socket", file=sys.stderr)
        return False

    # 3) Can we read & write?
    if not os.access(sock_path, os.R_OK | os.W_OK):
        print(f"❌  No read/write permission on {sock_path}", file=sys.stderr)
        return False

    print(f"✅  Podman socket OK at {sock_path}")
    return True

if __name__ == "__main__":
    if not check_podman_socket():
        sys.exit(1)
    # proceed to start your bot…

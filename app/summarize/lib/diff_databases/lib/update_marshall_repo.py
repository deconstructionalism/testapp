import subprocess
from app.lib.logger import logger


def update_marshall_repo() -> bool:
    """
    Get commit updates to marshall repo on designated branch if they exist and
    install/update packages.
    """

    cmd = f"sh ./scripts/refresh.sh"
    p = subprocess.Popen(cmd.split(" "), stdout=subprocess.PIPE)

    # log each line from stdout to logger
    for line in iter(lambda: p.stdout.readline(), b""):
        logger.info(line.decode(encoding="utf-8").strip())

    # get return code to figure out if repo had new commits fetched
    p.communicate()
    was_updated = p.returncode != 1

    return was_updated

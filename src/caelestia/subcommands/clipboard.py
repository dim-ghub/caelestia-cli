import subprocess
from argparse import Namespace


class Command:
    args: Namespace

    def __init__(self, args: Namespace) -> None:
        self.args = args

    def run(self) -> None:
        if self.args.delete:
            clip = subprocess.check_output(["cliphist", "list"])
            args = ["--prompt=del > ", "--placeholder=Delete from clipboard"]
            chosen = subprocess.check_output(["fuzzel", "--dmenu", *args], input=clip)
            subprocess.run(["cliphist", "delete"], input=chosen)
        else:
            subprocess.Popen(
                ["qs", "-c", "caelestia", "ipc", "call", "launcher", "openClipboard"],
                start_new_session=True,
            )

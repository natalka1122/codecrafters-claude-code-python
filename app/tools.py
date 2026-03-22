import shlex
import subprocess


def read(file_path: str) -> str:
    with open(file=file_path, mode="r") as f:
        return "\n".join(f.readlines())


def write(file_path: str, content: str) -> str:
    with open(file=file_path, mode="w") as f:
        f.writelines(content)
    return "Created the file"


def bash(command: str) -> str:
    result = subprocess.run(
        shlex.split(command),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=False,
        check=False,
        text=True,
    )
    return result.stdout + result.stderr

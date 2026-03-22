def read(file_path: str) -> str:
    with open(file=file_path, mode="r") as f:
        return "\n".join(f.readlines())


def write(file_path: str, content: str) -> str:
    with open(file=file_path, mode="w") as f:
        f.writelines(content)
    return "Created the file"
def read(file_path: str) -> str:
    with open(file=file_path, mode="r") as f:
        return "\n".join(f.readlines())

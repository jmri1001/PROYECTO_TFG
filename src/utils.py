from os import path


def relative_to(__file_path__: str, p: str) -> str:
    return path.join(path.dirname(__file_path__), p)

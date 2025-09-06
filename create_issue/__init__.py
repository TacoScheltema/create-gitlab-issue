# create_issue/__init__.py
from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("create-issue")
except PackageNotFoundError:
    __version__ = "0.0.0"

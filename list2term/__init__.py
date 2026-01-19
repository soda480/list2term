from importlib import metadata as _metadata
import os as _os

__all__ = ['Lines', '__version__']

def __getattr__(name: str):
    if name == "Lines":
        from .list2term import Lines
        return Lines
    raise AttributeError(name)

try:
    __version__ = _metadata.version(__name__)
except _metadata.PackageNotFoundError:
    __version__ = '1.2.0'

if _os.getenv('DEV'):
    __version__ = f'{__version__}+dev'

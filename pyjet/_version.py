try:
    from importlib_resources import files
except ImportError:
    from importlib.resources import files

__version__ = files("pyjet").joinpath("VERSION.txt").read_text().strip()

version = __version__
version_info = __version__.split(".")

FASTJET_VERSION = "3.3.4"
FJCONTRIB_VERSION = "1.045"

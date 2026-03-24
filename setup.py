import os

from setuptools import setup

try:
    from mypyc.build import mypycify

    opt_level = os.environ.get("MYPYC_OPT_LEVEL", "3")
    ext_modules = mypycify(["hash_utils/_core.py"], opt_level=opt_level)
except ImportError:
    ext_modules = []

setup(ext_modules=ext_modules)

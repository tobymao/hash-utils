import os

from setuptools import Extension, setup

try:
    from mypyc.build import mypycify

    opt_level = os.environ.get("MYPYC_OPT_LEVEL", "3")
    ext_modules = mypycify(["hash_utils/_core.py"], opt_level=opt_level)
except ImportError:
    ext_modules = []

ext_modules.append(Extension("hash_utils._fnv64", sources=["hash_utils/_fnv64.c"]))

setup(ext_modules=ext_modules)

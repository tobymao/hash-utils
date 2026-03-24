from setuptools import setup

try:
    from mypyc.build import mypycify

    ext_modules = mypycify(["hash_utils/_core.py"])
except ImportError:
    ext_modules = []

setup(ext_modules=ext_modules)

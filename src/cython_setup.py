from setuptools import setup, Extension
from Cython.Build import cythonize

ext = Extension(
    name="readings.process_monitor",
    sources=["src/readings/process_monitor.pyx"],
)

setup(
    ext_modules=cythonize([ext], language_level=3),
    package_dir={"": "src"},
)
# Third-party
from setuptools import find_packages, setup
import os


def read(fname):
   return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="krozark-functils",
    version="0.1.2",
    packages=find_packages(exclude=["tests"]),
    install_requires=["requests", "types-requests", "jinja2", "file-magic==0.4.*"],
    description='The aim of this project is to group some usefull python class',
    long_description=read('README.md'),
    long_description_content_type="text/markdown",
    license="BSD2",
    author='Maxime Barbier',
    author_email='maxime.barbier1991+py-functils@gmail.com',
    url="https://github.com/Krozark/py-functils",
    keywords="funcutils",
    extras_require={
        "dev": [
            "black",
            "coverage",
            "docformatter",
            "flake8",
            "isort",
            "mypy",
            "pre-commit",
            "pylint",
            "ipython",
        ]
    },
)

# Third-party
from setuptools import find_packages, setup

setup(
    name="krozark-funcutils",
    version="0.1",
    packages=find_packages(exclude=["tests"]),
    install_requires=["requests", "types-requests", "jinja2", "file-magic==0.4.*"],
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

from pathlib import Path
from setuptools import setup, find_packages
import oy as package


CWD = Path(__file__).parent
LONG_DESCRIPTION = (CWD / "README.md").read_text()

with open(CWD / "requirements.txt", "r") as reqs:
    REQUIREMENTS = [l.strip() for l in reqs.readlines()]


setup(
    name="oy",
    version=package.__version__,
    author="Musharraf Omer",
    author_email="ibnomer2011@hotmail.com",
    description="A lightweight, modular, and extensible content management system based on Flask.",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/mush42/oy-cms",
    license="MIT",
    packages=find_packages(exclude=["tests",]),
    platforms="any",
    include_package_data=True,
    package_data={"oy": ["project_templates/default/*"]},
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "oy=oy.cli:oy_group",
            "oyinit=oy.cli.oyinit:init_oy_project",
        ]
    },
    install_requires=REQUIREMENTS,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)

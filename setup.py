from setuptools import setup, find_packages
import oy as package


with open("README.md", "r") as readme:
    long_description = readme.read()


setup(
    name="Oy",
    version=package.__version__,
    author="Musharraf Omer",
    author_email="ibnomer2011@hotmail.com",
    description="A lightweight, modular, and extensible content management system.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mush42/oy-cms",
    license="MIT",
    packages=find_packages(exclude=("tests",)),
    platforms="any",
    include_package_data=True,
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "oy=oy.cli:oy_group",
            "oyinit=oy.cli.oyinit:init_oy_project",
        ]
    },
    install_requires=[
        "Flask",
        "Flask-Admin",
        "Flask-BabelEx",
        "Flask-Cors",
        "flask-marshmallow",
        "Flask-Migrate",
        "Flask-Security",
        "Flask-SQLAlchemy",
        "Flask-WTF",
        "marshmallow",
        "marshmallow-sqlalchemy",
        "Pillow",
        "speaklater",
        "unicode-slugify",
        "WTForms-Components",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)

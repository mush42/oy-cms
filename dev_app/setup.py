from setuptools import setup, find_packages

__version__ = "0.1"


setup(
    name="dev_app",
    version=__version__,
    packages=find_packages(),
    install_requires=["oy", "python-dotenv"],
)

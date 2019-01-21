import click
from flask.cli import FlaskGroup


oy_group = FlaskGroup(name="oy", add_default_commands=False, add_version_option=False, load_dotenv=True)


from . import database
from . import user


if __name__=='__main__':
    oy_group.main()

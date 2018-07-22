import click
from itertools import chain
from flask import current_app
from starlit.boot.sqla import db
from starlit.models.settings import SettingsProfile


def database_group():
    """Perform database operations"""


def create_db():
    """Create database tables."""
    click.echo("Creating database tables...")
    with current_app.app_context():
        db.create_all()
    click.secho("Database tables created.", fg='green', bold=True)


@click.option('--noinput', '-n', is_flag=True)
def drop_db(noinput):
    """Drop database tables"""
    click.secho("!!!!!!!!!", fg='red', blink=True)
    if not noinput:
        message = click.style(
          "This is a distructive operation. You will loose all  your data.\r\n\tDo you want to drop all database tables?",
          fg='red',
          blink=True)
        if not click.confirm(message):
            raise click.Abort()
    with current_app.app_context():
        db.drop_all()
    click.secho("Database tables dropped", fg='green', bold=True)


def clean_settings():
    click.secho("~~~~~~~~~~~~~~~~~~~~~~", fg='red')
    click.echo("Cleaning database tables..")
    # sqlalchemy raises exceptions if the tables have not been created
    # so we degrade gracefully
    try:
        profile = SettingsProfile.query.filter_by(is_active=True).one()
        click.echo('The active settings profile is: %s' %profile.name)
    except SQLAlchemyError:
        click.secho("No active settings profile. Exiting....", fg='red', bold=True)
        return
    active_settings = profile.settings
    current_app.provided_settings_dict = {}
    current_app._collect_provided_settings()
    app_settings = chain.from_iterable(current_app.provided_settings_dict.values())
    valid_settings = {s.name for s in app_settings}
    to_remove = set(active_settings) - valid_settings
    for k in to_remove:
        click.secho("\tRemoving setting::: %s" %k, fg='red')
        del active_settings[k]
    db.session.commit()
    click.secho("Database cleaned.", fg='green', bold=True)
    click.secho("~~~~~~~~~~~~~", fg='green')


def clean_db():
    """Clean the database tables."""
    clean_settings()

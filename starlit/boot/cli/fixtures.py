import click
from flask import current_app
from starlit.boot.sqla import db
from starlit.models.user import User


def install_fixtures():
    """Installs dummy content to kick start your starlit powered site."""
    if not User.query.filter(User.active==True).count():
        click.secho(user_not_created_msg, fg='yellow')
        if click.prompt("Would you like to create one now? (y/n):", default="y") == 'y':
            createsuperuser(noinput=False)
        else:
            raise click.Abort()
    click.echo('Installing fixtures in the database')
    click.echo('~~~~~~~~~~~~~~~~~')
    click.echo()
    for module in current_app.modules.values():
        if not module.fixtures:
            continue
        click.secho("Installing fixtures for module: " + module.import_name, fg='blue')
        module.install_fixtures()
    click.echo()
    click.secho("===============", fg='green')
    click.secho("Finished installing all available fixtures.", fg='green', bold=True)
    

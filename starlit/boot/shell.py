"""
    starlit.boot.shell
    ~~~~~~~~~~~~~~~~~
    
    Shell context processors for Starlit
"""


def make_shell_context():
    """Add starlit-specific variables to the shell context"""
    from starlit.boot.sqla import db
    from starlit.models.user import User

    return {"db": db, "User": User}

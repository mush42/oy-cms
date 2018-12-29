"""
    oy.boot.shell
    ~~~~~~~~~~~~~~~~~
    
    Shell context processors for Oy
"""


def make_shell_context():
    """Add oy-specific variables to the shell context"""
    from oy.boot.sqla import db
    from oy.models.user import User
    from oy.models.page import Page

    return {"db": db, "User": User, "Page": Page}

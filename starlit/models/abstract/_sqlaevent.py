# -*- coding: utf-8 -*-
"""	
    starlit.models.abstract._sqlaevent
    ~~~~~~~~~~

    Provide a convenient mechanism to hook into sqlalchemy's
    session life cycle events

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

class SQLAEvent(object):
    """Contains methods to be called during
        diffrent session lifecycle events

    Only models having  this class as
    a base class will be able to react to sqlalchemy events by implementing
    class methods
    """

    def before_flush(self, session, is_modified):
        """Called before the session is flushed"""
        raise NotImplementedError

    def after_flush(self, session, is_modified):
        """Called after the session has been flushed"""
        raise NotImplementedError

    def update(self):
        """Called when the instance is to be updated"""
        raise NotImplementedError

    def on_init(self):
        """Called after the instance has been initialized"""
        raise NotImplementedError

    def before_commit(self, session, is_modified):
        """Called before the session is commited"""
        raise NotImplementedError

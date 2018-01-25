"""Only models inheriting this class will be able to declare SQLA events as class methods""" 

class SQLAEvent(object):
    """Contains methods to be called during
        diffrent session lifecycle events
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
        """Called when initializing the instance"""
        raise NotImplementedError

    def before_commit(self, session, is_modified):
        """Called before the session is commited"""
        raise NotImplementedError

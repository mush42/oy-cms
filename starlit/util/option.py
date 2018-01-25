
class Option(object):
    """A Class implementing some sort of field interface"""
    def __init__(self,
            name, label, type,
            description=None, category='general', required=False,
            choices=None, default=None, field_options=None):
        kwargs = locals()
        kwargs.pop('self')
        for attr, value in kwargs.items():
            setattr(self, attr, value)

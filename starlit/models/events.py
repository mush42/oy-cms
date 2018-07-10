# -*- coding: utf-8 -*-
"""	
    starlit.models
    ~~~~~~~~~~

    Provides abstract and mixin :mod:`sqlalchemy` classes that are the core
    building blocks of any content management system.

    Another interesting functionality is the :class:`SQLAEvent` which provides
    a convenient mechanism to hook into sqlalchemy life cycle events. 

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from functools import partial
from sqlalchemy import event, inspect
from sqlalchemy.orm import mapper
from starlit.boot.sqla import db
from starlit.models.abstract import SQLAEvent
from starlit.helpers import get_method_in_all_bases


get_event_methods = partial(get_method_in_all_bases, exclude=[SQLAEvent])

def call_all_methods_on_this_instance(methods, instance, *args, **kwargs):
    for meth in methods:
        meth(instance, *args, **kwargs)


def call_method_in_all_bases(instances, method_name, session, is_modified):
    for instance in instances:
        methods = get_event_methods(instance.__class__, method_name)
        call_all_methods_on_this_instance(methods, instance, session, is_modified)


def process_events(event_name, session):
    for identity_set, modified in zip(('new', 'dirty'), (False, True)):
        call_method_in_all_bases(
            (obj for obj in getattr(session, identity_set) if isinstance(obj, SQLAEvent)),
            event_name, session, modified)


@event.listens_for(db.Session, 'before_flush')
def receive_before_flush(session, flush_context, instances):
    process_events('before_flush', session)


@event.listens_for(db.Session, 'after_flush')
def receive_after_flush(session, flush_context):
    process_events('after_flush', session)


@event.listens_for(db.session, 'before_commit')
def receive_before_commit(session):
    process_events('before_commit', session)


@event.listens_for(SQLAEvent, 'before_update', propagate=True)
def process_update_event(mapper, connection, target):
    methods = get_event_methods(target.__class__, 'update')
    call_all_methods_on_this_instance(methods, target)


@event.listens_for(mapper, 'init')
def process_init_cls(target, *args, **kwargs):
    if isinstance(target, SQLAEvent):
        methods = get_event_methods(target.__class__, 'on_init')
        call_all_methods_on_this_instance(methods, target)

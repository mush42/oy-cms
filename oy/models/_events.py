# -*- coding: utf-8 -*-
"""	
    oy.models.events
    ~~~~~~~~~~

    The :class:`SQLAEvent` provides
    a convenient mechanism to hook into sqlalchemy session and
    object life cycle events. 

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from functools import partial
from oy.boot.sqla import db
from oy.models.abstract import SQLAEvent
from oy.helpers import get_method_in_all_bases


get_event_handlers = partial(get_method_in_all_bases, exclude=[SQLAEvent])


def call_all_methods_on_this_instance(methods, instance, *args, **kwargs):
    for meth in methods:
        meth(instance, *args, **kwargs)


def call_method_in_all_bases(instances, method_name, session, is_modified):
    for instance in instances:
        methods = get_event_handlers(instance.__class__, method_name)
        call_all_methods_on_this_instance(methods, instance, session, is_modified)


def process_events(event_name, session):
    for identity_set, modified in zip(("new", "dirty"), (False, True)):
        instances = (
            obj for obj in getattr(session, identity_set) if isinstance(obj, SQLAEvent)
        )
        call_method_in_all_bases(instances, event_name, session, modified)


@db.event.listens_for(db.Session, "before_flush")
def receive_before_flush(session, flush_context, instances):
    process_events("before_flush", session)


@db.event.listens_for(db.Session, "after_flush")
def receive_after_flush(session, flush_context):
    process_events("after_flush", session)


@db.event.listens_for(db.Session, "after_flush_postexec")
def receive_after_flush_postexec(session, flush_context):
    call_method_in_all_bases(
        (obj for obj in session), "after_flush_postexec", session, True
    )


@db.event.listens_for(db.session, "before_commit")
def receive_before_commit(session):
    process_events("before_commit", session)


@db.event.listens_for(db.session, "after_commit")
def receive_after_commit(session):
    call_method_in_all_bases((obj for obj in session), "after_commit", session, True)


@db.event.listens_for(db.mapper, "init")
def process_init_cls(target, *args, **kwargs):
    if isinstance(target, SQLAEvent):
        methods = get_event_handlers(target.__class__, "on_init")
        call_all_methods_on_this_instance(methods, target)


def _call_dml_events(evt, instance, mapper, connection):
    if isinstance(instance, SQLAEvent):
        methods = get_event_handlers(instance.__class__, evt)
        call_all_methods_on_this_instance(
            methods, instance, mapper=mapper, connection=connection
        )


@db.event.listens_for(db.Mapper, "before_insert")
def _before_insert_dispatch(mapper, connection, instance):
    _call_dml_events("before_insert", instance, mapper, connection)


@db.event.listens_for(db.Mapper, "before_update")
def _before_update_dispatch(mapper, connection, instance):
    _call_dml_events("before_update", instance, mapper, connection)


@db.event.listens_for(db.Mapper, "before_delete")
def _before_delete_dispatch(mapper, connection, instance):
    _call_dml_events("before_delete", instance, mapper, connection)

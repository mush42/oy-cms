# -*- coding: utf-8 -*-
"""	
    oy.models.mixins.node_spec
    ~~~~~~~~~~

    Provides a mixin for dealing with the type
    of child and parent nodes.

    :copyright: (c) 2019 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from oy.boot.sqla import db


class NodeSpec:

    ALL_NODE_TYPES = (...,)

    @classmethod
    def configure_node_spec(cls):
        """Work up a tuple of types of ancestors
        and descendants this page is allowed to have.
        """
        cls.valid_child_node_types = cls._normalize_type_values(
            getattr(cls, "__allowed_children__", cls.ALL_NODE_TYPES)
        )
        cls.valid_parent_node_types = cls._normalize_type_values(
            getattr(cls, "__allowed_parents__", cls.ALL_NODE_TYPES)
        )

    @classmethod
    def is_valid_child(cls, child):
        model = db.inspect(child).mapper.class_
        if not cls.should_allow_children():
            return False
        elif cls.valid_child_node_types is cls.ALL_NODE_TYPES:
            return True
        return model in cls.valid_child_node_types

    @classmethod
    def is_valid_parent(cls, parent):
        model = db.inspect(parent).mapper.class_
        if not cls.should_allow_parents():
            return False
        elif cls.valid_parent_node_types is cls.ALL_NODE_TYPES:
            return True
        return model in cls.valid_parent_node_types

    @classmethod
    def should_allow_parents(cls):
        return bool(cls.valid_parent_node_types)

    @classmethod
    def should_allow_children(cls):
        return bool(cls.valid_child_node_types)

    @classmethod
    def _before_setting_parent(cls, instance, value, oldvalue=None, initiator=None):
        if not db.inspect(instance).mapper.class_.is_valid_parent(value):
            raise ValueError(
                f"{value.__class__.__name__} is not a valid parent for pages of type {cls.__name__}."
            )

    @classmethod
    def _before_appending_nodes(cls, instance, value, initiator=None):
        if not db.inspect(instance).mapper.class_.is_valid_child(value):
            raise ValueError(
                f"{value.__class__.__name__} is not a valid child type for pages of type {cls.__name__}."
            )

    @classmethod
    def _normalize_type_values(cls, values):
        if values == cls.ALL_NODE_TYPES:
            return cls.ALL_NODE_TYPES
        rv = []
        for val in values:
            if val in db.Model._decl_class_registry.values():
                rv.append(val)
            elif type(val) is str and val in cls._decl_class_registry:
                rv.append(cls._decl_class_registry[val])
            else:
                raise ValueError(
                    f"""
                    Model class {val} was not found among current model classes.
                    Maybe it has not been imported yet?
                """
                )
        return rv


@db.event.listens_for(db.mapper, "after_configured")
def configure_node_spec_listeners():
    dbmodels = [
        v
        for (k, v) in db.Model._decl_class_registry.items()
        if k != "_sa_module_registry"
    ]
    node_classes = [c for c in dbmodels if issubclass(c, NodeSpec)]
    for cls in node_classes:
        cls.configure_node_spec()


@db.event.listens_for(NodeSpec, "attribute_instrument", propagate=True)
def attributes_instromented(cls_, key, inst):
    if key == "children":
        db.event.listen(inst, "append", cls_._before_appending_nodes)
    elif key == "parent":
        db.event.listen(inst, "set", cls_._before_setting_parent)

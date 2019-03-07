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
        and descendants this node is allowed to have.
        """
        cls.valid_child_node_types = cls._normalize_type_values(
            getattr(cls, "__allowed_children__", cls.ALL_NODE_TYPES)
        )
        cls.valid_parent_node_types = cls._normalize_type_values(
            getattr(cls, "__allowed_parents__", cls.ALL_NODE_TYPES)
        )
        for parent in cls.valid_parent_node_types:
            if (parent != ...) and not parent.should_allow_children():
                raise TypeError(
                    f"""
                    Model class `{parent.__name__}` is configured to not
                    accept children, but it is listed as a possible
                    parent for model class `{cls.__name__}`.
                """
                )
            for child in cls.valid_child_node_types:
                if (child != ...) and not child.should_allow_parents():
                    raise TypeError(
                        f"""
                        Model class `{child.__name__}` is configured to not accept
                        parents but it is listed as a possible
                        child for model class `{cls.__name__}`.
                    """
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
                f"{cls.__name__} does not accept parents of type {value.__class__.__name__}."
            )

    @classmethod
    def _before_appending_nodes(cls, instance, value, initiator=None):
        if not db.inspect(instance).mapper.class_.is_valid_child(value):
            raise ValueError(
                f"{cls.__name__} does not accept children of type {value.__class__.__name__}."
            )

    @classmethod
    def _normalize_type_values(cls, values):
        if values == cls.ALL_NODE_TYPES:
            return cls.ALL_NODE_TYPES
        rv = []
        accepted_models = {}
        dbmodels = [
            (k, v)
            for (k, v) in db.Model._decl_class_registry.items()
            if not k.startswith("_")
        ]
        for name, model in dbmodels:
            if cls.__mapper__.common_parent(model.__mapper__):
                accepted_models[name] = model
        for val in values:
            if val in accepted_models.values():
                rv.append(val)
            elif type(val) is str and val in accepted_models:
                rv.append(accepted_models[val])
            else:
                raise TypeError(
                    f"""
                    Model class `{val.__name__}` could not be used in this tree.
                    Either it has no common base class with `{cls.__name__}` or it 
                    has not been imported yet.
                """
                )
        return rv


@db.event.listens_for(db.mapper, "after_configured")
def configure_node_spec_listeners():
    dbmodels = [
        v for (k, v) in db.Model._decl_class_registry.items() if not k.startswith("_")
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

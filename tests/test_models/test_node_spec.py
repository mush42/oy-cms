import pytest
from oy.models.mixins import SelfRelated, NodeSpec


def test_node_spec_basic(db, makemodel):
    class BaseNode(SelfRelated, NodeSpec, db.Model):
        id = db.Column(db.Integer, primary_key=True)
        type = db.Column(db.String(50))
        __mapper_args__ = {"polymorphic_identity": "base", "polymorphic_on": type}

    class AllowedChild(BaseNode):
        id = db.Column(db.Integer, db.ForeignKey(BaseNode.id), primary_key=True)
        __mapper_args__ = {"polymorphic_identity": "allowed_child"}

    class DisallowedChild(BaseNode):
        id = db.Column(db.Integer, db.ForeignKey(BaseNode.id), primary_key=True)
        __mapper_args__ = {"polymorphic_identity": "disallowed_child"}

    class AllowedParent(BaseNode):
        id = db.Column(db.Integer, db.ForeignKey(BaseNode.id), primary_key=True)
        __mapper_args__ = {"polymorphic_identity": "allowed_parent"}

    class DisallowedParent(BaseNode):
        id = db.Column(db.Integer, db.ForeignKey(BaseNode.id), primary_key=True)
        __mapper_args__ = {"polymorphic_identity": "disallowed_parent"}

    class SubNode1(BaseNode):
        id = db.Column(db.Integer, db.ForeignKey(BaseNode.id), primary_key=True)
        __mapper_args__ = {"polymorphic_identity": "subnode1"}
        __allowed_children__ = ["AllowedChild"]

    class SubNode2(BaseNode):
        id = db.Column(db.Integer, db.ForeignKey(BaseNode.id), primary_key=True)
        __mapper_args__ = {"polymorphic_identity": "subnode2"}
        __allowed_parents__ = ["AllowedParent"]

    class MultipleAllowedChildTypes(BaseNode):
        id = db.Column(db.Integer, db.ForeignKey(BaseNode.id), primary_key=True)
        __mapper_args__ = {"polymorphic_identity": "multi_child_node"}
        __allowed_children__ = ["AllowedChild", AllowedParent, DisallowedParent]

    class NoChildren(BaseNode):
        id = db.Column(db.Integer, db.ForeignKey(BaseNode.id), primary_key=True)
        __mapper_args__ = {"polymorphic_identity": "no_children"}
        __allowed_children__ = []

    class Orphan(BaseNode):
        id = db.Column(db.Integer, db.ForeignKey(BaseNode.id), primary_key=True)
        __mapper_args__ = {"polymorphic_identity": "orphan"}
        __allowed_parents__ = []

    db.create_all()
    BaseNode.__mapper__._configure_all()

    assert AllowedChild in SubNode1.valid_child_node_types
    assert DisallowedChild not in SubNode1.valid_child_node_types
    assert AllowedParent in SubNode2.valid_parent_node_types
    assert DisallowedParent not in SubNode2.valid_parent_node_types
    assert SubNode1.valid_parent_node_types is SubNode1.ALL_NODE_TYPES
    assert SubNode2.valid_child_node_types is SubNode2.ALL_NODE_TYPES

    parent_subnode1 = SubNode1()
    parent_subnode1.children.append(AllowedChild())
    db.session.commit()
    with pytest.raises(ValueError):
        parent_subnode1.children.append(DisallowedChild())
    sn1_parent = AllowedParent()
    parent_subnode1.parent = sn1_parent
    db.session.commit()

    child_subnode2 = SubNode2()
    sn2_parent = AllowedParent()
    child_subnode2.parent = sn2_parent
    db.session.commit()
    with pytest.raises(ValueError):
        child_subnode2.parent = DisallowedParent()
    with pytest.raises(ValueError):
        SubNode2(parent=DisallowedParent())

    multi_node = MultipleAllowedChildTypes()
    with pytest.raises(ValueError):
        multi_node.children = [AllowedChild(), DisallowedChild()]
    with pytest.raises(ValueError):
        MultipleAllowedChildTypes(children=[AllowedChild(), DisallowedChild()])
    multi_node.children.append(AllowedParent())

    assert not Orphan.should_allow_parents()
    orph = Orphan()
    with pytest.raises(ValueError):
        orph.parent = BaseNode()

    assert NoChildren.should_allow_parents()
    assert not NoChildren.should_allow_children()
    quite = NoChildren()
    with pytest.raises(ValueError):
        quite.children.append(AllowedChild())
    with pytest.raises(ValueError):
        NoChildren(children=[AllowedChild()])

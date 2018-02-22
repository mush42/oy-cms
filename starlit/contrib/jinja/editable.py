import werkzeug
import warnings
from flask import current_app, url_for, jsonify
from flask_security import current_user
from jinja2 import nodes
from jinja2.ext import Extension
from wtforms.widgets.core import html_params
from markupsafe import escape
from starlit.babel import gettext
from starlit.plugin import StarlitPlugin


def should_enable_inline_editing():
    if not current_app.config.get('ENABLE_INLINE_EDITING'):
        return False
    elif not current_user.is_authenticated or not current_user.is_active or not current_user.has_role('admin'):
        return False
    return True


import random
import json
import sqlalchemy as sa

TYPE_MAP = {
    sa.types.UnicodeText: 'textarea',
    sa.types.BigInteger: 'number',
    sa.types.SmallInteger: 'number',
    sa.types.Text: 'textarea',
    sa.types.Date: 'date',
    sa.types.DateTime: 'datetime',
    sa.types.Enum: 'select',
    sa.types.Float: 'number',
    sa.types.Integer: 'number',
    sa.types.Numeric: 'number',
    sa.types.Boolean: 'checkbox',
    sa.types.Unicode: 'text',
    sa.types.String: 'text',
    sa.types.Time: 'time',
}


class EditableExtension(Extension):
    tags = set(['editable'])
    
    def parse(self, parser):
        lineno = next(parser.stream).lineno
        parts = [parser.stream.expect('name').value]
        while parser.stream.current.type != 'block_end':
            parser.stream.expect('dot')
            parts.append(parser.stream.expect('name').value)
        body = parser.parse_statements(['name:endeditable'], drop_needle=True)
        call = self.call_method(
            '_editable_loader',
            [nodes.Name(parts[0], 'load'), nodes.Const(parts[1:]), nodes.Const(not body)])
        output_nodes = [
            nodes.Output([nodes.MarkSafe(call)])
        ]
        output_nodes.extend(body)
        output_nodes.extend([
            nodes.Output([nodes.MarkSafe(nodes.TemplateData('</span>'))]),
        ])
        block_name = '%s_%s_%d' %(parts[-2], parts[-1], random.randint(0, 500))
        return nodes.Block(block_name, output_nodes, True)

    def _editable_loader(self, parent, attrs, append_body=False):
        attr = attrs.pop()
        attrs.reverse()
        while attrs:
            parent = getattr(parent, attrs.pop())
        assert hasattr(parent, '_sa_class_manager'), '%s is not a sqlalchemy mapped class' %parent
        column = parent.__mapper__.columns.get(attr)
        if column is None:
            raise AttributeError('Model %s has no column %s' %(parent, attr))
        if not should_enable_inline_editing():
            if append_body:
                return getattr(parent, attr)
            else:
                return ''
        url = None
        try:
            url = self.api_url_for(parent.__class__, pk=parent.id)
        except werkzeug.routing.BuildError:
            warnings.warn('You have marked a field as (editable), but this field class do not have (AN API ENDPOINT), due to this the editable function has been disabled for the following field: (%s.%s)' %(parent.__class__.__name__, attr))
            return ''
        field_data = self.widget_for(column)
        label = column.info.get('label') or attr.replace('_', ' ').title()
        value = getattr(parent, attr)
        params = dict(
            class_='editable-content',
            data_type=field_data['type'],
            data_name=attr,
            data_url=url,
            data_label=label,
        )
        if field_data['type'] == 'select':
            choices = field_data['choices']
            choices['selected'] = value
            params['data-choices'] = json.dumps(choices)
        if field_data['type'] in ('checkbox', 'select'):
            params['data-value'] = json.dumps(value)
        html_attrs = html_params(**params)
        el = '<button class="edit-a11y-btn sr-only">{0}</button><span {1}>'.format(gettext('Edit {label}').format(label=label), html_attrs)
        if append_body:
            el = '{0}{1}'.format(el, escape(value))
        return el

    def widget_for(self, column):
        rv = dict()
        if  column.type not in TYPE_MAP and isinstance(column.type, sa.types.TypeDecorator):
            check_type = column.type.impl
        else:
            check_type = column.type
        rv['type'] = TYPE_MAP[type(check_type)]
        if column.info.get('markup') and column.info.get('markup_type') == 'html':
            rv['type'] = 'mce'
        choices = column.info.get('choices', [])
        if choices:
            rv['choices'] = dict([(k, str(v)) for k, v in choices])
        return rv

    def api_url_for(self, cls, pk):
        name = cls.__name__.lower()
        return url_for('canella-api.%s-resource' %name, pk=pk)


class EditablePlugin(StarlitPlugin):
    """Provide integration with starlit for the EditableExtenssion"""
    
    def init_app(self, app):
        super(EditablePlugin, self).init_app(app)
        app.jinja_env.extensions['starlit.contrib.jinja.editable.EditableExtension'] = EditableExtension(app.jinja_env)
        app.jinja_env.globals[should_enable_inline_editing] = should_enable_inline_editing

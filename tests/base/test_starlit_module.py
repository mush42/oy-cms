from starlit.wrappers import StarlitModule

__install_fixtures__ = False


def test_load_config_from_package_defaults(app):
    dummy_module = StarlitModule('dummy', __name__)
    app.register_module(dummy_module)
    assert app.config.get('DUMMY_CONFIG_VARIABLE')
    assert app.config['DUMMY_CONFIG_VARIABLE'] == 'test'


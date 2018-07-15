from .settings import *
from .settings_profile import *

def register_settings_admin(app, admin):
    admin.add_view(SettingsProfileAdmin(
        SettingsProfile,
        db.session,
        name=lazy_gettext('Settings Profiles'),
        category=gettext("Settings"),
        menu_icon_type='fa',
        menu_icon_value='fa-flag'
    ))
    categories = set()
    for category, settings in app.provided_settings:
        class SettingsAdmin(StarlitBaseView):
            settings_category = category
            @expose('/', methods=['Get', 'POST'])
            def index(self):
                form = make_settings_form_for_category(category=self.settings_category)
                if form.validate_on_submit():
                    update_settings_from_form(form.data)
                    flash("Settings were successfully saved")
                    return redirect(request.url)
                return self.render('starlit_admin/settings.html', form=form)
        admin.add_view(SettingsAdmin(
            name=category.title(),
            menu_icon_type='fa',
            menu_icon_value='fa-gear',
            category=gettext("Settings"),
            endpoint="admin-settings-{}".format(category),
            url="settings/{}".format(category)
        ))

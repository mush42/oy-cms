# -*-coding: utf-8-*-
"""

    [[ project_name ]].home_page
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This file implements the home page module.
"""

from oy.wrappers import OyModule
from oy.views import ContentView
from .models import HomePage
from .admin import register_admin


home_page = OyModule("home_page", __name__, template_folder="templates")


@home_page.contenttype_handler(HomePage)
class HomePageView(ContentView):
    """Request Handler for the HomePage content type."""

    def serve(self):
        return {"is_home": True}


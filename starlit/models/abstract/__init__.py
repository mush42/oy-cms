# -*- coding: utf-8 -*-
"""	
    starlit.models.abstract
    ~~~~~~~~~~

    Abstract classes to be used with starlit CMS classes.

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from .slugged import Slugged, Titled
from .metadata import Metadata
from .time_stampped import TimeStampped
from .publishable import Publishable
from .displayable import Displayable, DisplayableQuery
from .page import AbstractPage
from .polymorphic_prop import ProxiedDictMixin, DynamicProp
from ._sqlaevent import SQLAEvent

# -*- coding: utf-8 -*-
"""	
    oy.models.abstract
    ~~~~~~~~~~

    Abstract classes to be used with oy CMS classes.

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from ._sqlaevent import SQLAEvent
from .polymorphic_prop import ProxiedDictMixin, DynamicProp
from .slugged import Titled, Slugged, ScopedUniquelySlugged, MPSlugged
from .metadata import Metadata
from .time_stampped import TimeStampped
from .publishable import Publishable
from .misc import Orderable, SelfRelated
from .user_related import UserRelated
from .displayable import Displayable
from .abstract_page import AbstractPage

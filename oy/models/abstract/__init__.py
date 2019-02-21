# -*- coding: utf-8 -*-
"""	
    oy.models.abstract
    ~~~~~~~~~~

    Abstract classes to be used with oy CMS classes.

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from ._sqlaevent import SQLAEvent
from .polymorphic_prop import ProxiedDictMixin, ReadOnlyProxiedDictMixin, DynamicProp, DynamicPropWithFile
from .slugged import Titled, Slugged, ScopedUniquelySlugged
from .metadata import Metadata
from .time_stampped import TimeStampped
from .published import Published
from .misc import Ordered, SelfRelated
from .user_related import UserRelated
from .displayable import Displayable
from .abstract_page import AbstractPage
from .classifiable import Tagged, Categorized
from .has_comments import HasComments

# -*- coding: utf-8 -*-
"""	
    oy.models.mixins
    ~~~~~~~~~~

    Mixin classes to add more functionality.

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from ._sqlaevent import SQLAEvent
from .polymorphic_prop import ProxiedDictMixin, ImmutableProxiedDictMixin, DynamicProp
from .node_spec import NodeSpec
from .slugged import Titled, Slugged, ScopedUniquelySlugged
from .metadata import Metadata
from .time_stampped import TimeStampped
from .published import Published
from .misc import Ordered, SelfRelated
from .user_related import UserRelated
from .classifiable import Tagged, Categorized
from .has_comments import HasComments

##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""

$Id$
"""
from zope import interface
from zope.component import queryUtility
from zope.security.proxy import removeSecurityProxy
from zope.app.container.interfaces import INameChooser
from zope.copypastemove.interfaces import IContainerItemRenamer
from zojax.personal.space.interfaces import IPersonalSpace

from rwproperty import setproperty, getproperty


class PersonalSpaceSettings(object):

    manager = None
    homeFolder = None

    @getproperty
    def title(self):
        return self.space.title

    @setproperty
    def title(self, value):
        self.space.title = value

    @getproperty
    def description(self):
        return self.space.description

    @setproperty
    def description(self, value):
        self.space.description = value

    @getproperty
    def anonymous(self):
        return self.space.anonymous

    @setproperty
    def anonymous(self, value):
        self.space.anonymous = value

    @property
    def shortname(self):
        return self.space.__name__

    def changeShortName(self, name):
        if self.space.__name__ != name:
            INameChooser(self.manager).checkName(name, self.space)

            renamer = IContainerItemRenamer(self.manager)
            renamer.renameItem(self.space.__name__, name)

    def __bind__(self, principal=None, parent=None):
        clone = super(PersonalSpaceSettings, self).__bind__(principal, parent)

        clone.space = IPersonalSpace(principal, None)
        clone.manager = getattr(clone.space, '__parent__', None)

        return clone

    def isAvailable(self):
        if self.space is None:
            return False

        return super(PersonalSpaceSettings, self).isAvailable()

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
""" personal space menuitem

$Id$
"""
from zope import interface
from zope.viewlet.viewlet import ViewletBase
from zope.traversing.browser import absoluteURL
from zojax.personal.space.interfaces import _, IPersonalSpace


class PersonalSpaceMenuItem(ViewletBase):

    weight = 98

    def update(self):
        self.home = IPersonalSpace(self.manager.principal, None)

    def isAvailable(self):
        return self.home is not None

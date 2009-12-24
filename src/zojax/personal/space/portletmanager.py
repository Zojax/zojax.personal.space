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
from zope.component import getUtility
from zope.cachedescriptors.property import Lazy
from zojax.portlet.interfaces import IPortletsExtension
from zojax.personal.space.interfaces import IPersonalSpaceManager


class PortletManager(object):

    @Lazy
    def __data__(self):
        extension = IPortletsExtension(getUtility(IPersonalSpaceManager))

        name = u'%s.%s'%(self.context.__name__, self.__name__)
        return extension.getManagerData(self, name)

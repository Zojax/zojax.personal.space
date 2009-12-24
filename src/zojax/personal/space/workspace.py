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
from zope import interface, component, event
from zope.proxy import removeAllProxies
from zope.app.component.interfaces import ISite
from zope.lifecycleevent import ObjectCreatedEvent
from zope.lifecycleevent import ObjectModifiedEvent
from zope.security.proxy import removeSecurityProxy
from zojax.catalog.utils import getRequest
from zojax.content.space.interfaces import IRootSpace

from manager import PersonalSpaceManager
from interfaces import _, IPersonalSpaceManager, IPersonalSpaceManagerWorkspace


class PersonalSpaceManagerWorkspace(object):
    component.adapts(IRootSpace)
    interface.implements(IPersonalSpaceManagerWorkspace)

    name = 'people'
    weight = 99998
    description = _(u'Personal spaces for members.')

    def __init__(self, space):
        self.space = space

    @property
    def title(self):
        if self.isInstalled():
            return self.space['people'].title
        else:
            return _(u'People')

    def get(self):
        return self.space.get('people')

    def install(self):
        manager = self.space.get('people')

        if not IPersonalSpaceManager.providedBy(manager):
            manager = PersonalSpaceManager(
                title = u'People',
                description = u'Personal spaces for members.')
            event.notify(ObjectCreatedEvent(manager))

            removeAllProxies(self.space)['people'] = manager

            request = getRequest()
            if request is not None:
                manager.getPersonalSpace(request.principal)

            sm = component.getSiteManager()
            sm.registerUtility(manager, IPersonalSpaceManager)

            manager = self.space['people']

        return manager

    def uninstall(self):
        people = self.space['people']

        sm = component.getSiteManager()
        sm.unregisterUtility(people, IPersonalSpaceManager)

        del self.space['people']

    def isInstalled(self):
        return 'people' in self.space

    def isAvailable(self):
        return True

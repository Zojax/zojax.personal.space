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
from zope.location import LocationProxy
from zope.publisher.interfaces import NotFound
from zope.security.proxy import removeSecurityProxy
from zope.component import queryUtility, getUtilitiesFor
from zope.component import getAdapters, queryMultiAdapter
from zojax.statusmessage.interfaces import IStatusMessage
from zojax.portlet.interfaces import IPortletManager, IPortletsExtension
from zojax.portlet.browser.interfaces import IPortletManagerConfigMarker
from zojax.personal.space.interfaces import IPersonalWorkspaceDescription


class PortletManagers(object):

    def update(self):
        request = self.request
        context = self.context

        terms = []
        for name, desc in getUtilitiesFor(IPersonalWorkspaceDescription):
            managers = []

            for id, manager in getAdapters(
                (desc.createTemp(context), request, None), IPortletManager):
                managers.append((manager.title,
                                 {'name': 'ppm-%s-%s'%(name, id),
                                  'title': manager.title,
                                  'description': manager.description}))

            managers.sort()
            managers = [info for _t, info in managers]

            terms.append((desc.title,
                          {'name': name,
                           'title': desc.title,
                           'description': desc.description,
                           'managers': managers}))

        terms.sort()
        self.managers = [info for _t, info in terms]

    def isAvailable(self):
        return bool(self.managers)

    def postUpdate(self):
        pass


class PortletManagersPublisher(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def publishTraverse(self, request, name):
        if name.startswith('ppm-'):
            try:
                ws, name = name[4:].split('-', 1)
            except:
                raise NotFound(self.context, name, request)

            ws = queryUtility(IPersonalWorkspaceDescription, ws)
            if ws is not None:
                ws = ws.createTemp(self.context)
                manager = queryMultiAdapter(
                    (ws, request, None), IPortletManager, name)

                if manager is not None:
                    manager.updateConfigure()

                    interface.alsoProvides(manager, IPortletManagerConfigMarker)
                    return LocationProxy(manager, self.context, name)

        raise NotFound(self.context, name, request)

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
from zope.component import getAdapters, getUtility, queryUtility
from zope.app.intid.interfaces import IIntIds
from zope.app.container.interfaces import IObjectAddedEvent
from zope.lifecycleevent import ObjectModifiedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent

from zojax.ownership.interfaces import IOwnership
from zojax.content.type.container import ContentContainer
from zojax.content.type.searchable import ContentSearchableText
from zojax.content.space.interfaces import IWorkspaceFactory
from zojax.principal.profile.interfaces import IPersonalProfile

from interfaces import IPersonalSpace, IPersonalSpaceManager, \
                       IPersonalWorkspacesManagement


class PersonalSpace(ContentContainer):
    interface.implements(IPersonalSpace)

    anonymous = True

    @property
    def id(self):
        return getUtility(IIntIds).getId(self)

    @property
    def principal(self):
        return IOwnership(self).owner

    @property
    def principalId(self):
        return IOwnership(self).ownerId

    def isEnabled(self, workspaceFactory):
        if not workspaceFactory.isAvailable():
            return False
        workspaces = IPersonalWorkspacesManagement(self).workspaces
        if workspaces:
            if workspaceFactory.name in workspaces:
                return True
            else:
                return False
        else:
            return True


@component.adapter(IPersonalSpace, IObjectAddedEvent)
def personalSpaceAdded(space, event):
    for name, factory in getAdapters((space,), IWorkspaceFactory):
        if space.isEnabled(factory):
            factory.install()


@component.adapter(IPersonalProfile, IObjectModifiedEvent)
def personalProfileModified(profile, appevent):
    manager = queryUtility(IPersonalSpaceManager)
    if manager is not None:
        space = manager.getPersonalSpace(profile.__principal__)
        if space is not None:
            event.notify(ObjectModifiedEvent(space))


class personalSpaceSearchableText(ContentSearchableText):
    component.adapts(IPersonalSpace)

    def getSearchableText(self):
        text = super(personalSpaceSearchableText, self).getSearchableText()

        return getattr(IPersonalProfile(self.content.principal, None), 'title', '') + u' ' + text

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
from BTrees.OOBTree import OOBTree

from zope import interface, component, event
from zope.component import queryUtility, getUtility, getUtilitiesFor

from zope.lifecycleevent import ObjectCreatedEvent
from zope.security.proxy import removeSecurityProxy
from zope.security.interfaces import IGroup, IPrincipal
from zope.app.component.hooks import getSite
from zope.app.security.interfaces import IUnauthenticatedPrincipal
from zope.app.container.interfaces import INameChooser, IObjectMovedEvent

from zojax.site.interfaces import ISite
from zojax.content.type.container import ContentContainer
from zojax.content.type.interfaces import IContentType, IContentTypeChecker

from zojax.security.utils import getPrincipal, checkPermissionForPrincipal
from zojax.ownership.interfaces import IOwnership
from zojax.authentication.interfaces import IPrincipalRemovingEvent
from zojax.principal.profile.interfaces import IPersonalSpaceService
from zope.traversing.interfaces import IContainmentRoot

from space import PersonalSpace
from interfaces import _, \
    IPersonalSpace, IPersonalSpaceManager, IPersonalWorkspacesManagement


class PersonalSpaceManager(ContentContainer):
    interface.implements(IPersonalSpaceManager, IPersonalWorkspacesManagement)

    _allowed = 'qwertyuiopasdfghjklzxcvbnm1234567890'

    pagecount = 15
    searching = True

    workspaces = ()
    enabledWorkspaces = ()
    defaultWorkspace = 'profile'

    def __init__(self, **kw):
        super(PersonalSpaceManager, self).__init__(**kw)

        self.assignments = OOBTree()
        self.bassignments = OOBTree()

    @property
    def space(self):
        return self.__parent__

    def createSpace(self, title):
        space = PersonalSpace(title=title)
        event.notify(ObjectCreatedEvent(space))
        return space

    def canAssignPrincipal(self, principal):
        if (not IUnauthenticatedPrincipal.providedBy(principal) and
            IPrincipal.providedBy(principal) and
            not IGroup.providedBy(principal) and
            checkPermissionForPrincipal(principal,'zojax.PersonalSpace',self)):
            return True

        return False

    def assignPersonalSpace(self, principal, name=None):
        if principal.id in self.assignments:
            space = self[self.assignments[principal.id]]
            IOwnership(space).owner = principal
            return

        elif name in self:
            if name in self.bassignments:
                pid = self.bassignments[name]
                del self.bassignments[name]
                if pid in self.assignments:
                    del self.assignments[pid]

            space = self[name]
            IOwnership(space).owner = principal
            self.assignments[principal.id] = name
            self.bassignments[name] = principal.id
            return

        space = self.createSpace(principal.title)
        IOwnership(space).owner = principal

        if not name:
            title = [ch for ch in principal.title.lower()
                     if ch in self._allowed]
            if title:
                name = u''.join(title)
            else:
                name = principal.id

            name = INameChooser(self).chooseName(name, space)

        self.assignments[principal.id] = name
        self.bassignments[name] = principal.id
        self[name] = space

    def unassignPersonalSpace(self, principal, delete=True):
        if principal.id not in self.assignments:
            return
        name = self.assignments[principal.id]
        del self.assignments[principal.id]
        del self.bassignments[name]

        if delete is True:
            if name in self:
                del self[name]

    def getPersonalSpace(self, principal):
        if not self.canAssignPrincipal(principal):
            return

        if principal.id not in self.assignments:
            self.assignPersonalSpace(principal)
        else:
            name = self.assignments[principal.id]
            if name not in self:
                del self.assignments[principal.id]
                return self.getPersonalSpace(principal)

        return self.get(self.assignments[principal.id], None)

    def getPersonalSpaceById(self, principalId):
        if principalId in self.assignments:
            return self.get(self.assignments[principalId], None)

    def getPrincipal(self, space):
        if space in self:
            if space in self.bassignments:
                return getPrincipal(self.bassignments[space])

        return None


@component.adapter(IPersonalSpace)
@interface.implementer(IPersonalWorkspacesManagement)
def getPersonalWorkspacesManagement(space):
    """Get workspaces management."""
    return space.__parent__

@component.adapter(IPrincipal)
@interface.implementer(IPersonalSpace)
def getPersonalSpace(principal):
    """Get the home folder instance of the principal."""
    if IUnauthenticatedPrincipal.providedBy(principal):
        return None

    manager = getSite().get('people')
    if IPersonalSpaceManager.providedBy(manager):
        return manager.getPersonalSpace(principal)

    return None


@component.adapter(IPersonalSpace, IObjectMovedEvent)
def personalSpaceMoved(space, event):
    principal = None

    oldManager = removeSecurityProxy(event.oldParent)
    if IPersonalSpaceManager.providedBy(oldManager):
        principal = oldManager.getPrincipal(event.oldName)
        if principal is not None:
            oldManager.unassignPersonalSpace(principal, False)

    newManager = removeSecurityProxy(event.newParent)
    if IPersonalSpaceManager.providedBy(newManager) and principal:
        newManager.assignPersonalSpace(principal, event.newName)


@component.adapter(IPrincipalRemovingEvent)
def principalRemovingHandler(ev):
    site = getSite()
    sites = [site]
    if site is not None:
        if site.__parent__ is not None:
            site = site.__parent__
            sites = [site] + [site for site in site.values() if ISite.providedBy(site)]
    for site in sites:
        for name, manager in getUtilitiesFor(IPersonalSpaceManager, context=site):
            manager.unassignPersonalSpace(ev.principal)


class PersonalSpaceService(object):
    interface.implements(IPersonalSpaceService)

    def queryPersonalSpace(self, principal):
        return IPersonalSpace(principal, None)

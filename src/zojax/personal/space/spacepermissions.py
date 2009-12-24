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
from zope import component, interface
from zope.component import getUtility
from zope.securitypolicy.interfaces import Allow, Deny, Unset
from zope.securitypolicy.interfaces import IPrincipalPermissionMap
from zope.app.security.interfaces import IUnauthenticatedPrincipal

from interfaces import IPersonalSpace


class SpacePermissions(object):
    component.adapts(IPersonalSpace)
    interface.implements(IPrincipalPermissionMap)

    def __init__(self, space):
        self.space = space
        self.allow = space.anonymous
        self.anon = getUtility(IUnauthenticatedPrincipal).id

    def getPrincipalsForPermission(self, permission):
        if not self.allow and permission == 'zope.View':
            return (self.anon, Deny),
        else:
            return ()

    def getPermissionsForPrincipal(self, principal_id):
        if not self.allow and self.anon == principal_id:
            return ('zope.View', Deny),

        return ()

    def getSetting(self, permission_id, principal_id, default=None):
        if self.anon == principal_id and permission_id == 'zope.View':
            if not self.allow:
                return Deny

        return Unset

    def getPrincipalsAndPemrissions(self):
        pass

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
from zope.component import getAdapters
from zope.security import checkPermission
from zojax.content.space.interfaces import IWorkspaceFactory, IWorkspacesManagement


class PersonalSpace(object):

    def __call__(self, *args, **kw):
        context = self.context

        if not checkPermission('zope.View', context):
            self.space = context
            self.__parent__ = context.__parent__
            return super(PersonalSpace, self).__call__()

        workspaces = []
        defaultWorkspace = IWorkspacesManagement(context).defaultWorkspace

        redirectWorkspace = None

        for name, factory in getAdapters((context,), IWorkspaceFactory):
            if context.isEnabled(factory):
                workspaces.append((factory.weight, factory.title, name))
                if defaultWorkspace == name:
                    redirectWorkspace = name

        if workspaces:
            if redirectWorkspace is None:
                workspaces.sort()
                redirectWorkspace = workspaces[0][2]
            self.redirect('./%s/'%redirectWorkspace)
        else:
            self.redirect('./listing.html')

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
from zope import interface, component
from zojax.personal.space.interfaces import IPersonalSpace
from zojax.content.space.interfaces import IWorkspace, IWorkspaceFactory


class ITestWorkspace(IWorkspace):
    pass


class ITestWorkspaceFactory(IWorkspaceFactory):
    pass


class TestWorkspace(object):
    interface.implements(ITestWorkspace)

    __name__ = 'test'


class TestWorkspaceFactory(object):
    component.adapts(IPersonalSpace)
    interface.implements(ITestWorkspaceFactory)

    title = u'Test workspace'
    description = u''
    weight = 10
    name='test'

    def __init__(self, manager):
        self.manager = manager

    def install(self):
        ws = TestWorkspace()
        ws.__parent__ = self.manager

        return ws

    get = install

    def uninstall(self):
        pass

    def isInstalled(self):
        return True

    def isAvailable(self):
        return True


class TestWorkspaceFactory2(TestWorkspaceFactory):

    def isAvailable(self):
        return False

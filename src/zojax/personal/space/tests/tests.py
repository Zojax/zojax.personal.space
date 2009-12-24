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
""" zojax.workspace.manager tests

$Id$
"""
import os.path
import os, unittest, doctest
from zope import interface, component, schema
from zope.component import provideUtility, provideAdapter, provideHandler
from zope.app.rotterdam import Rotterdam
from zojax.filefield.testing import ZCMLLayer, FunctionalDocFileSuite
from zojax.layoutform.interfaces import ILayoutFormLayer

from zope.app.testing import setup
from zope.copypastemove import ObjectMover, ContainerItemRenamer
from zope.component.interface import provideInterface
from zope.app.component.site import SiteManagerContainer
from zope.security.interfaces import IPrincipal
from zope.traversing.interfaces import IPathAdapter
from zope.app.security.interfaces import IAuthentication
from zope.app.security.interfaces import IUnauthenticatedPrincipal

from zojax.security import utils
from zojax.ownership.owner import Ownership
from zojax.ownership.interfaces import IOwnerAware
from zojax.layoutform.interfaces import ILayoutFormLayer

from zojax.content.type.item import Item
from zojax.content.type.testing import setUpContents
from zojax.content.type.container import ContentContainer
from zojax.content.type.interfaces import IContentTypeType
from zojax.content.type.interfaces import IContainerContentsAware

from zojax.personal.space import interfaces, manager, space


class IDefaultSkin(ILayoutFormLayer, Rotterdam):
    """ skin """


class IPortal(interface.Interface):
    """ """


class Portal(ContentContainer, SiteManagerContainer):
    interface.implements(IPortal, IContainerContentsAware)


class Principal(object):
    interface.implements(IPrincipal)

    def __init__(self, id, title, description=''):
        self.id = id
        self.title = title
        self.description = description


class Auth(object):
    interface.implements(IAuthentication)

    principals = {'prin1': Principal('prin1', 'Principal 1'),
                  'prin2': Principal('prin2', 'Principal 2'),
                  'prin3': Principal('prin3', 'Principal 3'),
                  'prin4': Principal('prin4', 'Principal 4'),
                  'anon': Principal('anon', 'Anonymous')}
    interface.directlyProvides(principals['anon'], IUnauthenticatedPrincipal)

    def getPrincipal(self, id):
        return self.principals[id]


oldMethod = None
def checkPermissionForPrincipal(principal, permission, object):
    return True

def setUp(test):
    setup.placelessSetUp()
    setUpContents()

    provideUtility(Auth())
    provideAdapter(Ownership)
    provideAdapter(manager.getPersonalSpace)
    provideHandler(manager.personalSpaceMoved)
    provideHandler(manager.principalRemovingHandler)
    provideUtility(manager.PersonalSpaceService(), name="zojax.personal.space")

    provideAdapter(ObjectMover)
    provideAdapter(ContainerItemRenamer)

    interface.classImplements(space.PersonalSpace, IOwnerAware)

    global oldMethod
    oldMethod = utils.checkPermissionForPrincipal.func_code
    utils.checkPermissionForPrincipal.func_code = checkPermissionForPrincipal.func_code

def tearDown(test):
    utils.checkPermissionForPrincipal.func_code = oldMethod
    setup.placelessTearDown()


zojaxPersonalSpaceLayer = ZCMLLayer(
    os.path.join(os.path.split(__file__)[0], 'ftesting.zcml'),
    __name__, 'zojaxPersonalSpaceLayer', allow_teardown=True)


def getPath(filename):
    return os.path.join(os.path.dirname(__file__), filename)


class PrincipalInformation(object):

    readonly = True
    firstname = u''
    lastname = u''
    email = u''

    def __init__(self, principal):
        self.principal = principal

    @property
    def title(self):
        return self.principal.title


class IDefaultSkin(ILayoutFormLayer, Rotterdam):
    """ skin """


def test_suite():
    return unittest.TestSuite((
            doctest.DocFileSuite(
                'manager.txt',
                setUp=setUp, tearDown=tearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
            FunctionalDocFileSuite(
                "ws.txt",
                optionflags=doctest.ELLIPSIS|doctest.NORMALIZE_WHITESPACE,
                layer = zojaxPersonalSpaceLayer),
            FunctionalDocFileSuite(
                "testbrowser.txt",
                optionflags=doctest.ELLIPSIS|doctest.NORMALIZE_WHITESPACE,
                layer = zojaxPersonalSpaceLayer)
            ))

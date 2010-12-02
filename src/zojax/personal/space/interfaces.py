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
""" zojax.workspace.manager interfaces

$Id$
"""
from zope import schema, interface
from zope.i18nmessageid import MessageFactory

from zojax.security.interfaces import IPermissionCategory
from zojax.content.type.interfaces import IItem
from zojax.widget.checkbox.field import CheckboxList
from zojax.content.space.interfaces import \
    ISpace, IWorkspace, IWorkspaceFactory, IWorkspacesManagement

_ = MessageFactory('zojax.personal.space')


class IPersonalSpace(ISpace):
    """ personal space """

    principal = interface.Attribute('Principal')

    principalId = interface.Attribute('Principal id')

    anonymous = interface.Attribute('Anonymous access')
    
    listing = interface.Attribute('List in people view')
    

class IPersonalSpaceType(interface.Interface):
    """ personal space content type """


class IPersonalSpaceSettings(interface.Interface):
    """ Personal space settings """

    title = schema.TextLine(
        title = _(u'Title'),
        description = _(u'Title of personal space'),
        required = True)

    description = schema.Text(
        title = _(u'Description'),
        description = _(u'Description of personal space'),
        required = False)

    anonymous = schema.Bool(
        title = _(u'Anonymous view'),
        description = _('Allow non-members to view my profile.'),
        default = True,
        required = False)
    
    listing = schema.Bool(
        title = _(u'List space in people view'),
        description = _('Allow listing this space in people view.'),
        default = True,
        required = False)

    space = interface.Attribute('Personal space')
    manager = interface.Attribute('Members space')
    shortname = interface.Attribute('Personal space short name')

    def changeShortName(name):
        """Change short name."""


class IPersonalWorkspaceDescription(interface.Interface):
    """ personal workspace description """

    name = interface.Attribute('Workspace name')

    title = schema.TextLine(
        title = _(u'Title'),
        description = _(u'Title of personal space workspace'),
        required = True)

    description = schema.Text(
        title = _(u'Description'),
        description = _(u'Description of personal space workspace'),
        required = False)

    def createTemp(context):
        """ create temporal workspace object """


class IPersonalWorkspacePortlet(interface.Interface):
    """ personal workspace portlet type """


class IPersonalSpaceManager(IItem, IWorkspace):
    """ space manager """

    pagecount = schema.Int(
        title = _('Page count'),
        description = _('Number of people per page.'),
        default = 15,
        required = True)

    searching = schema.Bool(
        title = _('Allow searching'),
        default = True,
        required = True)

    def createSpace(title):
        """ clreate personal space for principal """

    def canAssignPrincipal(principal):
        """ can create assign principal """

    def assignPersonalSpace(principalId, name=None):
        """ addign personal space """

    def unassignPersonalSpace(principalId, delete=True):
        """ unassign personal space """

    def getPersonalSpace(principal):
        """ return personal space for principal object """

    def getPersonalSpaceById(principalId):
        """ return personal space for principal id """

    def getPrincipal(space):
        """ get principal for space name """


class IPersonalSpaceManagerWorkspace(IWorkspaceFactory):
    """ space manager workspace """


class IPersonalWorkspacesManagement(IWorkspacesManagement):
    """ workspace management """

    workspaces = CheckboxList(
        title = _(u'Workspaces'),
        description = _(u'Select workspaces for personal space.'),
        vocabulary = 'personal.space.workspaces',
        default = [],
        required = False)

    enabledWorkspaces = schema.List(
        title = _('Workspaces sorting and visibility'),
        description = _('Configure what workspaces have to be shown and in what order'),
        value_type = schema.Choice(
            vocabulary='personal.space.enabledworkspaces'),
        default = [],
        required = False)

    defaultWorkspace = schema.Choice(
        title = _(u'Default workspace'),
        description = _(u'Select default workspace for personal space.'),
        vocabulary = 'personal.space.enabledworkspaces',
        required = False,
        default = 'profile')


# permission category

class IPersonalPermission(IPermissionCategory):
    """ Personal workspaces permissions """

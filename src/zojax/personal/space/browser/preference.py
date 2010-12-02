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
from zope import interface, schema, component, event
from zope.component import getMultiAdapter
from zope.traversing.browser import absoluteURL
from zope.exceptions.interfaces import UserError
from zope.app.container.interfaces import INameChooser
from zope.lifecycleevent import ObjectModifiedEvent

from z3c.form import validator, interfaces

from zojax.layoutform import Fields, PageletEditForm
from zojax.personal.space.interfaces import _
from zojax.personal.space.interfaces import IPersonalSpaceManager
from zojax.personal.space.interfaces import IPersonalSpaceSettings


class IWorkspaceName(IPersonalSpaceSettings):

    shortname = schema.TextLine(
        title = _(u'Short Name'),
        description = _(u'Should not contain spaces, underscores or mixed case. '
                        "Short Name is part of the item's web address."),
        required = True)


class PersonalSpaceSettings(PageletEditForm):

    fields = Fields(IWorkspaceName)

    @property
    def prefix(self):
        return str(self.context.__id__)

    @property
    def label(self):
        return self.context.__title__

    @property
    def description(self):
        return self.context.__description__

    def getContent(self):
        context = self.context

        return {'title': context.title,
                'description': context.description,
                'shortname': context.shortname,
                'anonymous': context.anonymous,
                'listing': context.listing}

    shortName = None

    def applyChanges(self, data):
        context = self.context

        context.title = data['title']
        context.description = data['description']
        context.anonymous = data['anonymous']
        context.listing = data['listing']

        if context.shortname != data['shortname']:
            self.shortName = data['shortname']
            context.changeShortName(data['shortname'])

        event.notify(ObjectModifiedEvent(context.space))
        return True

    def nextURL(self):
        if self.shortName:
            ws = self.context
            parent = []
            while not IPersonalSpaceManager.providedBy(ws):
                parent.append(ws.__name__)
                ws = getattr(ws, '__parent__', None)
                if ws is None:
                    return u''

            url = absoluteURL(self.context.manager, self.request)
            parent.reverse()
            return '%s/%s/'%(url, '/'.join(parent))

        return ''


class NameError(schema.ValidationError):
    __doc__ = _(u'Content name already in use.')

    def __init__(self, msg):
        self.__doc__ = msg


class ContentNameValidator(validator.InvariantsValidator):
    component.adapts(
        interface.Interface,
        interface.Interface,
        PersonalSpaceSettings,
        interface.Interface,
        interface.Interface)

    def validate(self, data):
        form = self.view
        context = form.context
        shortname = data['shortname']
        widget = form.widgets['shortname']

        if widget.error or shortname == context.shortname:
            return super(ContentNameValidator, self).validate(data)

        errors = []

        chooser = INameChooser(context.manager)
        try:
            chooser.checkName(shortname, None)
        except UserError, err:
            exc = NameError(unicode(err))

            widget.error = getMultiAdapter(
                (exc, self.request, widget, widget.field, form, self.context),
                interfaces.IErrorViewSnippet)
            widget.error.update()
            errors.append(exc)

        return tuple(errors) + super(ContentNameValidator, self).validate(data)

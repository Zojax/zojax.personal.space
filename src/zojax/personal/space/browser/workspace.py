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
from zope import interface, event, schema
from zope.proxy import removeAllProxies
from zope.component import getMultiAdapter, getUtility
from zope.lifecycleevent import Attributes, ObjectModifiedEvent

from z3c.form.interfaces import IDataManager, IErrorViewSnippet

from zojax.layoutform import Fields
from zojax.wizard.step import WizardStepForm
from zojax.wizard.interfaces import ISaveable

from zojax.personal.space.interfaces import _, IPersonalWorkspacesManagement


class WorkspacesManagement(WizardStepForm):
    interface.implements(ISaveable)

    title = _('Workspaces')
    label = _('Workspaces management')

    fields = Fields(IPersonalWorkspacesManagement)

    def extractData(self, setErrors=True):
        data, errors = super(
            WorkspacesManagement, self).extractData(setErrors=setErrors)

        errs = []
        for error in errors:
            if IErrorViewSnippet.providedBy(error) and \
                    removeAllProxies(error).field.__name__=='enabledWorkspaces':
                continue
            errs.append(error)

        return data, tuple(errs)

    def applyChanges(self, data):
        content = self.getContent()
        enabled = getUtility(schema.interfaces.IVocabularyFactory, \
                             'personal.space.enabledworkspaces')(self.context)

        changes = {}
        for name in ('workspaces', 'defaultWorkspace', 'enabledWorkspaces'):
            if name not in data:
                continue

            field = self.fields[name]

            dm = getMultiAdapter((content, field.field), IDataManager)
            try:
                value = dm.get()
            except:
                value = object()

            if name == 'enabledWorkspaces' and data[name]:
                data[name] = [val for val in data[name] if val in enabled]

            if name == 'defaultWorkspace' and data[name]:
                if data[name] not in enabled:
                    for term in enabled:
                        data[name] = term.value
                        break

            if value != data[name]:
                dm.set(data[name])
                changes.setdefault(dm.field.interface, []).append(name)

        if changes:
            descriptions = []
            for interface, names in changes.items():
                descriptions.append(Attributes(interface, *names))

            event.notify(ObjectModifiedEvent(content, *descriptions))

        self.update()

        return changes

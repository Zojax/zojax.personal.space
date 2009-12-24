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
from zope.i18n import translate
from zojax.content.browser.breadcrumb import ContentBreadcrumb
from zojax.principal.profile.interfaces import IPersonalProfile
from zojax.personal.space.interfaces import IPersonalSpace


class PersonalSpaceBreadcrumb(ContentBreadcrumb):
    component.adapts(IPersonalSpace, interface.Interface)

    @property
    def name(self):
        principal = self.context.principal

        if principal.id == self.request.principal.id:
            return translate(u'My personal space', 'zojax.personal.space')
        else:
            title = IPersonalProfile(principal).title or principal.id
            return translate("${user_title}'s space", 'zojax.personal.space',
                             mapping={'user_title': title})

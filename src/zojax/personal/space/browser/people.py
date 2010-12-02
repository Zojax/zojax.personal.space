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
from zope.component import getUtility
from zope.index.text.parsetree import ParseError

from zojax.batching.batch import Batch
from zojax.statusmessage.interfaces import IStatusMessage
from zojax.catalog.interfaces import ICatalog
from zojax.filefield.interfaces import IImage
from zojax.ownership.interfaces import IOwnership
from zojax.principal.profile.interfaces import IPersonalProfile

from zojax.personal.space.interfaces import _, IPersonalSpace


class PeopleView(object):

    batch = ()

    def update(self):
        context = self.context
        request = self.request

        self.hasSpaces = bool(len(context)) and context.searching

        if 'form.search.clear' in request:
            self.redirect('./index.html')
            return

        catalog = getUtility(ICatalog)

        if 'form.search' in request:
            s = request.get('form.searchText', u'').strip()
            if s:
                query = {
                    'type': {'any_of': ('personal.space',)},
                    'searchableText': s,
                    'listInPeopleView': {'any_of':(True,)},
                    'searchContext':(context,),
                    'sort_on': 'title'}

                try:
                    results = catalog.searchResults(**query)
                except ParseError, e:
                    IStatusMessage(request).add(e, 'error')
                    return

                self.batch = Batch(results, size=context.pagecount,
                                   context=context, request=request)
            else:
                IStatusMessage(request).add(
                    _('Please enter one or more words for search.'), 'warning')
            return

        results = getUtility(ICatalog).searchResults(
            type = {'any_of': ('personal.space',)},
            listInPeopleView = {'any_of':(True,)},
            searchContext = (context,), sort_on='title')

        self.batch = Batch(results, size=context.pagecount,
                           context=context, request=request)

    def getMemberInfo(self, hf):
        if IPersonalSpace.providedBy(hf):
            principal = hf.principal
        else:
            principal = getattr(IOwnership(hf, None), 'owner', None)
            if principal is None:
                return
        try:
            profile = IPersonalProfile(principal)
        except TypeError:
            return

        image = profile.profileImage
        if IImage.providedBy(image) and image:
            w, h = image.width, image.height
            if w > 128:
                xscale = 128.0/w
            else:
                xscale = 1.0
            if h > 120:
                yscale = 120.0/h
            else:
                yscale = 1.0
            scale = xscale < yscale and xscale or yscale
            image = (int(round(w*scale)), int(round(h*scale)))
            default = False
        else:
            image = (128, 98)
            default = True

        info = {
            'id': hf.__name__,
            'title': profile.title,
            'description': principal.description,
            'manager': hf.title,
            'joined': profile.registered,
            'imagex': image[0],
            'imagey': image[1],
            'default': default,
            'photo': profile.photoUrl(self.request)}
        return info

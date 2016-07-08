from AccessControl import getSecurityManager
from Acquisition import aq_inner
from Acquisition import aq_parent
from euphorie.content.api.entry import access_api
from euphorie.content.countrymanager import ICountryManager
from euphorie.content.interfaces import IEuphorieContentSkinLayer
from five import grok
from plonetheme.nuplone.skin.interfaces import NuPloneSkin
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.membrane.interfaces.user import IMembraneUser
from zope.component import adapts
from zope.interface import directlyProvidedBy
from zope.interface import directlyProvides
from zope.publisher.interfaces.browser import IBrowserSkinType
from ZPublisher.BaseRequest import DefaultPublishTraverse


class Frontpage(grok.View):
    grok.context(IPloneSiteRoot)
    grok.layer(IEuphorieContentSkinLayer)
    grok.name("nuplone-view")
    grok.require("zope2.View")

    def render(self):
        user = getSecurityManager().getUser()
        if IMembraneUser.providedBy(user):
            mt = getToolByName(self.context, "membrane_tool")
            obj = mt.getUserObject(user_id=user.getUserId())
            if ICountryManager.providedBy(obj):
                self.request.response.redirect(aq_parent(obj).absolute_url())
            else:
                self.request.response.redirect(obj.absolute_url())
        else:
            portal = aq_inner(self.context)
            self.request.response.redirect(
                    "%s/sectors/" % portal.absolute_url())


class SitePublishTraverser(DefaultPublishTraverse):
    """Publish traverser to manage access to the CMS API.

    This traverser marks the request with IEuphorieContentSkinLayer. We cannot
    use BeforeTraverseEvent since in Zope2 that is only fired for site objects.
    """
    adapts(IPloneSiteRoot, NuPloneSkin)

    def publishTraverse(self, request, name):
        if name == 'api':
            return access_api(request).__of__(self.context)
        ifaces = [iface for iface in directlyProvidedBy(request)
                  if not IBrowserSkinType.providedBy(iface)]
        directlyProvides(request, IEuphorieContentSkinLayer, ifaces)
        return super(SitePublishTraverser, self)\
                .publishTraverse(request, name)

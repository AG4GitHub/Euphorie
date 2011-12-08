from zope.interface import Interface
from zope.component import queryMultiAdapter
from plone.dexterity.fti import DexterityFTI


class IConstructionFilter(Interface):
    """Extra object creation checks.

    This is used by :obj:`ConditionalDexterityFTI` as a named multi-adapter,
    adapting the FTI and the container using the name of the portal_type.
    """

    def __init__(fti, container):
        """Adapt on the FTI of the object being created and the target container"""

    def allowed():
        """Check if construction is allowed."""


class ConditionalDexterityFTI(DexterityFTI):
    """Special FTI which supports configurable object creation constrains.

    CMF calls to :obj:`isConstructionAllowed` method of the FTI to
    determine of an object of a type can be constructed. In euphorie
    we have some restrictions that only hold for a specific portal type,
    so we need an extension point that can configured per portal type.
    This is done by introducing a new :obj:`IConstructionFilter` named
    adapter.
    """
    def isConstructionAllowed(self, container):
        if not super(ConditionalDexterityFTI, self).isConstructionAllowed(container):
            return False

        filter=queryMultiAdapter((self, container), IConstructionFilter, self.getId())
        if filter is not None:
            return filter.allowed()

        return True


# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""Set up module."""

##############################################################################
# IMPORTS

from __future__ import absolute_import

__all__ = ["HAS_AGAMA", "HAS_GALPY"]


##############################################################################
# PARAMETERS

try:
    # THIRD PARTY
    import agama  # noqa: F401
except ImportError:
    HAS_AGAMA = False
else:
    HAS_AGAMA = True

# -------------------------------------

try:
    # THIRD PARTY
    import galpy  # noqa: F401
except ImportError:
    HAS_GALPY = False
else:
    HAS_GALPY = True

    # TODO better way of ensuring unit!
    # THIRD PARTY
    from galpy.util.config import __config__

    __config__.set("astropy", "astropy-units", "True")
    __config__.set("astropy", "astropy-coords", "True")


##############################################################################
# END

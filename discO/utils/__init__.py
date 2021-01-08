# -*- coding: utf-8 -*-
# see LICENSE.rst

"""Utilities."""

__all__ = [
    "resolve_frame_like",
]


##############################################################################
# IMPORTS

# BUILT-IN
import typing as T

# THIRD PARTY
from astropy.coordinates import (
    BaseCoordinateFrame,
    SkyCoord,
    sky_coordinate_parsers,
)

# PROJECT-SPECIFIC
from discO.common import FrameLikeType
from discO.config import conf

##############################################################################
# CODE
##############################################################################


def resolve_frame_like(
    frame: T.Optional[FrameLikeType], error_if_not_type: bool = True
):
    """Determine the frame and return a blank instance.

    .. todo::

        should this be in skycoord.utils? (but conf)

        This as a decorator, so it autoresolves

    Parameters
    ----------
    frame : frame-like instance or None (optional)
        If BaseCoordinateFrame, replicates without data.
        If str, uses astropy parsers to determine frame class
        If None (default), gets default frame name from config, and parses.

    error_if_not_type : bool
        Whether to raise TypeError if `frame` is not one of the allowed types.

    Returns
    -------
    frame : `~astropy.coordinates.BaseCoordinateFrame` instance
        Replicated without data.

    """
    # If no frame is specified, assume that the input footprint is in a
    # frame specified in the configuration
    if frame is None:
        name: str = conf.default_frame
        frame = sky_coordinate_parsers._get_frame_class(name.lower())()
    elif isinstance(frame, str):
        frame = sky_coordinate_parsers._get_frame_class(frame.lower())()
    elif isinstance(frame, BaseCoordinateFrame):
        frame = frame.replicate_without_data()
    elif isinstance(frame, SkyCoord):
        frame = frame.frame.replicate_without_data()

    elif error_if_not_type:
        raise TypeError(
            "Input coordinate frame must be an astropy "
            "coordinates frame subclass *instance*, not a "
            "'{}'".format(frame.__class__.__name__)
        )

    return frame


# /def


##############################################################################
# END
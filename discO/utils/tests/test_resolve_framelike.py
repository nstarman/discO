# -*- coding: utf-8 -*-

"""Testing :mod:`~discO.utils`."""

__all__ = [
    "Test_resolve_framelike",
]


##############################################################################
# IMPORTS

# THIRD PARTY
import astropy.coordinates as coord
import astropy.units as u
import pytest

# PROJECT-SPECIFIC
from discO.config import conf
from discO.utils import resolve_framelike

##############################################################################
# TESTS
##############################################################################


class Test_resolve_framelike:
    """Test function :func:`~discO.utils.resolve_framelike`."""

    def test_frame_is_none(self):
        """Test when frame is None."""
        # basic usage
        assert resolve_framelike(frame=None) == resolve_framelike(
            frame=conf.default_frame
        )

        # test changes with conf
        with conf.set_temp("default_frame", "galactocentric"):

            assert resolve_framelike(frame=None) == resolve_framelike(
                frame=conf.default_frame
            )

    # /def

    def test_frame_is_str(self):
        """Test when frame is a string."""
        # basic usage
        assert resolve_framelike(frame="icrs") == coord.ICRS()

    # /def

    def test_frame_is_BaseCoordinateFrame(self):
        """Test when frame is a BaseCoordinateFrame."""
        # basic usage
        assert resolve_framelike(frame=coord.ICRS()) == coord.ICRS()

        # replicates without data
        c = coord.ICRS(ra=1 * u.deg, dec=2 * u.deg)
        assert resolve_framelike(frame=c) == coord.ICRS()

    # /def

    def test_frame_is_SkyCoord(self):
        """Test when frame is a SkyCoord."""
        c = coord.ICRS(ra=1 * u.deg, dec=2 * u.deg)
        sc = coord.SkyCoord(c)

        # basic usage
        assert resolve_framelike(frame=sc) == coord.ICRS()

    # /def

    def test_error_if_not_type(self):
        """Test when frame is a SkyCoord."""

        # raise error if pass bad argument type
        with pytest.raises(TypeError):
            resolve_framelike(Exception, error_if_not_type=True)

        # check this is the default behavior
        with pytest.raises(TypeError):
            resolve_framelike(Exception)

        # check it doesn't error if
        assert (
            resolve_framelike(Exception, error_if_not_type=False) is Exception
        )

    # /def


# /class


# -------------------------------------------------------------------


##############################################################################
# END
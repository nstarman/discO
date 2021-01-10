# -*- coding: utf-8 -*-
"""Configure Test Suite.

This file is used to configure the behavior of pytest when using the Astropy
test infrastructure. It needs to live inside the package in order for it to
get picked up when running the tests inside an interpreter using
packagename.test

"""

##############################################################################
# IMPORTS

# BUILT-IN
import os

# THIRD PARTY
import pytest
from astropy.version import version as astropy_version

# PROJECT-SPECIFIC
from .setup_package import HAS_AGAMA, HAS_GALPY

# For Astropy 3.0 and later, we can use the standalone pytest plugin
if astropy_version < "3.0":
    from astropy.tests.pytest_plugins import *  # noqa

    del pytest_report_header
    ASTROPY_HEADER = True

else:
    try:
        from pytest_astropy_header.display import (
            PYTEST_HEADER_MODULES,
            TESTED_VERSIONS,
        )

        ASTROPY_HEADER = True
    except ImportError:
        ASTROPY_HEADER = False

# /if

##############################################################################
# CODE
##############################################################################


# ------------------------------------------------------
# Test collection: ignore patterns

collect_ignore = ["setup.py"]

# AGAMA
SKIP_NO_AGAMA = pytest.mark.skipif(not HAS_AGAMA, reason="needs agama")
if not HAS_AGAMA:
    collect_ignore.append("extern/agama/")

# Galpy
SKIP_NO_GALPY = pytest.mark.skipif(not HAS_GALPY, reason="needs galpy")
if not HAS_GALPY:
    collect_ignore.append("extern/galpy/")


# ------------------------------------------------------


def pytest_configure(config):
    """Configure Pytest with Astropy.

    Parameters
    ----------
    config : pytest configuration

    """
    if ASTROPY_HEADER:

        config.option.astropy_header = True

        # Customize the following lines to add/remove entries from the list of
        # packages for which version numbers are displayed when running the
        # tests.
        PYTEST_HEADER_MODULES.pop("Pandas", None)
        PYTEST_HEADER_MODULES["scikit-image"] = "skimage"

        # PROJECT-SPECIFIC
        from . import __version__

        packagename = os.path.basename(os.path.dirname(__file__))
        TESTED_VERSIONS[packagename] = __version__


# /def


# ------------------------------------------------------


@pytest.fixture(autouse=True)
def add_numpy(doctest_namespace):
    """Add NumPy to Pytest.

    Parameters
    ----------
    doctest_namespace : namespace

    """
    # THIRD PARTY
    import numpy

    # add to namespace
    doctest_namespace["np"] = numpy

    return


# def


@pytest.fixture(autouse=True)
def add_astropy(doctest_namespace):
    """Add Astropy stuff to Pytest.

    Parameters
    ----------
    doctest_namespace : namespace

    """
    # THIRD PARTY
    import astropy.coordinates as coord
    import astropy.units

    # add to namespace
    doctest_namespace["coord"] = coord
    doctest_namespace["u"] = astropy.units

    return


# def


# ------------------------------------------------------


# Uncomment the last two lines in this block to treat all DeprecationWarnings
# as exceptions. For Astropy v2.0 or later, there are 2 additional keywords,
# as follow (although default should work for most cases).
# To ignore some packages that produce deprecation warnings on import
# (in addition to 'compiler', 'scipy', 'pygments', 'ipykernel', and
# 'setuptools'), add:
#     modules_to_ignore_on_import=['module_1', 'module_2']
# To ignore some specific deprecation warning messages for Python version
# MAJOR.MINOR or later, add:
#     warnings_to_ignore_by_pyver={(MAJOR, MINOR): ['Message to ignore']}
# from astropy.tests.helper import enable_deprecations_as_exceptions  # noqa
# enable_deprecations_as_exceptions()

##############################################################################
# END

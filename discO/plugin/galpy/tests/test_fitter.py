# -*- coding: utf-8 -*-

"""Testing :mod:`~discO.plugin.galpy.fitter`."""

__all__ = [
    "Test_GalpyPotentialFitter",
    "Test_GalpySCFPotentialFitter",
]


##############################################################################
# IMPORTS

# THIRD PARTY
import pytest
from galpy import potential as gpot

# PROJECT-SPECIFIC
from discO.core.tests.test_fitter import (
    Test_PotentialFitter as PotentialFitterTester,
)
from discO.plugin.galpy import GalpyPotentialWrapper, fitter

##############################################################################
# TESTS
##############################################################################


class Test_GalpyPotentialFitter(
    PotentialFitterTester,
    obj=fitter.GalpyPotentialFitter,
):
    @classmethod
    def setup_class(cls):
        """Setup fixtures for testing."""
        cls.potential = gpot.Potential

        # register a unittest examples
        class SubClassUnitTest(cls.obj, key="unittest"):
            def __init__(
                self,
                potential_cls,
                frame=None,
                **kwargs,
            ):
                super().__init__(
                    potential_cls=potential_cls, frame=frame, **kwargs
                )

            # /defs

            def __call__(self, c, **kwargs):
                return GalpyPotentialWrapper(
                    gpot.Potential(),
                    frame=self.frame,
                )

            # /def

        cls.SubClassUnitTest = SubClassUnitTest
        # /class

        # make instance. It depends.
        if cls.obj is fitter.GalpyPotentialFitter:
            cls.inst = cls.obj(potential_cls=cls.potential, key="unittest")

    # /def

    #################################################################
    # Method Tests

    def test___new__(self):
        """Test method ``__new__``.

        This is a wrapper class that acts differently when instantiating
        a MeasurementErrorSampler than one of it's subclasses.

        """
        # there are no tests on super
        # super().test___new__()

        # --------------------------
        if self.obj is fitter.GalpyPotentialFitter:

            # --------------------------
            # for object not in registry

            with pytest.raises(ValueError) as e:
                self.obj(potential_cls=None, key=None)

            assert (
                "PotentialFitter has no registered fitter for key: None"
            ) in str(e.value)

            # ---------------
            # as wrapper

            klass = self.obj._registry["unittest"]

            msamp = self.obj(potential_cls=gpot.Potential, key="unittest")

            # test class type
            assert isinstance(msamp, klass)
            assert isinstance(msamp, self.obj)

            # test inputs
            assert msamp._fitter == self.potential

        # --------------------------
        else:  # never hit in Test_PotentialSampler, only in subs

            # ---------------
            # AOK

            msamp = self.obj()

            assert self.obj is not fitter.PotentialFitter
            assert isinstance(msamp, self.obj)
            assert isinstance(msamp, fitter.PotentialFitter)
            assert not hasattr(msamp, "_instance")
            assert msamp._fitter == self.potential

    # /def

    # -------------------------------

    def test___call__(self):
        """Test method ``__call__``."""
        # run tests on super
        super().test___call__()

        # TODO! actually run tests

    # /def


# /class


# -------------------------------------------------------------------


class Test_GalpySCFPotentialFitter(
    Test_GalpyPotentialFitter,
    obj=fitter.GalpySCFPotentialFitter,
):
    @classmethod
    def setup_class(cls):
        """Setup fixtures for testing."""
        super().setup_class()
        cls.potential = gpot.SCFPotential
        cls.inst = cls.obj()

    # /def

    # -------------------------------

    def test___call__(self):
        """Test method ``__call__``."""
        # run tests on super
        super().test___call__()

        # TODO! actually run tests

    # /def


# /class


##############################################################################
# END

# -*- coding: utf-8 -*-

"""Testing :mod:`~discO.plugin.agama.fitter`."""

__all__ = [
    "Test_AGAMAPotentialFitter",
    "Test_AGAMAMultipolePotentialFitter",
]


##############################################################################
# IMPORTS

# THIRD PARTY
import agama
import pytest

# PROJECT-SPECIFIC
from discO.core.tests.test_fitter import (
    Test_PotentialFitter as PotentialFitterTester,
)
from discO.plugin.agama import fitter

##############################################################################
# TESTS
##############################################################################


class Test_AGAMAPotentialFitter(
    PotentialFitterTester,
    obj=fitter.AGAMAPotentialFitter,
):
    @classmethod
    def setup_class(cls):
        """Setup fixtures for testing."""
        cls.potential = agama.Potential

        # register a unittest examples
        class SubClassUnitTest(cls.obj, key="unittest"):
            def __init__(
                self,
                symmetry="a",
                **kwargs,
            ):
                kwargs.pop("pot_type", None)  # clear from kwargs
                super().__init__(
                    pot_type="Multipole",
                    symmetry="a",
                    gridsizeR=20,
                    lmax=2,
                    **kwargs,
                )

            # /defs

        cls.SubClassUnitTest = SubClassUnitTest

        # make instance. It depends.
        if cls.obj is fitter.AGAMAPotentialFitter:
            cls.inst = cls.obj(pot_type="unittest", symmetry="a")

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
        if self.obj is fitter.AGAMAPotentialFitter:

            # --------------------------
            # for object not in registry

            with pytest.raises(ValueError) as e:
                self.obj(pot_type=None)

            assert (
                "PotentialFitter has no registered fitter for `pot_type`: None"
            ) in str(e.value)

            # ---------------
            # with return_specific_class

            klass = self.obj._registry["unittest"]

            msamp = self.obj(pot_type="unittest", return_specific_class=True)

            # test class type
            assert isinstance(msamp, klass)
            assert isinstance(msamp, self.obj)

            # test inputs
            assert msamp._fitter == self.potential

            # ---------------
            # as wrapper class

            klass = self.obj._registry["unittest"]

            msamp = self.obj(pot_type="unittest", return_specific_class=False)

            # test class type
            assert not isinstance(msamp, klass)
            assert isinstance(msamp, self.obj)
            assert isinstance(msamp._instance, klass)

            # test inputs
            assert msamp._fitter == self.potential

        # --------------------------
        else:  # never hit in Test_PotentialSampler, only in subs

            pot_type = tuple(self.obj._registry.keys())[0]

            # ---------------
            # Can't have the "key" argument

            with pytest.raises(ValueError) as e:
                self.obj(pot_type=pot_type, key="not None")

            assert "Can't specify 'pot_type'" in str(e.value)

            # ---------------
            # warning

            with pytest.warns(UserWarning):
                self.obj(
                    key=None,
                    return_specific_class=True,
                )

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


# /class


# -------------------------------------------------------------------


class Test_AGAMAMultipolePotentialFitter(
    Test_AGAMAPotentialFitter,
    obj=fitter.AGAMAMultipolePotentialFitter,
):
    @classmethod
    def setup_class(cls):
        """Setup fixtures for testing."""
        super().setup_class()
        cls.inst = cls.obj(symmetry="a")

    # /def


# /class


##############################################################################
# END

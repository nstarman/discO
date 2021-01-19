# -*- coding: utf-8 -*-

"""Testing :mod:`~discO.core.fitter`."""

__all__ = [
    "Test_PotentialFitter",
]


##############################################################################
# IMPORTS

# BUILT-IN
import inspect
from abc import abstractmethod

# THIRD PARTY
import astropy.coordinates as coord
import astropy.units as u
import numpy as np
import pytest

# PROJECT-SPECIFIC
from discO.core import fitter
from discO.core.tests.test_core import Test_PotentialBase as PotentialBase_Test

##############################################################################
# PARAMETERS

crd = coord.SkyCoord(
    coord.ICRS(
        ra=[
            269.77,
            211.53,
            135.49,
            3.85,
            42.11,
            212.56,
            203.11,
            61.49,
            344.11,
            98.63,
        ]
        * u.deg,
        dec=[
            -80.39242629,
            -3.67881258,
            -44.62636438,
            -7.46999137,
            -20.90390085,
            -64.15957604,
            -9.16456976,
            -33.66474899,
            -41.05292432,
            16.56923216,
        ]
        * u.deg,
        distance=[
            12.15818053,
            7.37721302,
            156.25820005,
            5.08874191,
            7.7856392,
            16.58761413,
            6.31741618,
            3.83061213,
            4.97326983,
            32.21408322,
        ]
        * u.kpc,
    ),
)
crd.mass = np.ones(10) * u.solMass

multicrd = crd.reshape((5, 2))
multicrd.mass = crd.mass.reshape((5, 2))


class FitterSubClass(fitter.PotentialFitter, key="test_discO"):
    def __call__(self, c, **kwargs):
        c.represent_as(coord.CartesianRepresentation)
        return object()

    # /def


# /class


##############################################################################
# PYTEST


def teardown_module(module):
    """Teardown any state that was previously set up."""
    FitterSubClass._registry.pop("test_discO", None)


# /def

##############################################################################
# TESTS
##############################################################################


class Test_PotentialFitter(PotentialBase_Test, obj=fitter.PotentialFitter):
    @classmethod
    def setup_class(cls):
        """Setup fixtures for testing."""
        cls.potential = object

        # register a unittest examples
        class SubClassUnitTest(cls.obj, key="unittest"):
            def __call__(self, c, **kwargs):
                c.represent_as(coord.CartesianRepresentation)
                return cls.potential()

        cls.SubClassUnitTest = SubClassUnitTest

        # make instance. It depends.
        if cls.obj is fitter.PotentialFitter:
            cls.inst = cls.obj(cls.potential, key="unittest")

    # /def

    @classmethod
    def teardown_class(cls):
        """Teardown fixtures for testing."""
        cls.SubClassUnitTest._registry.pop("unittest", None)

    # /def

    #################################################################
    # Method Tests

    def test___init_subclass__(self):
        """Test subclassing."""
        # When package is None, it is not registered
        class SubClass1(self.obj):
            pass

        assert None not in fitter.FITTER_REGISTRY
        assert SubClass1 not in fitter.FITTER_REGISTRY.values()

        # ------------------------
        # register a new
        try:

            class SubClass1(self.obj, key="pytest"):
                pass

        except Exception:
            pass
        finally:
            fitter.FITTER_REGISTRY.pop("pytest", None)

        # -------------------------------
        # error when already in registry

        try:
            # registered
            class SubClass1(self.obj, key="pytest"):
                pass

            # doing it again raises error
            with pytest.raises(KeyError):

                class SubClass1(self.obj, key="pytest"):
                    pass

        except Exception:
            pass
        finally:  # cleanup
            fitter.FITTER_REGISTRY.pop("pytest", None)

    # /def

    # -------------------------------

    def test__registry(self):
        """Test method ``_registry``.

        As ``_registry`` is never overwritten in the subclasses, this test
        should carry though.

        """
        # run tests on super
        super().test__registry()

        # -------------------------------
        assert isinstance(self.obj._registry, dict)

        # The unittest is already registered, so can
        # test for that.
        assert "unittest" in self.obj._registry.keys()
        assert self.SubClassUnitTest in self.obj._registry.values()
        assert self.obj._registry["unittest"] is self.SubClassUnitTest

    # /def

    # -------------------------------

    def test___class_getitem__(self):
        """Test method ``__class_getitem__``."""
        # run tests on super
        super().test___class_getitem__()

        # -------------------------------
        # test a specific item in the registry
        assert self.obj["unittest"] is self.SubClassUnitTest

    # /def

    # -------------------------------

    def test___new__(self):
        """Test method ``__new__``.

        This is a wrapper class that acts differently when instantiating
        a MeasurementErrorSampler than one of it's subclasses.

        """
        # there are no tests on super
        # super().test___new__()

        # --------------------------
        if self.obj is fitter.PotentialFitter:

            # ---------------
            # Need the "potential" argument
            with pytest.raises(TypeError) as e:
                self.obj()

            assert (
                "missing 1 required positional argument: 'potential_cls'"
            ) in str(e.value)

            # --------------------------
            # for object not in registry

            with pytest.raises(ValueError) as e:
                self.obj(self.potential())

            assert (
                "PotentialFitter has no registered fitter for key: builtins"
            ) in str(e.value)

            # ---------------
            # with return_specific_class

            klass = self.obj._registry["unittest"]

            msamp = self.obj(
                self.potential,
                key="unittest",
                return_specific_class=True,
            )

            # test class type
            assert isinstance(msamp, klass)
            assert isinstance(msamp, self.obj)

            # test inputs
            assert msamp._fitter == self.potential

            # ---------------
            # as wrapper class

            klass = self.obj._registry["unittest"]

            msamp = self.obj(
                self.potential,
                key="unittest",
                return_specific_class=False,
            )

            # test class type
            assert not isinstance(msamp, klass)
            assert isinstance(msamp, self.obj)
            assert isinstance(msamp._instance, klass)

            # test inputs
            assert msamp._fitter == self.potential

        # --------------------------
        else:  # never hit in Test_PotentialSampler, only in subs

            # ---------------
            # Can't have the "key" argument

            with pytest.raises(ValueError) as e:
                sig = inspect.signature(self.obj)
                ba = sig.bind_partial(
                    potential_cls=self.potential,
                    key="not None",
                )
                ba.apply_defaults()
                self.obj(*ba.args, **ba.kwargs)

            assert "Can't specify 'key'" in str(e.value)

            # ---------------
            # warning

            with pytest.warns(UserWarning):
                self.obj(
                    self.potential,
                    key=None,
                    return_specific_class=True,
                )

            # ---------------
            # AOK

            msamp = self.obj(self.potential, frame="icrs")

            assert self.obj is not fitter.PotentialFitter
            assert isinstance(msamp, self.obj)
            assert isinstance(msamp, fitter.PotentialFitter)
            assert not hasattr(msamp, "_instance")
            assert msamp._fitter == self.potential

    # /def

    # -------------------------------

    @abstractmethod
    def test___init__(self):
        """Test method ``__init__``."""
        # run tests on super
        super().test___init__()

        # --------------------------
        pass  # for subclasses. The setup_class actually tests this for here.

    # /def

    # -------------------------------

    def test___call__(self):
        """Test method ``__call__``.

        When Test_MeasurementErrorSampler this calls on the wrapped instance,
        which is GaussianMeasurementErrorSampler.

        We can't test the output, but can test that it "works".

        """
        # run tests on super
        super().test___call__()

    # /def

    # TODO! with hypothesis
    @pytest.mark.parametrize("sample", [crd])
    def test_call_parametrize(self, sample):
        """Parametrized call tests."""
        res = self.inst(sample)
        assert isinstance(res, self.potential)

    # /def

    # -------------------------------

    # TODO! with hypothesis
    @pytest.mark.parametrize("sample", [crd, multicrd])
    def test_fit(self, sample):
        """Test method ``fit``."""
        # for test need to assign correct potential type
        sample.potential = self.potential

        pots = self.inst.fit(sample)

        if len(sample.shape) == 1:
            assert isinstance(pots, sample.potential)

        else:
            assert isinstance(pots, np.ndarray)
            assert len(pots) == sample.shape[1]
            assert all([isinstance(p, sample.potential) for p in pots])

        # and then cleanup
        del sample.potential

    # /def


##############################################################################


# -------------------------------------------------------------------


class Test_PotentialFitter_SubClass(
    Test_PotentialFitter,
    obj=FitterSubClass,
):
    @classmethod
    def setup_class(cls):
        """Setup fixtures for testing."""
        super().setup_class()
        cls.inst = cls.obj(cls.potential)

    # /def


##############################################################################
# END
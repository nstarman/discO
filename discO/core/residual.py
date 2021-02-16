# -*- coding: utf-8 -*-

"""Residuals."""


__all__ = [
    "ResidualMethod",
    "GridResidual",
]


##############################################################################
# IMPORTS

# BUILT-IN
import abc
import typing as T
from types import MappingProxyType, ModuleType

# THIRD PARTY
import astropy.coordinates as coord

# PROJECT-SPECIFIC
import discO.type_hints as TH
from .core import CommonBase
from .wrapper import PotentialWrapper
from discO.utils.coordinates import resolve_representationlike

##############################################################################
# PARAMETERS

RESIDUAL_REGISTRY: T.Dict[str, object] = dict()  # key : sampler

##############################################################################
# CODE
##############################################################################


class ResidualMethod(CommonBase):
    """Calculate Residual.

    Parameters
    ----------
    original_potential : object or :class:`~discO.core.wrapper.PotentialWrapper`
        The original potential.
        In order to evaluate on a grid with a frame, should be a
        :class:`~discO.core.wrapper.PotentialWrapper`.

    observable : str (optional)

    representation_type : representation-resolvable (optional, keyword-only)
        The output representation type

    """

    #################################################################
    # On the class

    _registry = RESIDUAL_REGISTRY

    def __init_subclass__(cls, key: T.Union[str, ModuleType, None] = None):
        """Initialize subclass, adding to registry by `package`.

        This method applies to all subclasses, not matter the
        inheritance depth, unless the MRO overrides.

        """
        super().__init_subclass__(key=key)

        if key is not None:  # same trigger as CommonBase
            # cls._package defined in super()
            cls.__bases__[0]._registry[cls._key] = cls

        # TODO? insist that subclasses define a evaluate method
        # this "abstractifies" the base-class even though it can be used
        # as a wrapper class.

    # /def

    def __new__(cls, *args, method: T.Optional[str] = None, **kwargs):
        # The class ResidualMethod is a wrapper for anything in its registry
        # If directly instantiating a ResidualMethod (not subclass) we must
        # instead instantiate the appropriate subclass. Error if can't find.
        if cls is ResidualMethod:

            # a cleaner error than KeyError on the actual registry
            if method is None or not cls._in_registry(method):
                raise ValueError(
                    "ResidualMethod has no registered " f"method '{method}'",
                )

            # from registry. Registered in __init_subclass__
            kls = cls[method]
            return kls.__new__(kls, method=None, **kwargs)

        elif method is not None:
            raise ValueError(
                f"Can't specify 'method' on {cls.__name__}, "
                "only on ResidualMethod.",
            )

        return super().__new__(cls)

    # /def

    #################################################################
    # On the instance

    def __init__(
        self,
        *,
        original_potential: T.Optional[T.Any] = None,
        observable: str = "acceleration",  # TODO make None and have config
        representation_type: TH.OptRepresentationLikeType = None,
        **kwargs,
    ) -> None:
        kwargs.pop("method", None)
        self._observable: str = observable
        self._kwargs = MappingProxyType(kwargs)

        # representation type
        representation_type = (
            resolve_representationlike(representation_type)
            if not (
                representation_type is None or representation_type is Ellipsis
            )
            else representation_type
        )

        self._original_potential = PotentialWrapper(
            original_potential,
            # frame=frame,
            representation_type=representation_type,
        )

    # /def

    # ---------------------------------------------------------------

    @property
    def observable(self) -> str:
        """Observable."""
        return self._observable

    # /def

    @property
    def original_potential(self) -> PotentialWrapper:
        """Original potential."""
        return self._original_potential

    # /def

    @property
    def frame(self) -> TH.OptFrameType:
        """Representation Type."""
        return self.original_potential.frame

    # /def

    @property
    def representation_type(self) -> TH.OptRepresentationLikeType:
        """Representation Type."""
        return self.original_potential.representation_type

    # /def

    #################################################################
    # evaluate

    @abc.abstractmethod
    def evaluate_potential(
        self,
        potential: T.Union[PotentialWrapper, T.Any],
        observable: T.Optional[str] = None,
        points: T.Optional[TH.RepresentationType] = None,
        *,
        representation_type: TH.OptRepresentationLikeType = None,
        **kwargs,
    ) -> object:
        """Evaluate method on potential.

        Parameters
        ----------
        potential : object
        observable : str
            method in :class:`~PotentialWrapper`
        points : `~astropy.coordinates.BaseRepresentation` or None (optional)
            The points of the grid.
        **kwargs
            Passed to method in :class:`~PotentialWrapper`.

        Returns
        -------
        object

        """
        raise NotImplementedError("Must run on subclass.")

    # /def

    # -----------------------------------------------------

    def __call__(
        self,
        fit_potential: T.Any,
        original_potential: T.Optional[T.Any] = None,
        observable: T.Optional[str] = None,
        *,
        representation_type: TH.OptRepresentationLikeType = None,
        **kwargs,
    ) -> object:
        """Calculate Residual.

        Parameters
        ----------
        fit_potential : object or :class:`~discO.core.wrapper.PotentialWrapper`
            The fit potential.

        observable : str or None (optional)
            The quantity on which to calculate the residual.
            Must be method of :class:`~discO.core.wrapper.PotentialWrapper`.
            None (default) becomes the default value at initialization.

        representation_type: representation-resolvable (optional, keyword-only)
            The output representation type.

        Returns
        -------
        residual : object
            In `representation_type`.

        """
        # kwargs, mix in defaults, overriding with passed.
        kw = dict(self._kwargs.items())
        kw.update(kwargs)

        # potential
        original_potential = original_potential or self.original_potential
        if original_potential is None:  # both passed and init are None
            raise ValueError("`original_potential` not set. Need to pass.")

        observable = observable or self.observable
        if observable is None:  # TODO get from config
            raise ValueError("`observable` not set. Need to pass.")

        # get value on original potential
        origval = self.evaluate_potential(
            original_potential,
            observable=observable,
            points=self.points,
            representation_type=coord.CartesianRepresentation,
            **kw,
        )
        # get value on fit potential
        fitval = self.evaluate_potential(
            fit_potential,
            observable=observable,
            points=self.points,
            representation_type=coord.CartesianRepresentation,
            **kw,
        )

        # get difference
        residual = fitval - origval  # TODO! weighting by errors

        # output representation type
        # None -> default
        if representation_type is None:  # None -> default
            representation_type = self.representation_type
        if representation_type is None:  # still None -> base_representation
            representation_type = residual.base_representation
        representation_type = resolve_representationlike(representation_type)

        return residual.represent_as(representation_type)

    # /def

    # -----------------------------------------------------

    def run(
        self,
        fit_potential: T.Any,
        original_potential: T.Optional[T.Any] = None,
        observable: T.Optional[str] = None,
        *,
        representation_type: TH.OptRepresentationLikeType = None,
        **kwargs,
    ) -> object:
        """Calculate Residual.

        Parameters
        ----------
        fit_potential : object or :class:`~discO.core.wrapper.PotentialWrapper`
            The fit potential.

        observable : str or None (optional)
            The quantity on which to calculate the residual.
            Must be method of :class:`~discO.core.wrapper.PotentialWrapper`.
            None (default) becomes the default value at initialization.

        representation_type: representation-resolvable (optional, keyword-only)
            The output representation type.

        Returns
        -------
        residual : object
            In `representation_type`.

        """
        return self(
            fit_potential=fit_potential,
            original_potential=original_potential,
            observable=observable,
            representation_type=representation_type,
            **kwargs,
        )

    # /def


# /class

##############################################################################


class GridResidual(ResidualMethod, key="grid"):
    """Residual on a grid.

    .. todo::

        - want to allow grid to be in a Frame and awesomely transform

    """

    #################################################################
    # On the instance

    def __init__(
        self,
        grid: TH.RepresentationType,
        original_potential: T.Optional[T.Any] = None,
        observable: str = "acceleration",  # TODO make None and have config
        *,
        representation_type: TH.OptRepresentationLikeType = None,
        **kwargs,
    ) -> None:
        self.points = grid
        super().__init__(
            original_potential=original_potential,
            observable=observable,
            representation_type=representation_type,
            **kwargs,
        )

    # /def

    #################################################################
    # evaluate

    def evaluate_potential(
        self,
        potential: T.Union[PotentialWrapper, T.Any],
        observable: T.Optional[str] = None,
        points: T.Optional[TH.RepresentationType] = None,
        *,
        representation_type: TH.OptRepresentationLikeType = None,
        **kwargs,
    ) -> object:
        """Evaluate method on potential.

        Parameters
        ----------
        potential : object
        observable : str
            method in :class:`~PotentialWrapper`
        points : `~astropy.coordinates.BaseRepresentation` or None (optional)
            The points of the grid
        **kwargs
            Passed to method on :class:`~PotentialWrapper`

        Returns
        -------
        object

        """
        observable = observable or self.observable  # None -> stored
        if observable is None:  # still None
            raise ValueError("Need to pass observable.")

        if points is None:  # default to default
            points = self.points

        # get class to evaluate
        evaluator_cls = PotentialWrapper(
            potential,
            # frame=frame,
            representation_type=representation_type,
        )

        # get method from evaluator class
        evaluator = getattr(evaluator_cls, observable)

        # evaluate
        value = evaluator(
            points, representation_type=representation_type, **kwargs
        )

        # output representation type
        if representation_type is None:
            representation_type = value.base_representation
        representation_type = resolve_representationlike(representation_type)

        return value.represent_as(representation_type)

    # /def


# /class


##############################################################################
# END

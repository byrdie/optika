import abc
import dataclasses
import astropy.units as u
import named_arrays as na
import optika.mixins

__all__ = [
    "AbstractRoughnessParameters",
    "RoughnessParameters",
]


@dataclasses.dataclass(eq=False, repr=False)
class AbstractRoughnessParameters(
    optika.mixins.Printable,
):
    """collection of parameters used to compute the roughness of an optical surface"""

    @property
    @abc.abstractmethod
    def period_min(self) -> na.ScalarLike:
        """
        minimum period to consider when calculating roughness
        """

    @property
    @abc.abstractmethod
    def period_max(self) -> na.ScalarLike:
        """maximum period to consider when calculating roughness"""


@dataclasses.dataclass(eq=False, repr=False)
class RoughnessParameters(
    AbstractRoughnessParameters,
):
    period_min: na.ScalarLike = 0 * u.mm
    period_max: na.ScalarLike = 0 * u.mm

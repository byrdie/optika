import abc
import dataclasses
import numpy as np
import scipy.special
import astropy.units as u
import named_arrays as na

__all__ = [
    "AbstractInterfaceProfile",
    "ErfInterfaceProfile",
    "ExponentialInterfaceProfile",
    "LinearInterfaceProfile",
    "SinusoidalInterfaceProfile",
]


@dataclasses.dataclass(eq=False, repr=False)
class AbstractInterfaceProfile(
    abc.ABC,
):
    """
    Abstract interface describing the :cite:t:`Stearns1989`
    interface profile between two layers in a multilayer stack.
    """

    @property
    @abc.abstractmethod
    def width(self) -> u.Quantity | na.AbstractScalar:
        """
        Characteristic length scale of the interface profile.
        """

    @abc.abstractmethod
    def __call__(self, z: u.Quantity | na.AbstractScalar) -> na.AbstractScalar:
        """
        Calculate the fraction of atoms that are in the new layer vs. those
        that are in the current layer.

        Parameters
        ----------
        z
            the depth in the current layer
        """

    @abc.abstractmethod
    def reflectivity(
        self,
        wavelength: u.Quantity | na.AbstractScalar,
        direction: na.AbstractCartesian3dVectorArray,
    ) -> na.AbstractScalar:
        """
        Calculate the loss of the reflectivity due to this interface profile.

        Parameters
        ----------
        wavelength
            the wavelength of the incident light
        direction
            the propagation direction of the incident light, expressed in
            direction cosines.
        """


@dataclasses.dataclass(eq=False, repr=False)
class ErfInterfaceProfile(
    AbstractInterfaceProfile,
):
    """
    Error function interface profile between two layers in a multilayer stack.

    Examples
    --------

    Plot an error function interface profile as a function of depth

    .. jupyter-execute::

        import numpy as np
        import matplotlib.pyplot as plt
        import astropy.units as u
        import named_arrays as na
        import optika

        # Define an array of widths
        width = na.linspace(1, 2, axis="width", num=5) * u.nm

        # Define the interface profile
        p = optika.materials.profiles.ErfInterfaceProfile(width=width)

        # Define an array of depths into the material
        z = na.linspace(-5, 5, axis="z", num=101) * u.nm

        # Plot the interface profile as a function of depth
        fig, ax = plt.subplots(constrained_layout=True);
        na.plt.plot(z, p(z), ax=ax, axis="z", label=width);
        ax.set_xlabel(f"depth ({z.unit:latex_inline})");
        ax.set_ylabel(f"interface profile");
        ax.legend();

    Plot the reflectivity of the error function interface profile as a function
    of incidence angle

    .. jupyter-execute::

        # Define a wavelength
        wavelength = 304 * u.AA

        # Define an array of incidence angles
        angle = na.linspace(-90, 90, axis="angle", num=101) * u.deg

        # define an array of direction cosines based off of the incidence angles
        direction = na.Cartesian3dVectorArray(
            x=np.sin(angle),
            y=0,
            z=np.cos(angle),
        )

        # calculate the reflectivity for the given angles
        reflectivity = p.reflectivity(wavelength, direction)

        # Plot the reflectivity of the interface profile as a function of
        # incidence angle
        fig, ax = plt.subplots(constrained_layout=True);
        na.plt.plot(angle, reflectivity, ax=ax, axis="angle", label=width);
        ax.set_xlabel(f"angle ({angle.unit:latex_inline})");
        ax.set_ylabel(f"reflectivity");
        ax.legend();

    """

    width: u.Quantity | na.AbstractScalar = 0 * u.nm
    r"""
    the width of the Gaussian in the intergrand of :math:`\text{erf}(x)`
    """

    def __call__(self, z: u.Quantity | na.AbstractScalar) -> na.AbstractScalar:
        width = self.width
        x = z / (np.sqrt(2) * width)

        result = (1 + scipy.special.erf(x)) / 2

        return result

    def reflectivity(
        self,
        wavelength: u.Quantity | na.AbstractScalar,
        direction: na.AbstractCartesian3dVectorArray,
    ) -> na.AbstractScalar:
        s = 4 * np.pi * direction.z / wavelength
        result = np.exp(-np.square(s * self.width) / 2)
        return result


@dataclasses.dataclass(eq=False, repr=False)
class ExponentialInterfaceProfile(
    AbstractInterfaceProfile,
):
    """
    Exponential interface profile between two layers in a multilayer stack.

    Examples
    --------

    Plot an exponential interface profile as a function of depth

    .. jupyter-execute::

        import numpy as np
        import matplotlib.pyplot as plt
        import astropy.units as u
        import named_arrays as na
        import optika

        # Define an array of widths
        width = na.linspace(1, 2, axis="width", num=5) * u.nm

        # Define the interface profile
        p = optika.materials.profiles.ExponentialInterfaceProfile(width=width)

        # Define an array of depths into the material
        z = na.linspace(-5, 5, axis="z", num=101) * u.nm

        # Plot the interface profile as a function of depth
        fig, ax = plt.subplots(constrained_layout=True);
        na.plt.plot(z, p(z), ax=ax, axis="z", label=width);
        ax.set_xlabel(f"depth ({z.unit:latex_inline})");
        ax.set_ylabel(f"interface profile");
        ax.legend();

    Plot the reflectivity of the exponential interface profile as a function
    of incidence angle

    .. jupyter-execute::

        # Define a wavelength
        wavelength = 304 * u.AA

        # Define an array of incidence angles
        angle = na.linspace(-90, 90, axis="angle", num=101) * u.deg

        # define an array of direction cosines based off of the incidence angles
        direction = na.Cartesian3dVectorArray(
            x=np.sin(angle),
            y=0,
            z=np.cos(angle),
        )

        # calculate the reflectivity for the given angles
        reflectivity = p.reflectivity(wavelength, direction)

        # Plot the reflectivity of the interface profile as a function of
        # incidence angle
        fig, ax = plt.subplots(constrained_layout=True);
        na.plt.plot(angle, reflectivity, ax=ax, axis="angle", label=width);
        ax.set_xlabel(f"angle ({angle.unit:latex_inline})");
        ax.set_ylabel(f"reflectivity");
        ax.legend();

    """

    width: u.Quantity | na.AbstractScalar = 0 * u.nm
    r"""
    the width of the exponential
    """

    def __call__(self, z: u.Quantity | na.AbstractScalar) -> na.AbstractScalar:
        width = self.width

        sgn_z = np.sign(z)
        result = (1 + sgn_z - sgn_z * np.exp(-sgn_z * np.sqrt(2) * z / width)) / 2

        return result

    def reflectivity(
        self,
        wavelength: u.Quantity | na.AbstractScalar,
        direction: na.AbstractCartesian3dVectorArray,
    ) -> na.AbstractScalar:
        s = 4 * np.pi * direction.z / wavelength
        result = 1 / (1 + np.square(s * self.width) / 2)
        return result


@dataclasses.dataclass(eq=False, repr=False)
class LinearInterfaceProfile(
    AbstractInterfaceProfile,
):
    """
    Linear interface profile between two layers in a multilayer stack.

    Examples
    --------

    Plot an linear interface profile as a function of depth

    .. jupyter-execute::

        import numpy as np
        import matplotlib.pyplot as plt
        import astropy.units as u
        import named_arrays as na
        import optika

        # Define an array of widths
        width = na.linspace(1, 2, axis="width", num=5) * u.nm

        # Define the interface profile
        p = optika.materials.profiles.LinearInterfaceProfile(width=width)

        # Define an array of depths into the material
        z = na.linspace(-5, 5, axis="z", num=101) * u.nm

        # Plot the interface profile as a function of depth
        fig, ax = plt.subplots(constrained_layout=True);
        na.plt.plot(z, p(z), ax=ax, axis="z", label=width);
        ax.set_xlabel(f"depth ({z.unit:latex_inline})");
        ax.set_ylabel(f"interface profile");
        ax.legend();

    Plot the reflectivity of the linear interface profile as a function
    of incidence angle

    .. jupyter-execute::

        # Define a wavelength
        wavelength = 304 * u.AA

        # Define an array of incidence angles
        angle = na.linspace(-90, 90, axis="angle", num=101) * u.deg

        # define an array of direction cosines based off of the incidence angles
        direction = na.Cartesian3dVectorArray(
            x=np.sin(angle),
            y=0,
            z=np.cos(angle),
        )

        # calculate the reflectivity for the given angles
        reflectivity = p.reflectivity(wavelength, direction)

        # Plot the reflectivity of the interface profile as a function of
        # incidence angle
        fig, ax = plt.subplots(constrained_layout=True);
        na.plt.plot(angle, reflectivity, ax=ax, axis="angle", label=width);
        ax.set_xlabel(f"angle ({angle.unit:latex_inline})");
        ax.set_ylabel(f"reflectivity");
        ax.legend();

    """

    width: u.Quantity | na.AbstractScalar = 0 * u.nm
    """
    the width of the linear region
    """

    def __call__(self, z: u.Quantity | na.AbstractScalar) -> na.AbstractScalar:
        width = self.width

        result = (1 / 2) + z / (2 * np.sqrt(3) * width)

        result = np.minimum(1, np.maximum(result, 0))

        return result

    def reflectivity(
        self,
        wavelength: u.Quantity | na.AbstractScalar,
        direction: na.AbstractCartesian3dVectorArray,
    ) -> na.AbstractScalar:
        s = 4 * np.pi * direction.z / wavelength
        x = np.sqrt(3) * self.width * s
        result = np.sin(x.value) / x
        return result


@dataclasses.dataclass(eq=False, repr=False)
class SinusoidalInterfaceProfile(
    AbstractInterfaceProfile,
):
    """
    Sinusoidal interface profile between two layers in a multilayer stack.

    Examples
    --------

    Plot an sinusoidal interface profile as a function of depth

    .. jupyter-execute::

        import numpy as np
        import matplotlib.pyplot as plt
        import astropy.units as u
        import named_arrays as na
        import optika

        # Define an array of widths
        width = na.linspace(1, 2, axis="width", num=5) * u.nm

        # Define the interface profile
        p = optika.materials.profiles.SinusoidalInterfaceProfile(width=width)

        # Define an array of depths into the material
        z = na.linspace(-5, 5, axis="z", num=101) * u.nm

        # Plot the interface profile as a function of depth
        fig, ax = plt.subplots(constrained_layout=True);
        na.plt.plot(z, p(z), ax=ax, axis="z", label=width);
        ax.set_xlabel(f"depth ({z.unit:latex_inline})");
        ax.set_ylabel(f"interface profile");
        ax.legend();

    Plot the reflectivity of the sinusoidal interface profile as a function
    of incidence angle

    .. jupyter-execute::

        # Define a wavelength
        wavelength = 304 * u.AA

        # Define an array of incidence angles
        angle = na.linspace(-90, 90, axis="angle", num=101) * u.deg

        # define an array of direction cosines based off of the incidence angles
        direction = na.Cartesian3dVectorArray(
            x=np.sin(angle),
            y=0,
            z=np.cos(angle),
        )

        # calculate the reflectivity for the given angles
        reflectivity = p.reflectivity(wavelength, direction)

        # Plot the reflectivity of the interface profile as a function of
        # incidence angle
        fig, ax = plt.subplots(constrained_layout=True);
        na.plt.plot(angle, reflectivity, ax=ax, axis="angle", label=width);
        ax.set_xlabel(f"angle ({angle.unit:latex_inline})");
        ax.set_ylabel(f"reflectivity");
        ax.legend();

    """

    width: u.Quantity | na.AbstractScalar = 0 * u.nm
    """
    the characteristic size of the sine wave
    """

    def __call__(self, z: u.Quantity | na.AbstractScalar) -> na.AbstractScalar:


        width = self.width

        a = np.pi / (np.square(np.pi) - 8)
        z = np.minimum(a * width, np.maximum(z, -a * width))
        result = (1 / 2) + np.sin(np.pi * z / (2 * a * width) * u.rad) / 2

        # result = np.minimum(1, np.maximum(result, 0))

        return result

    def reflectivity(
        self,
        wavelength: u.Quantity | na.AbstractScalar,
        direction: na.AbstractCartesian3dVectorArray,
    ) -> na.AbstractScalar:
        width = self.width
        s = 4 * np.pi * direction.z / wavelength
        a = np.pi / (np.square(np.pi) - 8)
        x = a * width * s
        x1 = x - np.pi / 2
        x2 = x + np.pi / 2
        result = np.pi * (np.sin(x1 * u.rad) / x1 + np.sin(x2 * u.rad) / x2) / 4
        return result

# """
# Copyright 2005, Ross Ihaka. All Rights Reserved.
# Ported to python: Copyright 2018, Reto Stauffer.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 
#    1. Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
# 
#    2. Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
# 
#    3. The name of the Ross Ihaka may not be used to endorse or promote
#       products derived from this software without specific prior written
#       permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS `AS IS''
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL ROSS IHAKA BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
# IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# """


import sys
import numpy as np
import inspect

class colorlib:
    """Color Handling Superclass

    The `colorlib` class provides a series of methods methods
    which allow to convert colors between different color spaces
    and is not intended to be used by end-users (not exported).

    Users should use the dedicated classes for the available color spaces which
    all extend this class. These are
    :py:class:`CIELAB`, :py:class:`CIELUV`, :py:class:`CIEXYZ`,
    :py:class:`HLS`, :py:class:`HSV`, :py:class:`RGB`, :py:class:`hexcols`,
    :py:class:`polarLAB`, :py:class:`polarLUV`, and :py:class:`sRGB`.
    """

    # No initialization method, but some constants are specified here

    _KAPPA   = 24389.0 / 27.0
    """Static constant; required for coordinate transformations.
    Often approximated as 903.3."""

    _EPSILON = 216.0 / 24389.0
    """Static constant; required for coordinate transformations.
    Often approximated as 7.787."""

    # Default white spot
    XN = np.asarray([ 95.047])
    """X value for default white spot. Used for coordinate transformations."""
    YN = np.asarray([100.000])
    """Y value for default white spot. Used for coordinate transformations."""
    ZN = np.asarray([108.883])
    """Z value for default white spot. Used for coordinate transformations."""

    # Conversion function
    def DEG2RAD(self, x):
        """Convert degrees into radiant

        Args:
            x (float, array of floats): Value(s) in degrees.

        Returns:
            float, float array: Returns input `x` in radiant.
        """
        return np.pi / 180. * x


    # Conversion function
    def RAD2DEG(self, x):
        """Convert radiant to degrees

        Args:
            x (float, array of floats): Value(s) in radiant.

        Returns:
            float, array of floats: Returns input `x` in degrees.
        """
        return 180. / np.pi * x


    def _get_white_(self, __fname__, n, XN = None, YN = None, ZN = None):
        """Get Whitepoint

        For some color conversion functions the "white" definition (default
        white color) has to be specified. This function checks and prepares the
        `XN`, `YN`, and `ZN` definition. Defaults are used if the user does not specify a
        custom white point. If set, `XN`, `YN`, and `ZN` have to be of type `numpy.ndarray`,
        either of length one (will be expanded to length "n"), or of length `n`.

        Args:
            __fname__ (str): Name of the parent method, only used if errors are dropped.
            n (int): Number of colors to which `NX`, `NY`, and `NZ` will be expanded.
            XN (None, float, numpy.ndarray): Either `None` (default) or an
                `nd.array` of length one or length `n`. White point specification for
                dimension `X`, defaults to `None`.
            YN (None, float, numpy.ndarray): See `XN`. White point specification for
                dimension `Y`, defaults to `None`.
            YZ (None, numpy.ndarray): See `XN`. White point specification for
                dimension `Z`, defaults to `None`.

        Raises:
            TypeError: If `XN`, `YN` and `ZN` are invalid (not `None` nor in a format
                that can be converted into a `numpy.ndarray`).
            ValueError: If the resulting values `XN`, `YN`, and `ZN` are not all
                of the same length.

        Returns:
            list: Returns a list `[XN, YN, ZN]` with three `numpy.ndarrays`
            of length `n`. If the inputs `XN`, `YN`, `ZN` (or some) were `None`,
            the class defaults are used.
        """

        # Take defaults if not further specified
        if not XN: XN = self.XN
        if not YN: YN = self.YN
        if not ZN: ZN = self.ZN

        if isinstance(XN, float): XN = np.asarray([XN])
        if isinstance(YN, float): YN = np.asarray([YN])
        if isinstance(ZN, float): ZN = np.asarray([ZN])

        # Checking type
        if not np.all(isinstance(x, np.ndarray) for x in [XN, YN, ZN]):
            raise TypeError(f"Inputs to {__fname__} have to be of class `numpy.ndarray`.")

        # Expand if required
        if len(XN) == 1 and not len(XN) == n: XN = np.repeat(XN, n)
        if len(YN) == 1 and not len(YN) == n: YN = np.repeat(YN, n)
        if len(ZN) == 1 and not len(ZN) == n: ZN = np.repeat(ZN, n)

        # Check if all lengths match
        if not np.all([len(x) == n for x in [XN, YN, ZN]]):
            raise ValueError(f"Inputs XN/YN/ZN to {__fname__} have to be of the same length.")

        return [XN, YN, ZN]


    def _check_input_arrays_(self, __fname__, **kwargs):
        """Check Input Arrays

        Checks if all inputs in `kwargs` are of type `numpy.ndarray` and of the
        same length. If not, the script will throw an exception and stop.

        Args:
            __fname__ (str): Name of the method who called this check routine.
                Only used to drop a useful error message if required.
            **kwargs: Named keywords, objects to be checked.

        Returns:
            bool: Returns `True` if everything is OK, else an exception will be thrown.
        """

        # Message will be dropped if problems occur
        msg = "Problem while checking inputs \"{:s}\" to method \"{:s}\":".format(
                ", ".join(kwargs.keys()), __fname__)

        from numpy import asarray
        lengths = []
        for key,val in kwargs.items():

            try:
                val = asarray(val)
            except Exception as e:
                raise ValueError(f"input `{key}` to {self.__class__.__name__} " + \
                                  "could not have been converted to numpy.ndarray")
            # Else append length and proceed
            lengths.append(len(val))

        # Check if all do have the same length
        if not np.all([x == lengths[0] for x in lengths]):
            msg += " Arguments of different lengths: {:s}".format(
                   ", ".join(["{:s} = {:d}".format(kwargs.keys()[i],lengths[i]) \
                   for i in range(0,len(kwargs))]))
            raise ValueError(msg)

        # If all is fine, simply return True
        return True


    # -------------------------------------------------------------------
    # -------------------------------------------------------------------
    # -------------------------------------------------------------------
    # -------------------------------------------------------------------



    # ----- CIE-XYZ <-> Device dependent RGB -----
    #
    #  Gamma Correction
    #
    #  The following two functions provide gamma correction which
    #  can be used to switch between sRGB and linearized sRGB (RGB).
    #
    #  The standard value of gamma for sRGB displays is approximately 2.2,
    #  but more accurately is a combination of a linear transform and
    #  a power transform with exponent 2.4
    #
    #  gtrans maps linearized sRGB to sRGB.
    #  ftrans provides the inverse map.
    def gtrans(self, u, gamma):
        """Gamma Correction

        Function `gtrans` and `ftrans` provide gamma correction which
        can be used to switch between sRGB and linearised sRGB (RGB).

        The standard value of gamma for sRGB displays is approximately `2.2`,
        but more accurately is a combination of a linear transform and
        a power transform with exponent `2.4`.
        `gtrans` maps linearised sRGB to sRGB, `ftrans` provides the inverse mapping.

        Args:
            u (numpy.ndarray): Float array of length `N`.
            gamma (float, numpy.ndarray): gamma value; if float or
                `numpy.ndarray` of length one, `gamma` will be recycled if needed.

        Returns:
            numpy.ndarray: Gamma corrected values, same length as input `u`.
        """

        __fname__ = inspect.stack()[0][3] # Name of this method

        # Input check
        if isinstance(gamma, float): gamma = np.asarray([gamma])
        if len(gamma) == 1 and not len(gamma) == len(u):
            gamma = np.repeat(gamma, len(u))

        # Checking inputs
        self._check_input_arrays_(__fname__, u = u, gamma = gamma)

        # Transform
        for i,val in np.ndenumerate(u):
            if val > 0.00304: u[i] = 1.055 * np.power(val, (1. / gamma[i])) - 0.055
            else:             u[i] = 12.92 * val

        return u

    def ftrans(self, u, gamma):
        """Gamma Correction

        Function `gtrans` and `ftrans` provide gamma correction which
        can be used to switch between sRGB and linearised sRGB (RGB).

        The standard value of gamma for sRGB displays is approximately `2.2`,
        but more accurately is a combination of a linear transform and
        a power transform with exponent `2.4`.
        `gtrans` maps linearised sRGB to sRGB, `ftrans` provides the inverse mapping.

        Args:
            u (numpy.ndarray): Float array of length `N`.
            gamma (float, numpy.ndarray): gamma value; if float or
                `numpy.ndarray` of length one, `gamma` will be recycled if needed.

        Returns:
            numpy.ndarray: Gamma corrected values, same length as input `u`.
        """

        __fname__ = inspect.stack()[0][3] # Name of this method

        # Input check
        if isinstance(gamma, float): gamma = np.asarray([gamma])
        if len(gamma) == 1 and not len(gamma) == len(u):
            gamma = np.repeat(gamma, len(u))

        # Checking inputs
        self._check_input_arrays_(__fname__, u = u, gamma = gamma)

        # Transform 
        for i,val in np.ndenumerate(u):
            if val > 0.03928: u[i] = np.power((val + 0.055) / 1.055, gamma[i])
            else:             u[i] = val / 12.92

        return u

    def sRGB_to_RGB(self, R, G, B, gamma = 2.4):
        """Convert Standard RGB to RGB

        Args:
            R (numpy.ndarray): Intensities for red (`[0., 1.]`).
            G (numpy.ndarray): Intensities for green (`[0., 1.]`).
            B (numpy.ndarray): Intensities for blue  (`[0., 1.]`).
            gamma (float): gamma adjustment, defaults to `2.4`.

        Returns:
            list: Returns a list of `numpy.ndarray`s with `R`, `G`, and `B` values.
        """

        __fname__ = inspect.stack()[0][3] # Name of this method

        # Input check
        if isinstance(gamma, float): gamma = np.asarray([gamma])
        if len(gamma) == 1 and not len(gamma) == len(R):
            gamma = np.repeat(gamma, len(R))

        # Checking inputs
        self._check_input_arrays_(__fname__, R = R, G = G, B = B, gamma = gamma)

        # Apply gamma correction
        return [self.ftrans(x, gamma) for x in [R, G, B]]

    def RGB_to_sRGB(self, R, G, B, gamma = 2.4):
        """Convert RGB to Standard RGB

        Args:
            R (numpy.ndarray): Intensities for red (`[0., 1.]`).
            G (numpy.ndarray): Intensities for green (`[0., 1.]`).
            B (numpy.ndarray): Intensities for blue  (`[0., 1.]`).
            gamma (float): gamma adjustment, defaults to `2.4`.

        Returns:
            list: Returns a list of `numpy.ndarray`s with `R`, `G`, and `B` values.
        """

        __fname__ = inspect.stack()[0][3] # Name of this method

        # Input check
        if isinstance(gamma, float): gamma = np.asarray([gamma])
        if len(gamma) == 1 and not len(gamma) == len(R):
            gamma = np.repeat(gamma, len(R))

        # Checking inputs
        self._check_input_arrays_(__fname__, R = R, G = G, B = B, gamma = gamma)

        # Apply gamma correction
        return [self.gtrans(x, gamma) for x in [R, G, B]]

    # -------------------------------------------------------------------
    # -------------------------------------------------------------------
    # -------------------------------------------------------------------
    # -------------------------------------------------------------------

    ## ----- CIE-XYZ <-> Device independent RGB -----
    ## R, G, and B give the levels of red, green and blue as values
    ## in the interval [0., 1.].  X, Y and Z give the CIE chromaticies.
    ## XN, YN, ZN gives the chromaticity of the white point.
    def RGB_to_XYZ(self, R, G, B, XN = None, YN = None, ZN = None):
        """Convert RGB to CIEXYZ

        `R`, `G`, and `B` give the levels of red, green and blue as values
        in the interval `[0., 1.]`.
        `XN`, `YN`, and `ZN` allow to specify additional CIE chromaticities to
        specify a specific white point.

        Args:
            R (numpy.ndarray): Intensities for red (`[0., 1.]`).
            G (numpy.ndarray): Intensities for green (`[0., 1.]`).
            B (numpy.ndarray): Intensities for blue  (`[0., 1.]`).
            XN (None, numpy.ndarray): Chromaticity of the white point. If of
                length `1`, the white point specification will be recycled if needed.
                When not specified (all `None`) a default white point is used.
            YN: See `XN`.
            ZN: See `XN`.

        Returns:
            list: Returns corresponding coordinates of CIE chromaticities, a
            list of `numpy.ndarray`s of the same length as the inputs (`[X, Y, Z]`).
        """

        __fname__ = inspect.stack()[0][3] # Name of this method
        n = len(R) # Number of colors

        # Loading definition of white
        [XN, YN, ZN] = self._get_white_(__fname__, n, XN, YN, ZN)

        # Checking input
        self._check_input_arrays_(__fname__, R = R, G = G, B = B)

        # TODO only YN is used as in the original code. Is this correct, or
        # correct by accident?
        return [YN * (0.412453 * R + 0.357580 * G + 0.180423 * B),   # X
                YN * (0.212671 * R + 0.715160 * G + 0.072169 * B),   # Y
                YN * (0.019334 * R + 0.119193 * G + 0.950227 * B)]   # Z

    def XYZ_to_RGB(self, X, Y, Z, XN = None, YN = None, ZN = None):
        """Convert CIEXYZ to RGB

        `X`, `Y`, and `Z` specify the values in the three coordinates of the
        CIEXYZ color space,
        `XN`, `YN`, and `ZN` allow to specify additional CIE chromaticities to
        specify a specific white point.

        Args:
            X (numpy.ndarray): Values for the `X` dimension.
            Y (numpy.ndarray): Values for the `Y` dimension.
            Z (numpy.ndarray): Values for the `Z` dimension.
            XN (None, numpy.ndarray): Chromaticity of the white point. If of
                length `1`, the white point specification will be recycled if needed.
                When not specified (all `None`) a default white point is used.
            YN: See `XN`.
            ZN: See `XN`.

        Returns:
            list: Returns corresponding coordinates as a list of
            `numpy.ndarray`s of the same length as the inputs (`[R, G, B]`).
        """

        __fname__ = inspect.stack()[0][3] # Name of this method
        n = len(X) # Number of colors

        # Loading definition of white
        [XN, YN, ZN] = self._get_white_(__fname__, n, XN, YN, ZN)

        # Checking input
        self._check_input_arrays_(__fname__, X = X, Y = Y, Z = Z)

        # Only YN is used
        return [( 3.240479 * X - 1.537150 * Y - 0.498535 * Z) / YN,   # R
                (-0.969256 * X + 1.875992 * Y + 0.041556 * Z) / YN,   # G
                ( 0.055648 * X - 0.204043 * Y + 1.057311 * Z) / YN]   # B


    # -------------------------------------------------------------------
    # -------------------------------------------------------------------
    # -------------------------------------------------------------------
    # -------------------------------------------------------------------


    ## Unused as we are going CIE-XYZ <-> RGB <-> sRGB
    ##
    ##  ## ----- CIE-XYZ <-> sRGB -----
    ##  ## R, G, and B give the levels of red, green and blue as values
    ##  ## in the interval [0., 1.].  X, Y and Z give the CIE chromaticies.
    ##  ## XN, YN, ZN gives the chromaticity of the white point.
    ##  def sRGB_to_XYZ(self, R, G, B, XN = None, YN = None, ZN = None):
    ##      """sRGB to CIEXYZ.

    ##      R, G, and B give the levels of red, green and blue as values
    ##      in the interval `[0., 1.]`.  X, Y and Z give the CIE chromaticies.

    ##      Args:
    ##          R (numpy.ndarray): Indensities for red (`[0., 1.]`).
    ##          G (numpy.ndarray): Indensities for green (`[0., 1.]`).
    ##          B (numpy.ndarray): Indensities for blue  (`[0., 1.]`).
    ##          XN (None or numpy.ndarray): Chromaticity of the white point. If of
    ##              length 1 the white point specification will be recycled if length of
    ##              R/G/B is larger than one. If not specified (all three `None`) default
    ##              values will be used. Defaults to None, see also YN, ZN.
    ##          YN: See `XN`.
    ##          ZN: See `XN`.

    ##      Returns:
    ##          list: Returns corresponding X/Y/Z coordinates of CIE chromaticies, a list
    ##          of `numpy.ndarray`'s of the same length as the inputs (`[X, Y,
    ##          Z]`).
    ##      """

    ##      __fname__ = inspect.stack()[0][3] # Name of this method
    ##      n = len(R) # Number of colors

    ##      # Loading definition of white
    ##      [XN, YN, ZN] = self._get_white_(__fname__, n, XN, YN, ZN)

    ##      # Checking input
    ##      self._check_input_arrays_(__fname__, R = R, G = G, B = B)

    ##      # Transform R/G/B
    ##      R = self.ftrans(R, 2.4)
    ##      G = self.ftrans(G, 2.4)
    ##      B = self.ftrans(B, 2.4)

    ##      # Convert to X/Y/Z coordinates
    ##      return[YN * (0.412453 * R + 0.357580 * G + 0.180423 * B),   # X
    ##             YN * (0.212671 * R + 0.715160 * G + 0.072169 * B),   # Y
    ##             YN * (0.019334 * R + 0.119193 * G + 0.950227 * B)]   # Z

    ##  def XYZ_to_sRGB(self, X, Y, Z, XN = None, YN = None, ZN = None):
    ##      """CIEXYZ to sRGB.

    ##      R, G, and B give the levels of red, green and blue as values
    ##      in the interval `[0., 1.]`.  X, Y and Z give the CIE chromaticies.

    ##      Args:
    ##          X (numpy.ndarray): Values for the X dimension.
    ##          Y (numpy.ndarray): Values for the Y dimension.
    ##          Z (numpy.ndarray): Values for the Z dimension.
    ##          XN (None or numpy.ndarray): Chromaticity of the white point. If of
    ##              length 1 the white point specification will be recycled if length of
    ##              R/G/B is larger than one. If not specified (all three `None`) default
    ##              values will be used. Defaults to None, see also YN, ZN.
    ##          YN: See `XN`.
    ##          ZN: See `XN`.

    ##      Returns:
    ##          list: Returns corresponding X/Y/Z coordinates of CIE chromaticies, a list
    ##          of `numpy.ndarray`'s of the same length as the inputs (`[R, G, B]`).
    ##      """

    ##      __fname__ = inspect.stack()[0][3] # Name of this method
    ##      n = len(X) # Number of colors

    ##      # Loading definition of white
    ##      [XN, YN, ZN] = self._get_white_(__fname__, n, XN, YN, ZN)

    ##      # Checking input
    ##      self._check_input_arrays_(__fname__, X = X, Y = Y, Z = Z)

    ##      # Transform and return
    ##      return [self.gtrans(( 3.240479 * X - 1.537150 * Y - 0.498535 * Z) / YN, 2.4),   # R
    ##              self.gtrans((-0.969256 * X + 1.875992 * Y + 0.041556 * Z) / YN, 2.4),   # G
    ##              self.gtrans(( 0.055648 * X - 0.204043 * Y + 1.057311 * Z) / YN, 2.4)]   # B


    # -------------------------------------------------------------------
    # -------------------------------------------------------------------
    # -------------------------------------------------------------------
    # -------------------------------------------------------------------

    ## ----- CIE-XYZ <-> CIE-LAB ----- */


    def LAB_to_XYZ(self, L, A, B, XN = None, YN = None, ZN = None):
        """Convert CIELAB to CIEXYZ

        `L`, `A`, and `B` specify the values in the three coordinates of the
        CIELAB color space,
        `XN`, `YN`, and `ZN` allow to specify additional CIE chromaticities to
        specify a specific white point.

        Args:
            L (numpy.ndarray): Values for the `L` dimension.
            A (numpy.ndarray): Values for the `A` dimension.
            B (numpy.ndarray): Values for the `B` dimension.
            XN (None, numpy.ndarray): Chromaticity of the white point. If of
                length `1`, the white point specification will be recycled if needed.
                When not specified (all `None`) a default white point is used.
            YN: See `XN`.
            ZN: See `XN`.

        Returns:
            list: Returns corresponding coordinates of CIE chromaticities as a
            list of `numpy.ndarray`s of the same length as the inputs (`[X, Y, Z]`).
        """

        __fname__ = inspect.stack()[0][3] # Name of this method
        n = len(L) # Number of colors

        # Loading definition of white
        [XN, YN, ZN] = self._get_white_(__fname__, n, XN, YN, ZN)

        # Checking input
        self._check_input_arrays_(__fname__, L = L, A = A, B = B)

        # Result arrays
        X = np.ndarray(len(L), dtype = "float"); X[:] = 0.
        Y = np.ndarray(len(L), dtype = "float"); Y[:] = 0.
        Z = np.ndarray(len(L), dtype = "float"); Z[:] = 0.

        # Calculate Y
        for i,val in np.ndenumerate(L):
            if   val <= 0:    Y[i] = 0.
            elif val <= 8.0:  Y[i] = val * YN[i] / self._KAPPA
            elif val <= 100.: Y[i] = YN[i] * np.power((val + 16.) / 116., 3.)
            else:             Y[i] = YN[i]

        fy = np.ndarray(len(Y), dtype = "float")
        for i,val in np.ndenumerate(Y):
            if val <= (self._EPSILON * YN[i]):
                fy[i] = (self._KAPPA / 116.) * val / YN[i] + 16. / 116.
            else:
                fy[i] = np.power(val / YN[i], 1. / 3.)

        # Calculate X
        fx = fy + (A / 500.)
        for i,val in np.ndenumerate(fx):
            if np.power(val, 3.) <= self._EPSILON:
                X[i] = XN[i] * (val - 16. / 116.) / (self._KAPPA / 116.)
            else:
                X[i] = XN[i] * np.power(val, 3.)

        # Calculate Z
        fz = fy - (B / 200.)
        for i,val in np.ndenumerate(fz):
            if np.power(val, 3.) <= self._EPSILON:
                Z[i] = ZN[i] * (val - 16. / 116.) / (self._KAPPA / 116.)
            else:
                Z[i] = ZN[i] * np.power(val, 3)

        return [X, Y, Z]

    def XYZ_to_LAB(self, X, Y, Z, XN = None, YN = None, ZN = None):
        """Convert CIEXYZ to CIELAB

        `X`, `Y`, and `Z` specify the values in the three coordinates of the
        CIELAB color space,
        `XN`, `YN`, and `ZN` allow to specify additional CIE chromaticities to
        specify a specific white point.

        Args:
            X (numpy.ndarray): Values for the `X` dimension.
            Y (numpy.ndarray): Values for the `Y` dimension.
            Z (numpy.ndarray): Values for the `Z` dimension.
            XN (None, numpy.ndarray): Chromaticity of the white point. If of
                length `1`, the white point specification will be recycled if needed.
                When not specified (all `None`) a default white point is used.
            YN: See `XN`.
            ZN: See `XN`.

        Returns:
            list: Returns corresponding coordinates of CIE chromaticities as
            a list of `numpy.ndarray`s of the same length as the inputs (`[L, A, B]`).
        """

        __fname__ = inspect.stack()[0][3] # Name of this method
        n = len(X) # Number of colors

        # Loading definition of white
        [XN, YN, ZN] = self._get_white_(__fname__, n, XN, YN, ZN)

        # Checking input
        self._check_input_arrays_(__fname__, X = X, Y = Y, Z = Z)

        # Support function
        def f(t, _KAPPA, _EPSILON):
            for i,val in np.ndenumerate(t):
                if val > _EPSILON:
                    t[i] = np.power(val, 1./3.)
                else:
                    t[i] = (_KAPPA / 116.) * val + 16. / 116.
            return t

        # Scaling
        xr = X / XN;
        yr = Y / YN;
        zr = Z / ZN;

        # Calculate L
        L = np.ndarray(len(X), dtype = "float"); L[:] = 0.
        for i,val in np.ndenumerate(yr):
            if val > self._EPSILON:
                L[i] = 116. * np.power(val, 1./3.) - 16.
            else:
                L[i] = self._KAPPA * val

        xt = f(xr, self._KAPPA, self._EPSILON);
        yt = f(yr, self._KAPPA, self._EPSILON);
        zt = f(zr, self._KAPPA, self._EPSILON);
        return [L, 500. * (xt - yt), 200. * (yt - zt)]  # [L, A, B]


    # -------------------------------------------------------------------
    # -------------------------------------------------------------------
    # -------------------------------------------------------------------
    # -------------------------------------------------------------------

    ## Commented as not yet used
    ##
    ## def XYZ_to_HLAB(self, X, Y, Z, XN = None, YN = None, ZN = None):
    ##     """CIE-XYZ to Hunter LAB.

    ##     .. note::
    ##         Note that the Hunter LAB is no longer part of the public API,
    ##         but the code is still here in case needed.

    ##     Args:
    ##         X (numpy.ndarray): Values for the X dimension.
    ##         Y (numpy.ndarray): Values for the Y dimension.
    ##         Z (numpy.ndarray): Values for the Z dimension.
    ##         XN (None or numpy.ndarray): Chromaticity of the white point. If of
    ##             length 1 the white point specification will be recycled if length of
    ##             R/G/B is larger than one. If not specified (all three `None`) default
    ##             values will be used. Defaults to None, see also YN, ZN.
    ##         YN: See `XN`.
    ##         ZN: See `XN`.

    ##     Returns:
    ##         list: Returns corresponding Hunter LAB chromaticies, a list of
    ##         `numpy.ndarray`'s of the same length as the inputs (`[L, A, B]`).
    ##     """

    ##     __fname__ = inspect.stack()[0][3] # Name of this method
    ##     n = len(X) # Number of colors

    ##     # Loading definition of white
    ##     [XN, YN, ZN] = self._get_white_(__fname__, n, XN, YN, ZN)

    ##     # Checking input
    ##     self._check_input_arrays_(__fname__, X = X, Y = Y, Z = Z)

    ##     # Transform
    ##     X = X / XN; Y = Y / YN; Z = Z / ZN;
    ##     l = np.sqrt(Y);
    ##     return [10. * l, 17.5 * (((1.02 * X) - Y) / l), 7. * ((Y - (0.847 * Z)) / l)] # [L, A, B]


    ## def HLAB_to_XYZ(self, L, A, B, XN = None, YN = None, ZN = None):
    ##     """Hunter LAB to CIE-XYZ.

    ##     .. note::
    ##         Note that the Hunter LAB is no longer part of the public API,
    ##         but the code is still here in case needed.

    ##     Args:
    ##         L (numpy.ndarray): Values for the L dimension.
    ##         A (numpy.ndarray): Values for the A dimension.
    ##         B (numpy.ndarray): Values for the B dimension.
    ##         XN (None or numpy.ndarray): Chromaticity of the white point. If of
    ##             length 1 the white point specification will be recycled if length of
    ##             R/G/B is larger than one. If not specified (all three `None`) default
    ##             values will be used. Defaults to None, see also YN, ZN.
    ##         YN: See `XN`.
    ##         ZN: See `XN`.

    ##     Returns:
    ##         list: Returns corresponding CIE-XYZ chromaticies, a list of
    ##         `numpy.ndarray`'s of the same length as the inputs (`[X, Y, Z]`).
    ##     """

    ##     __fname__ = inspect.stack()[0][3] # Name of this method
    ##     n = len(L) # Number of colors

    ##     # Loading definition of white
    ##     [XN, YN, ZN] = self._get_white_(__fname__, n, XN, YN, ZN)

    ##     # Checking input
    ##     self._check_input_arrays_(__fname__, L = L, A = A, B = B)

    ##     # Transform
    ##     vY = L / 10.;
    ##     vX = (A / 17.5) * (L / 10);
    ##     vZ = (B / 7) * (L / 10);
    ##     vY = vY * vY;

    ##     Y = vY * XN
    ##     X = (vX + vY) / 1.02 * YN
    ##     Z = - (vZ - vY) / 0.847 * ZN

    ##     return [X, Y, Z]


    # -------------------------------------------------------------------
    # -------------------------------------------------------------------
    # -------------------------------------------------------------------
    # -------------------------------------------------------------------
    def LAB_to_polarLAB(self, L, A, B):
        """Convert CIELAB to the polar representation (polarLAB)

        Converts colors from the CIELAB color space into its polar
        representation (`polarLAB`).
        Inverse function of :py:func:`polarLAB_to_LAB`.

        Args:
            L (numpy.ndarray): Values for the `L` dimension.
            A (numpy.ndarray): Values for the `A` dimension.
            B (numpy.ndarray): Values for the `B` dimension.

        Returns:
            list: Returns corresponding polar LAB chromaticities as a list of
            `numpy.ndarray`s of the same length as the inputs (`[L, A, B]`).
        """

        __fname__ = inspect.stack()[0][3] # Name of this method

        # Checking input
        self._check_input_arrays_(__fname__, L = L, A = A, B = B)

        # Compute H
        H = self.RAD2DEG(np.arctan2(B, A))
        for i,val in np.ndenumerate(H):
            while val > 360.:   val -= 360.
            while val <   0.:   val += 360.
            H[i] = val
        # Compute C
        C = np.sqrt(A * A + B * B)

        return [L, C, H]

    def polarLAB_to_LAB(self, L, C, H):
        """Convert polarLAB to CIELAB

        Convert colors from the polar representation of the CIELAB
        color space into CIELAB coordinates.
        Inverse function of :py:func:`LAB_to_polarLAB`.

        Args:
            L (numpy.ndarray): Values for the polar `L` dimension.
            A (numpy.ndarray): Values for the polar `A` dimension.
            B (numpy.ndarray): Values for the polar `B` dimension.

        Returns
            list: Returns corresponding CIELAB chromaticities as a list of
            `numpy.ndarray`s of the same length as the inputs (`[L, A, B]`).
        """

        __fname__ = inspect.stack()[0][3] # Name of this method

        # Checking input
        self._check_input_arrays_(__fname__, L = L, C = C, H = H)

        A = np.cos(self.DEG2RAD(H)) * C
        B = np.sin(self.DEG2RAD(H)) * C

        return [L, A, B]

    # -------------------------------------------------------------------
    # -------------------------------------------------------------------
    # -------------------------------------------------------------------
    # -------------------------------------------------------------------
    def sRGB_to_HSV(self, r, g, b):
        """Convert RGB to HSV

        Args:
            r (numpy.ndarray): Intensities for red (`[0., 1.]`).
            g (numpy.ndarray): Intensities for green (`[0., 1.]`).
            b (numpy.ndarray): Intensities for blue (`[0., 1.]`).

        Returns:
            list: Returns a `numpy.ndarray` with the corresponding coordinates in the
            HSV color space (`[h, s, v]`). Same length as the inputs.
        """

        __fname__ = inspect.stack()[0][3] # Name of this method

        # Checking input
        self._check_input_arrays_(__fname__, r = r, g = g, b = b)

        # Support function
        def gethsv(r, g, b):
            x = np.min([r, g, b])
            y = np.max([r, g, b])
            if y != x:
                f = g - b if r == x else b - r if g == x else r - g
                i = 3. if r == x else 5. if g == x else 1.
                h = 60. * (i - f /(y - x))
                s = (y - x)/y
                v = y
            else:
                h = 0.
                s = 0.
                v = y
            return [h, s, v]

        # Result arrays
        h = np.ndarray(len(r), dtype = "float"); h[:] = 0.
        s = np.ndarray(len(r), dtype = "float"); s[:] = 0.
        v = np.ndarray(len(r), dtype = "float"); v[:] = 0.

        # Calculate h/s/v
        for i in range(0, len(r)):
            tmp = gethsv(r[i], g[i], b[i])
            h[i] = tmp[0]; s[i] = tmp[1]; v[i] = tmp[2]

        return [h, s, v]


    def HSV_to_sRGB(self, h, s, v):
        """Convert HSV to Standard RGB (sRGB)

        Args:
            h (nympy.ndarray): Hue values.
            s (numpy.ndarray): Saturation.
            v (numpy.ndarray): Value (the value-dimension of HSV).

        Returns:
            list: Returns a list of `numpy.ndarray`s with the corresponding
            coordinates in the sRGB color space (`[r, g, b]`). Same length as
            the inputs.
        """

        __fname__ = inspect.stack()[0][3] # Name of this method

        # Checking input
        self._check_input_arrays_(__fname__, h = h, s = s, v = v)

        # Support function
        def getrgb(h, s, v):

            # If Hue is not defined:
            if h == np.nan: return np.repeat(v, 3)

            # Convert to [0-6]
            h = h / 60.
            i = np.floor(h)
            f = h - i

            if (i % 2) == 0:  # if i is even 
                f = 1 - f

            m = v * (1 - s)
            n = v * (1 - s * f)
            if i in [0, 6]:    return [v, n, m]
            elif i == 1:       return [n, v, m]
            elif i == 2:       return [m, v, n]
            elif i == 3:       return [m, n, v]
            elif i == 4:       return [n, m, v]
            elif i == 5:       return [v, m, n]
            else:
                Exception("Ended up in a non-defined ifelse with i = %d".format(i))

        # Result arrays
        r = np.ndarray(len(h), dtype = "float"); r[:] = 0.
        g = np.ndarray(len(h), dtype = "float"); g[:] = 0.
        b = np.ndarray(len(h), dtype = "float"); b[:] = 0.

        for i in range(0,len(h)):
           tmp = getrgb(h[i], s[i], v[i])
           r[i] = tmp[0]; g[i] = tmp[1]; b[i] = tmp[2]

        return [r, g, b]


    # -------------------------------------------------------------------
    # -------------------------------------------------------------------
    # -------------------------------------------------------------------
    # -------------------------------------------------------------------
    def sRGB_to_HLS(self, r, g, b):
        """Convert Standard RGB (sRGB) to HLS

        All r/g/b values in `[0., 1.]`, h in `[0., 360.]`, l and s in `[0., 1.]`.
        From: http://wiki.beyondunreal.com/wiki/RGB_To_HLS_Conversion.

        Args:
            r (numpy.ndarray): Intensities for red (`[0., 1.]`)
            g (numpy.ndarray): Intensities for green (`[0., 1.]`)
            b (numpy.ndarray): Intensities for blue (`[0., 1.]`)

        Returns:
            list: Returns a list of `numpy.ndarray`s with the corresponding
            coordinates in the HLS color space (`[h, l, s]`). Same length as
            the inputs.
        """

        __fname__ = inspect.stack()[0][3] # Name of this method

        # Checking input
        self._check_input_arrays_(__fname__, r = r, g = g, b = b)

        # Support function
        def gethls(r, g, b):
            min = np.min([r, g, b])
            max = np.max([r, g, b])

            l = (max + min)/2.;

            if max != min:
                if   l <  0.5: s = (max - min) / (max + min)
                elif l >= 0.5: s = (max - min) / (2. - max - min)

                if r == max:  h = (g - b) / (max - min);
                if g == max:  h = 2. + (b - r) / (max - min);
                if b == max:  h = 4. + (r - g) / (max - min);

                h = h * 60.;
                if h < 0.:    h = h + 360.;
                if h > 360.:  h = h - 360.;
            else:
                s = 0
                h = 0;

            return [h, l, s]

        # Result arrays
        h = np.ndarray(len(r), dtype = "float"); h[:] = 0.
        l = np.ndarray(len(r), dtype = "float"); l[:] = 0.
        s = np.ndarray(len(r), dtype = "float"); s[:] = 0.

        for i in range(0,len(h)):
           tmp = gethls(r[i], g[i], b[i])
           h[i] = tmp[0]; l[i] = tmp[1]; s[i] = tmp[2]

        return [h, l, s]


    def HLS_to_sRGB(self, h, l, s):
        """Convert HLC to Standard RGB (sRGB)

        All r/g/b values in `[0., 1.]`, h in `[0., 360.]`, l and s in `[0., 1.]`.

        Args:
            h (numpy.ndarray): Hue values.
            l (numpy.ndarray): Lightness.
            s (numpy.ndarray): Saturation.

        Returns:
            list: Returns a list of `numpy.ndarray`s with the corresponding
            coordinates in the sRGB color space (`[r, g, b]`). Same length as
            the inputs.
        """

        __fname__ = inspect.stack()[0][3] # Name of this method

        # Checking input
        self._check_input_arrays_(__fname__, h = h, l = l, s = s)

        # Support function qtrans
        def qtrans(q1, q2, hue):
            if hue > 360.:   hue = hue - 360.
            if hue < 0:      hue = hue + 360.

            if hue < 60.:    return q1 + (q2 - q1) * hue / 60.
            elif hue < 180.: return q2
            elif hue < 240.: return q1 + (q2 - q1) * (240. - hue) / 60.
            else:            return q1

        # Support function
        def getrgb(h, l, s):
            p2 = l * (1. + s) if l <= 0.5 else l + s - (l * s)
            p1 = 2 * l - p2

            # If saturation is zero
            if (s == 0):    return np.repeat(l, 3)
            # Else
            return [qtrans(p1, p2, h + 120.),   # r
                    qtrans(p1, p2, h),          # g
                    qtrans(p1, p2, h - 120.)]   # b

        # Result arrays
        r = np.ndarray(len(h), dtype = "float"); r[:] = 0.
        g = np.ndarray(len(h), dtype = "float"); g[:] = 0.
        b = np.ndarray(len(h), dtype = "float"); b[:] = 0.

        for i in range(0,len(r)):
           tmp = getrgb(h[i], l[i], s[i])
           r[i] = tmp[0]; g[i] = tmp[1]; b[i] = tmp[2]

        return [r, g, b]


    # -------------------------------------------------------------------
    # -------------------------------------------------------------------
    # -------------------------------------------------------------------
    # -------------------------------------------------------------------
    def XYZ_to_uv(self, X, Y, Z):
        """Convert CIEXYZ to u and v

        Args:
            X (numpy.ndarray): Values for the `Z` dimension.
            Y (numpy.ndarray): Values for the `Y` dimension.
            Z (numpy.ndarray): Values for the `Z` dimension.

        Returns:
            list: Returns a list of `numpy.ndarray`s (`[u, v]`). 
        """

        __fname__ = inspect.stack()[0][3] # Name of this method

        # Checking input
        self._check_input_arrays_(__fname__, X = X, Y = Y, Z = Z)

        # Result array
        x = np.ndarray(len(X), dtype = "float"); x[:] = 0.
        y = np.ndarray(len(X), dtype = "float"); y[:] = 0.

        t = X + Y + Z
        idx = np.where(t != 0)
        x[idx] = X[idx] / t[idx];
        y[idx] = Y[idx] / t[idx];

        return [2.0 * x / (6. * y - x + 1.5),    # u
                4.5 * y / (6. * y - x + 1.5)]    # v

    def XYZ_to_LUV(self, X, Y, Z, XN = None, YN = None, ZN = None):
        """Convert CIEXYZ to CIELUV.

        `X`, `Y`, and `Z` specify the values in the three coordinates of the
        CIELAB color space,
        `XN`, `YN`, and `ZN` allow to specify additional CIE chromaticities to
        specify a specific white point.

        Args:
            X (numpy.ndarray): Values for the `X` dimension.
            Y (numpy.ndarray): Values for the `Y` dimension.
            Z (numpy.ndarray): Values for the `Z` dimension.
            XN (None, numpy.ndarray): Chromaticity of the white point. If of
                length `1`, the white point specification will be recycled if needed.
                When not specified (all `None`) a default white point is used.
            YN: See `XN`.
            ZN: See `XN`.

        Returns:
            list: Returns corresponding coordinates of CIE chromaticities as
            a list of `numpy.ndarray`s of the same length as the inputs (`[L, U, V]`).
        """

        __fname__ = inspect.stack()[0][3] # Name of this method
        n = len(X) # Number of colors

        # Loading definition of white
        [XN, YN, ZN] = self._get_white_(__fname__, n, XN, YN, ZN)

        # Checking input
        self._check_input_arrays_(__fname__, X = X, Y = Y, Z = Z)

        # Convert X/Y/Z and XN/YN/ZN to uv
        [u,  v]  = self.XYZ_to_uv(X,  Y,  Z )
        [uN, vN] = self.XYZ_to_uv(XN, YN, ZN)

        # Calculate L
        L = np.ndarray(len(X), dtype = "float"); L[:] = 0.
        y = Y / YN
        for i,val in np.ndenumerate(y):
            L[i] = 116. * np.power(val, 1./3.) - 16. if val > self._EPSILON else self._KAPPA * val

        # Calculate U/V
        return [L, 13. * L * (u - uN), 13. * L * (v - vN)]  # [L, U, V]

    def LUV_to_XYZ(self, L, U, V, XN = None, YN = None, ZN = None):
        """Convert CIELUV to CIELAB.

        `L`, `U`, and `V` specify the values in the three coordinates of the
        CIELAB color space,
        `XN`, `YN`, and `ZN` allow to specify additional CIE chromaticities to
        specify a specific white point.

        Args:
            L (numpy.ndarray): Values for the `L` dimension.
            U (numpy.ndarray): Values for the `U` dimension.
            V (numpy.ndarray): Values for the `V` dimension.
            XN (None, numpy.ndarray): Chromaticity of the white point. If of
                length `1`, the white point specification will be recycled if needed.
                When not specified (all `None`) a default white point is used.
            YN: See `XN`.
            ZN: See `XN`.

        Returns:
            list: Returns corresponding coordinates of CIE chromaticities as
            a list of `numpy.ndarray`s of the same length as the inputs (`[L, A, B]`).
        """

        __fname__ = inspect.stack()[0][3] # Name of this method
        n = len(L) # Number of colors

        # Loading definition of white
        [XN, YN, ZN] = self._get_white_(__fname__, n, XN, YN, ZN)

        # Checking input
        self._check_input_arrays_(__fname__, L = L, U = U, V = V)

        # Result arrays
        X = np.ndarray(len(L), dtype = "float"); X[:] = 0.
        Y = np.ndarray(len(L), dtype = "float"); Y[:] = 0.
        Z = np.ndarray(len(L), dtype = "float"); Z[:] = 0.

        # Check for which values we do have to do the transformation
        def fun(L, U, V):
            return False if L <= 0. and U == 0. and V == 0. else True
        idx = np.where([fun(L[i], U[i], V[i]) for i in range(0, len(L))])[0]
        if len(idx) == 0: return [X, Y, Z]

        # Compute Y
        for i in idx:
            Y[i] = YN[i] * (np.power((L[i] + 16.)/116., 3.) if L[i] > 8. else L[i] / self._KAPPA)

        # Calculate X/Z
        from numpy import finfo, fmax

        # Avoiding division by zero
        eps = np.finfo(float).eps*10
        L = fmax(eps, L)

        [uN, vN] = self.XYZ_to_uv(XN, YN, ZN)
        u = U / (13. * L) + uN
        v = V / (13. * L) + vN
        X =  9.0 * Y * u / (4 * v)
        Z =  -X / 3. - 5. * Y + 3. * Y / v

        return [X, Y, Z]


    ## ----- LUV <-> polarLUV ----- */
    def LUV_to_polarLUV(self, L, U, V):
        """Convert CIELUV to the polar representation (polarLUV; HCL)

        Converts colors from the CIELUV color space into its polar
        representation (`polarLUV`). The `polarLUV` color space
        is also known as the HCL (Hue-Chroma-Luminance) color space
        which this package uses frequently, e.g., when creating
        efficient color maps. Inverse function of :py:func:`polarLUV_to_LUV`.

        Args:
            L (numpy.ndarray): Values for the `L` dimension.
            U (numpy.ndarray): Values for the `U` dimension.
            V (numpy.ndarray): Values for the `V` dimension.

        Returns:
            list: Returns corresponding polar LUV chromaticities as a list of
            `numpy.ndarray`s of the same length as the inputs (`[L, A, B]`),
            also known as `[H, C, L]` coordinates.
        """

        __fname__ = inspect.stack()[0][3] # Name of this method

        self._check_input_arrays_(__fname__, L = L, U = U, V = V)

        # Calculate polarLUV coordinates
        C = np.sqrt(U * U + V * V)
        H = self.RAD2DEG(np.arctan2(V, U))
        for i,val in np.ndenumerate(H):
            while val > 360: val -= 360.
            while val < 0.:  val += 360.
            H[i] = val

        return [L, C, H]

    def polarLUV_to_LUV(self, L, C, H):
        """Convert Polar CIELUV (HCL) to CIELUV

        Convert colors from the polar representation of the CIELUV color space,
        also known as HCL (Hue-Chroma-Luminance) color space, into CIELAB
        coordinates.
        Inverse function of :py:func:`LUV_to_polarLUV`.

        Args:
            L (numpy.ndarray): Values for the polar `L` dimension.
            U (numpy.ndarray): Values for the polar `U` dimension.
            V (numpy.ndarray): Values for the polar `V` dimension.

        Returns
            list: Returns corresponding CIELAB chromaticities as a list of
            `numpy.ndarray`s of the same length as the inputs (`[L, U, V]`).
        """

        __fname__ = inspect.stack()[0][3] # Name of this method

        # Checking input
        self._check_input_arrays_(__fname__, L = L, C = C, H = H)

        H = self.DEG2RAD(H)
        return [L, C * np.cos(H), C * np.sin(H)] # [L, U, V]


    def sRGB_to_hex(self, r, g, b, fixup = True):
        """Convert Standard RGB (sRGB) to Hex Colors

        Args:
            r (numpy.ndarray): Intensities for red (`[0., 1.,]`).
            g (numpy.ndarray): Intensities for green (`[0., 1.,]`).
            b (numpy.ndarray): Intensities for blue (`[0., 1.,]`).
            fixup (bool): Whether or not the `rgb` values should be corrected
                if they lie outside the defined RGB space (outside `[0., 1.,]`),
                defaults to `True`.

        Returns:
            list: A list with hex color strings.
        """

        # Color fixup: limit r/g/b to [0-1]
        def rgbfixup(r, g, b):
            def fun(x):
                return np.asarray([np.max([0, np.min([1, e])]) \
                       if np.isfinite(e) else np.nan for e in x])
            return [fun(r), fun(g), fun(b)]

        def rgbcleanup(r, g, b):
            def fun(x):
                return np.asarray([e if np.logical_and(e >= 0., e <= 1.)
                       else np.nan for e in x])
            return [fun(r), fun(g), fun(b)]

        # Checking which r/g/b values are outside limits.
        # This only happens if fixup = FALSE.
        def validrgb(r, g, b):
            idxr = np.isfinite(r)
            idxg = np.isfinite(g)
            idxb = np.isfinite(b)
            return np.where(idxr * idxg * idxb)[0]

        # Support function to create hex coded colors
        def gethex(r, g, b):

            # Converts integers to hex string
            def applyfun(x):
                x = np.asarray(x * 255. + .5, dtype = int)
                return "#{:02X}{:02X}{:02X}".format(x[0], x[1], x[2])

            h = np.vstack([r,g,b]).transpose().flatten().reshape([len(r), 3])
            return np.apply_along_axis(applyfun, 1, h)

        # Let's do the conversion!
        if fixup: [r, g, b] = rgbfixup(r, g, b)
        else:     [r, g, b] = rgbcleanup(r, g, b)

        # Create return array
        res = np.ndarray(len(r), dtype = "|S7"); res[:] = ""

        # Check valid r/g/b coordinates
        valid = validrgb(r,g,b)
        if len(valid) > 0:
            # Convert valid colors to hex
            res[valid] = gethex(r[valid], g[valid], b[valid])

        # Create return list with NAN's for invalid colors
        res = [np.nan if len(x) == 0 else x.decode() for x in res]

        # Return numpy array
        return np.asarray(res)

    def hex_to_sRGB(self, hex_, gamma = 2.4):
        """Convert Hex Colors to Standard RGB (sRGB)

        Args:
            hex_ (str, list of str): hex color string or list of strings.
            gamma (float): Gamma correction factor, defaults to `2.4`.

        Returns:
            list: Returns a list of `numpy.ndarray`s with the corresponding
            red, green, and blue intensities (`[r, g, b]`), all in `[0., 1.]`.
        """

        if isinstance(hex_,str): hex_ = [hex_]
        hex_ = np.asarray(hex_)

        # Check for valid hex colors
        def validhex(hex_):
            from re import match
            #TODO(R): Can I outsource this to check_hex_colors not to have
            #         the same expression hanging around twice?
            return np.where([match("^#[0-9A-Fa-f]{6}([0-9]{2})?$$", x) is not None for x in hex_])[0]

        # Convert hex to rgb
        def getrgb(x):
            def applyfun(x):
                return np.asarray([int(x[i:i+2], 16) for i in (1, 3, 5)])
            rgb = [applyfun(e) for e in x]
            rgb = np.vstack(rgb).transpose().flatten().reshape([3,len(x)])
            return [rgb[0] / 255., rgb[1] / 255., rgb[2] / 255.]

        # Result arrays
        r = np.ndarray(len(hex_), dtype = "float"); r[:] = np.nan 
        g = np.ndarray(len(hex_), dtype = "float"); g[:] = np.nan 
        b = np.ndarray(len(hex_), dtype = "float"); b[:] = np.nan 

        # Check valid hex colors
        valid = validhex(hex_)
        if not len(valid) == 0:
            # Decode valid hex strings
            rgb = getrgb(hex_[valid])
            r[valid] = rgb[0]
            g[valid] = rgb[1]
            b[valid] = rgb[2]

        return [r, g, b]


# -------------------------------------------------------------------
# Color object base class
# will be extended by the different color classes.
# -------------------------------------------------------------------
class colorobject:
    """Superclass for All Color Objects

    A series of constructors are available to construct `colorobjects` in a
    variety of different color spaces, all inheriting from this class. This
    superclass provides the general functionality to handle colors (sets of
    colors) and convert colors from and to different color spaces.

    Users should use the dedicated classes for the available color spaces which
    all extend this class. These are: CIELAB, CIELUV, CIEXYZ, hexcols, HLS,
    HSV, polarLAB, polarLUV, RGB, and sRGB.
    """

    import numpy as np

    # Allowed/defined color spaces
    ALLOWED = ["CIEXYZ", "CIELUV", "CIELAB", "polarLUV", "polarLAB",
               "RGB", "sRGB", "HCL", "HSV", "HLS", "hex"]
    """List of allowed/defined color spaces; used to check when converting
    colors from one color space to another."""

    # Used to store alpha if needed. Will only be used for some of
    # the colorobject objects as only few color spaces allow alpha
    # values.
    ALPHA = None
    """Used to store (keep) transparency when needed; will be dropped during conversion."""

    GAMMA = 2.4 # Used to adjust RGB (sRGB_to_RGB and back).
    """Gamma value used used to adjust RGB colors; currently a fixed value of 2.4."""

    # Standard representation of colorobject objects.
    def __repr__(self, digits = 2):
        """Color Object Standard Representation

        Standard representation of the color object; shows the values
        of all coordinates (or the hex strings if hex colors).

        Args:
            digits (int): Number of digits, defaults to `2`.

        Returns:
            str: Returns a string of the colors/coordinates of the current object.
        """
        dims = list(self._data_.keys())    # Dimensions

        from .colorlib import hexcols
        import numpy as np

        # Sorting the dimensions
        from re import match
        if   match("^(hex\_|alpha){1,2}$",  "".join(dims)): dims = ["hex_"]
        elif match("^(R|G|B|alpha){3,4}$", "".join(dims)): dims = ["R", "G", "B"]
        elif match("^(L|A|B|alpha){3,4}$", "".join(dims)): dims = ["L", "A", "B"]
        elif match("^(L|U|V|alpha){3,4}$", "".join(dims)): dims = ["L", "U", "V"]
        elif match("^(H|C|L|alpha){3,4}$", "".join(dims)): dims = ["H", "C", "L"]
        elif match("^(X|Y|Z|alpha){3,4}$", "".join(dims)): dims = ["X", "Y", "Z"]
        elif match("^(H|S|V|alpha){3,4}$", "".join(dims)): dims = ["H", "S", "V"]
        elif match("^(H|L|S|alpha){3,4}$", "".join(dims)): dims = ["H", "L", "S"]

        # Number of colors
        ncol = max([0 if self._data_[x] is None else len(self._data_[x]) for x in dims])

        # Add 'alpha' to object 'dims' if we have defined alpha values
        # for this colorobject. Else alpha will not be printed.
        if "alpha" in list(self._data_.keys()):
            if self._data_["alpha"] is not None: dims += ["alpha"]

        # Start creating the string:
        res = ["{:s} color object ({:d} colors)".format(self.__class__.__name__, ncol)]

        # Show header
        fmt = "".join(["{:>", "{:d}".format(digits + 6), "s}"])
        res.append("    " + "".join([fmt.format(x) for x in dims]))

        # Show data
        # In case of a hexcols object: string formatting and
        # nan-replacement beforehand.
        if isinstance(self, hexcols):
            data = {}
            fmt = "".join(["{:", "{:d}.{:d}".format(6 + digits, 3), "f}"])
            data["hex_"] = np.ndarray(ncol, dtype = "|S7")
            for n in range(0, ncol):
                x = self._data_["hex_"][n]
                data["hex_"][n] = fmt.format(x) if isinstance(x, float) else x[0:7]
            data["alpha"] = self.get("alpha")
            fmt = "{:>8s}"
        else:
            fmt = "".join(["{:", "{:d}.{:d}".format(6+digits, digits), "f}"])
            data = self._data_

        # Print object content
        count = 0
        for n in range(0, ncol):
            if (n % 10) == 0: 
                tmp = "{:3d}:".format(n+1)
            else:
                tmp = "    "
            for d in dims:
                # Special handling for alpha
                if d == "alpha":
                    if data[d][n] is None:
                        tmp += "  ---"
                    elif isinstance(data[d][n], float):
                        if np.isnan(data[d][n]):
                            tmp += "  ---"
                        elif isinstance(self, hexcols):
                            tmp += "    {:02X}".format(int(255. * data[d][n]))
                        else:
                            tmp += "    {:4.2f}".format(data[d][n])
                else:
                    if data[d] is None or data[d][n] is None:
                        tmp += "  ---"
                    elif isinstance(data[d][n], str) or isinstance(data[d][n], np.bytes_):
                        tmp += fmt.format(data[d][n])
                    else:
                        tmp += fmt.format(float(data[d][n]))

            count += 1
            res.append(tmp)

            if count >= 30 and ncol > 40:
                res.append("".join([" ......"]*len(dims)))
                res.append("And {:d} more [truncated]".format(ncol - count))
                break

        return "\n".join(res)

    def __call__(self, fixup = True, rev = False):
        """Magic Method

        Default call method of all color objects. Always returns
        hex colors, same as the `.colors()` method does.

        Args:
            fixup (bool): Fix colors outside defined color space, defaults to `True`.
            rev (bool): Revert colors, defaults to `False`.

        Returns:
            list: Returns a list of hex colors.
        """
        return self.colors(fixup = fixup, rev = rev)

    def __iter__(self):
        self.n = -1
        return self

    def __next__(self):
        if self.n < (self.length() - 1):
            self.n += 1
            res = self[self.n]
            return res
        else:
            raise StopIteration

    ## Required by python2
    ## TODO(R) Can be removed?
    #def next(self):
    #    """Next method

    #    Originally required by python2.
    #    """
    #    return self.__next__()

    def __getitem__(self, key):
        if not isinstance(key, int):
            raise TypeError("argument `key` must be integer (index)")

        from copy import deepcopy
        from numpy import array, newaxis
        res = deepcopy(self)
        for n in list(res._data_.keys()):
            # If None: keep it as it is, else subset
            if res._data_[n] is None: continue
            res._data_[n] = res._data_[n][newaxis, key]

        return res


    def get_whitepoint(self):
        """Get White Point

        This method returns the definition of the white point in use. If not
        explicitly set via the :py:method:`set_whitepoint` method, a default white
        point is used.

        Returns:
            dict: Returns a dict with `X`, `Y`, `Z`, the white point specification
            for the three dimensions.

        Example:

            >>> from colorspace.colorlib import hexcols
            >>> c = hexcols("#ff0000")
            >>> c.get_whitepoint()
        """
        return {"X": self.WHITEX, "Y": self.WHITEY, "Z": self.WHITEZ}

    def set_whitepoint(self, **kwargs):
        """Set White Point

        A white point definition is used to adjust the colors.
        This method allows to set custom values. If not explicitly
        set a default specification is used. The :py:method:`get_whitepoint`
        method can be used to extract the currently used definition.

        Args:
            **kwargs: Named arguments. Allowed are `X`, `Y`, and `Z`,
                each of which must be float: White specification for
                dimension `X`/`Y`/`Z`.

        Returns:
            No return, stores the new definition on the object.

        Example:

            >>> from colorspace.colorlib import hexcols
            >>> c = hexcols("#ff0000")
            >>> c.set_whitepoint(X = 100., Y = 100., Z = 101.)
            >>> c.get_whitepoint()
        """
        for key,arg in kwargs.items():
            if   key == "X":  self.WHITEX = float(arg)
            elif key == "Y":  self.WHITEY = float(arg)
            elif key == "Z":  self.WHITEZ = float(arg)
            else: 
                raise ValueError("error in {:s}.set_whitepoint: ".format(self.__class__name__) + \
                        "argument \"{:s}\" not recognized.".format(key))


    def _check_if_allowed_(self, x):
        """Check for Valid Transformation

        Helper function checking if the transformation of the current
        object into another color space is allowed or not.
        An exception will be thrown if the transformation is not possible.

        Args:
            x (str): Name of the target color space.

        Returns:
            No return, raises an Exception if the transformation is invalid.
        """
        if not x in self.ALLOWED:
            raise Exception("transformation from {:s}".format(self.__class__.__name__) + \
                    f" to \"{x}\" is unknown (not implemented). " + \
                    f"The following are allowed: {', '.join(self.ALLOWED)}")
        return


    def _transform_via_path_(self, via, fixup):
        """Transform Colors along Path

        Helper function to transform a colorobject into a new color
        space. Calls the :py:func:`to` method one or multiple times along 'a path'
        as specified by `via`.

        Returns:
            No return, converts the current color space object (see method :py:func:`to`).

        Args:
            via (list of strings): The path via which the current color object
                should be transformed. For example: A :py:class:`hexcols`
                object can be transformed into CIEXYZ by specifying
                `via = ["sRGB", "RGB", "CIEXYZ"]`.
            fixup (bool): Whether or not to correct invalid rgb values outside
                `[0., 1.]` if necessary
        """
        for v in via:   self.to(v, fixup = fixup)

    def _colorobject_check_input_arrays_(self, **kwargs):
        """Colorobject Check User Input

        Checks if all inputs in `**kwargs` are of type `numpy.ndarray` OR lists
        (will be converted to `numpy.ndarray`s) and that all are of the same length.
        If not, the script will throw an exception.

        If `alpha` is given it is handled in a special way. If `alpha = None`
        it will simply be dropped (no alpha channel specified), else it is
        handled like the rest and has to fulfill the requirements all the
        other dimensions have to (length and type).

        Args:
            **kwargs: Named keywords, objects to be checked.

        Returns:
            bool: Returns `True` if all checks where fine, throws an exception
            if the inputs do not fulfil the requirements.
        """

        from numpy import asarray, float64

        # Message will be dropped if problems occur
        msg = f"Problem while checking inputs \"{', '.join(kwargs.keys())}\" " + \
              f"to class \"{self.__class__.__name__}\"."

        res = {}
        lengths = []
        keys_to_check = []
        for key,val in kwargs.items():
            # No alpha provided, simply proceed
            if key == "alpha" and val is None: continue

            keys_to_check.append(key)

            # If is list: convert to ndarray no matter how long the element is
            if isinstance(val,float) or isinstance(val,int):
                val = np.asarray([val])
            elif isinstance(val,list):
                val = np.asarray(val)

            # For alpha, R, G, and B: check range
            if isinstance(self, RGB) or isinstance(self, sRGB):
                if np.max(val) > 1. or np.max(val) < 0.:
                    raise ValueError("wrong values specified for " + \
                            f"dimension {key} in {self.__class__.__name__}: " + \
                            "values have to lie within [0., 1.]")

            # Check object type
            from numpy import asarray
            try:
                val = asarray(val)
            except Exception as e:
                raise ValueError(f"input {key} to {self.__class__.__name__}" + \
                        f" could not have been converted to `numpy.ndarray`: {str(e)}")

            # Else append length and proceed
            lengths.append(len(val))

            # Append to result vector
            if isinstance(val, int) or isinstance(val, float): val = [val]
            res[key] = val if key == "hex_" else asarray(val, float64)

        # Check if all do have the same length
        if not np.all([x == lengths[0] for x in lengths]):
            msg += "Arguments of different lengths: {:s}".format(
                   ", ".join(["{:s} = {:d}".format(keys_to_check[i], lengths[i]) \
                    for i in range(0, len(keys_to_check))]))
            raise ValueError(msg)

        return res


    def hasalpha(self):
        """Check for Alpha Channel

        Small helper function to check whether the current color object
        has alpha channel or not.

        Returns:
            bool: `True` if alpha values are present, `False` if not.
        """
        if not "alpha" in self._data_.keys():
            return False
        elif self._data_["alpha"] is None:
            return False
        else:
            return True


    def dropalpha(self):
        """Remove Alpha Channel

        Remove alpha channel from the color object, if defined
        (see :py:method:`hasalpha`).
        """
        if self.hasalpha():
            del self._data_["alpha"]

        return


    def specplot(self, **kwargs):
        """Color Spectrum Plot

        Visualization of the spectrum of this color object.
        Internally calls :py:func:`specplot <colorspace.specplot.specplot>`,
        additional arguments to this main function can be forwarded via the
        `**kwargs` argument.

        Args:
            **kwargs: Additional named arguments forwarded to
                :py:func:`specplot <colorspace.specplot.specplot>`.

        Example:

            >>> from colorspace.colorlib import HCL
            >>> cols = HCL([260, 80, 30], [80, 0, 80], [30, 90, 30])
            >>> cols.specplot();
            >>> cols.specplot(rgb = False, figsize = (6, 0.5));
        """
        from copy import copy
        cols = copy(self)
        cols.to("hex")

        if isinstance(cols, colorobject):
            from .specplot import specplot
            specplot(cols.colors(), **kwargs)


    def swatchplot(self, **kwargs):
        """Palette Swatch Plot

        Visualization the color palette of this color object.
        Internally calls :py:func:`specplot <colorspace.specplot.specplot>`,
        additional arguments to this main function can be forwarded via the
        `**kwargs` argument.

        Args:
            **kwargs: Additional named arguments forwarded to
                :py:func:`swatchplot <colorspace.swatchplot.swatchplot>`.

        Example:

            >>> from colorspace.colorlib import HCL
            >>> cols = HCL(H = [160, 210, 260, 310, 360],
            >>>            C = [ 70,  40,  10,  40,  70],
            >>>            L = [ 50,  70,  90,  70,  50])
            >>> cols.swatchplot();
            >>> cols.swatchplot(figsize = (6, 0.5));
        """

        from .swatchplot import swatchplot
        if "show_names" in kwargs.keys():
            del kwargs["show_names"]
        swatchplot(pals = self.colors(), show_names = False, **kwargs)

    def colors(self, fixup = True, rev = False):
        """Extract Hex Colors

        Returns hex colors of the current color object by converting
        the current color object into an object of class :py:class:`hexcols`.

        If the object contains alpha values, the alpha level is added to the
        hex string if and only if alpha is not equal to `1.0`.

        Args:
            fixup (bool): Whether or not to correct rgb values outside the
                defined range of `[0., 1.]`, defaults to `True`.
            rev (bool): Should the color palette be reversed? Defaults to `False`.

        Returns:
            list: Returns a list of hex color strings.

        Example:

            >>> from colorspace.colorlib import HCL
            >>> cols = HCL([0, 40, 80], [30, 60, 80], [85, 60, 35])
            >>> cols.colors()
        """

        from copy import copy
        x = copy(self)
        x.to("hex", fixup = fixup)
        if x.hasalpha():
            res = x.get("hex_")
            # Appending alpha if alpha < 1.0
            for i in range(0, len(res)):
                if self._data_["alpha"][i] < 1.0:
                    res[i] += "{:02d}".format(int(self._data_["alpha"][i] * 100.))
            # Return hex with alpha
            colors = res
        else:
            colors = x.get("hex_")

        if rev:
            from numpy import flip
            colors = flip(colors)
        return [str(x) for x in colors]


    def get(self, dimname = None):
        """Extracting Color Coordinates

        Extracts and returns the current values of a all or one specific coordinate
        for all colors of this color object.

        Args:
            dimname (None, str): If `None` (default) values of all coordinates
                of the current color object are returned. A specific coordinate
                can be specified if needed.

        Returns:
            dict, numpy.ndarray: If argument `dimname = None` a dictionary is returned
            containing the values of all colors for all coordinates of the current
            color space, each entry of the dictionary is a `numpy.ndarray`.
            When a specific dimension is requested, a single `numpy.ndarray` is
            returned.

        Raises:
            TypeError: If `dimname` is neither `None` or str.
            ValueError: If the dimension specified on `dimnames` does not
                exist.

        Example:

            >>> from colorspace.colorlib import HCL
            >>> cols = HCL([260, 80, 30], [80, 0, 80], [30, 90, 30])
            >>> cols.get()
            >>> cols.get("H")
        """

        # Return all coordinates
        from copy import copy
        if dimname is None:
            return copy(self._data_)
        # No string?
        elif not isinstance(dimname, str):
            raise TypeError("argument `dimname` must be None or str")
        # Else only the requested dimension
        elif not dimname in self._data_.keys():
            # Alpha channel never defined, return None (which
            # is a valid value for "no alpha")
            if dimname == "alpha":
                return None
            else:
                raise ValueError(f"{self.__class__.__name__} has no dimension {dimname}.")

        return copy(self._data_[dimname])


    def set(self, **kwargs):
        """Set/Manipulate Colors

        Allows to manipulate the current colors. The named input arguments
        have to fulfil a specific set or requirements. If not, the function
        raises exceptions. The requirements:

        * Dimension has to exist
        * New data/values must be of same length and type as the existing ones

        Args:
            **kwargs: Named arguments. The key is the name of the dimension to
                be changed, the value an object which fulfills the requirements
                (see description of this method)

        Returns:
            No return, modifies the current color object.

        Raises:
            ValueError: If the dimension does not exist.
            ValueError: If the new data can't be converted into
                `numpy.array` (is done automatically if needed).
            ValueError: If new data has wrong length (does not match the
                number of colors/length of current values).

        Example:

            >>> from colorspace.colorlib import HCL
            >>> cols = HCL([260, 80, 30], [80, 0, 80], [30, 90, 30])
            >>> print(cols)
            >>> #:
            >>> cols.set(H = [150, 150, 30])
            >>> print(cols)
        """
        # Looping over inputs
        from numpy import asarray, ndarray
        for key,vals in kwargs.items():
            key.upper()

            # Check if the key provided by the user is a valid dimension
            # of the current object.
            if not key in self._data_.keys():
                raise ValueError(f"{self.__class__.__name__} has no dimension {key}")

            # In case the input is a single int/float or a list; try
            # to convert the input into a numpy.array using the same
            # dtype as the existing dimension (loaded via self.get(key)).
            if isinstance(vals, (list, int, float)):
                if isinstance(vals, (int, float)): vals = [vals]
                t = type(self.get(key)[0]) # Current type (get current dimension)
                try:
                    vals = np.asarray(vals, dtype = t)
                except Exception as e:
                    raise ValueError(f"problems converting new data to {t} " + \
                            f" in {self.__class__.__name__}: {str(e)}")

            # New values do have to have the same length as the old ones,
            n = len(self.get(key))
            t = type(self.get(key)[0])
            try:
                vals = np.asarray(vals, dtype = t)
            except Exception as e:
                raise ValueError("problems converting new data to {:s} ".format(t) + \
                    " in {:s}: {:s}".format(self.__class__.__name__, str(e)))
            if not vals.size == n:
                raise ValueError("number of values to be stored on the object " + \
                    f"{self.__class__.__name__} have to match the current dimension")

            self._data_[key] = vals

    def length(self):
        """Get Number of Colors

        Returns the number of colors defined in this color object.

        Return:
            int: Number of colors defined.
        """
        # Number of colors
        return max([0 if self._data_[x] is None else len(self._data_[x]) for x in self._data_.keys()])

    def __len__(self):
        return self.length()


    def _cannot(self, from_, to):
        """Error: Conversion not Possible

        Helper function used to raise an exception as a specific
        transformation is not possible by definition.

        Args:
            from_ (str): Name of the current color space.
            to (str): Name of the target color space.

        Raises:
            Exception: Always, that is the intent of this method.
        """
        raise Exception(f"Cannot convert class \"{from_}\" to \"{to}\".")

    def _ambiguous(self, from_, to):
        """Error: Conversion Ambiguous

        Helper function used to raise an exception as a specific
        transformation is ambiguous and therefore not possible by definition.

        Args:
            from_ (str): Name of the current color space.
            to (str): Name of the target color space.

        Raises:
            Exception: Always, that is the intent of this method.
        """
        raise Exception(f"Conversion not possible, ambiguous conversion from \"{from_}\" to \"{to}\".")


# -------------------------------------------------------------------
# PolarLUV or HCL object
# -------------------------------------------------------------------
class polarLUV(colorobject):
    """Create polarLUV (HCL) Color Object

    Creates a color object in the polar representation of the :py:class:`CIELUV`
    color space, also known as the Hue-Chroma-Luminance (HCL) color space.
    Can be converted to: :py:class:`CIEXYZ`, :py:class:`CIELUV`,
    :py:class:`CIELAB`, :py:class:`RGB`, :py:class:`sRGB`,
    :py:class:`polarLAB`, and :py:class:`hexcols`.
    Not allowed (ambiguous) are transformations to :py:class:`HSV` and :py:class:`HLS`.

    Args:
        H (int, float, list, numpy.array):
            Numeric value(s) for hue dimension (`[-360., 360.]`).
        C (int, float, list, numpy.array):
            Numeric value(s) for chroma dimension (`[0., 100.+]`).
        L (int, float, list, numpy.array):
            Numeric value(s) for luminance dimension (`[0., 100.]`).
        alpha (None, float, list, numpy.array): Numeric value(s) for the alpha
            channel (`[0., 1.]`) where `0.` equals full transparency, `1.` full
            opacity. If `None` (default) no transparency is added.

    Example:

        >>> from colorspace.colorlib import polarLUV, HCL
        >>> # Constructing color object with one single color via float
        >>> polarLUV(100., 30, 50.)
        >>> #: polarLUV is the HCL color space, this
        >>> #  is equivalent to the command above.
        >>> HCL(100., 30, 50.)
        >>> #: Constructing object via lists
        >>> HCL([100, 80], [30, 50], [30, 80])
        >>> #: Constructing object via numpy arrays
        >>> from numpy import asarray
        >>> HCL(asarray([100, 80]), asarray([30, 50]), asarray([30, 80]))
    """

    def __init__(self, H, C, L, alpha = None):

        # Checking inputs, save inputs on object
        self._data_ = {} # Dict to store the colors/color dimensions
        tmp = self._colorobject_check_input_arrays_(H = H, C = C, L = L, alpha = alpha)
        for key,val in tmp.items(): self._data_[key] = val
        # White spot definition (the default)
        self.set_whitepoint(X = 95.047, Y = 100.000, Z = 108.883)

    def to(self, to, fixup = True):
        """Transform Color Space

        Allows to transform the current object into a different color space,
        if possible.

        Args:
            to (str): Name of the color space into which the colors should be
                converted (e.g., `CIEXYZ`, `HCL`, `hex`, `RGB`, ...)
            fixup (bool): Whether or not colors outside the defined rgb color space
                should be corrected if necessary, defaults to True.

        Returns:
            No return, converts the object into a new color space and modifies
            the underlying object. After calling this method the object will
            be of a different class.
        """
        self._check_if_allowed_(to)
        from . import colorlib
        clib = colorlib()

        # Nothing to do (converted to itself)
        if to in ["HCL", self.__class__.__name__]:
            return

        # This is the only transformation from polarLUV -> LUV
        elif to == "CIELUV":
            [L, U, V] = clib.polarLUV_to_LUV(self.get("L"), self.get("C"), self.get("H"))
            self._data_ = {"L" : L, "U" : U, "V" : V, "alpha" : self.get("alpha")}
            self.__class__ = CIELUV

        # The rest are transformations along a path
        elif to == "CIEXYZ":
            via = ["CIELUV", to]
            self._transform_via_path_(via, fixup = fixup)

        elif to == "CIELAB":
            via = ["CIELUV", "CIEXYZ", to]
            self._transform_via_path_(via, fixup = fixup)

        elif to == "RGB":
            via = ["CIELUV", "CIEXYZ", to]
            self._transform_via_path_(via, fixup = fixup)

        elif to == "sRGB":
            via = ["CIELUV", "CIEXYZ", to]
            self._transform_via_path_(via, fixup = fixup)

        elif to == "polarLAB":
            via = ["CIELUV", "CIEXYZ", "CIELAB", to]
            self._transform_via_path_(via, fixup = fixup)

        elif to == "hex":
            via = ["CIELUV", "CIEXYZ", "sRGB", to]
            self._transform_via_path_(via, fixup = fixup)

        elif to in ["HLS", "HSV"]:
            self._ambiguous(self.__class__.__name__, to)

        else: self._cannot(self.__class__.__name__, to)

# polarLUV is HCL, make copy
HCL = polarLUV


# -------------------------------------------------------------------
# CIELUV color object
# -------------------------------------------------------------------
class CIELUV(colorobject):
    """Create CIELUV Color Object

    Creates a color object in the CIELUV color space.
    Can be converted to: :py:class:`CIEXYZ`, :py:class:`CIELUV`,
    :py:class:`CIELAB`, :py:class:`RGB`, :py:class:`sRGB`,
    :py:class:`polarLAB`, and :py:class:`hexcols`.
    Not allowed (ambiguous) are transformations to :py:class:`HSV` and :py:class:`HLS`.

    Args:
        L (int, float, list, numpy.array):
            Numeric value(s) for L dimension.
        U (int, float, list, numpy.array):
            Numeric value(s) for U dimension.
        V (int, float, list, numpy.array):
            Numeric value(s) for L dimension.
        alpha (None, float, list, numpy.array): Numeric value(s) for the alpha
            channel (`[0., 1.]`) where `0.` equals full transparency, `1.` full
            opacity. If `None` (default) no transparency is added.

    Example:

        >>> from colorspace.colorlib import CIELUV
        >>> # Constructing color object with one single color via float
        >>> CIELUV(0, 10, 10)
        >>> #: Constructing object via lists
        >>> CIELUV([10, 30], [20, 80], [100, 40])
        >>> #: Constructing object via numpy arrays
        >>> from numpy import asarray
        >>> CIELUV(asarray([10, 30]), asarray([20, 80]), asarray([100, 40]))

    """
    def __init__(self, L, U, V, alpha = None):

        # checking inputs, save inputs on object
        self._data_ = {} # Dict to store the colors/color dimensions
        tmp = self._colorobject_check_input_arrays_(L = L, U = U, V = V, alpha = alpha)
        for key,val in tmp.items(): self._data_[key] = val
        # White spot definition (the default)
        self.set_whitepoint(X = 95.047, Y = 100.000, Z = 108.883)


    def to(self, to, fixup = True):
        """Transform Color Space

        Allows to transform the current object into a different color space,
        if possible.

        Args:
            to (str): Name of the color space into which the colors should be
                converted (e.g., `CIEXYZ`, `HCL`, `hex`, `RGB`, ...)
            fixup (bool): Whether or not colors outside the defined rgb color space
                should be corrected if necessary, defaults to True.

        Returns:
            No return, converts the object into a new color space and modifies
            the underlying object. After calling this method the object will
            be of a different class.
        """
        self._check_if_allowed_(to)
        from . import colorlib
        clib = colorlib()

        # Nothing to do (converted to itself)
        if to == self.__class__.__name__:
            return
        # Transformation from CIELUV -> CIEXYZ
        elif to == "CIEXYZ":
            [X, Y, Z] = clib.LUV_to_XYZ(self.get("L"), self.get("U"), self.get("V"),
                                        self.WHITEX, self.WHITEY, self.WHITEZ)
            self._data_ = {"X" : X, "Y" : Y, "Z" : Z, "alpha" : self.get("alpha")}
            self.__class__ = CIEXYZ

        # Transformation from CIELUV -> polarLUV (HCL)
        elif to in ["HCL","polarLUV"]:
            [L, C, H] = clib.LUV_to_polarLUV(self.get("L"), self.get("U"), self.get("V"))
            self._data_ = {"L" : L, "C" : C, "H" : H, "alpha" : self.get("alpha")}
            self.__class__ = polarLUV

        # The rest are transformations along a path
        elif to == "CIELAB":
            via = ["CIEXYZ", to]
            self._transform_via_path_(via, fixup = fixup)

        elif to == "RGB":
            via = ["CIEXYZ", to]
            self._transform_via_path_(via, fixup = fixup)

        elif to == "sRGB":
            via = ["CIEXYZ", "RGB", to]
            self._transform_via_path_(via, fixup = fixup)

        elif to == "polarLAB":
            via = ["CIEXYZ", "CIELAB", to]
            self._transform_via_path_(via, fixup = fixup)

        elif to == "hex":
            via = ["CIEXYZ", "RGB", "sRGB", to]
            self._transform_via_path_(via, fixup = fixup)

        elif to in ["HLS", "HSV"]:
            self._ambiguous(self.__class__.__name__, to)

        else: self._cannot(self.__class__.__name__, to)

# -------------------------------------------------------------------
# CIEXYZ color object
# -------------------------------------------------------------------
class CIEXYZ(colorobject):
    """Create CIEXYZ Color Object

    Creates a color object in the CIEXYZ color space.
    Can be converted to: :py:class:`CIEXYZ`, :py:class:`CIELUV`,
    :py:class:`CIELAB`, :py:class:`RGB`, :py:class:`sRGB`,
    :py:class:`polarLAB`, and :py:class:`hexcols`.
    Not allowed (ambiguous) are transformations to :py:class:`HSV` and :py:class:`HLS`.

    Args:
        X (int, float, list, numpy.array):
            Numeric value(s) for X dimension.
        Y (int, float, list, numpy.array):
            Numeric value(s) for Y dimension.
        Z (int, float, list, numpy.array):
            Numeric value(s) for Z dimension.
        alpha (None, float, list, numpy.array): Numeric value(s) for the alpha
            channel (`[0., 1.]`) where `0.` equals full transparency, `1.` full
            opacity. If `None` (default) no transparency is added.

    Example:

        >>> from colorspace.colorlib import CIEXYZ
        >>> # Constructing color object with one single color via float
        >>> CIEXYZ(80, 30, 10)
        >>> #: Constructing object via lists
        >>> CIEXYZ([10, 0], [20, 80], [40, 40])
        >>> #: Constructing object via numpy arrays
        >>> from numpy import asarray
        >>> CIEXYZ(asarray([10, 0]), asarray([20, 80]), asarray([40, 40]))

    """
    def __init__(self, X, Y, Z, alpha = None):

        # checking inputs, save inputs on object
        self._data_ = {} # Dict to store the colors/color dimensions
        tmp = self._colorobject_check_input_arrays_(X = X, Y = Y, Z = Z, alpha = alpha)
        for key,val in tmp.items(): self._data_[key] = val
        # White spot definition (the default)
        self.set_whitepoint(X = 95.047, Y = 100.000, Z = 108.883)


    def to(self, to, fixup = True):
        """Transform Color Space

        Allows to transform the current object into a different color space,
        if possible.

        Args:
            to (str): Name of the color space into which the colors should be
                converted (e.g., `CIEXYZ`, `HCL`, `hex`, `RGB`, ...)
            fixup (bool): Whether or not colors outside the defined rgb color space
                should be corrected if necessary, defaults to True.

        Returns:
            No return, converts the object into a new color space and modifies
            the underlying object. After calling this method the object will
            be of a different class.
        """
        self._check_if_allowed_(to)
        from . import colorlib
        clib = colorlib()

        # Nothing to do (converted to itself)
        if to == self.__class__.__name__:
            return

        # Transformation from CIEXYZ -> CIELUV
        elif to == "CIELUV":
            [L, U, V] = clib.XYZ_to_LUV(self.get("X"), self.get("Y"), self.get("Z"),
                                        self.WHITEX, self.WHITEY, self.WHITEZ) 
            self._data_ = {"L" : L, "U" : U, "V" : V, "alpha" : self.get("alpha")}
            self.__class__ = CIELUV

        # Transformation from CIEXYZ -> CIELAB
        elif to == "CIELAB":
            [L, A, B] = clib.XYZ_to_LAB(self.get("X"), self.get("Y"), self.get("Z"),
                                        self.WHITEX, self.WHITEY, self.WHITEZ) 
            self._data_ = {"L" : L, "A" : A, "B" : B, "alpha" : self.get("alpha")}
            self.__class__ = CIELAB

        # Transformation from CIEXYZ -> RGB
        elif to == "RGB":
            [R, G, B] = clib.XYZ_to_RGB(self.get("X"), self.get("Y"), self.get("Z"),
                                        self.WHITEX, self.WHITEY, self.WHITEZ) 
            self._data_ = {"R" : R, "G" : G, "B" : B, "alpha" : self.get("alpha")}
            self.__class__ = RGB

        # The rest are transformations along a path
        elif to == "polarLAB":
            via = ["CIELAB", to]
            self._transform_via_path_(via, fixup = fixup)

        elif to in ["HCL", "polarLUV"]:
            via = ["CIELUV", to]
            self._transform_via_path_(via, fixup = fixup)

        elif to == "sRGB":
            via = ["RGB", to]
            self._transform_via_path_(via, fixup = fixup)

        elif to == "hex":
            via = ["RGB", "sRGB", to]
            self._transform_via_path_(via, fixup = fixup)

        elif to in ["HLS", "HSV"]:
            self._ambiguous(self.__class__.__name__, to)

        else: self._cannot(self.__class__.__name__, to)


class RGB(colorobject):
    """Create RGB Color Object

    Allows conversions to: :py:class:`CIELAB`, :py:class:`CIELUV`,
    :py:class:`CIEXYZ`, :py:class:`HLS`, :py:class:`HSV`, :py:class:`hexcols`.
    :py:class:`polarLAB`, :py:class:`polarLUV` and :py:class:`sRGB`.

    Args:
        R (int, float, list, numpy.array):
            Numeric value(s) for red intensity (`[0., 1.]`).
        G (int, float, list, numpy.array):
            Numeric value(s) for green intensity (`[0., 1.]`).
        B (int, float, list, numpy.array):
            Numeric value(s) for blue intensity (`[0., 1.]`).
        alpha (None, float, list, numpy.array): Numeric value(s) for the alpha
            channel (`[0., 1.]`) where `0.` equals full transparency, `1.` full
            opacity. If `None` (default) no transparency is added.

    Example:

        >>> from colorspace.colorlib import RGB
        >>> # Constructing color object with one single color via float
        >>> RGB(1., 0.3, 0.5)
        >>> #: Constructing object via lists
        >>> RGB([1., 0.8], [0.5, 0.5], [0.0, 0.2])
        >>> #: Constructing object via numpy arrays
        >>> from numpy import asarray
        >>> RGB(asarray([1., 0.8]), asarray([0.5, 0.5]), asarray([0.0, 0.2]))

    """

    def __init__(self, R, G, B, alpha = None):

        # checking inputs, save inputs on object
        self._data_ = {} # Dict to store the colors/color dimensions

        tmp = self._colorobject_check_input_arrays_(R = R, G = G, B = B, alpha = alpha)
        for key,val in tmp.items(): self._data_[key] = val
        # White spot definition (the default)
        self.set_whitepoint(X = 95.047, Y = 100.000, Z = 108.883)


    def to(self, to, fixup = True):
        """Transform Color Space

        Allows to transform the current object into a different color space,
        if possible.

        Args:
            to (str): Name of the color space into which the colors should be
                converted (e.g., `CIEXYZ`, `HCL`, `hex`, `RGB`, ...)
            fixup (bool): Whether or not colors outside the defined rgb color space
                should be corrected if necessary, defaults to True.

        Returns:
            No return, converts the object into a new color space and modifies
            the underlying object. After calling this method the object will
            be of a different class.
        """
        self._check_if_allowed_(to)
        from . import colorlib
        clib = colorlib()

        # Nothing to do (converted to itself)
        if to == self.__class__.__name__:
            return

        # Transform from RGB -> sRGB
        elif to == "sRGB":
            [R, G, B] = clib.RGB_to_sRGB(self.get("R"), self.get("G"), self.get("B"),
                                           self.GAMMA)
            self._data_ = {"R" : R, "G" : G, "B" : B, "alpha" : self.get("alpha")}
            self.__class__ = sRGB

        # Transform from RGB -> CIEXYZ
        elif to == "CIEXYZ":
            [X, Y, Z] = clib.RGB_to_XYZ(self.get("R"), self.get("G"), self.get("B"),
                                        self.WHITEX, self.WHITEY, self.WHITEZ)
            self._data_ = {"X" : X, "Y" : Y, "Z" : Z, "alpha" : self.get("alpha")}
            self.__class__ = CIEXYZ

        # The rest are transformations along a path
        elif to in ["HLS", "HSV", "hex"]:
            via = ["sRGB", to]
            self._transform_via_path_(via, fixup = fixup)

        elif to in ["CIELUV", "CIELAB"]: 
            via = ["CIEXYZ", to]
            self._transform_via_path_(via, fixup = fixup)

        elif to in ["HCL","polarLUV"]:
            via = ["CIEXYZ", "CIELUV", to]
            self._transform_via_path_(via, fixup = fixup)

        elif to == "polarLAB":
            via = ["CIEXYZ", "CIELAB", to]
            self._transform_via_path_(via, fixup = fixup)

        elif to in ["HLS", "HSV", "hex"]:
            via = ["sRGB", to]
            self._transform_via_path_(via, fixup = fixup)

        else: self._cannot(self.__class__.__name__, to)


class sRGB(colorobject):
    """Create Standard RGB (sRGB) Color Object

    Allows conversions to: :py:class:`CIELAB`, :py:class:`CIELUV`,
    :py:class:`CIEXYZ`, :py:class:`HLS`, :py:class:`HSV`, :py:class:`RGB`,
    :py:class:`hexcols`. :py:class:`polarLAB` and :py:class:`polarLUV`.

    Args:
        R (int, float, list, numpy.array):
            Numeric value(s) for red intensity (`[0., 1.]`).
        G (int, float, list, numpy.array):
            Numeric value(s) for green intensity (`[0., 1.]`).
        B (int, float, list, numpy.array):
            Numeric value(s) for blue intensity (`[0., 1.]`).
        alpha (None, float, list, numpy.array): Numeric value(s) for the alpha
            channel (`[0., 1.]`) where `0.` equals full transparency, `1.` full
            opacity. If `None` (default) no transparency is added.
        gamma (None, float): If `None` (default) the default gamma value is used.
            Can be specified to overwrite the default.

    Example:

        >>> from colorspace.colorlib import sRGB
        >>> # Constructing color object with one single color via float
        >>> sRGB(1., 0.3, 0.5)
        >>> #: Constructing object via lists
        >>> sRGB([1., 0.8], [0.5, 0.5], [0.0, 0.2])
        >>> #: Constructing object via numpy arrays
        >>> from numpy import asarray
        >>> sRGB(asarray([1., 0.8]), asarray([0.5, 0.5]), asarray([0.0, 0.2]))

    """

    def __init__(self, R, G, B, alpha = None, gamma = None):

        # checking inputs, save inputs on object
        self._data_ = {} # Dict to store the colors/color dimensions
        tmp = self._colorobject_check_input_arrays_(R = R, G = G, B = B, alpha = alpha)
        for key,val in tmp.items(): self._data_[key] = val

        # White spot definition (the default)
        self.set_whitepoint(X = 95.047, Y = 100.000, Z = 108.883)

        if isinstance(gamma, float): self.GAMMA = gamma


    def to(self, to, fixup = True):
        """Transform Color Space

        Allows to transform the current object into a different color space,
        if possible.

        Args:
            to (str): Name of the color space into which the colors should be
                converted (e.g., `CIEXYZ`, `HCL`, `hex`, `RGB`, ...)
            fixup (bool): Whether or not colors outside the defined rgb color space
                should be corrected if necessary, defaults to True.

        Returns:
            No return, converts the object into a new color space and modifies
            the underlying object. After calling this method the object will
            be of a different class.
        """
        self._check_if_allowed_(to)
        from . import colorlib
        clib = colorlib()

        # Nothing to do (converted to itself)
        if to == self.__class__.__name__:
            return

        # Transformation sRGB -> RGB
        elif to == "RGB":
            [R, G, B] = clib.sRGB_to_RGB(self.get("R"), self.get("G"), self.get("B"),
                                         gamma = self.GAMMA)
            self._data_ = {"R" : R, "G" : G, "B" : B, "alpha" : self.get("alpha")}
            self.__class__ = RGB

        # Transformation sRGB -> hex
        elif to == "hex":
            hex_ = clib.sRGB_to_hex(self.get("R"), self.get("G"), self.get("B"), fixup)
            self._data_ = {"hex_" : hex_, "alpha" : self.get("alpha")}
            self.__class__ = hexcols

        # Transform from RGB -> HLS
        elif to == "HLS":
            [H, L, S] = clib.sRGB_to_HLS(self.get("R"), self.get("G"), self.get("B"))
            self._data_ = {"H" : H, "L" : L, "S" : S, "alpha" : self.get("alpha")}
            self.__class__ = HLS

        # Transform from RGB -> HSV
        elif to == "HSV":
            [H, S, V] = clib.sRGB_to_HSV(self.get("R"), self.get("G"), self.get("B"))
            self._data_ = {"H" : H, "S" : S, "V" : V, "alpha" : self.get("alpha")}
            self.__class__ = HSV

        # The rest are transformations along a path
        elif to in ["CIEXYZ"]:
            via = ["RGB", to]
            self._transform_via_path_(via, fixup = fixup)

        elif to in ["CIELUV", "CIELAB"]:
            via = ["RGB", "CIEXYZ", to]
            self._transform_via_path_(via, fixup = fixup)

        elif to in ["HCL","polarLUV"]:
            via = ["RGB", "CIEXYZ", "CIELUV", to]
            self._transform_via_path_(via, fixup = fixup)

        elif to == "polarLAB":
            via = ["RGB", "CIEXYZ", "CIELAB", to] 
            self._transform_via_path_(via, fixup = fixup)

        else: self._cannot(self.__class__.__name__, to)


class CIELAB(colorobject):
    """Create CIELAB Color Object

    Creates a color object in the CIELAB color space.
    Can be converted to: :py:class:`CIEXYZ`, :py:class:`CIELUV`,
    :py:class:`CIELAB`, :py:class:`RGB`, :py:class:`sRGB`,
    :py:class:`polarLAB`, and :py:class:`hexcols`.
    Not allowed (ambiguous) are transformations to :py:class:`HSV` and :py:class:`HLS`.

    Args:
        L (int, float, list, numpy.array):
            Numeric value(s) for L dimension.
        A (int, float, list, numpy.array):
            Numeric value(s) for A dimension.
        B (int, float, list, numpy.array):
            Numeric value(s) for B dimension.
        alpha (None, float, list, numpy.array): Numeric value(s) for the alpha
            channel (`[0., 1.]`) where `0.` equals full transparency, `1.` full
            opacity. If `None` (default) no transparency is added.

    Example:

        >>> from colorspace.colorlib import CIELAB
        >>> # Constructing color object with one single color via float
        >>> CIELAB(-30, 10, 10)
        >>> #: Constructing object via lists
        >>> CIELAB([-30, 30], [20, 80], [40, 40])
        >>> #: Constructing object via numpy arrays
        >>> from numpy import asarray
        >>> CIELAB(asarray([-30, 30]), asarray([20, 80]), asarray([40, 40]))

    """

    def __init__(self, L, A, B, alpha = None):

        # checking inputs, save inputs on object
        self._data_ = {} # Dict to store the colors/color dimensions
        tmp = self._colorobject_check_input_arrays_(L = L, A = A, B = B, alpha = alpha)
        for key,val in tmp.items(): self._data_[key] = val
        # White spot definition (the default)
        self.set_whitepoint(X = 95.047, Y = 100.000, Z = 108.883)


    def to(self, to, fixup = True):
        """Transform Color Space

        Allows to transform the current object into a different color space,
        if possible.

        Args:
            to (str): Name of the color space into which the colors should be
                converted (e.g., `CIEXYZ`, `HCL`, `hex`, `RGB`, ...)
            fixup (bool): Whether or not colors outside the defined rgb color space
                should be corrected if necessary, defaults to True.

        Returns:
            No return, converts the object into a new color space and modifies
            the underlying object. After calling this method the object will
            be of a different class.
        """
        self._check_if_allowed_(to)
        from . import colorlib
        clib = colorlib()

        # Nothing to do (converted to itself)
        if to == self.__class__.__name__:
            return

        # Transformations CIELAB -> CIEXYZ
        elif to == "CIEXYZ":
            [X, Y, Z] = clib.LAB_to_XYZ(self.get("L"), self.get("A"), self.get("B"),
                                        self.WHITEX, self.WHITEY, self.WHITEZ)
            self._data_ = {"X" : X, "Y" : Y, "Z" : Z, "alpha" : self.get("alpha")}
            self.__class__ = CIEXYZ

        # Transformation CIELAB -> polarLAB
        elif to == "polarLAB":
            [L, A, B] = clib.LAB_to_polarLAB(self.get("L"), self.get("A"), self.get("B"))
            self._data_ = {"L" : L, "A" : A, "B" : B, "alpha" : self.get("alpha")}
            self.__class__ = polarLAB

        # The rest are transformations along a path
        elif to == "CIELUV":
            via = ["CIEXYZ", to]
            self._transform_via_path_(via, fixup = fixup)

        elif to in ["HCL","polarLUV"]:
            via = ["CIEXYZ", "CIELUV", to]
            self._transform_via_path_(via, fixup = fixup)

        elif to == "RGB":
            via = ["CIEXYZ", to]
            self._transform_via_path_(via, fixup = fixup)

        elif to == "sRGB":
            via = ["CIEXYZ", "RGB", to]
            self._transform_via_path_(via, fixup = fixup)

        elif to == "hex":
            via = ["CIEXYZ", "RGB", "sRGB", to]
            self._transform_via_path_(via, fixup = fixup)

        elif to in ["HLS", "HSV"]:
            self._ambiguous(self.__class__.__name__, to)

        else: self._cannot(self.__class__.__name__, to)


class polarLAB(colorobject):
    """Create Polar LAB Color Object

    Creates a color object in the polar representation of the
    :py:class:`CIELAB` color space.
    Can be converted to: :py:class:`CIEXYZ`, :py:class:`CIELUV`,
    :py:class:`CIELAB`, :py:class:`RGB`, :py:class:`sRGB`,
    :py:class:`polarLAB`, and :py:class:`hexcols`.
    Not allowed (ambiguous) are transformations to :py:class:`HSV` and :py:class:`HLS`.

    Args:
        L (int, float, list, numpy.array):
            Numeric value(s) for L dimension.
        A (int, float, list, numpy.array):
            Numeric value(s) for A dimension.
        B (int, float, list, numpy.array):
            Numeric value(s) for B dimension.
        alpha (None, float, list, numpy.array): Numeric value(s) for the alpha
            channel (`[0., 1.]`) where `0.` equals full transparency, `1.` full
            opacity. If `None` (default) no transparency is added.

    TODO: Add examples.
    """

    def __init__(self, L, A, B, alpha = None):

        # checking inputs, save inputs on object
        self._data_ = {} # Dict to store the colors/color dimensions
        tmp = self._colorobject_check_input_arrays_(L = L, A = A, B = B, alpha = alpha)
        for key,val in tmp.items(): self._data_[key] = val
        # White spot definition (the default)
        self.set_whitepoint(X = 95.047, Y = 100.000, Z = 108.883)


    def to(self, to, fixup = True):
        """Transform Color Space

        Allows to transform the current object into a different color space,
        if possible.

        Args:
            to (str): Name of the color space into which the colors should be
                converted (e.g., `CIEXYZ`, `HCL`, `hex`, `RGB`, ...)
            fixup (bool): Whether or not colors outside the defined rgb color space
                should be corrected if necessary, defaults to True.

        Returns:
            No return, converts the object into a new color space and modifies
            the underlying object. After calling this method the object will
            be of a different class.
        """
        self._check_if_allowed_(to)
        from . import colorlib
        clib = colorlib()

        # Nothing to do (converted to itself)
        if to == self.__class__.__name__:
            return

        # The only transformation we need is from polarLAB -> LAB
        elif to == "CIELAB":
            [L, A, B] = clib.polarLAB_to_LAB(self.get("L"), self.get("A"), self.get("B"))
            self._data_ = {"L" : L, "A" : A, "B" : B, "alpha" : self.get("alpha")}
            self.__class__ = CIELAB

        # The rest are transformationas along a path
        elif to == "CIEXYZ":
            via = ["CIELAB", to]
            self._transform_via_path_(via, fixup = fixup)

        elif to == "CIELUV":
            via = ["CIELAB", "CIEXYZ", to]
            self._transform_via_path_(via, fixup = fixup)

        elif to in ["HCL", "polarLUV"]:
            via = ["CIELAB", "CIEXYZ", "CIELUV", to]
            self._transform_via_path_(via, fixup = fixup)

        elif to == "RGB":
            via = ["CIELAB", "CIEXYZ", to]
            self._transform_via_path_(via, fixup = fixup)

        elif to == "sRGB":
            via = ["CIELAB", "CIEXYZ", "RGB", to]
            self._transform_via_path_(via, fixup = fixup)

        elif to == "hex":
            via = ["CIELAB", "CIEXYZ", "RGB", "sRGB", to]
            self._transform_via_path_(via, fixup = fixup)

        elif to in ["HLS", "HSV"]:
            self._ambiguous(self.__class__.__name__, to)

        else: self._cannot(self.__class__.__name__, to)


class HSV(colorobject):
    """Create HSV Color Object

    Creates a color object in the Hue-Saturation-Value (HSV) color space.
    Can be converted to: :py:class:`RGB`, :py:class:`sRGB`, :py:class:`HLS`,
    and :py:class:`hexcols`.
    Not allowed (ambiguous) are transformations to :py:class:`CIEXYZ`,
    :py:class:`CIELUV`, :py:class:`CIELAB`, :py:class:`polarLUV`, and
    :py:class:`polarLAB`.

    Args:
        H (int, float, list, numpy.array):
            Numeric value(s) for Hue dimension.
        S (int, float, list, numpy.array):
            Numeric value(s) for Saturation dimension.
        V (int, float, list, numpy.array):
            Numeric value(s) for Value dimension.
        alpha (None, float, list, numpy.array): Numeric value(s) for the alpha
            channel (`[0., 1.]`) where `0.` equals full transparency, `1.` full
            opacity. If `None` (default) no transparency is added.

    Examples:

        >>> #: Constructing object via numpy arrays
        >>> from colorspace.colorlib import HSV
        >>> # Constructing color object with one single color via float
        >>> HSV(150, 150, 10)
        >>> #: Constructing object via lists
        >>> HSV([150, 150, 10], [1.5, 0, 1.5], [0.1, 0.7, 0.1])
        >>> #: Constructing object via numpy arrays
        >>> from numpy import asarray
        >>> cols = HSV(asarray([150, 150, 150]),
        >>>            asarray([1.5, 0, 1.5]),
        >>>            asarray([0.1, 0.7, 0.1]))
        >>> cols
        >>> #: Converting to RGB
        >>> cols.to("RGB")
        >>> cols
    """

    def __init__(self, H, S, V, alpha = None):

        # checking inputs, save inputs on object
        self._data_ = {} # Dict to store the colors/color dimensions
        tmp = self._colorobject_check_input_arrays_(H = H, S = S, V = V, alpha = alpha)
        for key,val in tmp.items(): self._data_[key] = val
        # White spot definition (the default)
        self.set_whitepoint(X = 95.047, Y = 100.000, Z = 108.883)


    def to(self, to, fixup = True):
        """Transform Color Space

        Allows to transform the current object into a different color space,
        if possible.

        Args:
            to (str): Name of the color space into which the colors should be
                converted (e.g., `CIEXYZ`, `HCL`, `hex`, `RGB`, ...)
            fixup (bool): Whether or not colors outside the defined rgb color space
                should be corrected if necessary, defaults to True.

        Returns:
            No return, converts the object into a new color space and modifies
            the underlying object. After calling this method the object will
            be of a different class.
        """
        self._check_if_allowed_(to)
        from . import colorlib
        clib = colorlib()

        # Nothing to do (converted to itself)
        if to == self.__class__.__name__:
            return

        # The only transformation we need is back to RGB
        elif to == "sRGB":
            [R, G, B] = clib.HSV_to_sRGB(self.get("H"), self.get("S"), self.get("V"))
            self._data_ = {"R" : R, "G" : G, "B" : B, "alpha" : self.get("alpha")}
            self.__class__ = sRGB

        # The rest are transformations along a path
        elif to == "RGB":
            via = ["sRGB", to]
            self._transform_via_path_(via, fixup = fixup)

        elif to == "hex":
            via = ["sRGB", to]
            self._transform_via_path_(via, fixup = fixup)

        elif to == "HLS":
            via = ["sRGB", to]
            self._transform_via_path_(via, fixup = fixup)

        elif to in ["CIEXYZ", "CIELUV", "CIELAB", "polarLUV", "HCL", "polarLAB"]:
            self._ambiguous(self.__class__.__name__, to)

        else: self._cannot(self.__class__.__name__, to)


class HLS(colorobject):
    """Create HLS Color Object

    Creates a color object in the Hue-Lightness-Saturation (HLS) color space.
    Can be converted to: :py:class:`RGB`, :py:class:`sRGB`, :py:class:`HSV`,
    and :py:class:`hexcols`.
    Not allowed (ambiguous) are transformations to :py:class:`CIEXYZ`,
    :py:class:`CIELUV`, :py:class:`CIELAB`, :py:class:`polarLUV`, and
    :py:class:`polarLAB`.

    Args:
        H (int, float, list, numpy.array):
            Numeric value(s) for Hue dimension.
        L (int, float, list, numpy.array):
            Numeric value(s) for Lightness dimension.
        S (int, float, list, numpy.array):
            Numeric value(s) for Saturation dimension.
        alpha (None, float, list, numpy.array): Numeric value(s) for the alpha
            channel (`[0., 1.]`) where `0.` equals full transparency, `1.` full
            opacity. If `None` (default) no transparency is added.

    Examples:

        >>> from colorspace.colorlib import HLS
        >>> # Constructing color object with one single color via float
        >>> HLS(150, 0.1, 3)
        >>> #: Constructing object via lists
        >>> HLS([150, 0, 10], [0.1, 0.7, 0.1], [3, 0, 3])
        >>> #: Constructing object via numpy arrays
        >>> from numpy import asarray
        >>> cols = HLS(asarray([150, 0, 10]),
        >>>            asarray([0.1, 0.7, 0.1]),
        >>>            asarray([3, 0, 3]))
        >>> cols
        >>> #: Converting to RGB
        >>> cols.to("RGB")
        >>> cols
    """

    def __init__(self, H, L, S, alpha = None):

        # checking inputs, save inputs on object
        self._data_ = {} # Dict to store the colors/color dimensions
        tmp = self._colorobject_check_input_arrays_(H = H, L = L, S = S, alpha = None)
        for key,val in tmp.items(): self._data_[key] = val
        # White spot definition (the default)
        self.set_whitepoint(X = 95.047, Y = 100.000, Z = 108.883)


    def to(self, to, fixup = True):
        """Transform Color Space

        Allows to transform the current object into a different color space,
        if possible.

        Args:
            to (str): Name of the color space into which the colors should be
                converted (e.g., `CIEXYZ`, `HCL`, `hex`, `RGB`, ...)
            fixup (bool): Whether or not colors outside the defined rgb color space
                should be corrected if necessary, defaults to True.

        Returns:
            No return, converts the object into a new color space and modifies
            the underlying object. After calling this method the object will
            be of a different class.
        """
        self._check_if_allowed_(to)
        from . import colorlib
        clib = colorlib()

        # Nothing to do (converted to itself)
        if to == self.__class__.__name__:
            return

        # The only transformation we need is back to RGB
        elif to == "sRGB":
            [R, G, B] = clib.HLS_to_sRGB(self.get("H"), self.get("L"), self.get("S"))
            self._data_ = {"R" : R, "G" : G, "B" : B, "alpha" : self.get("alpha")}
            self.__class__ = sRGB

        # The rest are transformations along a path
        elif to == "RGB":
            via = ["sRGB", to]
            self._transform_via_path_(via, fixup = fixup)

        elif to == "hex":
            # TODO(R): Fails!!!!! Reason: walks trough RGB > sRGB with GAMMA.
            via = ["sRGB", to]
            self._transform_via_path_(via, fixup = fixup)

        elif to == "HSV":
            via = ["sRGB", to]
            self._transform_via_path_(via, fixup = fixup)

        elif to in ["CIEXYZ", "CIELUV", "CIELAB", "polarLUV", "HCL", "polarLAB"]:
            self._ambiguous(self.__class__.__name__, to)

        else: self._cannot(self.__class__.__name__, to)


class hexcols(colorobject):
    """Create Hex Color Object

    Creates a color object using hex colors (string).
    Can be converted to all other color spaces: :py:class:`CIELAB`,
    :py:class:`CIELUV`, :py:class:`CIEXYZ`, :py:class:`HLS`, :py:class:`HSV`,
    :py:class:`RGB`, :py:class:`polarLAB`, :py:class:`polarLUV`, and
    :py:class:`sRGB`.

    Args:
        hex_ (str, list of str, numpy.ndarray of type str):
            Hex colors. Only six and eight digit hex colors are allowed (e.g.,
            `#000000` or `#00000050` if with alpha channel). If invalid hex
            colors are provided the object will raise an exception. Invalid hex
            colors will be handled as `numpy.nan`.

    Examples:

        >>> from colorspace.colorlib import hexcols
        >>> # Creating hex color object from string
        >>> hexcols("#cecece")
        >>> #: Creating hex color object from list of strings
        >>> hexcols(["#ff0000", "#00ff00"])
        >>> #: Creating hex colors via numpy array
        >>> from numpy import asarray
        >>> cols = hexcols(asarray(["#ff000030", "#00ff0030"]))
        >>> cols
        >>> #: Convert hex colors to another color space (CIEXYZ)
        >>> cols.to("CIEXYZ")
        >>> cols
    """

    def __init__(self, hex_):

        from colorspace import check_hex_colors
        import numpy as np

        self._data_ = {} # Dict to store the colors/color dimensions

        # This is the one step where we extract transparency from
        # hex colors once we enter the world of colorobjects.
        def get_alpha(hex_):
            return [None if len(x) == 0 else int(x, 16) / 255 for x in [x[7:9] for x in hex_]]

        # Forwarding input 'hex_' to check_hex_colors which will throw
        # an error if we do not understand this input type.
        self._data_["hex_"]  = np.asarray(check_hex_colors(hex_), dtype = "<U9")
        tmp = np.asarray(get_alpha(hex_), dtype = "float")
        if not np.all(np.isnan(tmp)): self._data_["alpha"] = tmp

        # White spot definition (the default)
        self.set_whitepoint(X = 95.047, Y = 100.000, Z = 108.883)


    def to(self, to, fixup = True):
        """Transform Color Space

        Allows to transform the current object into a different color space,
        if possible.

        Args:
            to (str): Name of the color space into which the colors should be
                converted (e.g., `CIEXYZ`, `HCL`, `hex`, `RGB`, ...)
            fixup (bool): Whether or not colors outside the defined rgb color space
                should be corrected if necessary, defaults to True.

        Returns:
            No return, converts the object into a new color space and modifies
            the underlying object. After calling this method the object will
            be of a different class.
        """
        self._check_if_allowed_(to)
        from . import colorlib
        clib = colorlib()

        # Nothing to do (converted to itself)
        if to in ["hex", self.__class__.__name__]:
            return

        # The only transformation we need is from hexcols -> sRGB
        elif to == "sRGB":
            [R, G, B] = clib.hex_to_sRGB([x[0:7] for x in self.get("hex_")])
            alpha = self.get("alpha")
            self._data_ = {"R": R, "G": G, "B": B}
            if alpha is not None: self._data_["alpha"] = alpha
            self.__class__ = sRGB

        # The rest are transformations along a path
        elif to == "RGB":
            via = ["sRGB", to]
            self._transform_via_path_(via, fixup = fixup)

        elif to in ["HLS", "HSV"]:
            via = ["sRGB", to]
            self._transform_via_path_(via, fixup = fixup)

        elif to in ["CIEXYZ"]:
            via = ["sRGB", "RGB", to]
            self._transform_via_path_(via, fixup = fixup)

        elif to in ["CIELUV", "CIELAB"]:
            via = ["sRGB", "RGB", "CIEXYZ", to]
            self._transform_via_path_(via, fixup = fixup)

        elif to in ["HCL", "polarLUV"]:
            via = ["sRGB", "RGB", "CIEXYZ", "CIELUV", to]
            self._transform_via_path_(via, fixup = fixup)

        elif to in "polarLAB":
            via = ["sRGB", "RGB", "CIEXYZ", "CIELAB", to]
            self._transform_via_path_(via, fixup = fixup)

        else: self._cannot(self.__class__.__name__, to)


def compare_colors(a, b, exact = False, _all = True, atol = None):
    """Compare Sets of Colors

    Compares two sets of colors based on two color objects. The objects
    provided on argument `a` and `b` must inherit from `colorobject`.
    This can be any of the following classes: :py:class:`CIELAB`,
    :py:class:`CIELUV`, :py:class:`CIEXYZ`, :py:class:`HLS`, :py:class:`HSV`,
    :py:class:`RGB`, :py:class:`hexcols`, :py:class:`polarLAB`,
    :py:class:`polarLUV`, or :py:class:`sRGB`.

    Args:
        a (colorobject): Object which inherits from `colorobject`.
        b (colorobject): Object which inherits from `colorobject`.
        exact (bool): Default `False`, check for colors being nearly equal
            (see `atol`). If set to `True` the coordinates must be identical.
            Note: in case `a` and `b` are hex colors
            (colorspace.colorlib.hexcols) strings will always be matched exactly.
        _all (boolean): Default `True`; the function will return `True` if
            all colors are identical/nearly equal. If set to `False` the return
            will be a list of booleans containing `True` and `False` for each
            pair of colors.
        atol (None or float): Absolute tolerance for the distance measure
            between two colors to be considered as nearly equal. Only used if
            `exact = False`, else `atol = 1e-6` is used.  If set to `None`
            the tolerance will automatically be set depending on the type of the
            objects. Defaults to None.


    Returns:
        bool, list: Returns `True` if all colors of `a` are exactly equal or
        nearly equal (see arguments) to the colors in object `b`. If `_all =
        False`, a list of booleans is returned indicating pair-wise comparison
        of all colors in `a` and `b`.

    Example:

        >>> from colorspace.colorlib import *
        >>>
        >>> # Three RGB colors
        >>> a = RGB([0.5, 0.5], [0.1, 0.1], [0.9, 0.9])
        >>> b = RGB([0.5, 0.5], [0.1, 0.1], [0.9, 0.91])
        >>> 
        >>> compare_colors(a, b)
        >>> #:
        >>> compare_colors(a, b, atol = 0.1)
        >>> #:
        >>> compare_colors(a, b, exact = True)
        >>> #:
        >>> compare_colors(a, b, exact = True, _all = False)
        >>>
        >>> #: Same example using two sets of hexcolor objects
        >>> x = hexcols(["#ff00ff", "#003300"])
        >>> y = hexcols(["#ff00ff", "#003301"])
        >>> compare_colors(x, y)
        >>> #:
        >>> compare_colors(x, y, _all = False)
        >>>
        >>> #: Convert HEX to HCL (polarLUV) and back, compare the
        >>> # resulting colors to the original ones; should be identical
        >>> from copy import deepcopy
        >>> z  = hexcols(["#ff00ff", "#003301"])
        >>> zz = deepcopy(z)
        >>> zz.to("HCL")
        >>> print(zz)
        >>> #:
        >>> zz.to("hex")
        >>> print(zz)
        >>> #:
        >>> compare_colors(z, zz)

    Raises:
        TypeError: If `a` or `b` are not objects of a class which inherits from
            `colorspace.colorlib.colorobject`.
        TypeError: If `a` and `b` are not of the same class.
        ValueError: If `a` and `b` are not of the same length, i.e., do not contain
            the same number of colors.
        ValueError: If `exact` or `_all` are not boolean.
        ValueError: If `atol` is neither `None` nor float.
    """

    from numpy import sqrt, isclose

    if not isinstance(a, colorobject):
        raise TypeError("argument `a` must be an object based on colorspace.colorlib.colorobject.")
    if not isinstance(b, colorobject):
        raise TypeError("argument `b` must be an object based on colorspace.colorlib.colorobject.")
    if not type(a) == type(b):
        raise TypeError("Input `a` and `b` not of same class.")
    if not a.length() == b.length():
        raise ValueError("Objects do not contain the same number of colors.")
    if not isinstance(exact, bool):
        raise TypeError("argument `exact` must be boolean.")
    if not isinstance(_all, bool):
        raise TypeError("argument `_all` must be boolean.")
    if not isinstance(atol, float) and not isinstance(atol, type(None)):
        raise TypeError("argument `atol` must be float or None.")

    if exact: atol = 1e-6

    def distance(a, b):
        dist = 0
        for n in list(a._data_.keys()):
            dist += (a.get(n)[0] - b.get(n)[0])**2.0
        return sqrt(dist)

    # Compare hex colors; always on string level
    if isinstance(a, hexcols):
        # Getting coordinates
        res = [a[i].get("hex_")[0].upper() == b[i].get("hex_")[0].upper() for i in range(0, a.length())]
    # Calculate absolute difference between coordinates R/G/B[/alpha].
    # Threading alpha like another coordinates as all coordinates are scaled [0-1].
    elif isinstance(a, RGB) or isinstance(a, sRGB) or \
         isinstance(a, HLS) or isinstance(a, HSV):
        # HEX precision in RGB coordinates is about sqrt((1./255.)**2 * 3) / 2 = 0.003396178
        if not atol: atol = 0.005
        res = [distance(a[i], b[i]) for i in range(0, a.length())]
        res = isclose(res, 0, atol = atol)
    # HCL or polarLUV (both return instance polarLUV)
    # TODO(R): Calculating the Euclidean distance on HCL and (if available) alpha
    #          which itself is in [0, 1]. Should be weighted differently?
    elif isinstance(a, polarLUV) or isinstance(a, CIELUV) or isinstance(a, CIELAB) or \
         isinstance(a, polarLAB) or isinstance(a, CIEXYZ) :

        if not atol: atol = 1
        res = [distance(a[i], b[i]) for i in range(0, a.length())]
        res = isclose(res, 0, atol = atol)


    # If _all is True: check if all elements are True
    if _all:
        from numpy import all
        res = all(res)
    return res





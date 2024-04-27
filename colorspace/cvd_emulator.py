

def cvd_emulator(image = "DEMO", cvd = "desaturate", severity = 1.0,
        output = None, dropalpha = False, **figargs):
    """Check Images for Color Constraints

    Simulate color deficiencies on png, jpg, and jpeg files. Takes an existing
    pixel image and simulates different color vision deficiencies.

    The function displays a matplotlib figure if `output = None`.
    If `output` is set, a new figure will be stored with simulated colors.
    If only one color vision deficiency is defined (e.g., `cvd = "desaturate"`)
    a figure of the same type and size as the input figure is created.
    When multiple `cvd`'s are specified, a multi-panel plot will be created.

    Requires the python modules `matplotlib` and `imageio` to be installed.

    Args:
        image (str): Name of the figure which should be converted
            (png/jpg/jpeg). If `image = "DEMO"` the package demo figure is used.
        cvd (str, list): Color vision deficiency or deficiencies. Allowed types are
            `"deutanope"`, `"protanope"`, `"tritanope"`, `"desaturated"`,
            and `"original"` (unmodified).
        severity (float): How severe the color vision deficiency is
            (`[0.,1.]`).  Also used as the amount of desaturation if `cvd`
            includes `"desaturate"`.
        output (None, string): If `None` an interactive plotting window will
            be opened. A string (file name/path) can be given to write the result
            to disc.
        dropalpha (bool): Drop alpha channel, defaults to `False`.  Only
            useful for png figures having an alpha channel.
        **figargs: forwarded to `matplotlib.pyplot.subplot`.

    Returns:
        matplotlib.figure.Figure, str: If `output = None` the figure
        handler is returned, else the return of the function is identical
        to `output`; the figure which has just been created.

    Example:

        >>> from colorspace.cvd_emulator import cvd_emulator
        >>> cvd_emulator("DEMO", "deutan", 0.5);
        >>> #:
        >>> cvd_emulator("DEMO", "desaturate", 1.0, "output.png");
        >>> #:
        >>> cvd_emulator("DEMO", ["original", "deutan", "protan"],
        >>>              0.5, dropalpha = True);

    Raises:
        ValueError: If `cvd` is empty.
        ValueError: If no valid `cvd` method is provided.
        FileNotFounderror: If the file specified on `image` does not exist.
        ImportError: When python module 'imageio' cannot be imported (not installed).
        IOError: If file `image` cannot be read using `imageio.imread`.
        ImportError: If `matplotlib.pyplot` cannot be imported (`matplotlib` not installed?).
    """

    import os
    import inspect

    # Conver to ..?
    allowed = ["protan", "tritan", "deutan", "desaturate", "original"]
    tmp     = []
    if isinstance(cvd, str): cvd = [cvd]
    if len(cvd) == 0:
        raise ValueError("no valid `cvd` method provided")
    else:
        for c in cvd:
            if c in allowed:
                tmp.append(c)
            else:
                raise ValueError(f"cvd = \"{cvd}\" not allowed. Allowed: {', '.join(allowed)}.")
    cvd = tmp; del tmp

    # If image = "DEMO": use package demo image.
    if image == "DEMO":
        resource_package = os.path.dirname(__file__)
        image = os.path.join(resource_package, "data", "colorful.png")

    # Check if file exists
    if not os.path.isfile(image):
        raise FileNotFoundError(f"file \"{image}\" not found")

    # Wrong input for output
    if not output is None and not isinstance(output, str):
        raise ValueError("output has to be None or a string (file name)")

    # Import imageio
    try:
        import imageio
    except Exception as e:
        raise ImportError(f"requires python module \"imageio\" which is not installed: {e}")

    # Read image data
    try:
        img = imageio.imread(image)
    except Exception as e:
        raise IOError(str(e))

    # Extracting colors (scale from [0,255] to [0.,1.])
    data = {}
    if img.shape[2] == 3:
        [data["R"], data["G"], data["B"]] = \
                [img[:,:,i].flatten() / 255. for i in [0,1,2]]
    elif img.shape[2] == 4:
        [data["R"], data["G"], data["B"], data["alpha"]] = \
                [img[:,:,i].flatten() / 255. for i in [0,1,2,3]]

    # Create sRGB with or without
    from .colorlib import sRGB
    if not "alpha" in data.keys():
        rgba = sRGB(data["R"], data["G"], data["B"])
    else:
        rgba = sRGB(data["R"], data["G"], data["B"], data["alpha"])

    # Drop alpha
    if dropalpha: rgba.dropalpha()

    # Apply color deficiency
    from . import CVD
    try:
        import matplotlib.pyplot as plt
    except Exception as e:
        raise ImportError(f"problems importing `matplotlib.pyplot`: {e}")

    from numpy import ceil
    if len(cvd) <= 3: [nrow, ncol] = [1, len(cvd)]
    else:             [nrow, ncol] = [int(ceil(len(cvd)/2.)), 2]

    # Start plotting
    plt.subplots(nrow, ncol, **figargs)
    for c in range(0, len(cvd)):

        # Start plotting
        if len(cvd) == 1:
            fig = plt.figure(**figargs)
        else:
            fig = plt.subplot(nrow, ncol, c + 1)

        if cvd[c] == "original":
            cols = rgba
        else:
            fun  = getattr(CVD, cvd[c])
            cols = fun(rgba, severity)

        # Convert RGB [0.-1.] to [0,255], uint8
        def fun(x, shape):
            from numpy import fmin, fmax
            x = fmax(0, fmin(255, x*255))
            return x.reshape(shape)

        # Shape of the new figure
        if cols.hasalpha():  shape = [img.shape[0],img.shape[1],4]
        else:                shape = [img.shape[0],img.shape[1],3]

        # Create new image matrix and fill in the data
        from numpy import ndarray, uint8
        imnew = ndarray(shape, dtype = uint8)
        imnew[:,:,0] = fun(cols.get("R"), shape[0:2])
        imnew[:,:,1] = fun(cols.get("G"), shape[0:2])
        imnew[:,:,2] = fun(cols.get("B"), shape[0:2])
        if cols.hasalpha():
            imnew[:,:,3] = fun(cols.get("alpha"), shape[0:2])

        import matplotlib.pyplot as plt
        plt.imshow(imnew)
        plt.axis("off")

    # Adjusting outer margins
    #plt.subplots_adjust(left = 0., right = 1., top = 1., bottom = 0.1)
    plt.tight_layout()

    # Show or save image.
    if output is None:
        plt.show()
        return plt
    else:
        # Write a simple figure:
        if len(cvd) == 1:
            imageio.imwrite(output, imnew)
        # Save matplotlib panel plot
        else:
            plt.savefig(output)

    return output



# Tkinter was renamed to tkinter Py2->Py3,
# make sure the correct module is loaded.
import sys
if sys.version_info.major < 3:
    from Tkinter import *
else:
    from tkinter import *


# -------------------------------------------------------------------
# -------------------------------------------------------------------
# -------------------------------------------------------------------
class Slider(object):
    """Initializes a new Slider object for the graphical user interface
    :py:class:`choose_palette.gui`. A Slider is a combination of a ``Tk.Frame``
    including a ``Tk.Label``, ``Tk.Slider``, and a ``Tk.Entry`` element with
    all necessary interactions.

    Args:
        x (int): X-position on the Tk interface
        y (int): Y-position on the Tk interface
        width (int): Width of the Slider object (``Tk.Frame`` taking up ``Tk.Scale``,
            ``Tk.Label``, and ``Tk.Entry``)
        height (int): height of the Slider object (``Tk.Frame`` taking up ``Tk.Scale``,
            ``Tk.Label``, and ``Tk.Entry``)
        type_ (str): Name of the Slider
        from_ (float): Lower value of the Slider (see :py:func:`isValidInt`, :py:func:`isValidFloat`)
        to (numeric): Upper value of the Slider (see :py:func:`isValidInt`, :py:func:`isValidFloat`)
        resolution (float): Resolution of the slider, the increments when moving the Slider
        kwargs: Unused.
    """

    _Frame     = None # Used to store the Tk.Frame object
    _Scale     = None # Used to store the Tk.Scale object
    _Label     = None # Used to store the Tk.Label object
    _Entry     = None # Used to store the Tk.Entry object
    _Value     = None # Used to store/trac the current value of the Slider
    _name      = None # Name of the slider
    _is_active = True # Bool, used to store the Slider state

    FGACTIVE     = "#b0b0b0"
    BGACTIVE     = "#b0b0b0"
    FGDISABLED   = "#dadada"
    BGDISABLED   = "#efefef"
    DISABLED     = "#b0b0b0"
    BGDEFAULT    = "#d9d9d9"


    def __init__(self, master, name, x, y, width, height, active,
                 type_, from_, to, resolution, **kwargs):

        if type_ == "int":
            self._Value = IntVar(master)
            vcmd = getattr(self, "isValidInt")
        elif type_ == "float":
            self._Value = DoubleVar(master)
            vcmd = getattr(self, "isValidFloat")
        else:
            raise Exception("unknown type_ when initializing {:s}".format(self.__class__.__name__))

        self._name = name

        # Frame around the slider objects
        self._Frame = Frame(master)
        self._Frame.place(x = x, y = y, width = width, height = height)

        # Object handling slider actions/callbacks
        self._Scale = Scale(self._Frame, variable = self._Value, orient = HORIZONTAL,
                showvalue = 0, length = width - 100, width = 15, 
                from_ = from_, to = to, resolution = resolution)
        self._Scale.place(x = 50)

        # Plading the label
        self._Label = Label(self._Frame, text = name.upper())
        self._Label.config(anchor = CENTER)
        self._Label.place(x = 0)

        # Adding text element
        self._Entry = Entry(self._Frame, bd = 0, width = 4)
        self._Entry.insert(INSERT, 0)

        # Register a function which checks if the user input is valid or not.
        vcmd = self._Entry.register(vcmd)
        self._Entry.config(justify = RIGHT, validate = "key",
                           validatecommand = (vcmd, "%P", from_, to))
        self._Entry.place(x = width - 40)

        # Changing the Tk.Value triggers the GUI update
        def fun(event, parent):
            val = event.widget.get()
            # Empty? Use existing value
            if len(val) == 0:
                event.widget.insert(0, self._Value.get())
            # Else change value
            else:
                # Just to double-check: must be a number
                try:
                    val = float(val)
                    self._Value.set(event.widget.get())
                # This exception should never happen!
                except:
                    pass
        self._Entry.bind("<Return>",   lambda event: fun(event, self))
        self._Entry.bind("<FocusOut>", lambda event: fun(event, self))

        # Tracing the _Value
        self._Value.trace(mode = "w", callback = self.OnTrace)

        # Disbale if necessary
        if not active: self.disable()

    def isValidInt(self, x, from_ = -999, to = 999):
        """Helper function to check whether ``x`` is a valid integer
        in the range ``[from_,to]``.

        Args:
            x (int): Value to be validated
            from_ (int): Lower limit of the valid range, defaults to -999.
            to (int): Upper limit of the valid range, defaults to 999.

        Returns:
            bool: Returns ``True`` if ``x`` is a valid float within
            ``[from_, to]`` and ``False`` otherwise.
        """
        # If empty
        if len(x) == 0: return True
        import re
        # If not matching signed integer: return False
        if not re.match("^-?(0|[1-9]|[1-9][0-9]{1,2})?$", x): return False
        # Only a "-": that's Ok
        if re.match("^-$", x): return True
        # Outside range? Return False
        if float(x) < float(from_) or float(x) > float(to):
            return False
        # Else True
        return True

    def isValidFloat(self, x, from_ = -999., to = 999.):
        """Helper function to check whether ``x`` is a valid float
        in the range ``[from_,to]``.

        Args:
            x (float): Value to be validated.
            from_ (float): Lower limit of the valid range, defaults to -999.
            to (float): Upper limit of the valid range, defaults to 999.

        Returns:
            bool: Returns ``True`` if ``x`` is a valid float within
            ``[from_, to]`` and ``False`` otherwise.
        """
        # If empty
        if len(x) == 0: return True
        # If no valid float: return False
        try:
            x     = float(x)
            from_ = float(from_)
            to    = float(to)
        except Exception as e:
            return False
        # If more than one digits:
        import re
        if from_ >= 0:
            if not re.match("[0-9]+(\\.|\\.[0-9])?$", str(x)): return False
        else:
            if not re.match("-?[0-9]+(\\.|\\.[0-9])?$", str(x)): return False
        return True

    def OnTrace(self, *args, **kwargs):
        """Triggered when :py:func:`Slider.trace` is triggered. The method
        is loading the current value and sets the ``Tk.Scale`` and
        ``Tk.Entry`` element to the new value.
        """
        val = self._Value.get()
        self.set(self._Value.get())

    def name(self):
        """name()

        Returns
        -------
        str
            Returns the name of the :py:class:`Slider`.
        """
        return self._name

    def set(self, val):
        # Reading text value and adjust slider
        self._Scale.set(val)
        # Setting Text
        self._Entry.delete(0, END)
        self._Entry.insert(0, val)

    def get(self):
        """Allows to get attributes from the object.

        Returns:
            int, float: Returns the current value of the slider.  The return
            value depends on the slider config (`int` or `float`).
        """
        return self._Value.get()


    def trace(self, mode, *args, **kwargs):
        """Trace method of the :py:class:`Slider` object.

        Args:
            mode (str): Default is ``w`` (call observer when variable is written).
            args: Passed to ``Tkinter.<vartype>.trace()``, at least
                one argument (a callback function) should be provided.
            **kwargs: Passed to ``Tkinter.<vartype>.trace()``, unused.
        """
        self._Value.trace(mode, *args, **kwargs)

    def disable(self):
        """Disables the :py:class:`Slider`."""

        self._Scale.configure(state = "disabled",
                relief = FLAT,
                bg = self.FGDISABLED,
                activebackground = self.FGDISABLED,
                troughcolor = self.BGDISABLED)
        self._Label.configure(fg = self.DISABLED)
        self._Entry.configure(state = "disabled",
                relief = FLAT,
                fg = self.DISABLED,
                bg = self.BGDISABLED)
        self._is_active = False

    def enable(self):
        """Enables the :py:class:`Slider`."""

        self._Scale.configure(state = "active",
                bg = self.FGACTIVE,
                activebackground = self.FGACTIVE,
                troughcolor = self.BGACTIVE)
        self._Label.configure(fg = "black")
        self._Entry.configure(state = "normal",
                relief = FLAT,
                fg = "#000000", bg = "white")
        self._is_active = True

    def is_active(self):
        """To check if a :py:class:`Slider` is active or not.

        Returns:
            Returns ``True`` if the :py:class:`Slider` is active
            and ``False`` if currently inactive.
        """
        ##return not self._Scale.config()["state"][4] == "disabled"
        return self._is_active



# -------------------------------------------------------------------
# -------------------------------------------------------------------
# -------------------------------------------------------------------
class defaultpalettecanvas(object):
    """Sets up a ``Tk.Canvas`` element containing the colors of the default
    HCL color palettes which will be placed in the top part of the GUI.

    Args:
        palframe (``Tk.Frame``): The bounding ``Tk.Frame`` which takes up the palettes.
        sliders (list): List of :py:class:`Slider` objects. When a user selets a new
            default palette the sliders will be set to the specification
            given the selected palette (and enabled/disabled corresponding
            to the palette specification).
        pal (:py:class:`defaultpalette`): The default color palette.
        n (int): Number of colors to be drawn.
        xpos (float): X-position within ``Tk.Canvas`` (palframe input).
        figwidth (float): Width of the ``Tk.Canvas`` element (palframe input).
        figheight (float): Width of the ``Tk.Canvas`` element (palframe input).
    """

    def __init__(self, palframe, sliders, pal, n, xpos, figwidth, figheight):  

        self._palframe = palframe
        self._sliders  = sliders
        self._pal      = pal

        colors = pal.colors(n)
        self._draw_canvas(colors, xpos, figwidth, figheight)

    def _draw_canvas(self, colors, xpos, figwidth, figheight):

        # Compute width and height of the color map
        offset = 0 # White frame around the palettes
        n = len(colors)
        h = (figheight - 2. * offset) / len(colors)
        w = figwidth  - 2. * offset

        canvas = Canvas(self._palframe, width = figwidth,
                        height = figheight, bg = "#ffffff")
        canvas.place(x = xpos, y = 0)
        # Binding for interaction
        canvas.bind("<Button-1>", lambda event: \
                self._activate(event, self._pal, self._sliders))

        for i in range(0, n):
            canvas.create_rectangle(offset, i*h, w, (i+1)*h,
                                    width = 0, fill = colors[i])

    def _activate(self, event, pal, sliders):

        # Loading settings of the current palette
        settings = pal.get_settings()
        for elem in sliders:
            # Setting value, ensable slider
            if elem.name() == "n":
                continue
            elif elem.name() in settings.keys():
                elem.set(settings[elem.name()])
                elem.enable()
            # Disable slider
            else:
                elem.disable()


# -------------------------------------------------------------------
# -------------------------------------------------------------------
# -------------------------------------------------------------------
class currentpalettecanvas(object):
    """Draws the current palette (the palette as specified on the
    GUI), will be displayed in the lower part of the GUI.

    Args:
        parent (``Tk``): The ``Tk`` object (interface).
        x (float): X-position on the interface.
        y (float): Y-position on the interface.
        width (float): Width of the palette on the interface.
        height (float): Height of the palette on the interface.
    """

    def __init__(self, parent, x, y, width, height):

        self.parent = parent
        self.x      = x
        self.y      = y
        self.width  = width
        self.height = height

        self.canvas = Canvas(self.parent, width = self.width, height = self.height)
        self.canvas.config(borderwidth = 1, bg = "#000000")
        self.canvas.place(x = self.x, y = self.y + 20)

    def _draw_canvas(self, colors):

        from numpy import floor

        n = len(colors)
        w = floor(float(self.width) / float(len(colors)))
        h = self.height
        # Overwrite everything with a white box
        self.canvas.create_rectangle(0, 0, self.width, self.height + 1, width = 0, fill = "white")
        for i in range(0, n):
            # Dropping Nan's
            if len(str(colors[i])) < 7: continue
            # Last box to self.width
            x1 = (i+1) * w if i < (n-1) else self.width
            self.canvas.create_rectangle(i*w, 0, x1, h+1,
                    width = 0, fill = colors[i])



# -------------------------------------------------------------------
# -------------------------------------------------------------------
# -------------------------------------------------------------------
def choose_palette(**kwargs):
    """Graphical user interface to choose HCL based color palettes.  Returns an
    object of :py:class:`palettes.diverging_hcl`,
    :py:class:`palettes.qualitative_hcl`, or
    :py:class:`palettes.sequential_hcl` with user-defined default settings.

    Args:
        kwargs: See :py:class:`choose_palette.gui`.

    Returns:
        `palettes.hclpalette` object
        The object allows to get colors in different ways, the default is a
        list with hex colors. See :py:class:`palettes.hclpalette` or, more
        specifically, the manual of the depending palette
        (:py:class:`palettes.diverging_hcl`,
        :py:class:`palettes.qualitative_hcl`, or
        :py:class:`palettes.sequential_hcl`).
    """

    obj = gui(**kwargs)

    from . import palettes
    method = getattr(palettes, obj.method())

    # Overwrite __init__ method, add new defaults
    import sys
    if sys.version_info.major < 3:
        varnames = list(method.__init__.im_func.func_code.co_varnames)
        defaults = list(method.__init__.im_func.func_defaults)
    else:
        varnames = list(method.__init__.__code__.co_varnames)
        defaults = list(method.__init__.__defaults__)


    # Getting current parameters from slider object
    settings = {}
    for s in obj.sliders():
        # Only read active sliders
        if not s.is_active(): continue
        # If active, store current value
        settings[s.name()] = s.get()

    # Prepare new default arguments
    for key in ["h","c","l","p"]:
        k1  = "{:s}1".format(key)
        k2  = "{:s}2".format(key)
        key = "power" if key == "p" else key
        if k1 in settings.keys() and k2 in settings.keys():
            settings[key] = [settings[k1], settings[k2]]
            del settings[k1]
            del settings[k2]
        elif k1 in settings.keys():
            settings[key] = settings[k1]
            del settings[k1]
        elif k2 in settings.keys():
            settings[key] = settings[k2]
            del settings[k2]

    for idx,key in enumerate(varnames[1:(len(defaults)+1)]):
        if key in settings.keys():
            defaults[idx] = settings[key]

    # Ugly but functional
    # Possibly nicer with functools.partial
    import types
    method.__init__ = types.FunctionType(method.__init__.__code__,
                                         method.__init__.__globals__,
                                         method.__init__.__name__,
                                         tuple(defaults),
                                         method.__init__.__closure__)

    return method()


# -------------------------------------------------------------------
# This is the GUI itself (called by choose_palette which is handling
# the return).
# -------------------------------------------------------------------
class gui(object):
    """Graphical user interface to choose custom HCL-basec color palettes.

    Args:
        kwargs: Optional, can be used to change the defaults when starting the
            GUI. Currently a parameter called ``palette`` is allowed to
            specify the initial color palette. If not set, ``palette = "Blue-Red"``
            is used.

    Example:
        >>> colorspace.choose_palette()
    """

    WIDTH = 400
    HEIGHT = 700
    FRAMEHEIGHT = 100
    FRAMEWIDTH  = WIDTH - 20

    # Slider settings
    _slider_settings = {
        "h1"   : {"type": "int",   "from": -360, "to": 360, "resolution": 1},
        "h2"   : {"type": "int",   "from": -360, "to": 360, "resolution": 1},
        "c1"   : {"type": "int",   "from": 0,    "to": 100, "resolution": 1},
        "cmax" : {"type": "int",   "from": 0,    "to": 180, "resolution": 1},
        "c2"   : {"type": "int",   "from": 0,    "to": 100, "resolution": 1},
        "l1"   : {"type": "int",   "from": 0,    "to": 100, "resolution": 1},
        "l2"   : {"type": "int",   "from": 0,    "to": 100, "resolution": 1},
        "p1"   : {"type": "float", "from": 0,    "to": 3,   "resolution": .1},
        "p2"   : {"type": "float", "from": 0,    "to": 3,   "resolution": .1},
        "n"    : {"type": "int",   "from": 2,    "to": 30,  "resolution": 1}
    }
    _sliders = []

    # Canvas for the current palette
    _currentpalette = None

    # Dropdown menu (Dropdown)
    _Dropdown       = None

    # Frame taking up the default palettes
    _palframe       = None

    # Tkiter object for the demo
    _demoTk         = None

    # Used to store the control buttons (desaturate, reversed, ...)
    _control        = None

    # Initialize defaults
    _setting_names = ["h1","h2","c1","cmax","c2","l1","l2","p1","p2","n"]
    _settings       = {}
    for key in _setting_names:
        _settings[key] = 7 if key == "n" else None


    def __init__(self, **kwargs):

        # Initialization arguments, if any
        init_args = {}
        # Default if no inputs are set
        if not "palette" in kwargs.keys():  palette = "Blue-Red"
        else:                               palette = kwargs["palette"]

        # Find initial values
        from . import hclpalettes
        self._palettes = hclpalettes()
        pal            = self._palettes.get_palette(palette)

        # Store palette name and palette type to select
        # the correct dropdown entries
        init_args["name"] = pal.name()
        init_args["type"] = pal.type()
        for key,val in pal.get_settings().items():
            init_args[key] = val

        # Save palette settings
        self.settings(**pal.get_settings())

        # Initialize gui
        self._master         = self._init_master()
        # The different palette types
        self._Dropdown       = self._add_paltype_dropdown(pal.type())
        # Adding current palette has to be before the sliders
        # as they need the current palette canvas for the
        # to be able to be reactive.
        self._sliders        = self._add_sliders()
        # Adding dropdown menu and select color map
        # Add the frame with the default palettes
        # on top of the GUI
        self._palframe       = self._add_palframe(pal.type())
        ## Add the horizontal color map for current colors.
        self._currentpalette = self._add_currentpalettecanvas()
        self._draw_currentpalette()

        self._DEMO           = self._add_demo_options()
        self._add_return_button()

        # Adding control checkboxes and radio buttons
        self._control = self._add_control()

        # Initialize interface
        mainloop()

    def _add_paltype_dropdown(self, type_):
        """Adds a drop down menu to the GUI which allowes to
        switch between the different types of the default
        palettes (see also :py:class:`palettes.hclpalettes`).

        Args:
        type_ (str): The default selected palette type on GUI initialization.
        """
        opts = self.palettes().get_palette_types()

        paltypevar = StringVar(self.master())
        paltypevar.set(type_) # default value

        # Option menu
        menu = OptionMenu(self.master(), paltypevar, *opts,
                          command = self.OnPaltypeChange) #obj.selected)
        menu.config(width = 40, pady = 5, padx = 5)
        menu.grid(column = 1, row = len(opts))
        menu.place(x = 10, y = 30)

        return paltypevar

    def OnPaltypeChange(self, *args, **kwargs):
        """The callback function of the drop down element. Triggered
        every time the drop down element changes.
        """

        # Updating the palette-frame.
        self._palframe = self._add_palframe(args[0])

        # Take first palette
        p = self.palettes().get_palettes(args[0])[0]

        # Enable/disable/set sliders
        settings = p.get_settings()
        for elem in self.sliders():
            # Setting value, ensable slider
            if elem.name() == "n":
                continue
            elif elem.name() in settings.keys():
                elem.set(settings[elem.name()])
                elem.enable()
            # Disable slider
            else:
                elem.disable()

    def _add_control(self):
        """Adds the check buttons (``Tk.Checkbutton``) and radio button
        (``Tk.Radiobutton``) elements. Color fixup, revert colors,
        and CVD options.
        """
        control = {}

        frame = Frame(self.master(), height = 30, width = self.WIDTH - 20)
        frame.grid()
        frame.place(x = 10, y = self.HEIGHT - 140)
        col = 0; row = 0

        # Fixup colors
        fixupvar      = BooleanVar()
        fixupbutton   = Checkbutton(frame, text="Fixup colors",
                                    variable = fixupvar, command = self.OnChange)
        fixupbutton.grid(column = col, row = row, sticky = "w"); row += 1
        fixupbutton.select()
        control["fixup"] = fixupvar

        # Reverse colors
        revvar      = BooleanVar()
        revbutton   = Checkbutton(frame, text="Reverse colors",
                                  variable = revvar, command = self.OnChange)
        revbutton.grid(column = col, row = row, sticky = "w"); row += 1
        control["reverse"] = revvar

        # Butons for Desaturation/CVD
        ypos = self.HEIGHT - 40

        desatvar    = BooleanVar()
        desatbutton = Checkbutton(frame, text="Desaturation",
                                  command = self.OnChange, variable = desatvar)
        desatbutton.grid(column = col, row = row, sticky = "w"); row += 1
        control["desaturate"] = desatvar

        cvdvar      = BooleanVar()
        cvdbutton   = Checkbutton(frame, text="Color blindness",
                                  command = self.OnChange, variable = cvdvar)
        cvdbutton.grid(column = col, row = row, sticky = "w"); col += 1
        control["cvd"] = cvdvar

        # Radio buttons for CVD
        ypos = self.HEIGHT - 20
        cvdtypevar  = StringVar()
        radio_deutan = Radiobutton(frame, text = "deutan", command = self.OnChange,
                                   variable = cvdtypevar, value = "deutan")
        radio_protan = Radiobutton(frame, text = "protan", command = self.OnChange,
                                   variable = cvdtypevar, value = "protan")
        radio_tritan = Radiobutton(frame, text = "tritan", command = self.OnChange,
                                   variable = cvdtypevar, value = "tritan")
        radio_deutan.grid(column = col, row = row, sticky = "w"); col += 1
        radio_protan.grid(column = col, row = row, sticky = "w"); col += 1
        radio_tritan.grid(column = col, row = row, sticky = "w"); col += 1
        cvdtypevar.set("deutan")
        control["cvdtype"] = cvdtypevar

        return control

    def control(self):
        """Get control options.

        Returns:
            dict: Returns a dictionary with the current control options (see
            :py:func:`_add_control`).
        """


        if not self._control:
            return {"reverse" : False, "desaturate" : False, "cvd" : False,
                    "cvdtype" : "deutan", "fixup": True}
        else:
            res = {}
            res["reverse"]    = self._control["reverse"].get()
            res["desaturate"] = self._control["desaturate"].get()
            res["cvd"]        = self._control["cvd"].get()
            res["cvdtype"]    = self._control["cvdtype"].get()
            res["fixup"]      = self._control["fixup"].get()
            return res


    def settings(self, *args, **kwargs):
        """Used to load/store current palette settings (gui settings).

        Args:
            args: Strings to load one/several parameters.
            kwargs: Named arguments, used to store values.

        Returns:
            dict: Returns a dictionary with the current slider settings.
        """
        # Return current settings
        if len(args) == 0 and len(kwargs) == 0:
            return self._settings
        # Return some settings
        elif len(args):
            res = {}
            for key in args:
                if not isinstance(key, str): continue
                # Loading setting
                if key in self._setting_names:
                    res[key] = self._settings[key]
            if len(res) == 1:   return res[list(res.keys())[0]]
            else:               return reskk
        # Store values, if possible.
        else:
            for key,val in kwargs.items():
                if key in self._setting_names:
                    self._settings[key] = val

    def _init_master(self):
        """Initializes the ``Tk`` GUI window."""

        # initialize mater TK interface
        master = Tk()
        master.wm_title("Colorspace - Choose Color Palette")
        master.configure()
        master.resizable(width=False, height=False)
        master.geometry("{:d}x{:d}".format(self.WIDTH, self.HEIGHT))
        master.bind("<Return>", self._return_to_python)
        master.bind("<Escape>", self._return_to_python)

        return master

    def master(self):
        """
        Returns:
            ``Tk``: Returns the ``Tk`` GUI object.
        """
        return self._master

    def palettes(self):
        """
        Returns:
            :py:class:`palettes.hclpalettes`: Returns the default palettes available.
        """
        return self._palettes

    def sliders(self):
        """
        Returns:
            list: List of :py:class:`Slider` objects.
        """
        return self._sliders

    def palframe(self):
        """
        Returns:
            ``Tk.Frame``: Returns the palette frame (``Tk.Frame`` object, see
            :py:func:`_add_palframe`).
        """

        return self._palframe

    def _add_palframe(self, type_):
        """
        Adds a ``Tk.Frame`` to the ``Tk`` element (see :py:func:`_init_master`).
        This frame is used to take up the default palettes.
        """

        ##scroll dev### if hasattr(self, "_palframe"):
        ##scroll dev###     if not self._palframe is None: self._palframe.destroy()

        ##scroll dev### frame = Frame(self.master())
        ##scroll dev### frame.place(x = 10, y = 80)

        ##scroll dev### # Loading palettes of currently selected palette type
        ##scroll dev### from numpy import min
        ##scroll dev### pals = self.palettes().get_palettes(type_) ###self.dd_type.get())
        ##scroll dev### for child in frame.winfo_children(): child.destroy()

        ##scroll dev### canvas = Canvas(frame, bg = "#ffffff",
        ##scroll dev###               scrollregion = (0,0,2000,0),
        ##scroll dev###               height = self.FRAMEHEIGHT, width = self.FRAMEWIDTH)

        ##scroll dev### scroll = Scrollbar(frame, orient = HORIZONTAL)
        ##scroll dev### scroll.pack(side = BOTTOM,fill = X)
        ##scroll dev### scroll.config(command = canvas.xview)

        ##scroll dev### canvas.config(xscrollcommand = scroll.set)
        ##scroll dev### canvas.pack(fill = BOTH, expand = True)

        if hasattr(self, "_palframe"):
            if not self._palframe is None: self._palframe.destroy()

        frame = Frame(self.master(), bg = "#ffffff",
                      height = self.FRAMEHEIGHT, width = self.FRAMEWIDTH)
        frame.place(x = 10, y = 80)

        # Loading palettes of currently selected palette type
        from numpy import min, sum
        pals = self.palettes().get_palettes(type_) ###self.dd_type.get())
        for child in frame.winfo_children(): child.destroy()

        # Number of palettes to be drawn (where gui = 1 in palette config)
        npals    = sum([x.get("gui") for x in pals])

        # Adding new canvas
        figwidth = min([30, self.FRAMEWIDTH / npals])
        xpos = 0
        for pal in pals:
            if pal.get("gui") <= 0: continue
            defaultpalettecanvas(frame, self.sliders(), pal, 5, xpos, figwidth, self.FRAMEHEIGHT)
            xpos += figwidth

        return frame

    def _add_currentpalettecanvas(self):
        """
        Adds a ``Tk.Canvas`` object to the GUI to display the
        current color palette as specified by the GUI settings.

        Returns:
            ``Tk.Canvas``: Returns the canvas.
        """
        canvas = currentpalettecanvas(self.master(),
               x = 20, y = 500, width = self.WIDTH - 40, height = 30) 

        return canvas

    def _draw_currentpalette(self):
        """Shows the colors in the current palette frame."""

        # Re-draw the canvas.
        self._currentpalette._draw_canvas(self.get_colors())

    def get_colors(self):
        """
        Returns:
            list: Returns a list of hex colors and ``nan`` given the current
            settings on the GUI. ``numpy.nan`` will be returned if ``fixup`` is
            set to False but some colors lie outside the RGB color space.
        """

        # Getting current arguments
        params = {}
        for elem in self.sliders():
            if elem.is_active():
                params[elem.name()] = float(elem.get())

        # Manipulate params
        from re import match
        for dim in ["h", "c", "l","p"]:
            dim1 = "{:s}1".format(dim)
            dim2 = "{:s}2".format(dim)
            dim3 = "{:s}max".format(dim)
            dim = "power" if dim == "p" else dim
            # Boolean vector
            check = [dim1 in params.keys(), dim2 in params.keys(), dim3 in params.keys()]
            if check[0] and check[1] and check[2]:
                params[dim] = [params[dim1], params[dim2], params[dim3]]
                del params[dim1]; del params[dim2]; del params[dim3]
            elif check[0] and check[2]:
                # Diverging chemes: only [c1, cmax] allowed, for
                # others [c1, c2, cmax] (sequential)
                if match(".*[Dd]iverging.*", self._Dropdown.get()) and dim == "c":
                    params[dim] = [params[dim1], params[dim3]]
                else:
                    params[dim] = [params[dim1], params[dim1], params[dim3]]
                del params[dim1]; del params[dim3]
            elif check[0] and check[1]:
                params[dim] = [params[dim1], params[dim2]]
                del params[dim1]
                del params[dim2]
            elif check[0]:
                params[dim] = params[dim1]
                del params[dim1]

        for elem in self.sliders():
            if elem.name() == "n":
                n = elem.get()
                break

        # Check if we have to return the colors reversed.
        # and whether or not fixup is set to True/False
        control = self.control()
        if not "h" in params.keys(): sys.exit("whoops, lost h")
        if "n" in params: del params["n"]
        params["fixup"] = control["fixup"]

        # Craw colors from current color map
        from . import palettes
        type_    = self._Dropdown.get()
        colorfun = self.palettes().get_palettes(type_)[0].method()
        fun      = getattr(palettes, colorfun)

        # Return colors
        colors = fun(**params)(n, rev = control["reverse"])

        # Do we have to desaturate the colors?
        if control["desaturate"]:
            from .CVD import desaturate
            colors = desaturate(colors)

        # Do we have to apply CVD simulation?
        if control["cvd"]:
            from . import CVD
            fun = getattr(CVD, control["cvdtype"])
            colors = fun(colors)

        return colors

    def method(self):
        """
        Returns:
            str: Returns the name of the object which has to be called to get
            the colors. The name of the object is defined in the palconfig
            config files. For "Diverging" palettes this will be
            :py:class:`palettes.diverging_hcl`, for "Qualitative"
            :py:class:`palettes.qualitative_hcl`, and for "Sequential" palettes
            :py:class:`palettes.sequential_hcl`.
        """
        type_    = self._Dropdown.get()
        colorfun = self.palettes().get_palettes(type_)[0].method()
        return colorfun


    def _add_sliders(self):
        """
        Adds a set of sliders to the GUI.

        Returns:
            list: A list of :py:class:`Slider` objects.
        """

        sliders = []

        # For each key in self._setting_names add a Slider object
        # (a Slider is a combined Tkinter.Scale, Tkinter.Entry, and
        # Tkinter.Label element with bindings).
        for idx,key in enumerate(self._setting_names):
            # Initialize with default 0 if nothing yet specified.
            s = Slider(self.master(),
                       key,                                            # name
                       10, 100 + idx * 30 + self.FRAMEHEIGHT,          # x, y
                       self.WIDTH - 20, 30,                            # width, height
                       False if self.settings()[key] is None else True,    # active
                       type_      = self._slider_settings[key]["type"],
                       from_      = self._slider_settings[key]["from"],
                       to         = self._slider_settings[key]["to"],
                       resolution = self._slider_settings[key]["resolution"])
            if not self.settings(key): s.set("0")
            else:                      s.set(str(self.settings(key)))

            # Append slider to list
            sliders.append(s)

        # Add the trace element to make them interactive
        # (an observer, call OnChange whenever the Scale changes).
        for x in sliders:
            x.trace("w", self.OnChange)

        return sliders

    # Callback when an item is getting changed
    def OnChange(self, *args, **kwargs):
        """
        Triggered any time the slider values or control arguments change.
        Draws new current palette (see :py:func:`_draw_currentpalette`).
        """
        self._draw_currentpalette()

        # Is the demo running?
        if self._demoTk: self._show_demo(True)


    def _add_demo_options(self):
        """
        Adds a ``Tk.Button`` to open the demo plot window.

        Todo:
            * Currently not enabled (have had some problems with the interaction/update).
        """
        but = Button(self.master(), text = "Demo",
                command = self._show_demo,
                pady = 5, padx = 5)
        but.place(x = self.WIDTH - 70, y = self.HEIGHT - 40)

        # Variable to store current selection
        opts = ["Bar", "Heatmap", "Pie", "Spine", "Matrix", "Lines", "Spectrum"]
        demovar = StringVar(self.master())
        demovar.set(opts[0]) # default value

        # Demo plot option menu. No callback
        menu = OptionMenu(self.master(), demovar, *opts,
                          command = self.OnChange)
        menu.config(width = 10, pady = 5, padx = 5)
        menu.grid(column = 1, row = len(opts))
        menu.place(x = 180, y = self.HEIGHT - 40)

        return demovar

    def _add_return_button(self):
        """
        Adds the button to return to python, a ``Tk.Button`` element.
        When clicked :py:func:`_return_to_python` is triggered (callback
        function for this button).
        """

        but = Button(self.master(), text = "Return to python",
                command = self._return_to_python, pady = 5, padx = 5)
        but.place(x = 10, y = self.HEIGHT - 40)


    def _return_to_python(self, *args):
        """
        Returns to :py:func:`choose_palette`. Destroys the ``Tk`` interface
        but not the object such that :py:func:`choose_palette` can read the
        settings of the sliders and control elements. Used to create the
        palette which will then be returned to the console/user console.
        """
        # Destroy the demo figure if not already closed
        try:
            import matplotlib.pyplot as plt
            plt.close(self._demo_Figure)
        except:
            pass
        # Close demo window if not already closed
        try:
            self._demoTk.destroy()
        except:
            pass
        self.master().destroy()
        self.master().quit()


    def _show_demo(self, update = False):
        """Show demo.

        Args:
            update (bool): Default is false.

        Todo;
            * Implement and test.

        .. note::
            Requires matplotlib. Will show a message if matplotlib is
            not installed on the machine.
        """
        try:
            import matplotlib
            matplotlib.use("TkAgg")
            #from matplotlib.backends.backend_tkagg import FigureCanvasAgg
            #import matplotlib.backends.tkagg as tkagg
            #from matplotlib.figure import Figure
            hasmatplotlib = True
        except:
            hasmatplotlib = False

        # If has matplotlib: plot
        if hasmatplotlib:

            def draw_figure(canvas, figure, loc=(0, 0)):
                """Draw a matplotlib figure onto a Tk canvas

                loc: location of top-left corner of figure on canvas in pixels.

                Inspired by matplotlib source: lib/matplotlib/backends/backend_tkagg.py
                """
                figure_canvas_agg = FigureCanvasAgg(figure)
                figure_canvas_agg.draw()
                figure_x, figure_y, figure_w, figure_h = figure.bbox.bounds
                figure_w, figure_h = int(figure_w), int(figure_h)
                photo = PhotoImage(master=canvas, width=figure_w, height=figure_h)

                # Position: convert from top-left anchor to center anchor
                canvas.create_image(loc[0] + figure_w/2, loc[1] + figure_h/2, image=photo)

                # Unfortunately, there's no accessor for the pointer to the native renderer
                tkagg.blit(photo, figure_canvas_agg.get_renderer()._renderer, colormode=2)

                # Return a handle which contains a reference to the photo object
                # which must be kept live or else the picture disappears
                return photo



            import matplotlib
            matplotlib.use("TkAgg")
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            import matplotlib.pyplot as plt

            # Initialize plot
            if not hasattr(self, "_demo_Figure"):
                self._demo_Figure = plt.figure()
            if not update:
                self._demoTk = Tk()
                self._demoTk.protocol("WM_DELETE_WINDOW", self._close_demo) #demoTk.destroy)
                self._demoTk.wm_title("colorspace demoplot")
                self._demo_Axis   = self._demo_Figure.add_subplot(211)
                self._demo_Canvas = FigureCanvasTkAgg(self._demo_Figure, master=self._demoTk)
                self._demo_Canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)

            # Getting demo function
            from . import demos
            fun = getattr(demos, self._DEMO.get())

            # Update plot
            fun(self.get_colors(), fig = self._demo_Figure)
            self._demo_Canvas.draw()
            self._demo_Canvas.flush_events()

        else:

            info = [""]
            info.append("To be able to run the demo plots")
            info.append("the python matplotlib package has to be")
            info.append("installed.")
            info.append("")
            info.append("Install matplotlib and try again!")

            txt = Text(self._demoTk, height=10, width=45)
            txt.pack()
            txt.insert(END, "\n".join(info))

    def _close_demo(self):

        import matplotlib.pyplot as plt
        if not self._demoTk is None: self._demoTk.destroy()
        self._demoTk = None




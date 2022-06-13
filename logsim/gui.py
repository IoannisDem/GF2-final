"""Implement the graphical user interface for the Logic Simulator.

Used in the Logic Simulator project to enable the user to run the simulation
or adjust the network properties.

Classes:
--------
MyGLCanvas - handles all canvas drawing operations.
Gui - configures the main window and all the widgets.
SwitchFrame - configures popup window for switch control.
MonitorFrame - configures popup window for monitor control.
ErrorFrame - configures popup window for error display.
"""
import sys
import os
from cgi import print_environ
import wx
import wx.glcanvas as wxcanvas
from OpenGL import GL, GLUT


import builtins

from wx.lib.mixins.inspection import InspectionMixin

# Set "_" to call translation
builtins.__dict__["_"] = wx.GetTranslation

# Languages available in code
sup_lang = [wx.LANGUAGE_ENGLISH,
            wx.LANGUAGE_GREEK]


class MyGLCanvas(wxcanvas.GLCanvas):
    """Handle all drawing operations.

    This class contains functions for drawing onto the canvas. It
    also contains handlers for events relating to the canvas.

    Parameters
    ----------
    parent: parent window.
    size: canvas size.
    devices: instance of the devices.Devices() class.
    monitors: instance of the monitors.Monitors() class.

    Public methods
    --------------
    init_gl(self): Configure the OpenGL context.

    render(self, text): Handle all drawing operations.

    on_paint(self, event): Handle the canvas paint event.

    on_size(self, event): Handle the canvas resize event.

    on_mouse(self, event): Handle mouse events.

    on_key(self, event): Handle key press events.

    Non-public methods
    -------------

    _render_text(self, text, x_pos, y_pos): Handle text drawing
                                           operations.

    _render_trace(self, trace, label=None): Draw new signal trace.

    _update_max_xy(self, x, y): Update max_x and max_y values.
    """

    def __init__(self, parent, size):
        """Initialise canvas properties and useful variables."""
        super().__init__(parent, -1, size=size,
                         attribList=[wxcanvas.WX_GL_RGBA,
                                     wxcanvas.WX_GL_DOUBLEBUFFER,
                                     wxcanvas.WX_GL_DEPTH_SIZE, 16, 0])
        GLUT.glutInit()
        self.init = False
        self.context = wxcanvas.GLContext(self)
        self.parent = parent

        # Initialise variables for panning
        self.pan_x = 0
        self.pan_y = 0
        self.last_mouse_x = 0  # Previous mouse x position
        self.last_mouse_y = 0  # Previous mouse y position

        # Initialise variables for zooming and scrolling
        self.zoom = 2.0
        self.max_y = 0
        self.max_x = 0

        # Update variables for panning
        self.pan_y -= (self.zoom - 1.0) * size.height/2

        # Initialise display variables for signal sketch
        self.traces = {}
        self.periods = 0
        self.trace_num = 0
        self.shift_px = 50
        self.period_px = 20
        self.colours = [(1.0, 0.0, 0.0),
                        (0.0, 1.0, 0.0)]  # Red and Green

        # Bind events to the canvas
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key)
        self.Bind(wx.EVT_PAINT, self.on_paint)

    def init_gl(self):
        """Configure and initialise the OpenGL context."""
        size = self.GetClientSize()
        self.SetCurrent(self.context)
        GL.glDrawBuffer(GL.GL_BACK)
        GL.glClearColor(1.0, 1.0, 1.0, 0.0)
        GL.glViewport(0, 0, size.width, size.height)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(0, size.width, 0, size.height, -1, 1)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        GL.glTranslated(self.pan_x, self.pan_y, 0.0)
        GL.glScaled(self.zoom, self.zoom, self.zoom)

    def render(self):
        """Handle all drawing operations."""
        self.max_x, self.max_y = 0, 0  # Reset max values
        size = self.GetClientSize()
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        # Clear everything
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        for label, trace in self.traces.items():
            self._render_trace(trace, label=label)

        # Draw mesh to indicate periods
        if len(self.traces) > 0:
            GL.glPushAttrib(GL.GL_ENABLE_BIT)
            GL.glLineStipple(1, 0xAAAA)
            GL.glColor3f(0.0, 0.0, 0.0)
            GL.glEnable(GL.GL_BLEND)
            GL.glEnable(GL.GL_LINE_STIPPLE)
            GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
            GL.glColor4f(0.0, 0.0, 0.0, 0.25)
            GL.glBegin(GL.GL_LINES)
            for i in range(self.periods):
                GL.glVertex2f(self.shift_px + self.period_px*(i+1),
                              size.height - 20)
                GL.glVertex2f(self.shift_px + self.period_px*(i+1),
                              size.height - self.max_y - 5)
            GL.glEnd()
            GL.glPopAttrib()

        # Reset number of traces for next render
        self.trace_num = 0

        # We have been drawing to the back buffer, flush the graphics pipeline
        # and swap the back buffer to the front
        GL.glFlush()
        self.SwapBuffers()

    def on_paint(self, event):
        """Handle the paint event."""
        self.render()

    def on_size(self, event):
        """Handle the canvas resize event."""
        # Reset view on resize
        size = self.GetClientSize()
        self.pan_x = 0
        self.pan_y = -(self.zoom - 1.0) * size.height

        # Forces reconfiguration of the viewport, modelview and projection
        # matrices on the next paint event
        self.init = False

    def on_mouse(self, event):
        """Handle mouse events."""
        text = ""

        # Calculate object coordinates of the mouse position
        size = self.GetClientSize()
        if event.ButtonDown():
            self.SetFocus()
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            text = "".join([_("Mouse button pressed at: "), str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.ButtonUp():
            text = "".join([_("Mouse button released at: "), str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.Leaving():
            text = "".join([_("Mouse left canvas at: "), str(event.GetX()),
                            ", ", str(event.GetY())])
        if (event.GetWheelRotation() < 0 and
                self.pan_y + size.height * self.zoom
                - 20 * self.zoom < self.max_y * self.zoom):
            self.pan_y -= 0.1*event.GetWheelRotation()
            self.init = False
            string = _("Negative mouse wheel rotation. Scrolling down: ")
            text = "".join([string, str(self.pan_y)])
        if (event.GetWheelRotation() > 0 and
                self.pan_y > -((self.zoom - 1.0) * size.height)):
            self.pan_y -= 0.1*event.GetWheelRotation()
            self.init = False
            text = "".join([_("Positive mouse wheel rotation. Scrolling up: "),
                            str(self.pan_y)])

        if text:
            self.render()
            self.parent.update_info(text)
        else:
            self.Refresh()  # Triggers the paint event

    def on_key(self, event):
        """Handle key press events."""
        key = event.GetKeyCode()
        size = self.GetClientSize()
        text = None
        if (key == wx.WXK_UP and self.pan_y
                > -((self.zoom - 1.0) * size.height)):
            self.pan_y -= 20
            self.init = False
            text = "".join([_("Up arrow press. Scrolling up: "),
                            str(self.pan_y)])
        if (key == wx.WXK_DOWN and self.pan_y + size.height * self.zoom
                - 20 * self.zoom < self.max_y * self.zoom):
            self.pan_y += 20
            self.init = False
            text = "".join([_("Down arrow press. Scrolling down: "),
                            str(self.pan_y)])
        if key == wx.WXK_LEFT and self.pan_x < 0:
            self.pan_x += 20
            self.init = False
            text = "".join([_("Left arrow press. Scrolling left: "),
                            str(self.pan_x)])
        if (key == wx.WXK_RIGHT and self.pan_x - size.width + 20 * self.zoom
                > - self.max_x * self.zoom):
            self.pan_x -= 20
            self.init = False
            text = "".join([_("Right arrow press. Scrolling right: "),
                            str(self.pan_x)])

        if text:
            self.render()
            self.parent.update_info(text)
        else:
            self.Refresh()  # Triggers the paint event

    def _render_text(self, text, x_pos, y_pos):
        """Handle text drawing operations."""
        GL.glColor3f(0.0, 0.0, 0.0)  # text is black
        GL.glRasterPos2f(x_pos, y_pos)
        font = GLUT.GLUT_BITMAP_HELVETICA_12

        for character in text:
            if character == "\n":
                y_pos = y_pos - 20
                GL.glRasterPos2f(x_pos, y_pos)
            else:
                GLUT.glutBitmapCharacter(font, ord(character))

    def _render_trace(self, trace, label=None):
        """Draw new signal trace."""
        size = self.GetClientSize()

        # Draw trace
        GL.glColor3f(*self.colours[0])
        GL.glBegin(GL.GL_LINE_STRIP)
        for i in range(len(trace)):
            x = (i * self.period_px) + self.shift_px
            x_next = (i+1) * self.period_px + self.shift_px
            if trace[i] == 1:
                y = size.height - 25 - 50*(self.trace_num)
            else:
                y = size.height - 50*(self.trace_num+1)
            self._update_max_xy(x, y)
            GL.glVertex2f(x, y)
            GL.glVertex2f(x_next, y)
        GL.glEnd()

        # Draw axes
        GL.glColor3f(0.0, 0.0, 0.0)
        GL.glBegin(GL.GL_LINES)
        GL.glVertex2f(self.shift_px, size.height - 50*(self.trace_num+1) + 30)
        GL.glVertex2f(self.shift_px, size.height - 50*(self.trace_num+1) - 10)
        GL.glVertex2f(self.shift_px-5, size.height - 50*(self.trace_num+1) - 5)
        GL.glVertex2f(x_next + 10, size.height - 50*(self.trace_num+1) - 5)
        GL.glEnd()
        self._update_max_xy(x_next + 10,
                            size.height - 50 * (self.trace_num+1) - 10)

        # Draw numbers in axis
        for num in range(self.periods+1):
            shift_x = 5  # Shift label in x direction
            shift_x += (len(str(num)) - 1)*3
            self._render_text(str(num),
                              self.shift_px + self.period_px*(num) - shift_x,
                              size.height - 50*(self.trace_num+1) - 12)

        # Draw label
        if label is None:
            label = _("Trace {}").format(self.trace_num + 1)
        self._render_text(label, self.shift_px - 40 - self.pan_x / self.zoom,
                          size.height - 50 * (self.trace_num + 1) + 10)

        # Update trace number
        self.trace_num += 1

    def _update_max_xy(self, x, y):
        """Update max_x and max_y values."""
        if self.GetVirtualSize().GetHeight() - y > self.max_y:
            # y is measured from the top - change in coordinates
            self.max_y = self.GetVirtualSize().GetHeight() - y
        if x > self.max_x:
            # x is measured from the left
            self.max_x = x


class SwitchFrame(wx.Frame):
    """Configure the popup switch menu frame window.

    Parameters
    ----------
    parent: parent of the window.
    style: styling of window, including borders
    button: switch button object assigned to event
    devices: devices object in simulator
    canvas: canvas window frame

    Public methods
    --------------
    on_close(self, event): Event handler for closing window

    on_listbox(self, event): Event handler for updating listbox selection

    on_check(self, event): Event handler for updating checkbox value
    """

    def __init__(self, parent, style, button, devices, canvas):
        """Initialise instance of class."""
        wx.Frame.__init__(self, parent, title=_("Edit Switches"), style=style)

        self.button = button
        self.devices = devices
        self.canvas = canvas
        self.parent = parent

        # Set switch choices from devices - IMPLEMENT
        switch_id = devices.find_devices(self.devices.SWITCH)
        self.switch_values = {}
        for i in switch_id:
            device = self.devices.get_device(i)
            name = self.devices.get_signal_name(i, None)
            self.switch_values[name] = [i, device.switch_state]
        choices = list(self.switch_values)

        # Set widgets
        self.listbox = wx.ListBox(self, wx.ID_ANY, choices=choices)
        self.check = wx.CheckBox(self, wx.ID_ANY, _("Switch ON"))

        # Set sizers
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        main_sizer.Add(self.listbox, 1, wx.ALIGN_LEFT | wx.ALL, 2)
        main_sizer.Add(self.check, 1, wx.ALIGN_RIGHT | wx.ALL, 2)

        self.listbox.SetMinSize((125, 200))
        self.SetSize((250, 250))
        self.SetSizeHints(250, 250)
        self.SetMaxSize((250, 250))

        # Bind events
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.Bind(wx.EVT_LISTBOX, self.on_listbox)
        self.Bind(wx.EVT_CHECKBOX, self.on_check)

        # Set initial selection
        self.listbox.SetSelection(0)
        self.on_listbox(None)

        self.SetSizer(main_sizer)
        wx.CallAfter(self.Refresh)

    def on_close(self, event):
        """Close window on pressing close button."""
        self.Show(False)
        self.Destroy()
        self.button.Enable(True)

    def on_listbox(self, event):
        """Update screen depending on switch selection."""
        index = self.listbox.GetSelection()
        string = self.listbox.GetString(index)
        value = self.switch_values[string][1]
        self.check.SetValue(value)

    def on_check(self, event):
        """Update switch values depending on check state."""
        value = self.check.GetValue()
        index = self.listbox.GetSelection()
        string = self.listbox.GetString(index)
        self.switch_values[string][1] = value
        switch_id = self.switch_values[string][0]

        if self.devices.set_switch(switch_id, value):
            text = _("Switch {} set to {}.").format(string, value)
        else:
            text = _("Could not change switch state.")
        self.canvas.render()
        self.parent.update_info(text)


class MonitorFrame(wx.Frame):
    """Configure the popup monitors menu frame window.

    Parameters
    ----------
    parent: parent of the window.
    style: styling of window, including borders
    button: monitors button object assigned to event
    canvas: canvas window frame
    monitors: monitors object in simulator

    Public methods
    --------------
    on_close(self, event): Event handler for
                           closing window

    on_add_button(self, event): Add a new monitor by
                                reading textCtrl

    on_remove_button(self, event): Remove a new selected monitor,
                                   or from textCtrls

    on_mon_selection(self, event): Unselect unmonitored listbox

    on_unmon_selection(self, event): Unselect monitored listbox

    """

    def __init__(self, parent, style, button, canvas, monitors):
        """Initiate instance of class."""
        wx.Frame.__init__(self, parent, title=_("Edit Monitors"), style=style)

        self.button = button
        self.monitors = monitors
        self.canvas = canvas
        self.names = self.monitors.names

        # Set monitor information
        sig_names = self.monitors.get_signal_names()
        self.monitor_dictionary = {"monitored": sig_names[0],
                                   "unmonitored": sig_names[1]}
        choices_mon = self.monitor_dictionary["monitored"]
        choices_unmon = self.monitor_dictionary["unmonitored"]

        # Set widgets
        mon_title = wx.StaticText(self, wx.ID_ANY, _("Monitored"))
        unmon_title = wx.StaticText(self, wx.ID_ANY, _("Unmonitored"))
        mon_title.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT,
                                  wx.FONTSTYLE_NORMAL,
                                  wx.FONTWEIGHT_BOLD,
                                  True))
        unmon_title.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT,
                                    wx.FONTSTYLE_NORMAL,
                                    wx.FONTWEIGHT_BOLD,
                                    True))
        self.add_button = wx.Button(self, wx.ID_ANY,
                                    _("◀ Add"), size=(100, 50))
        self.listbox_mon = wx.ListBox(self, wx.ID_ANY,
                                      choices=choices_mon)
        self.listbox_unmon = wx.ListBox(self, wx.ID_ANY,
                                        choices=choices_unmon)
        self.remove_button = wx.Button(self, wx.ID_ANY, _("Remove ▶"),
                                       size=(100, 50))
        self.info_text = wx.StaticText(self, wx.ID_ANY, "")

        # Set sizers
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        right_sizer = wx.BoxSizer(wx.VERTICAL)
        central_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(left_sizer, 1, wx.ALL | wx.ALIGN_LEFT, 4)
        main_sizer.Add(central_sizer, 1, wx.TOP | wx.ALIGN_CENTER, 40)
        main_sizer.Add(right_sizer, 5, wx.ALL | wx.ALIGN_RIGHT, 3)

        # Add widgets to sizers
        left_sizer.Add(mon_title, 4, wx.ALL | wx.ALIGN_LEFT, 10)
        left_sizer.Add(self.listbox_mon, 4, wx.ALL | wx.ALIGN_LEFT, 10)
        central_sizer.Add(self.add_button, 1, wx.ALL | wx.ALIGN_CENTER, 15)
        central_sizer.Add(self.remove_button, 1, wx.ALL | wx.ALIGN_CENTER, 15)
        central_sizer.Add(self.info_text, 1, wx.RIGHT | wx.ALIGN_LEFT, 15)
        right_sizer.Add(unmon_title, 4, wx.ALL | wx.ALIGN_RIGHT, 10)
        right_sizer.Add(self.listbox_unmon, 4, wx.ALL | wx.ALIGN_RIGHT, 10)

        self.listbox_mon.SetMinSize((100, 200))
        self.listbox_unmon.SetMinSize((100, 200))
        self.SetSize((430, 300))
        self.SetSizeHints(430, 300)
        self.SetMaxSize((430, 300))

        # Bind events
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.add_button.Bind(wx.EVT_BUTTON, self.on_add_button)
        self.remove_button.Bind(wx.EVT_BUTTON, self.on_remove_button)
        self.listbox_mon.Bind(wx.EVT_LISTBOX, self.on_mon_selection)
        self.listbox_unmon.Bind(wx.EVT_LISTBOX, self.on_unmon_selection)

        # Initialise buttons
        self.remove_button.Enable(False)
        self.add_button.Enable(False)

        # Colours
        self.colours = [(255, 0, 0),
                        (0, 255, 0)]

        self.SetSizer(main_sizer)
        wx.CallAfter(self.Refresh)

    def on_close(self, event):
        """Close window on pressing close button."""
        self.Show(False)
        self.Destroy()
        self.button.Enable(True)

    def on_add_button(self, event):
        """Add a new monitor by reading textCtrl."""
        index = self.listbox_unmon.GetSelection()
        text = self.info_text
        if index != wx.NOT_FOUND:
            string = self.listbox_unmon.GetString(index)
            text.SetLabel(_("Device {} \nnow monitored.").format(string))
            self.monitor_dictionary["unmonitored"].remove(string)
            self.monitor_dictionary["monitored"].append(string)
            device_id = self.names.query(string)
            port_id = None
            if "." in string:
                ind = string.index(".") + 1
                port_id = self.names.query(string[ind:])
                device_id = self.names.query(string[:ind-1])
            [device, port] = device_id, port_id
            self.monitors.make_monitor(device, port)
            self.listbox_mon.Append(string)
            self.listbox_unmon.Delete(index)
            text.SetForegroundColour((0, 0, 0))

    def on_remove_button(self, event):
        """Remove a new selected monitor, or from textCtrl."""
        index = self.listbox_mon.GetSelection()
        text = self.info_text
        if index != wx.NOT_FOUND:
            string = self.listbox_mon.GetString(index)
            text.SetLabel(_("Device {} \nnow unmonitored.").format(string))
            self.monitor_dictionary["monitored"].remove(string)
            self.monitor_dictionary["unmonitored"].append(string)

            device_id = self.names.query(string)
            port_id = None
            if "." in string:
                ind = string.index(".") + 1
                port_id = self.names.query(string[ind:])
                device_id = self.names.query(string[:ind-1])
            [device, port] = device_id, port_id
            self.monitors.remove_monitor(device, port)
            self.listbox_mon.Delete(index)
            self.listbox_unmon.Append(string)
            text.SetForegroundColour((0, 0, 0))

    def on_mon_selection(self, event):
        """Unselect unmonitored listbox, enable add."""
        self.listbox_unmon.SetSelection(-1)
        self.add_button.Enable(False)
        self.remove_button.Enable(True)

    def on_unmon_selection(self, event):
        """Unselect monitored listbox, enable remove."""
        self.listbox_mon.SetSelection(-1)
        self.remove_button.Enable(False)
        self.add_button.Enable(True)


class ConnectionFrame(wx.Frame):
    """Configure the popup connection menu frame window.

    Parameters
    ----------
    parent: parent of the window.
    style: styling of window, including borders
    button: monitors button object assigned to event
    canvas: canvas window frame
    network: network of connections in logsim

    Public methods
    --------------
    on_close(self, event): Event handler for
                           closing window

    on_add(self, event): Event handler for
                         add check box

    on_remove(self, event): Event handler for
                            remove check box

    on_list_sel(self, event): Event handler for
                              any list selection

    on_con_button(self, event): Event handler for
                                connect button

    Non-public methods
    ------------------
    _remove_connection(
        self, id1, port1,
        id2, port2): Removes connection between the
                     provided devices and ports

    """

    def __init__(self, parent, style, button, canvas, network):
        """Initiate instance of class."""
        wx.Frame.__init__(self, parent,
                          title=_("Edit Connections"), style=style)

        self.button = button
        self.network = network
        self.canvas = canvas
        self.devices = network.devices
        self.parent = parent

        # Set inputs and outputs in network
        self.dev_ID = self.devices.find_devices()
        self.con_inp = []  # Connected inputs
        self.disc_inp = []  # Disconnected inputs
        self.switch_id = self.devices.find_devices(self.devices.SWITCH)
        self.out = []
        for id in self.dev_ID:
            if id not in self.switch_id:
                device = self.devices.get_device(id)
                for port_id in device.inputs:
                    # Append inputs
                    name = self.devices.get_signal_name(id, port_id)
                    con = self.network.get_connected_output(id, port_id)
                    if con is not None:
                        self.con_inp.append(name)
                    else:
                        self.disc_inp.append(name)
                for port_id in device.outputs:
                    # Append output ports
                    name = self.devices.get_signal_name(id, port_id)
                    self.out.append(name)
            else:
                # Append switches
                name = self.devices.get_signal_name(id, None)
                self.out.append(name)

        # Set widgets
        output_text = wx.StaticText(self, wx.ID_ANY, _("Outputs"))
        input_text = wx.StaticText(self, wx.ID_ANY, _("Inputs"))
        output_text.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT,
                                    wx.FONTSTYLE_NORMAL,
                                    wx.FONTWEIGHT_BOLD,
                                    True))
        input_text.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT,
                                   wx.FONTSTYLE_NORMAL,
                                   wx.FONTWEIGHT_BOLD,
                                   True))

        self.input_box = wx.ListBox(self, wx.ID_ANY, choices=self.con_inp)
        self.output_box = wx.ListBox(self, wx.ID_ANY, choices=[])
        self.add_check = wx.CheckBox(self, wx.ID_ANY, _("Add"))
        self.remove_check = wx.CheckBox(self, wx.ID_ANY, _("Remove"))
        self.con_button = wx.Button(self, wx.ID_ANY, _("Disconnect"))
        self.text = wx.StaticText(self, wx.ID_ANY, "")

        # Set sizers
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        right_sizer = wx.BoxSizer(wx.VERTICAL)
        central_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(left_sizer, 1, wx.ALL | wx.ALIGN_LEFT, 4)
        main_sizer.Add(central_sizer, 1, wx.TOP | wx.ALIGN_CENTER, 40)
        main_sizer.Add(right_sizer, 5, wx.ALL | wx.ALIGN_RIGHT, 3)

        # Add widgets to sizers
        left_sizer.Add(input_text, 4, wx.ALL | wx.ALIGN_CENTER, 10)
        left_sizer.Add(self.input_box, 40, wx.EXPAND, 10)
        central_sizer.Add(self.add_check, 1, wx.ALL | wx.ALIGN_CENTER, 15)
        central_sizer.Add(self.remove_check, 1, wx.ALL | wx.ALIGN_CENTER, 15)
        central_sizer.Add(self.con_button, 1, wx.ALL | wx.ALIGN_CENTER, 15)
        central_sizer.Add(self.text, 1, wx.LEFT, 10)
        right_sizer.Add(output_text, 4, wx.ALL, 10)
        right_sizer.Add(self.output_box, 40, wx.EXPAND, 10)

        self.input_box.SetSizeHints((100, 300))
        self.output_box.SetSizeHints((100, 300))
        self.SetSize((340, 300))
        self.SetSizeHints(340, 300)
        self.SetMaxSize((340, 300))

        # Bind events
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.add_check.Bind(wx.EVT_CHECKBOX, self.on_add)
        self.remove_check.Bind(wx.EVT_CHECKBOX, self.on_remove)
        self.input_box.Bind(wx.EVT_LISTBOX, self.on_list_sel)
        self.output_box.Bind(wx.EVT_LISTBOX, self.on_list_sel)
        self.con_button.Bind(wx.EVT_BUTTON, self.on_con_button)

        # Colours
        self.colours = [(255, 0, 0),
                        (0, 255, 0)]

        # Initialise connection mode
        self.remove_check.SetValue(1)
        self.add_check.Enable(True)
        self.remove_check.Enable(False)
        self.con_button.Enable(False)

        # Initialise attributes
        self.id1, self.port_id1 = None, None
        self.id2, self.port_id2 = None, None

        self.SetSizer(main_sizer)
        wx.CallAfter(self.Refresh)

    def on_close(self, event):
        """Close window on pressing close button."""
        self.Show(False)
        self.Destroy()
        self.button.Enable(True)
        # If inputs left unconnected, notify on close
        if len(self.disc_inp) > 0:
            text = _("Some inputs were left disconnected. "
                     "System may oscillate.")
            self.parent.update_info(text, False,
                                    self.parent.colours[0])

    def on_add(self, event):
        """Change mode to add connections."""
        self.input_box.Clear()
        self.input_box.Append(self.disc_inp)
        self.output_box.Clear()
        self.output_box.Append(self.out)
        self.remove_check.SetValue(0)
        self.add_check.Enable(False)
        self.remove_check.Enable(True)
        self.con_button.SetLabel(_("Connect"))
        self.con_button.Enable(False)
        self.text.SetLabel("")

    def on_remove(self, event):
        """Change mode to remove connections."""
        self.input_box.Clear()
        self.input_box.Append(self.con_inp)
        self.output_box.Clear()
        self.add_check.SetValue(0)
        self.add_check.Enable(True)
        self.remove_check.Enable(False)
        self.con_button.SetLabel(_("Disconnect"))
        self.con_button.Enable(False)
        self.text.SetLabel("")

    def on_list_sel(self, event):
        """Handle event when input is selected."""
        inp = self.input_box.GetSelection()
        out = self.output_box.GetSelection()
        if self.remove_check.GetValue() is True:
            # Remove mode
            name = self.input_box.GetString(inp)
            id1, port_id1 = self.devices.get_signal_ids(name)
            id2, port_id2 = self.network.get_connected_output(id1,
                                                              port_id1)
            out = self.devices.get_signal_name(id2, port_id2)
            self.output_box.Clear()
            self.output_box.Append(out)
            self.output_box.SetSelection(0)
            self.con_button.Enable(True)

            # Set attribute variables - memory
            self.id1, self.port_id1 = id1, port_id1
            self.id2, self.port_id2 = id2, port_id2
        elif (inp != wx.NOT_FOUND and out != wx.NOT_FOUND):
            # Add mode
            inp_name = self.input_box.GetString(inp)
            out_name = self.output_box.GetString(out)
            id1, port_id1 = self.devices.get_signal_ids(inp_name)
            id2, port_id2 = self.devices.get_signal_ids(out_name)
            self.con_button.Enable(True)

            # Set attribute variables - memory
            self.id1, self.port_id1 = id1, port_id1
            self.id2, self.port_id2 = id2, port_id2
        self.text.SetLabel("")

    def on_con_button(self, event):
        """Handle event for button presses."""
        inp = self.input_box.GetSelection()
        name = self.input_box.GetString(inp)
        if self.remove_check.GetValue() is True:
            # Remove mode
            self._remove_connection(self.id1, self.port_id1,
                                    self.id2, self.port_id2)
            self.con_inp.remove(name)
            self.disc_inp.append(name)
            ind = self.input_box.GetSelection()
            self.input_box.Delete(ind)
            self.input_box.SetSelection(-1)
            self.output_box.Clear()
            self.con_button.Enable(False)
            self.text.SetLabel(_("Input {}\ndisconnected").format(name))
        else:
            # Add mode
            self.network.make_connection(self.id2,
                                         self.port_id2,
                                         self.id1,
                                         self.port_id1)
            self.disc_inp.remove(name)
            self.con_inp.append(name)
            ind = self.input_box.GetSelection()
            out_ind = self.output_box.GetSelection()
            out_name = self.output_box.GetString(out_ind)

            self.input_box.Delete(ind)
            self.input_box.SetSelection(-1)
            self.output_box.SetSelection(-1)
            self.con_button.Enable(False)
            label = _("Input {}\nconnected to\n{}")
            self.text.SetLabel(label.format(name, out_name))

    def _remove_connection(self, id1, port1, id2, port2):
        """Remove connection from 1 (input) to 2 (output)."""
        first_device = self.devices.get_device(id1)
        first_device.inputs[port1] = None


class ErrorFrame(wx.Frame):
    """Configure the popup error display frame window.

    Parameters
    ----------
    parent: parent of the window.
    style: styling of window, including borders
    errorHandler: errorHandler object from logsim
    run_button: button object assigned to the running
                of the simulation

    Public methods
    --------------
    on_close(self, event): Event handler for closing window
    """

    def __init__(self, parent, style, error_handler, run_button):
        """Initialise instance of the SwitchPopup class."""
        wx.Frame.__init__(self, parent, title=_("Error display"), style=style)

        self.run = run_button

        # Set widgets
        string = ""
        string = _("> Errors in definition file. Code cannot be "
                   "compiled. Fix errors, then re-open file.\n\n")
        string += _("> Number of errors detected:{}\n\n").format(
                  error_handler.error_count)
        for error in error_handler.error_list:
            # Error must be split into each of its lines for translation
            error_msg = error_handler.error_builder(error).split("\n")
            error_msg[0] = _(error_msg[0])
            error_msg[3] = _(error_msg[3])
            error_string = "\n".join(error_msg)
            string += _("> ERROR: {}\n").format(error_string)
        scroll_win = wx.ScrolledWindow(self, wx.ID_ANY, style=wx.SUNKEN_BORDER
                                       | wx.HSCROLL | wx.VSCROLL)
        text = wx.TextCtrl(scroll_win, wx.ID_ANY, style=wx.TE_MULTILINE
                           | wx.TE_READONLY)
        text.SetValue(string)
        text.SetFont(wx.Font(10, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL,
                             wx.FONTWEIGHT_NORMAL, False))

        # Set sizers
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Add widgets to sizers
        main_sizer.Add(text, 1, wx.TOP | wx.LEFT | wx.EXPAND, 10)

        self.SetSize((500, 500))
        self.SetSizeHints(500, 500)
        self.SetMaxSize((500, 500))

        # Bind events
        self.Bind(wx.EVT_CLOSE, self.on_close)

        text.ShowPosition(0)

        self.SetSizer(main_sizer)
        wx.CallAfter(self.Refresh)

    def on_close(self, event):
        """Close window on pressing close button, enable run button."""
        self.Show(False)
        self.run.Enable(True)
        self.Destroy()


class Gui(wx.Frame):
    """Configure the main window and all the widgets.

    This class provides a graphical user interface for the Logic Simulator and
    enables the user to change the circuit properties and run simulations.

    Parameters
    ----------
    title: title of the window.
    names: Names class object
    devices: Devices class object
    network: Network class object
    monitors: Monitors class object
    error_handler: ErrorHandler class object

    Public methods
    --------------
    run_network(self, cycles): Run the network for the specified
                               number of simulation cycles.

    update_traces(self): Update traces displayed on canvas.

    update_info(self, text,
                dev=True, col=(0,0,0)): Update info text.

    on_menu(self, event): Event handler for the file menu.

    on_spin_cycle(self, event): Event handler for when the user changes
                                the number of cycles spin control.

    on_spin(self, event): Event handler for when the user changes the spin
                           control value.

    on_run_button(self, event): Event handler for when the user clicks the run
                                button.

    on_continue_button(self, event): Event handler for when the user clicks
                                     the continue button.

    on_switches_button(self, event): Event handler for when the user clicks
                                     the switches button.

    on_monitors_button(self, event): Event handler for when the user clicks
                                     the monitors button.

    on_connection_button(self, event): Event handler for when the user clicks
                                        the connections button.

    on_right_button(self, event): Event handler for when the user clicks
                                  the right button.

    on_left_button(self, event): Event handler for when the user clicks
                                  the left button.

    on_home_button(self, event): Event handler for when the user clicks
                                  the home button.
    """

    def __init__(self, title, names, devices,
                 network, monitors, error_handler):
        """Initialise widgets and layout."""
        super().__init__(parent=None, title=_(title), size=(800, 600))

        # Logic simulator details
        self.names = names
        self.devices = devices
        self.monitors = monitors
        self.network = network
        self.error_handler = error_handler

        # Configure the menu bar
        fileMenu = wx.Menu()
        viewMenu = wx.Menu()
        colourMenu = wx.Menu()
        helpMenu = wx.Menu()
        menuBar = wx.MenuBar()
        fileMenu.Append(wx.ID_OPEN, _("&Open"))
        fileMenu.Append(wx.ID_EXIT, _("&Exit"))
        viewMenu.Append(wx.ID_INFO, _("&Dev Info"))
        helpMenu.Append(wx.ID_ABOUT, _("&About"))
        viewMenu.Append(wx.ID_SELECT_COLOR, _("&Colour"), colourMenu)
        menuBar.Append(fileMenu, _("&File"))
        menuBar.Append(viewMenu, _("&View"))
        menuBar.Append(helpMenu, _("&Help"))
        self.SetMenuBar(menuBar)

        # Configure sub menus for colour options
        self.monochrome_ID = 999
        self.red_ID = 998
        self.magenta_ID = 997
        self.purple_ID = 996
        colourMenu.Append(self.monochrome_ID, _("&Monochrome"))
        colourMenu.Append(self.red_ID, _("&Red"))
        colourMenu.Append(self.magenta_ID, _("&Magenta"))
        colourMenu.Append(self.purple_ID, _("&Purple"))

        # Configure the widgets
        self.cycles = 10
        self.text_cycle = wx.StaticText(self, wx.ID_ANY, _("Cycles:"))
        self.spin_cycle = wx.SpinCtrl(self, wx.ID_ANY, str(self.cycles), min=1)
        self.run_button = wx.Button(self, wx.ID_ANY, _("Compile"),
                                    size=(130, 50))
        self.continue_button = wx.Button(self, wx.ID_ANY,
                                         _("Continue"), size=(130, 50))
        self.switches_button = wx.Button(self, wx.ID_ANY,
                                         _("Edit Switches"), size=(130, 50))
        self.monitors_button = wx.Button(self, wx.ID_ANY,
                                         _("Edit Monitors"), size=(130, 50))
        self.connection_button = wx.Button(self, wx.ID_ANY,
                                           _("Edit Connections"),
                                           size=(130, 50))
        self.right_button = wx.Button(self, wx.ID_ANY, "▶", size=(50, 50))
        self.left_button = wx.Button(self, wx.ID_ANY, "◀", size=(50, 50))
        self.home_button = wx.Button(self, wx.ID_ANY, "🏠", size=(50, 50))
        self.simulation_text = wx.StaticText(self, wx.ID_ANY,
                                             _("Simulated Signals"))
        self.simulation_text.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT,
                                             wx.FONTSTYLE_NORMAL,
                                             wx.FONTWEIGHT_BOLD,
                                             True))
        self.dev_text = wx.StaticText(self, wx.ID_ANY, "")
        self.dev_text.SetFont(wx.Font(10, wx.FONTFAMILY_MODERN,
                                      wx.FONTSTYLE_NORMAL,
                                      wx.FONTWEIGHT_NORMAL,
                                      False))

        # Canvas for drawing signals
        self.canvas = MyGLCanvas(self, wx.Size(300, 1000))
        self.canvas.SetSizeHints(300, 1100)

        # Bind events to widgets
        self.Bind(wx.EVT_MENU, self.on_menu)
        self.spin_cycle.Bind(wx.EVT_SPINCTRL, self.on_spin_cycle)
        self.run_button.Bind(wx.EVT_BUTTON, self.on_run_button)
        self.continue_button.Bind(wx.EVT_BUTTON, self.on_continue_button)
        self.switches_button.Bind(wx.EVT_BUTTON, self.on_switches_button)
        self.monitors_button.Bind(wx.EVT_BUTTON, self.on_monitors_button)
        self.connection_button.Bind(wx.EVT_BUTTON, self.on_connection_button)
        self.right_button.Bind(wx.EVT_BUTTON, self.on_right_button)
        self.left_button.Bind(wx.EVT_BUTTON, self.on_left_button)
        self.home_button.Bind(wx.EVT_BUTTON, self.on_home_button)

        # Configure sizers for layout
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        right_sizer = wx.BoxSizer(wx.VERTICAL)
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        arrow_sizer = wx.BoxSizer(wx.HORIZONTAL)

        main_sizer.Add(left_sizer, 10, wx.EXPAND, 5)
        main_sizer.Add(right_sizer, 1, wx.ALL, 5)

        left_sizer.Add(self.simulation_text, 1, wx.TOP | wx.ALIGN_CENTER, 2)
        left_sizer.Add(self.dev_text, 1, wx.BOTTOM | wx.ALIGN_BOTTOM, 2)
        left_sizer.Add(self.canvas, 50, wx.EXPAND | wx.ALL, 5)

        right_sizer.Add(self.text_cycle, 1,
                        wx.ALIGN_CENTER | wx.ALIGN_BOTTOM | wx.TOP, 30)
        right_sizer.Add(self.spin_cycle, 1, wx.ALIGN_CENTER)
        right_sizer.Add(self.run_button, 1, wx.ALL | wx.ALIGN_CENTER, 5)
        right_sizer.Add(self.continue_button, 1,
                        wx.ALL | wx.ALIGN_CENTER, 5)
        right_sizer.Add(self.switches_button, 1,
                        wx.ALL | wx.ALIGN_CENTER, 5)
        right_sizer.Add(self.monitors_button, 1,
                        wx.ALL | wx.ALIGN_CENTER, 5)
        right_sizer.Add(self.connection_button, 1,
                        wx.ALL | wx.ALIGN_CENTER, 5)
        right_sizer.Add(arrow_sizer, 1,
                        wx.ALIGN_BOTTOM | wx.ALIGN_CENTER | wx.TOP, 30)
        right_sizer.Add(self.home_button, 1, wx.ALIGN_CENTER)

        arrow_sizer.Add(self.left_button, 1, wx.ALIGN_LEFT)
        arrow_sizer.Add(self.right_button, 1, wx.ALIGN_RIGHT)

        # Disable continue button if first run not performed
        self.continue_button.Enable(False)

        self.SetSizeHints(600, 600)
        self.SetMinSize((600, 600))
        self.SetSizer(main_sizer)

        # Colours
        self.colours = [(255, 0, 0), (0, 255, 0)]

        # Boolean determining if simulation has compiled
        self.compiled = False

        # Disable developer mode (displaying info text) by default
        self.info_text_true = False

    def run_network(self, cycles):
        """Run the network for the specified number of simulation cycles.

        Return True if successful.
        """
        for i in range(cycles):
            if self.network.execute_network():
                self.monitors.record_signals()
            else:
                self.update_info(_("Error! Network oscillating. "
                                   "Verify connections."), False,
                                 self.colours[0])
                return False

        return True

    def update_traces(self):
        """Update traces displayed on canvas."""
        traces = {}
        for device_id, output_id in self.monitors.monitors_dictionary:
            new_trace = []
            signal_list = self.monitors.monitors_dictionary[
                          (device_id, output_id)]
            for signal in signal_list:
                new_trace.append(signal)
            name = self.devices.get_signal_name(device_id, output_id)
            traces[name] = new_trace
        self.canvas.traces = traces

    def update_info(self, text, dev=True, col=(0, 0, 0)):
        """Update information text."""
        self.dev_text.SetLabel("")
        if self.info_text_true and dev:
            self.dev_text.SetForegroundColour((0, 0, 0))
            self.dev_text.SetLabel(" > " + text)
        elif not dev:
            self.dev_text.SetForegroundColour(col)
            self.dev_text.SetLabel(" " + text)

    def on_menu(self, event):
        """Handle the event when the user selects a menu item."""
        event_id = event.GetId()
        if event_id == wx.ID_EXIT:
            self.Close(True)
        if event_id == wx.ID_ABOUT:
            wx.MessageBox(_("Logic Simulator, Team 17"),
                          _("About Logsim"), wx.ICON_INFORMATION | wx.OK)
        if event_id == wx.ID_OPEN:
            file_name = _("Open vi file")
            open_file_dialog = wx.FileDialog(self, file_name, "definition_files/", "",
                                             wildcard="VI files (*.vi)|*.vi",
                                             style=wx.FD_OPEN
                                             + wx.FD_FILE_MUST_EXIST)
            if open_file_dialog.ShowModal() == wx.ID_CANCEL:
                self.update_info(_("Open file cancelled."))
                return     # the user changed idea...

            # Open file, restart program
            path = open_file_dialog.GetPath()
            print(_("Opening file="), path)
            sys.stdout.flush()
            os.execv(sys.executable, ["python3"] + [sys.argv[0]] + [path])
        if event_id == wx.ID_INFO:
            if self.info_text_true:
                self.dev_text.Hide()
            else:
                self.dev_text.Show()
            self.info_text_true = not self.info_text_true
            self.update_info(_("Developer mode toggled."))
        if event_id == self.monochrome_ID:
            self.canvas.colours = [(0.1, 0.1, 0.1), (0.1, 0.1, 0.1)]
            self.colours = [(25, 25, 25), (25, 25, 25)]
            self.update_info(_("Changing colour scheme to Monochrome"))
        if event_id == self.red_ID:
            self.canvas.colours = [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0)]
            self.colours = [(255, 0, 0), (0, 255, 0)]
            self.update_info(_("Changing colour scheme to Red"))
        if event_id == self.magenta_ID:
            self.canvas.colours = [(0.83, 0.07, 0.35), (0.10, 0.52, 1.0)]
            self.colours = [(212, 17, 89), (26, 133, 255)]
            self.update_info(_("Changing colour scheme to Magenta"))
        if event_id == self.purple_ID:
            self.canvas.colours = [(0.29, 0.0, 0.57), (0.10, 1.0, 0.10)]
            self.colours = [(75, 0, 146), (26, 255, 26)]
            self.update_info(_("Changing colour scheme to Purple"))
        self.canvas.render()

    def on_spin_cycle(self, event):
        """Handle the event when the user updates spin control."""
        spin_value = self.spin_cycle.GetValue()
        self.cycles = spin_value
        text = "".join([_("New number of cycles per execution: "),
                       str(spin_value)])
        self.canvas.render()
        self.update_info(text)

    def on_run_button(self, event):
        """Handle the event when the user clicks the run button."""
        if not self.compiled:
            # Disable run button if errors exist
            if self.error_handler.error_count > 0:
                self.run_button.Enable(False)
                error_window = ErrorFrame(self.GetTopLevelParent(),
                                          wx.DEFAULT_FRAME_STYLE,
                                          self.error_handler,
                                          self.run_button)
                error_window.Show(True)
                text = _("Errors in definition file. Code cannot be compiled."
                         "Fix errors, then re-open file.")
                self.update_info(text, False, self.colours[0])
                self.run_button.SetLabel(_("Error"))
            else:
                text = _("Definition file compiled.")
                self.run_button.SetLabel(_("Run"))
                self.compiled = True
                self.canvas.render()
                self.update_info(text)
        else:
            self.monitors.reset_monitors()
            self.devices.cold_startup()
            cycles = self.spin_cycle.GetValue()
            self.canvas.periods = cycles
            if self.run_network(cycles):
                self.update_traces()
                self.update_info(_("Simulation running for {} cycles").format(
                                   cycles))
                self.canvas.render()
                self.continue_button.Enable(True)
            self.on_home_button(None, False)  # Send to home

    def on_continue_button(self, event):
        """Handle the event when the user clicks the continue button."""
        cycles = self.spin_cycle.GetValue()
        canvas = self.canvas
        size = canvas.GetClientSize()

        if self.run_network(cycles):
            canvas.periods += cycles

            self.update_traces()
            translation = _("Continuing for {} cycles. Total: {} cycles.")
            text = translation.format(cycles, canvas.periods)
            canvas.render()
            self.update_info(text)

    def on_switches_button(self, event):
        """Handle the event when the user clicks the switches button."""
        pop = SwitchFrame(self.GetTopLevelParent(), wx.DEFAULT_FRAME_STYLE,
                          self.switches_button, self.devices, self.canvas)

        width, height = self.GetSize()
        pos = self.ClientToScreen(int(width/4), int(height / 4))
        pop.SetPosition(pos)
        pop.Show(True)
        self.switches_button.Enable(False)
        text = _("Switches button pressed.")
        self.canvas.render()
        self.update_info(text)

    def on_monitors_button(self, event):
        """Handle the event when the user clicks the monitors button."""
        pop = MonitorFrame(self.GetTopLevelParent(), wx.DEFAULT_FRAME_STYLE,
                           self.monitors_button, self.canvas, self.monitors)

        pop.colours = self.colours
        width, height = self.GetSize()
        pos = self.ClientToScreen(int(width/4), int(height / 4))
        pop.SetPosition(pos)
        pop.Show(True)
        self.monitors_button.Enable(False)
        text = _("Monitors button pressed.")
        self.canvas.render()
        self.update_info(text)

    def on_connection_button(self, event):
        """Handle the event when the user clicks the connections button."""
        pop = ConnectionFrame(self.GetTopLevelParent(),
                              wx.DEFAULT_FRAME_STYLE,
                              self.connection_button,
                              self.canvas, self.network)
        pop.colours = self.colours
        width, height = self.GetSize()
        pos = self.ClientToScreen(int(width/4), int(height / 4))
        pop.SetPosition(pos)
        pop.Show(True)
        self.connection_button.Enable(False)
        text = _("Connection button pressed.")
        self.canvas.render()
        self.update_info(text)

    def on_right_button(self, event):
        """Handle event where right button is pressed."""
        canvas = self.canvas
        size = canvas.GetClientSize()
        if (canvas.pan_x - size.width
                > - canvas.max_x * canvas.zoom):
            # Do not move pan more than necessary
            if (canvas.pan_x - 2 * size.width
                    > - canvas.max_x * canvas.zoom):
                canvas.pan_x -= size.width
            else:
                canvas.pan_x = (- canvas.max_x * canvas.zoom
                                + size.width)
            canvas.init = False
            self.update_info(_("Scrolling right: {}.").format(
                          canvas.pan_x))
            canvas.render()

    def on_left_button(self, event):
        """Handle event where left button is pressed."""
        canvas = self.canvas
        size = canvas.GetClientSize()
        if canvas.pan_x < 0:
            if canvas.pan_x > -size.width:
                canvas.pan_x = 0
            else:
                canvas.pan_x += size.width
            canvas.init = False
            self.update_info(_("Scrolling left: {}.").format(
                             canvas.pan_x))
            canvas.render()

    def on_home_button(self, event, show_text=True):
        """Handle event where home button is pressed."""
        canvas = self.canvas
        size = canvas.GetClientSize()
        canvas.pan_x = 0
        canvas.pan_y = -(canvas.zoom - 1.0) * size.height
        canvas.init = False
        if show_text:
            self.update_info(_("Resetting view"))
        canvas.render()


class MyApp(wx.App, InspectionMixin):
    """Configure main app and its language."""

    def OnInit(self):
        """Initialise app, set default language."""
        self.Init()

        lang = wx.Locale.GetSystemLanguage()
        # If lang not supported, default to english
        if lang in sup_lang:
            wx_lang = lang
        else:
            wx_lang = wx.LANGUAGE_ENGLISH

        # Create locale
        self.locale = wx.Locale(wx_lang)
        if self.locale.IsOk():
            base_path = os.path.abspath(os.path.dirname(sys.argv[0]))
            sys.path.append(base_path)
            self.locale.AddCatalogLookupPathPrefix("locale")
            self.locale.AddCatalog("logsim")
        else:
            self.locale = None

        return True

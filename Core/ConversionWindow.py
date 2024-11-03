import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class ConversionWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Data conversion")
        self.set_border_width(20)
        self.set_default_size(600, 400)
        self.set_position(Gtk.WindowPosition.CENTER)

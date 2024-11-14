import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class DataLoadWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Data load")
        self.set_border_width(20)
        self.set_default_size(600, 400)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_resizable(False)
        self.set_modal(True)

        self.grid = Gtk.Grid()

        self.add(self.grid)

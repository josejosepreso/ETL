import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class MessageDialogWindow(Gtk.Window):
    def __init__(self, message):
        super().__init__(title="Error")
        dialog = Gtk.MessageDialog(transient_for=self, flags=0, message_type=Gtk.MessageType.ERROR, buttons=Gtk.ButtonsType.OK,text=message)
        dialog.run()
        dialog.destroy()

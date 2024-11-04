import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from Core.DBManager import DBManager

class FieldsWindow(Gtk.Window):
    def __init__(self, user, pswd, source, isQuery):
        super().__init__(title="Select columns")
        self.set_border_width(20)
        self.set_default_size(250, 350)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_resizable(False)

        db = DBManager(user, pswd)
        label = "consulta" if isQuery else "tabla"
        columns = db.get_query_columns(source) if isQuery else db.get_columns_names(source)

        self.grid = Gtk.Grid(column_homogeneous=True, row_homogeneous=False, column_spacing=10, row_spacing=10)
        self.label = Gtk.Label()
        self.label.set_markup("<b>Columnas de la {text}</b>".format(text=label))
        self.grid.attach(self.label, 0, 1, 1, 1)

        self.scrollableGrid = Gtk.Grid(column_homogeneous=True, row_homogeneous=False, column_spacing=10, row_spacing=10)
        self.scrolledWindow = Gtk.ScrolledWindow()
        self.scrolledWindow.set_vexpand(True)

        if columns is None:
            self.destroy()
            return None

        for i in range(0, len(columns)):
            checkButton = Gtk.CheckButton(label=columns[i])
            checkButton.set_active(True)
            self.scrollableGrid.attach(checkButton, 0, i+2, 1, 1)
        
        self.scrolledWindow.add(self.scrollableGrid)
        self.grid.attach(self.scrolledWindow, 0, 2, 3, 1)

        self.okButton = Gtk.Button(label="Aceptar")
        self.okButton.connect("clicked", self.confirm)

        self.cancelButton = Gtk.Button(label="Cancelar")
        self.cancelButton.connect("clicked", self.cancel)

        self.grid.attach(self.okButton, 0, 5, 2, 1)
        self.grid.attach_next_to(self.cancelButton, self.okButton, Gtk.PositionType.RIGHT, 1, 1)

        self.add(self.grid)

    def confirm(self):
        print("TODO")

    def cancel(self, e):
        self.destroy()

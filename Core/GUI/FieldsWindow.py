import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from Core.DBManager import DBManager
from Core.GUI.MessageDialogWindow import MessageDialogWindow 

class FieldsWindow(Gtk.Window):
    def __init__(self, user, pswd, source, isQuery, selectedFields):
        super().__init__(title="Select columns")
        self.user = user
        self.pswd = pswd
        self.source = source
        self.isQuery = isQuery
        self.selectedFields = {}

        db = DBManager(self.user, self.pswd)
        label = "consulta" if self.isQuery else "tabla"
        columns = db.get_query_columns(self.source) if self.isQuery else db.get_columns_names(self.source)

        if columns is None:
            self.destroy()
            message = "No se encontraron columnas."
            if ";" in source: message += " Consulta no debe incluir \";\""
            MessageDialogWindow(message)
            return None

        self.set_border_width(20)
        self.set_default_size(500, 350)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_resizable(False)
        self.set_modal(True)

        self.grid = Gtk.Grid(column_homogeneous=True, row_homogeneous=False, column_spacing=10, row_spacing=10)
        self.label = Gtk.Label()
        self.label.set_markup("<b>Columnas de la {text}</b>".format(text=label))
        self.grid.attach(self.label, 0, 1, 1, 1)

        self.scrollableGrid = Gtk.Grid(column_homogeneous=True, row_homogeneous=False, column_spacing=10, row_spacing=10)
        self.scrolledWindow = Gtk.ScrolledWindow()
        self.scrolledWindow.set_vexpand(True)

        for i in range(0, len(columns)):

            checkButton = Gtk.CheckButton(label=columns[i])
            
            checkButton.set_active(False)
            self.selectedFields[columns[i]] = 0

            if len(selectedFields) != 0 and (not isinstance(selectedFields[columns[i]], int) or selectedFields[columns[i]] == 1):
                checkButton.set_active(True)
                self.selectedFields[columns[i]] = 1

            checkButton.connect("toggled", self.update_selected_fields, columns[i])

            self.scrollableGrid.attach(checkButton, 0, i + 2, 1, 1)
        
        self.scrolledWindow.add(self.scrollableGrid)
        self.grid.attach(self.scrolledWindow, 0, 2, 3, 1)

        self.okButton = Gtk.Button(label="Aceptar")
        self.okButton.connect("clicked", self.confirm, selectedFields)

        self.cancelButton = Gtk.Button(label="Cancelar")
        self.cancelButton.connect("clicked", self.cancel)

        self.grid.attach(self.okButton, 0, 5, 2, 1)
        self.grid.attach_next_to(self.cancelButton, self.okButton, Gtk.PositionType.RIGHT, 1, 1)

        self.add(self.grid)

    def confirm(self, e, selectedFields):

        for key in self.selectedFields:
            selectedFields[key] = self.selectedFields[key]   

        self.destroy()

    def cancel(self, e):
        self.destroy()

    def update_selected_fields(self, e, key):
        self.selectedFields[key] = 0 if self.selectedFields[key] == 1 else 1

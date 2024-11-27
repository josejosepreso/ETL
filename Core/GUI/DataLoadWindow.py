import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from Core.DBManager import DBManager

class DataLoadWindow(Gtk.Window):
    def __init__(self, user, password, sourceFields, destination, mapping):
        super().__init__(title="Data load")

        db = DBManager(user, password)

        columns = db.get_columns_names(destination)

        if columns is None:
            return None

        self.mapping = {}

        self.set_border_width(20)
        self.set_default_size(850, 550)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_resizable(True)
        self.set_modal(True)

        self.grid = Gtk.Grid(column_homogeneous=True, row_homogeneous=False, column_spacing=10, row_spacing=10)
        self.scrolledWindow = Gtk.ScrolledWindow()

        prevlabel = Gtk.Label()
        prevlabel.set_markup("<b>Origen</b>")
        self.grid.attach(prevlabel, 0, 0, 1, 1)
        
        currentlabel = Gtk.Label()
        currentlabel.set_markup("<b>Destino</b>")
        
        self.grid.attach_next_to(currentlabel, prevlabel, Gtk.PositionType.RIGHT, 1, 1)

        for field in sourceFields:
            if sourceFields[field] == 1 or not isinstance(sourceFields[field], int):
                currentlabel = Gtk.Label(field)
                self.grid.attach_next_to(currentlabel, prevlabel, Gtk.PositionType.BOTTOM, 1, 1)
                
                combobox = Gtk.ComboBoxText()
                for column in columns:
                    combobox.append_text(column)
                    combobox.connect("changed", self.on_field_change, currentlabel.get_text())

                self.mapping[field] = ""

                if field in mapping and mapping[field] != "":
                    self.mapping[field] = mapping[field]
                    combobox.set_active(list(columns).index(mapping[field]))
                    
                self.grid.attach_next_to(combobox, currentlabel, Gtk.PositionType.RIGHT, 1, 1)
                
                prevlabel = currentlabel

        self.okButton = Gtk.Button(label="Aceptar")
        self.okButton.connect("clicked", self.done, mapping)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=0)
                
        self.scrolledWindow.add(self.grid)

        box.pack_start(self.scrolledWindow, True, True, 0)
        box.pack_end(self.okButton, False, False, 0)

        self.add(box)

    def on_field_change(self, e, key):
        self.mapping[key] = e.get_active_text()
        
    def done(self, e, mapping):
        for k in self.mapping:
            mapping[k] = self.mapping[k]

        self.destroy()

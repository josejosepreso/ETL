import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class ConversionWindow(Gtk.Window):
    def __init__(self, sourceFields):
        super().__init__(title="Data conversion")

        self.sourceFields = {}
        # checkBox : comboBox
        self.fieldsActions = {}
        # comboBox : comboBox
        self.actionsActions = {}
        
        self.set_border_width(20)
        self.set_default_size(850, 300)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_resizable(False)
        self.set_modal(True)

        self.scrolledWindow = Gtk.ScrolledWindow()
        self.mainGrid = Gtk.Grid(column_homogeneous=True, row_homogeneous=False, column_spacing=10, row_spacing=10)
        self.grid = Gtk.Grid(column_homogeneous=True, row_homogeneous=False, column_spacing=10, row_spacing=10)
        
        previous = None
                
        for k in sourceFields:
            if not isinstance(sourceFields[k], int) or sourceFields[k] == 1:
                current = Gtk.CheckButton(label=k)
                current.connect("toggled", self.on_button_toggled, current)
                
                self.grid.attach_next_to(current, previous, Gtk.PositionType.BOTTOM, 1, 1)
                
                action = Gtk.ComboBoxText()
                self.grid.attach_next_to(action, current, Gtk.PositionType.RIGHT, 1, 1)
                self.grid.attach_next_to(Gtk.Label(""), action, Gtk.PositionType.RIGHT, 1, 1)
                
                previous = current

                self.fieldsActions[current] = action
                self.actionsActions[action] = None

                if not isinstance(sourceFields[k], int):
                    current.set_active(True)

                    fn = sourceFields[k]

                    if "LOWER" in fn:
                        action.set_active(0)

                    if "UPPER" in fn:
                        action.set_active(1)

                    if "EXTRACT" in fn:
                        action.set_active(2)
                        self.on_action_change(action, current)

                    if "CONCAT" in fn:
                        action.set_active(3)

        self.scrolledWindow.add(self.grid)

        self.mainGrid.attach(self.scrolledWindow, 0, 0, 1, 35)

        okButton = Gtk.Button(label="Aceptar")
        okButton.connect("clicked", self.done, sourceFields)

        self.mainGrid.attach_next_to(okButton, self.scrolledWindow, Gtk.PositionType.BOTTOM, 1, 1)
        
        self.add(self.mainGrid)

    def on_button_toggled(self, button, name):
        comboBox = self.fieldsActions[name]
        
        if button.get_active():
            comboBox.set_entry_text_column(0)
            comboBox.append_text("Convertir valor a minuscula")
            comboBox.append_text("Convertir valor a mayuscula")
            comboBox.append_text("De fecha/hora extraer...")
            comboBox.append_text("Concatenar con...")
        
            comboBox.connect("changed", self.on_action_change, name)

            return None
            
        comboBox.remove_all()

        self.sourceFields[name.get_label()] = 1

        self.on_action_change(comboBox, name)

    def on_action_change(self, comboBox, checkBox):

        # print(sourceFields)

        action = self.actionsActions[comboBox]

        if action is not None:
            action.destroy()

        del action
        
        action = comboBox.get_active()

        field = checkBox.get_label()        

        if action == 0:
            self.sourceFields[field] = "LOWER(%s)"%(field)

        if action == 1:
            self.sourceFields[field] = "UPPER(%s)"%(field)

        if action < 2:
            return None
            
        options = Gtk.ComboBoxText()
        options.set_entry_text_column(0)
        
        if action == 2:
            options.append_text("Año")
            options.append_text("Mes")
            options.append_text("Dia")
            options.append_text("Hora")

            options.connect("changed", self.on_unit_change, field)
            
        if action == 3:
            for current in self.sourceFields:
                options.append_text(current)

            options.connect("changed", self.on_field_change, field)

        self.grid.attach_next_to(options, comboBox, Gtk.PositionType.RIGHT, 1, 1)

        self.actionsActions[comboBox] = options
                
        self.mainGrid.show_all()

    def on_unit_change(self, unit, field):

        s = ""

        u = unit.get_active()

        if u == 0:
            s = "YEAR"
        if u == 1:
            s = "MONTH"
        if u == 2:
            s = "DAY"
        else:
            s = "HOUR"
        
        self.sourceFields[field] = "EXTRACT(%s FROM %s)"%(s,field)

    def on_field_change(self, field1, field):
        self.sourceFields[field] = "CONCAT(%s,%s)"%(field,field1.get_active_text())

    def done(self, e, fields):
        for field in self.sourceFields:
            fields[field] = self.sourceFields[field]

        self.destroy()
        

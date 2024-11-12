import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from Core.GUI.ConversionWindow import ConversionWindow
from Core.DBManager import DBManager
from Core.GUI.FieldsWindow import FieldsWindow
from Core.GUI.DataViewWindow import DataViewWindow
from Core.GUI.MessageDialogWindow import MessageDialogWindow
import json

class Window(Gtk.Window):
    def __init__(self):
        super().__init__(title="ETL")
        self.set_border_width(20)
        self.set_default_size(1124, 616)
        self.set_position(Gtk.WindowPosition.CENTER)
        # self.set_resizable(False)
        #
        self.data = []
        self.prevSelectedRow = None
        #
        # Source connection
        self.sourceConnectionLabel = Gtk.Label(label="Iniciar sesion", halign=Gtk.Align.START)
        self.sourceConnectionUser = Gtk.Entry(placeholder_text="Usuario")
        self.sourceConnectionPassword = Gtk.Entry(placeholder_text="Contraseña")
        #
        self.sourceConnectionUser.set_text("C##BD_BICICLETAS")
        self.sourceConnectionPassword.set_text("oracle")
        #
        self.sourceConnectionPassword.set_visibility(False)
        self.sourceConnectButton = Gtk.Button(label="Conectar")
        self.sourceConnectButton.connect("clicked", self.get_source_connection)
        # Source object
        self.sourceLabel = Gtk.Label(halign=Gtk.Align.START)
        self.sourceLabel.set_markup("<b>Objeto de origen</b>")
        self.sourceType1 = Gtk.RadioButton.new_with_label_from_widget(None, "Tabla")
        self.sourceType1.connect("toggled", self.activate_table, "1")
        self.sourceType2 = Gtk.RadioButton.new_from_widget(self.sourceType1)
        self.sourceType2.set_label("Consulta")
        self.sourceType2.connect("toggled", self.activate_query, "2")
        # Source tables
        self.sourceTable = Gtk.ComboBoxText()
        self.sourceTable.connect("changed", self.on_source_table_changed)
        # Source SQL command
        self.scrolledWindow = Gtk.ScrolledWindow()
        self.scrolledWindow.set_vexpand(True)
        self.scrolledWindow.set_hexpand(False)
        self.queryField = Gtk.TextView()
        self.queryField.set_sensitive(False)
        self.scrolledWindow.add(self.queryField)
        #
        # self.fieldsLabel = Gtk.Label(label="Campos", halign=Gtk.Align.START)
        self.selectFieldsButton = Gtk.Button(label="Seleccionar campos")
        self.selectFieldsButton.connect("clicked", self.select_source_fields)
        self.selectFieldsButton.set_sensitive(False)

        self.viewDataButton = Gtk.Button(label="Visualizar datos")
        self.viewDataButton.connect("clicked", self.view_data)
        self.viewDataButton.set_sensitive(False)

        anotherGrid = Gtk.Grid(column_homogeneous=True, row_homogeneous=True, column_spacing=10, row_spacing=10)
        anotherGrid.attach(self.selectFieldsButton, 0, 0, 1, 1)
        anotherGrid.attach_next_to(self.viewDataButton, self.selectFieldsButton, Gtk.PositionType.RIGHT, 1, 1)        
        #
        self.selectedSourceFields = {}
        # Source grid
        sourceGrid = Gtk.Grid(column_homogeneous=True, row_homogeneous=False, column_spacing=10, row_spacing=10)
        
        sourceGrid.attach(self.sourceConnectionLabel, 0, 1, 1, 1)
        sourceGrid.attach_next_to(self.sourceConnectionUser, self.sourceConnectionLabel, Gtk.PositionType.RIGHT, 1, 1)
        sourceGrid.attach_next_to(self.sourceConnectionPassword, self.sourceConnectionUser, Gtk.PositionType.RIGHT, 1, 1)        
        sourceGrid.attach_next_to(self.sourceConnectButton, self.sourceConnectionPassword, Gtk.PositionType.RIGHT, 1, 1)
        
        sourceGrid.attach(self.sourceType1, 0, 3, 1, 1)
        sourceGrid.attach_next_to(self.sourceTable, self.sourceType1, Gtk.PositionType.RIGHT, 3, 1)
        sourceGrid.attach(self.sourceType2, 0, 4, 1, 1)
        sourceGrid.attach_next_to(self.scrolledWindow, self.sourceType2, Gtk.PositionType.RIGHT, 3, 1)

        #sourceGrid.attach(self.fieldsLabel, 0, 5, 1, 1)
        sourceGrid.attach_next_to(anotherGrid, self.scrolledWindow, Gtk.PositionType.BOTTOM, 3, 1)
        # Source box
        sourceBox = Gtk.Box(spacing=0)
        sourceBox.pack_start(sourceGrid, True, True, 20)

        #
        self.destinationLabel = Gtk.Label(halign=Gtk.Align.START)
        self.destinationLabel.set_markup("<b>Objeto de destino</b>")

        # Destination connection
        self.destinationConnectionLabel = Gtk.Label(label="Iniciar Sesion", halign=Gtk.Align.START)
        
        self.destinationConnectionUser = Gtk.Entry(placeholder_text="Usuario")
        self.destinationConnectionPassword = Gtk.Entry(placeholder_text="Contraseña")
        self.destinationConnectionPassword.set_visibility(False)        
        
        self.destinationConnectButton = Gtk.Button(label="Conectar")
        self.destinationConnectButton.connect("clicked", self.get_destination_connection)

        self.destinationTableLabel = Gtk.Label(label="Tabla", halign=Gtk.Align.START)
        # Destination tables
        self.destinationTable = Gtk.ComboBoxText()
        
        destinationGrid = Gtk.Grid(column_homogeneous=True, row_homogeneous=False, column_spacing=10, row_spacing=10)
        # destinationGrid.attach(self.destinationLabel, 0, 4, 1, 1)
        destinationGrid.attach(self.destinationConnectionLabel, 0, 1, 1, 1)
        destinationGrid.attach_next_to(self.destinationConnectionUser, self.destinationConnectionLabel, Gtk.PositionType.RIGHT, 1, 1)
        destinationGrid.attach_next_to(self.destinationConnectionPassword, self.destinationConnectionUser, Gtk.PositionType.RIGHT, 1, 1)        
        destinationGrid.attach_next_to(self.destinationConnectButton, self.destinationConnectionPassword, Gtk.PositionType.RIGHT, 1, 1)
        destinationGrid.attach(self.destinationTableLabel, 0, 2, 1, 1)
        destinationGrid.attach_next_to(self.destinationTable, self.destinationTableLabel, Gtk.PositionType.RIGHT, 3, 1)
        #Destination box
        destinationBox = Gtk.Box(spacing=0)
        destinationBox.pack_start(destinationGrid, True, True, 20)
        
        self.transformationLabel = Gtk.Label(halign=Gtk.Align.START)
        self.transformationLabel.set_markup("<b>Conversion</b>")
        self.conversionConfig = Gtk.Button(label="Configurar conversion de datos")
        self.conversionConfig.connect("clicked", self.configure)
        self.conversionConfig.set_sensitive(False)

        self.done = Gtk.Button(label="Ejecutar")
        self.done.connect("clicked", self.done_func)
        #
        #
        self.addButton = Gtk.Button(label="Agregar")
        self.addButton.connect("clicked", self.add_new)
        self.delButton = Gtk.Button(label="Eliminar")
        self.delButton.connect("clicked", self.delete)
        #
        buttonsGrid = Gtk.Grid(column_homogeneous=True, row_homogeneous=False, column_spacing=10, row_spacing=10)
        buttonsGrid.attach(self.addButton, 0, 0, 1, 1)
        buttonsGrid.attach_next_to(self.delButton, self.addButton, Gtk.PositionType.RIGHT, 1, 1)
        #
        self.list = Gtk.ScrolledWindow()
        self.list.set_vexpand(True)
        self.list.set_hexpand(False)
        self.listBox = Gtk.ListBox()
        self.listBox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        #
        self.list.add(self.listBox)
        self.listBox.connect("row-activated", self.on_list_change)
        #
        grid = Gtk.Grid(column_homogeneous=True, row_homogeneous=False, column_spacing=15, row_spacing=10)
        grid.attach(self.list, 0, 0, 1, 5)
        grid.attach_next_to(self.sourceLabel, self.list, Gtk.PositionType.RIGHT, 1, 1)
        grid.attach_next_to(sourceBox, self.sourceLabel, Gtk.PositionType.BOTTOM, 3, 1)
        grid.attach_next_to(self.destinationLabel, sourceBox, Gtk.PositionType.BOTTOM, 1, 1)
        grid.attach_next_to(destinationBox, self.destinationLabel, Gtk.PositionType.BOTTOM, 3, 1)
        grid.attach_next_to(self.transformationLabel, destinationBox, Gtk.PositionType.BOTTOM, 1, 1)
        grid.attach_next_to(self.conversionConfig, self.transformationLabel, Gtk.PositionType.BOTTOM, 3, 1)
        grid.attach_next_to(buttonsGrid, self.list, Gtk.PositionType.BOTTOM, 1, 1)
        grid.attach(self.done, 0, 6, 4, 1)
        #
        new = json.loads(self.get_new_format())
        self.data.append(new)
        row = Gtk.ListBoxRow()
        label = Gtk.Label('Tarea #1', halign=Gtk.Align.START)
        row.add(label)
        self.listBox.add(row)
        self.listBox.select_row(row)
        self.prevSelectedRow = self.listBox.get_selected_row()
        #
        self.add(grid)

    def on_source_table_changed(self, widget):
        self.selectedSourceFields = {}

    def configure(self, widget):
        conversionWin = ConversionWindow()
        conversionWin.show_all()

    def activate_table(self, widget, n):
        self.queryField.set_sensitive(False)
        self.sourceTable.set_sensitive(True)
        self.selectedSourceFields = {}

    def activate_query(self, widget, n):
        self.sourceTable.set_sensitive(False)
        self.queryField.set_sensitive(True)
        self.selectedSourceFields = {}

    def get_source_connection(self, widget):

        self.sourceTable.remove_all()
        
        if self.sourceConnectionUser.get_text() == '' and self.sourceConnectionPassword.get_text() == '':
            return None
        
        db = DBManager(self.sourceConnectionUser, self.sourceConnectionPassword)
        
        tables = db.get_user_tables()

        if tables is None:
            self.selectFieldsButton.set_sensitive(False)
            self.viewDataButton.set_sensitive(False)
            MessageDialogWindow("Error conectando a la base de datos")
            return None

        self.sourceTable.set_entry_text_column(0)
        for table in tables:
            self.sourceTable.append_text(table)

        self.selectFieldsButton.set_sensitive(True)
        self.viewDataButton.set_sensitive(True)
        
    def get_destination_connection(self, widget):
        
        self.destinationTable.remove_all()

        if self.destinationConnectionUser.get_text() == "" and self.destinationConnectionPassword.get_text() == "":
            return None
        
        db = DBManager(self.destinationConnectionUser, self.destinationConnectionPassword)
        
        tables = db.get_user_tables()

        if tables is None:
            MessageDialogWindow("Error conectando a la base de datos")
            self.conversionConfig.set_sensitive(False)
            return None

        self.destinationTable.set_entry_text_column(0)
        for table in tables:
            self.destinationTable.append_text(table)

    def view_data(self, widget):
        self.show_modal(1)

    def select_source_fields(self, widget):
        self.show_modal(0)

    def show_modal(self, action):
        if (
            (self.sourceTable.get_active_text() is None and self.sourceTable.get_sensitive()) or 
            (len(self.get_query_content()) == 0 and self.queryField.get_sensitive())
        ):
            return None
    
        isQuery = True
        source = self.get_query_content()

        if self.sourceTable.get_sensitive():
            isQuery = False
            source = self.sourceTable.get_active_text()

        if action == 0:
            FieldsWindow(self.sourceConnectionUser, self.sourceConnectionPassword, source, isQuery, self.selectedSourceFields).show_all()
            return None
        
        DataViewWindow(self.sourceConnectionUser, self.sourceConnectionPassword, source, isQuery, self.selectedSourceFields).show_all()
        
    def done_func(self, widget):
        # print(self.selectedSourceFields)
        print("TODO")

    def get_query_content(self):
        buffer = self.queryField.get_buffer()
        startIter, endIter = buffer.get_bounds()
        content = buffer.get_text(startIter, endIter, False)

        return content

    def add_new(self, e):
        row = Gtk.ListBoxRow()
        label = Gtk.Label("Tarea #%s"%(len(self.data) + 1), halign=Gtk.Align.START)
        row.add(label)
        self.listBox.add(row)

        new = json.loads(self.get_new_format())

        self.data.append(new)
        # print(self.data)

        self.listBox.show_all()

    def delete(self, e):
        current = self.listBox.get_selected_row()
        self.prevSelectedRow = None        
        self.data.pop(current.get_index())
        self.listBox.remove(current)
        self.listBox.show_all()

    def on_list_change(self, e, row):

        # if row.get_index() == self.prevSelectedRow.get_index():
            # return None
        if self.prevSelectedRow is not None:
            index = self.prevSelectedRow.get_index()
            
            self.data[index]["source"]["user"] = self.sourceConnectionUser.get_text()
            self.data[index]["source"]["password"] = self.sourceConnectionPassword.get_text()
            
            self.data[index]["source"]["type"] = '0' if self.sourceTable.get_sensitive() else '1'
        	
            self.data[index]["source"]["table"] = self.sourceTable.get_active()
            self.data[index]["source"]["fields"] = self.selectedSourceFields
            self.data[index]["source"]["query"] = self.get_query_content()

            self.data[index]["destination"]["user"] = self.destinationConnectionUser.get_text()
            self.data[index]["destination"]["password"] = self.destinationConnectionPassword.get_text()
            self.data[index]["destination"]["table"] = self.destinationTable.get_active()            
        
        self.prevSelectedRow = row
        
        self.show_current()

    def show_current(self):
        
        obj = self.data[self.listBox.get_selected_row().get_index()]

        # print(obj)
        
        source = obj["source"]

        self.sourceConnectionUser.set_text(source["user"])
        self.sourceConnectionPassword.set_text(source["password"])

        if int(source["type"]) == 0:
            self.sourceType1.set_active(1)
            
        if int(source["type"]) == 1:
            self.sourceType2.set_active(1)

        query = source["query"]
        textBuffer = Gtk.TextBuffer()
        textBuffer.set_text(query, len(query))
        self.queryField.set_buffer(textBuffer)

        #
        destination = obj["destination"]

        self.destinationConnectionUser.set_text(destination["user"])
        self.destinationConnectionPassword.set_text(destination["password"])
        #
        self.get_source_connection(self)
        self.get_destination_connection(self)
        #
        self.sourceTable.set_active(int(source["table"]))
        self.destinationTable.set_active(int(destination["table"]))
        #
        self.selectedSourceFields = source["fields"]        

    def get_new_format(self):
        return '{"source":{"type":"0","user":"","password":"","table":"-1","query":"","fields":"{}"},"destination":{"user":"","password":"","table":"-1"}}'

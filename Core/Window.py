import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from Core.ConversionWindow import ConversionWindow
from Core.DBManager import DBManager

class Window(Gtk.Window):
    def __init__(self):
        super().__init__(title="ETL")
        self.set_border_width(20)
        self.set_default_size(1100, 650)
        self.set_position(Gtk.WindowPosition.CENTER)

        # Source connection
        self.sourceConnectionLabel = Gtk.Label(label="Base de datos", halign=Gtk.Align.START)
        self.sourceConnectionEntry = Gtk.Entry()
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
        # Source SQL command
        self.scrolledWindow = Gtk.ScrolledWindow()
        self.scrolledWindow.set_vexpand(True)
        self.scrolledWindow.set_hexpand(False)
        self.queryField = Gtk.TextView()
        self.queryField.set_sensitive(False)
        self.scrolledWindow.add(self.queryField)
        # Source grid
        sourceGrid = Gtk.Grid(column_homogeneous=True, row_homogeneous=False, column_spacing=10, row_spacing=10)
        
        sourceGrid.attach(self.sourceConnectionLabel, 0, 1, 1, 1)
        sourceGrid.attach_next_to(self.sourceConnectionEntry, self.sourceConnectionLabel, Gtk.PositionType.RIGHT, 2, 1)
        sourceGrid.attach_next_to(self.sourceConnectButton, self.sourceConnectionEntry, Gtk.PositionType.RIGHT, 1, 1)
        
        sourceGrid.attach(self.sourceType1, 0, 3, 1, 1)
        sourceGrid.attach_next_to(self.sourceTable, self.sourceType1, Gtk.PositionType.RIGHT, 3, 1)
        sourceGrid.attach(self.sourceType2, 0, 4, 1, 1)
        sourceGrid.attach_next_to(self.scrolledWindow, self.sourceType2, Gtk.PositionType.RIGHT, 3, 1)
        # Source box
        sourceBox = Gtk.Box(spacing=0)
        sourceBox.pack_start(sourceGrid, True, True, 20)

        #
        self.destinationLabel = Gtk.Label(halign=Gtk.Align.START)
        self.destinationLabel.set_markup("<b>Objeto de destino</b>")

        # Destination connection
        self.destinationConnectionLabel = Gtk.Label(label="Base de datos", halign=Gtk.Align.START)
        self.destinationConnectionEntry = Gtk.Entry()
        self.destinationConnectButton = Gtk.Button(label="Conectar")
        self.destinationConnectButton.connect("clicked", self.get_destination_connection)

        self.destinationTableLabel = Gtk.Label(label="Tabla", halign=Gtk.Align.START)
        # Destination tables
        self.destinationTable = Gtk.ComboBoxText()
        
        destinationGrid = Gtk.Grid(column_homogeneous=True, row_homogeneous=False, column_spacing=10, row_spacing=10)
        # destinationGrid.attach(self.destinationLabel, 0, 4, 1, 1)
        destinationGrid.attach(self.destinationConnectionLabel, 0, 1, 1, 1)
        destinationGrid.attach_next_to(self.destinationConnectionEntry, self.destinationConnectionLabel, Gtk.PositionType.RIGHT, 2, 1)
        destinationGrid.attach_next_to(self.destinationConnectButton, self.destinationConnectionEntry, Gtk.PositionType.RIGHT, 1, 1)
        destinationGrid.attach(self.destinationTableLabel, 0, 2, 1, 1)
        destinationGrid.attach_next_to(self.destinationTable, self.destinationTableLabel, Gtk.PositionType.RIGHT, 3, 1)
        #Destination box
        destinationBox = Gtk.Box(spacing=0)
        destinationBox.pack_start(destinationGrid, True, True, 20)
        
        self.conversionConfig = Gtk.Button(label="Configurar conversion")
        self.conversionConfig.connect("clicked", self.configure)

        self.done = Gtk.Button(label="Enviar")
        self.done.connect("clicked", self.done_func)

        grid = Gtk.Grid(column_homogeneous=True, row_homogeneous=False, column_spacing=10, row_spacing=10)
        grid.attach(self.sourceLabel, 0, 1, 1, 1)
        grid.attach(sourceBox, 0, 2, 3, 1)
        grid.attach(self.destinationLabel, 0, 3, 1, 1)
        grid.attach(destinationBox, 0, 4, 3, 1)
        grid.attach(self.conversionConfig, 0, 5, 3, 1)
        grid.attach(self.done, 0, 6, 3, 1)

        self.add(grid)

    def configure(self, widget):
        conversionWin = ConversionWindow()

        conversionWin.show_all()

    def activate_table(self, widget, n):
        self.queryField.set_sensitive(False)
        self.sourceTable.set_sensitive(True)

    def activate_query(self, widget, n):
        self.sourceTable.set_sensitive(False)
        self.queryField.set_sensitive(True)

    def get_source_connection(self, widget):
        self.sourceTable.remove_all()

        db = DBManager("C##BD_BICICLETAS", "oracle", None)
        
        tables = db.get_user_tables()

        self.sourceTable.set_entry_text_column(0)
        for table in tables:
            self.sourceTable.append_text(table)
        
    def get_destination_connection(self, widget):
        self.destinationTable.remove_all()
        
        tables = ["xxx", "yyy"]
        self.destinationTable.set_entry_text_column(0)
        for table in tables:
            self.destinationTable.append_text(table)

    def done_func(self, widget):
        buffer = self.queryField.get_buffer()
        startIter, endIter = buffer.get_bounds()
        text = buffer.get_text(startIter, endIter, False)

        print(text)

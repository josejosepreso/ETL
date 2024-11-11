import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from Core.DBManager import DBManager
from Core.GUI.MessageDialogWindow import MessageDialogWindow

class DataView(Gtk.Window):
    def __init__(self, user, pswd, source, isQuery, selectedFields):
        super().__init__(title="Data")
        self.user = user
        self.pswd = pswd
        self.source = source
        self.isQuery = isQuery
        self.selectedFields = selectedFields

        db = DBManager(self.user, self.pswd)
    
        data = db.get_data(self.source, self.selectedFields, self.isQuery)
        
        fields = []
        for field in self.selectedFields:
            if int(self.selectedFields[field]) == 1:
                fields.append(field)

        if len(fields) == 0:
            self.destroy()
            return None

        self.set_border_width(20)
        self.set_default_size(750, 450)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_resizable(True)
        self.set_modal(True)

        self.dataListStore = Gtk.ListStore(*[str for i in range(0, len(fields))])
        for row in data:
            self.dataListStore.append([str(cell) for cell in row])

        self.treeview = Gtk.TreeView(model=self.dataListStore)
        for i, column_title in enumerate(fields):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            self.treeview.append_column(column)

        self.grid = Gtk.Grid()
        self.grid.set_column_homogeneous(True)
        self.grid.set_row_homogeneous(True)

        self.scrollableTreeList = Gtk.ScrolledWindow()
        self.scrollableTreeList.set_vexpand(True)
        self.scrollableTreeList.set_hexpand(True)

        self.scrollableTreeList.add(self.treeview)
        
        self.grid.add(self.scrollableTreeList)
        
        self.add(self.grid)

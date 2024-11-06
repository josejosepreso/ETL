from Core.GUI.Window import Window
from Core.GUI.Window import Gtk

def main():
    window = Window()
    window.connect("delete-event", Gtk.main_quit)
    window.show_all()
    
    Gtk.main()

if __name__ == "__main__":
    main()

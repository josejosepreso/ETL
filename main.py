from Core.Window import Window
from Core.Window import Gtk

def main():
    window = Window()
    window.connect("delete-event", Gtk.main_quit)
    window.show_all()
    
    Gtk.main()

if __name__ == "__main__":
    main()

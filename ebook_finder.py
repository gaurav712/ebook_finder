import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango, Gdk

from gigsebook import FetchData
from book_info import BookInfoWindow
from threading import Thread

EBOOK_FINDER_GLADE_FILE = "ebook_finder.glade"
#INFO_BOX_GLADE_FILE = "info_box.glade"

DEFAULT_PADDING = 2

class BookEntry:

    def __init__(self, book, parent_list_box, window):

        self.window = window
        self.book = book

        # horizontal info section
        self.year_label = Gtk.Label(label = self.book["year"])
        self.size_label = Gtk.Label(label = self.book["size"])
        self.pages_label = Gtk.Label(label = self.book["pages"])
        self.ext_label = Gtk.Label(label = self.book["extention"])
        self.language_label = Gtk.Label(label = self.book["language"])
        self.select_button = Gtk.Button(label = "→")
        self.select_button.connect("clicked", self.load_ebook_info)

        self.horizontal_info_section = Gtk.Box()
        self.horizontal_info_section.pack_start(self.language_label, False, False, DEFAULT_PADDING)
        self.horizontal_info_section.pack_start(self.year_label, False, False, DEFAULT_PADDING)
        self.horizontal_info_section.pack_start(self.size_label, False, False, DEFAULT_PADDING)
        self.horizontal_info_section.pack_start(self.pages_label, False, False, DEFAULT_PADDING)
        self.horizontal_info_section.pack_start(self.ext_label, False, False, DEFAULT_PADDING)
        self.horizontal_info_section.pack_end(self.select_button, False, False, DEFAULT_PADDING)

        # vertical info section
        self.title_label = Gtk.Label(label = self.book["title"])
        self.title_label.set_ellipsize(Pango.EllipsizeMode.START)
        self.title_label.set_xalign(-1)
        self.title_label.set_name("title_label")

        self.author_label = Gtk.Label(label = self.book["author"])
        self.author_label.set_ellipsize(Pango.EllipsizeMode.START)
        self.author_label.set_xalign(-1)

        self.publication_label = Gtk.Label(label = self.book["publication"])
        self.publication_label.set_xalign(-1)
        self.publication_label.set_name("publication_label")

        self.vertical_info_section = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        self.vertical_info_section.pack_start(self.title_label, False, False, DEFAULT_PADDING)
        self.vertical_info_section.pack_start(self.author_label, False, False, DEFAULT_PADDING)
        self.vertical_info_section.pack_start(self.publication_label, False, False, DEFAULT_PADDING)

        # now the horizontal section
        self.vertical_info_section.pack_start(self.horizontal_info_section, False, False, 10)

        # TODO: use glade template
        #self.builder = Gtk.Builder()
        #self.builder.new_from_file(INFO_BOX_GLADE_FILE)

        #self.info_text_section_box = self.builder.get_object("info_text_section_box")

        self.list_box_row = Gtk.ListBoxRow()
        self.list_box_row.add(self.vertical_info_section)
        #self.list_box_row.add(self.info_text_section_box)

        parent_list_box.add(self.list_box_row)

    def load_ebook_info(self, button):
        print(self.book["title"])
        self.window.set_visible(False)
        self.book_info_window = BookInfoWindow(self.book, self.make_window_visible)

    def make_window_visible(self):
        self.window.set_visible(True)

class EbookListWindow:

    def __init__(self, title):

        self.allow_input = True

        # to draw the root window using glade
        self.builder = Gtk.Builder()
        self.builder.add_from_file(EBOOK_FINDER_GLADE_FILE)

        # connect the signals
        self.builder.connect_signals(self)

        # set window title
        self.window = self.builder.get_object("root_window")
        self.window.set_title(title)

        # limit window size
        self.window.set_default_size(600, 450)
        self.window.set_resizable(False)

        # appear in center
        self.window.set_position(Gtk.WindowPosition.CENTER)

        # load style-sheet
        self.css_provider = Gtk.CssProvider()
        self.file = open("style.css", "rb")
        self.css_provider.load_from_data(self.file.read())
        self.file.close()
        self.context = Gtk.StyleContext()
        self.screen = Gdk.Screen.get_default()
        self.context.add_provider_for_screen(self.screen, self.css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        self.search_bar = self.builder.get_object("search_bar")
        self.search_entry = self.builder.get_object("search_entry")

        self.list_box = self.builder.get_object("list_box")

        self.list_box_row = Gtk.ListBoxRow()
        self.help_label = Gtk.Label()
        self.help_label.set_text("Start typing to search ebooks...")
        self.list_box_row.add(self.help_label)
        self.list_box.add(self.list_box_row)
        self.list_box.set_selection_mode(Gtk.SelectionMode.NONE)

        # reveal widgets
        self.window.show_all()

    def destroy_window(self, window):
        Gtk.main_quit()

    # pop up search_bar
    def reveal_search_bar(self, window, event):
        self.search_bar.handle_event(event)

    # initiate search
    def start_search(self, widget, event):
        
        # 65293 = Return
        if self.allow_input and event.keyval == 65293:
            self.query = self.search_entry.get_text()

            if self.query != "":
                print("Starting search with query: " + self.search_entry.get_text())
                self.allow_input = False
            else:
                return

            self.search_thread = StartSearch(self.query, self.list_box, self.list_box_row, self.window, self.reset_allow_input)
            self.search_thread.start()

    def reset_allow_input(self):
        self.allow_input = True

    # open info page
    def row_activated(self, list_box, row):
        print(row.get_index())

class StartSearch(Thread):

    def __init__(self, query, list_box, list_box_row, window, reset_allow_input):
        super().__init__();

        self.query = query
        self.list_box = list_box
        self.list_box_row = list_box_row
        self.window = window
        self.reset_allow_input = reset_allow_input

    def run(self):

        self.books = FetchData(self.query).data

        self.list_box.remove(self.list_box_row)

        for book in self.books:
            BookEntry(book, self.list_box, self.window)

        # refresh the window
        self.window.show_all()

        # allow to search now
        self.reset_allow_input()

ebookListWindow = EbookListWindow("Ebook Finder")
Gtk.main()

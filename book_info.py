import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf, Gio
from threading import Thread
from urllib3 import PoolManager
from bs4 import BeautifulSoup
from re import search
from subprocess import call

BOOK_INFO_GLADE_FILE = "book_info.glade"

class BookInfoWindow:
    
    def __init__(self, book, make_window_visible):

        self.book = book
        self.make_window_visible = make_window_visible

        # Create widgets from the Glade file
        self.builder = Gtk.Builder()
        self.builder.add_from_file(BOOK_INFO_GLADE_FILE)

        # Connect the signals
        self.builder.connect_signals(self)

        # To set the window title
        self.window = self.builder.get_object("root_window")
        self.window.set_title(self.book["title"])

        # limit window size
        self.window.set_default_size(600, 450)
        self.window.set_resizable(False)

        # appear in center
        self.window.set_position(Gtk.WindowPosition.CENTER)

        # Fill in rest of the widgets
        self.fill_widgets()

        # Show all widgets
        self.window.show_all()

    def fill_widgets(self):

        # title
        self.title_label = self.builder.get_object("title_label")
        self.title_label.set_text(self.book["title"])

        # author
        self.author_label = self.builder.get_object("author_label")
        self.author_label.set_text(self.book["author"])

        # publication
        self.publication_label = self.builder.get_object("publication_label")
        self.publication_label.set_text(self.book["publication"])

        # language
        self.language_label = self.builder.get_object("language_label")
        self.language_label.set_text(self.book["language"])

        # year
        self.year_label = self.builder.get_object("year_label")
        self.year_label.set_text(self.book["year"])

        # size
        self.size_label = self.builder.get_object("size_label")
        self.size_label.set_text(self.book["size"])

        # pages
        self.pages_label = self.builder.get_object("pages_label")
        self.pages_label.set_text(self.book["pages"])

        # extention
        self.ext_label = self.builder.get_object("ext_label")
        self.ext_label.set_text(self.book["extention"])

        # description
        self.description_label = self.builder.get_object("description_label")
        self.set_description = SetDescription(self.description_label, self.book["links"][0])
        self.set_description.start()

        # load image
        self.image_widget = self.builder.get_object('cover_image')
        self.load_cover = LoadCover(self.image_widget, self.book["links"][0])
        self.load_cover.start()

    def download_ebook(self, download_button):
        print("downloading ebook..")
        call(["firefox", self.book["links"][0]])

    #def mirror_changed(self, mirror_selection_combo_box):
        #print("mirror_changed")

    def destroy_window(self, window):
        #Gtk.main_quit()
        self.window.destroy()
        self.make_window_visible()

class LoadCover(Thread):
    
    def __init__(self, image_widget, url):
        super().__init__()

        self.image_widget = image_widget
        self.url = url

    def run(self):
        self.http = PoolManager()

        self.data = self.http.request('GET', self.url, preload_content=False)
        self.soup = BeautifulSoup(self.data.data, 'lxml')
        self.lines = str(self.soup.find_all('table')[0])
        self.match = search('"/covers/[0-9]/*.*.jpg"', self.lines)
        self.match = self.lines[(self.match.start() + 1):(self.match.end() - 1)]
        self.image_url = 'http://library.lol' + self.match

        print(self.image_url)
        self.image = self.http.request('GET', self.image_url, preload_content=False)

        self.loader = GdkPixbuf.PixbufLoader.new()
        self.loader.set_size(150, 200)
        self.loader.write(self.image.data)
        self.pixbuf = self.loader.get_pixbuf()
        self.loader.close()
        self.image_widget.set_from_pixbuf(self.pixbuf)

class SetDescription(Thread):
    def __init__(self, description_label, url):
        super().__init__()
        self.description_label = description_label
        self.url = url

    def run(self):
        self.http = PoolManager()
        self.data = self.http.request('GET', self.url)

        self.soup = BeautifulSoup(self.data.data, 'lxml')
        self.table_data = str(self.soup.find_all('table')[0])
        self.match = search('<div>Description:<br/>*.*</div>', self.table_data)
        self.description = self.table_data[(self.match.start() + 22):(self.match.end() - 5)]

        self.description_label.set_text(self.description)

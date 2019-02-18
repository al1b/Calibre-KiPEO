import re
from PyQt5.Qt import QAction, QInputDialog, QMessageBox
from css_parser.css import CSSRule

# The base class that all tools must inherit from
from calibre.gui2.tweak_book.plugin import Tool

from calibre import force_unicode
from calibre.gui2 import error_dialog
from calibre.ebooks.oeb.polish.container import OEB_DOCS, OEB_STYLES, serialize

from libpyarabicshaping import pyarabicshaping
from io import open

def reshape_book(container, verbose=False):
    for name, media_type in container.mime_map.iteritems():
        if media_type in OEB_DOCS:

            if(verbose):
                print('processing ' + name)

            # read file content
            oed_doc_file_name = container.name_to_abspath(name)
            oeb_doc_file = open(oed_doc_file_name, 'r', encoding='utf-8')
            oeb_doc_content = oeb_doc_file.read()
            oeb_doc_file.close()   

            # reshape and write the file
            oeb_doc_file = container.open(name, 'w')
            oeb_doc_content = pyarabicshaping.arabic_shape(oeb_doc_content)
            oeb_doc_file.write(oeb_doc_content)
            oeb_doc_file.close()
        

            # flag files as dirty
            container.dirty(name)
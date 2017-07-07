import re
from PyQt5.Qt import QAction, QInputDialog, QMessageBox
from cssutils.css import CSSRule

# The base class that all tools must inherit from
from calibre.gui2.tweak_book.plugin import Tool

from calibre import force_unicode
from calibre.gui2 import error_dialog
from calibre.ebooks.oeb.polish.container import OEB_DOCS, OEB_STYLES, serialize

from libpyarabicshaping import pyarabicshaping
from io import open

class KiPEOTool(Tool):
    name = 'KiPEOTool'
    allowed_in_toolbar = True
    allowed_in_menu = True

    def create_action(self, for_toolbar=True):
        ac = QAction(get_icons('images/icon.png'), 'Reshape book by KiPEO', self.gui) 
        if not for_toolbar:
            self.register_shortcut(ac, 'kipeo-tool', default_keys=('Ctrl+Shift+Alt+D',))
        ac.triggered.connect(self.start_reshape)
        return ac

    def start_reshape(self):
        # Ensure any in progress editing the user is doing is present in the container
        self.boss.commit_all_editors_to_container()
        try:
            self.reshape()
        except Exception:
            # Something bad happened report the error to the user
            import traceback
            error_dialog(self.gui, _('Failed to reshape fonts'), _(
                'Failed to reshape fonts, click "Show details" for more info'),
                det_msg=traceback.format_exc(), show=True)
            # Revert to the saved restore point
            self.boss.revert_requested(self.boss.global_undo.previous_container)
        # else:
        #     # Show the user what changes we have made, allowing her to
        #     # revert them if necessary
        #     self.boss.show_current_diff()
        #     # Update the editor UI to take into account all the changes we
        #     # have made
        #     self.boss.apply_container_update_to_gui()

    def reshape(self):
        self.boss.add_savepoint('Before: Reshape')

        container = self.current_container

        for name, media_type in container.mime_map.iteritems():
            if media_type in OEB_DOCS:
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
        
        self.show_success()
    
    def show_success(self):
        message = QMessageBox(self.gui)
        message.setIcon(QMessageBox.Information)
        message.setText("KiPEO has reshaped your e-book.\r\nWould you like to see what we have changed?")
        message.setWindowTitle("KiPEO")
        message.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        message.show()

        user_choice = message.exec_()
        if user_choice == QMessageBox.Yes:
            #Show the user what changes we have made, allowing her to
            #revert them if necessary
            self.boss.show_current_diff()
            #Update the editor UI to take into account all the changes we
            #have made
            self.boss.apply_container_update_to_gui()
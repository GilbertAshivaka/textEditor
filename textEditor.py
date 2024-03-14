import sys
from string import punctuation
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QTextEdit, QToolBar, QMessageBox, QFileDialog, QLabel, QDockWidget, QLineEdit, QFormLayout, QPushButton, QSizePolicy
from PyQt6.QtGui import QAction, QIcon, QTextDocument, QTextCursor
from pathlib import Path
from PyQt6.QtCore import QSize, Qt, QEvent


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowIcon(QIcon(r'C:\Users\Admin\PyQt\assets\icons8-pencil-48.png'))
        self.setGeometry(100, 100, 800, 400)

        self.title = 'Awsome Editor'
        self.filters = 'Text files (*.txt)'

        self.set_title()

        self.path = None

        self.text_editor = QTextEdit()
        self.text_editor.textChanged.connect(self.count_words)

        container = QWidget(self)
        container.setLayout(QVBoxLayout())
        container.layout().addWidget(self.text_editor)
        self.setCentralWidget(container)
        container.setContentsMargins(5, 5, 20, 5)
        

        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu('&File')
        edit_menu = menu_bar.addMenu('&Edit')
        help_menu = menu_bar.addMenu('&Help')


        #Adding new action to the window 
        new_action = QAction(QIcon(r'C:\Users\Admin\PyQt\assets\icons8-new-file-48.png'), '&New', self)
        new_action.setStatusTip('Create new document')
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.new_document)
        file_menu.addAction(new_action)

        open_action = QAction(QIcon(r'C:\Users\Admin\PyQt\assets\icons8-open-document-48.png'), '&Open...', self)
        open_action.setStatusTip('Open Existing document')
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_document)
        file_menu.addAction(open_action)

        save_action = QAction(QIcon(r'C:\Users\Admin\PyQt\assets\icons8-save-48.png'), '&Save', self)
        save_action.setStatusTip('Save document')
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_document)
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        #Search action 
        search_action = QAction(QIcon(r'C:\Users\Admin\PyQt\assets\icons8-search-40.png'), '&Search', self)
        search_action.setStatusTip('Search for a word in the document')
        search_action.setShortcut('Ctrl+F')
        search_action.triggered.connect(self.show_search_dock)

        #Exit action 
        exit_action = QAction(QIcon(r'C:\Users\Admin\PyQt\assets\icons8-logout-48.png'), '&Exit', self)
        exit_action.setStatusTip('Exit the program')
        exit_action.setShortcut('Alt+F4')
        exit_action.triggered.connect(self.close_event)
        file_menu.addAction(exit_action)


        #Edit menu
        undo_action = QAction(QIcon(r'C:\Users\Admin\PyQt\assets\icons8-undo-40.png'), '&Undo', self)
        undo_action.setShortcut('Ctrl+Z')
        undo_action.setStatusTip('Go to previous action')
        undo_action.triggered.connect(self.text_editor.undo)
        edit_menu.addAction(undo_action)


        redo_action = QAction(QIcon(r'C:\Users\Admin\PyQt\assets\icons8-redo-40.png'), '&Redo', self)
        redo_action.setShortcut('Ctrl+Y')
        redo_action.setStatusTip('Return to the undone action')
        redo_action.triggered.connect(self.text_editor.redo)
        edit_menu.addAction(redo_action)

        about_action = QAction(QIcon(r'C:\Users\Admin\PyQt\assets\icons8-info-48.png'), '&About', self)
        about_action.setShortcut('F1')
        about_action.setStatusTip('About')
        help_menu.addAction(about_action)

        toolbar = QToolBar('Toolbar')
        self.addToolBar(toolbar)
        toolbar.setIconSize(QSize(16, 16))

        #Adding Actions
        toolbar.addAction(new_action)
        toolbar.addAction(save_action)
        toolbar.addAction(open_action)
        toolbar.addSeparator()

        toolbar.addAction(undo_action)
        toolbar.addAction(redo_action)
        toolbar.addSeparator()

        toolbar.addAction(search_action)
        toolbar.addAction(exit_action)


        self.status_bar = self.statusBar()

        self.status_bar.showMessage('Ready', 5000)
        
        #A function to display the number of characters
        self.word_count = QLabel('Length: 0')
        self.status_bar.addPermanentWidget(self.word_count)


        self.dock = QDockWidget('Search')
        self.dock.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock)
        self.dock.setMinimumSize(200, 400)
        self.dock.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)

        search_form = QWidget()
        layout = QFormLayout(search_form)
        search_form.setLayout(layout)

        self.search_term = QLineEdit(search_form)
        self.search_term.setPlaceholderText('Enter term to search....')
        layout.addRow(self.search_term)

        btn_search = QPushButton('Go', clicked=self.search)
        layout.addRow(btn_search)
        
        #Adding the search form to the dockwidget
        self.dock.setWidget(search_form)
        self.dock.installEventFilter(self)
        


        self.show()

    def show_search_dock(self):
        self.dock.show()

    def search(self):  
        term = self.search_term.text().strip()
        if not term:
            return
        
        cur = self.text_editor.find(term)

        if not cur:
            QMessageBox.information(self, 'Term Not Found', f'The term "{term}" was not found.')
        
    
    def set_title(self, filename=None):
        title = f"{filename if filename else 'Untitled'}- {self.title}"
        self.setWindowTitle(title)

    
    def confirm_save(self):
        if not self.text_editor.document().isModified():
            return True 
        
        message = f"Do you want to save changes to {self.path if self.path else 'Untitled'}?"
        MsgBoxBtn = QMessageBox.StandardButton
        MsgBoxBtn = MsgBoxBtn.Save | MsgBoxBtn.Discard | MsgBoxBtn.Cancel

        button = QMessageBox.question(
            self,
            self.title,
            message,
            buttons=MsgBoxBtn
        )

        if button == MsgBoxBtn.Cancel:
            return False
        
        if button == MsgBoxBtn.Save:
            self.save_document()
        
        return True
    
    def new_document(self):
        if self.confirm_save():
            self.text_editor.clear()
            self.set_title()

    '''def write_document(self):
        self.path.write_text(self.text_editor.toPlainText())
        self.status_bar.showMessage('The document has been saved...', 3000)
    '''

    '''def save_document(self):
        if (self.path):
            return self.path.write_text(self.text_editor.toPlainText())
        
        filename, _ = QFileDialog.getSaveFileName(self, 'Save File', filter=self.filters)

        if not filename:
            return
        
        self.path = Path(filename)
        self.path.write_text(self.text_editor.toPlainText())
        self.status_bar.showMessage('The document has been saved...', 5000)
        self.set_title()
    '''
    
    def save_document(self):
        if self.path:
            self.path.write_text(self.text_editor.toPlainText())
            self.status_bar.showMessage('The document has been saved...', 3000)
        else:
            filename, _ = QFileDialog.getSaveFileName(self, 'Save File', filter=self.filters)
            if filename:
                self.path = Path(filename)
                self.path.write_text(self.text_editor.toPlainText())
                self.set_title()
                self.status_bar.showMessage('The document has been saved...', 3000)

    def open_document(self):
        filename, _ = QFileDialog.getOpenFileName(self, filter=self.filters)

        if filename:
            self.path = Path(filename)
            self.text_editor.setText(self.path.read_text())
            self.set_title(filename)
            

    '''def quit(self):
        self.confirm_save()
        self.destroy
    '''

    def close_event(self, event):
        if self.text_editor.document().isModified():
            reply = QMessageBox.question(self, 'Save Changes',
                                         'Do you want to save changes to the document?',
                                         QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard |
                                         QMessageBox.StandardButton.Cancel)

            if reply == QMessageBox.StandardButton.Save:
                self.save_document()
            elif reply == QMessageBox.StandardButton.Cancel:
                event.ignore()

    def closeEvent(self, event):
        self.close_event(event)

    
    def count_words(self):
        text = self.text_editor.toPlainText()
        for c in punctuation:
            text = text.replace(c, "")
        
        self.words =text.split()
        self.word_count.setText(f'{len(self.words)} WORDS')
        
    def width(self, obj, event):
        if obj ==self.dock and event.type() == QEvent.Type.Resize:
            print(f"Dock widget width is {self.dock.width}")
        return super().eventFilter(obj, event)



if __name__ == '__main__':
    try:
        import ctypes
        myappid = 'mycompany.myproduct.subproduct.version'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    finally:
        app = QApplication(sys.argv)
        window = MainWindow()
        sys.exit(app.exec())
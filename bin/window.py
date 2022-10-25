import os
from json import load
from PyQt5.QtWidgets import (
        QWidget,
        QMainWindow,
        QLabel,
        QGridLayout,
        QShortcut,
        QStatusBar
        )
from PyQt5.QtCore import Qt, pyqtSlot, QObject, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QPalette, QColor
from PIL import Image
from pynput import keyboard

import tree
import extensions

'''
TO DO:
    * Compatibility for markdown and text files
    * Test for fit_to_image - done
    * Checks for window params types, limits
    * Dir mode along with jump mode
    * Change pynput from GlobalHotKeys to single key events
    * Zoom in/out

    * Compatibility when current node is provided as full path - done
    * Add flags and tests for always_on_top, borderless_window - done
'''


class KeyListener(QObject):
    window_toggle_signal = pyqtSignal(bool)
    update_window_signal = pyqtSignal()

    def __init__(self, window):
        super(KeyListener, self).__init__()
        self.window = window

        self.key_window_toggle = self.window.config['key_window_toggle']
        self.key_window_exit = self.window.config['key_window_exit']
        self.key_up = self.window.config['key_up']
        self.key_down = self.window.config['key_down']
        self.key_left = self.window.config['key_left']
        self.key_right = self.window.config['key_right']

    def node_up(self):
        if self.window.window_visible is True:
            if self.window.current_node.level > 0:
                self.window.current_node = self.window.tree.get_node(
                        by='location',
                        node_level=self.window.current_node.level-1,
                        node_position=0
                        )
                self.update_window_signal.emit()

    def node_down(self):
        if self.window.window_visible is True:
            if self.window.current_node.level < self.window.tree_length - 1:
                self.window.current_node = self.window.tree.get_node(
                        by='location',
                        node_level=self.window.current_node.level+1,
                        node_position=0
                        )
                self.update_window_signal.emit()

    def node_right(self):
        if self.window.window_visible is True:
            if self.window.current_node.position < self.window.level_length - 1:
                self.window.current_node = self.window.tree.get_node(
                        by='location',
                        node_level=self.window.current_node.level,
                        node_position=self.window.current_node.position + 1
                        )
                self.update_window_signal.emit()

    def node_left(self):
        if self.window.window_visible is True:
            if self.window.current_node.position > 0:
                self.window.current_node = self.window.tree.get_node(
                        by='location',
                        node_level=self.window.current_node.level,
                        node_position=self.window.current_node.position - 1
                        )
                self.update_window_signal.emit()

    def window_exit(self):
        print('Exiting...')
        self.window.close()

    def window_toggle(self):
        if self.window.window_visible is False:
            self.window_toggle_signal.emit(True)
            self.window.window_visible = True
        else:
            self.window_toggle_signal.emit(False)
            self.window.window_visible = False

    def run(self):
        with keyboard.GlobalHotKeys({
            self.key_window_toggle: self.window_toggle,
            self.key_window_exit: self.window_exit,
            self.key_up: self.node_up,
            self.key_down: self.node_down,
            self.key_left: self.node_left,
            self.key_right: self.node_right}
                                    ) as listener:
            listener.join()


class Window(QMainWindow):
    def __init__(self, screen_size):
        super(Window, self).__init__()

        self.screen_size = screen_size

        # self.window_position_x = 0
        # self.window_position_y = 0
        self.file_type_state = 'file'

        self.load_config()
        self.clean_config()

        self.load_ui()

        self.init_tree()

        if (self.config["window_stays_on_top"] is True) and (self.config["window_borderless"] is True):
            self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        elif (self.config["window_borderless"] is True):
            self.setWindowFlags(Qt.FramelessWindowHint)
        elif (self.config["window_stays_on_top"] is True):
            self.setWindowFlags(Qt.WindowStaysOnTopHint)

        self.key_listener_thread = QThread()

        self.key_listener = KeyListener(self)
        self.key_listener.window_toggle_signal.connect(self.window_toggle)
        self.key_listener.update_window_signal.connect(self.window_update)
        self.key_listener.moveToThread(self.key_listener_thread)

        self.key_listener_thread.started.connect(self.key_listener.run)
        self.key_listener_thread.start()
        print('Running...')

        self.window_visible = False

    @pyqtSlot(bool)
    def window_toggle(self, signal_value):
        if signal_value is True:
            self.show()
        else:
            self.hide()

    @pyqtSlot()
    def window_update(self):
        self.update_node()

    def load_ui(self):
        self.widget = QWidget(self)

        self.layout = QGridLayout(self.widget)

        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)

        palette = QPalette()
        color = QColor(self.config['background_color'])
        palette.setColor(QPalette.Window, color)

        self.widget.setAutoFillBackground(True)
        self.widget.setPalette(palette)

        self.widget.setLayout(self.layout)

        self.setCentralWidget(self.widget)

        self.window_w = int((int(self.config['window_width'].strip('%'))/100) * self.screen_size.width())
        self.window_h = int((int(self.config['window_height'].strip('%'))/100) * self.screen_size.height())

    def load_config(self):
        config_file_path = os.path.join(os.path.dirname(__file__), 'config.json')
        with open(config_file_path, 'r') as config_file:
            self.config = load(config_file)

    def clean_config(self):
        temp_config = {}
        for key, value in self.config.items():
            if type(key) == str and type(value) == str:
                key = key.replace(' ', '')
                value = value.replace(' ', '')
            temp_config[key] = value
        self.config.clear()
        self.config = temp_config

    def init_tree(self):
        '''The function initiates the tree instance.
        Further it checks if the current_node is a valid image file'''

        self.tree = tree.Tree(self.config['starting_directory'])
        self.tree_length = len(self.tree.tree_dict.keys())

        if self.config['starting_directory'] != self.config['starting_node']:
            current_node = tree.clean(self.config["starting_node"], operation="get_root_node")
            self.current_node = self.tree.get_node(by='name', node_name=current_node)

            # starting_node has failed
            if self.current_node is None:
                print("Failed to find starting_node, running using starting_directory")
                current_node = tree.clean(self.config["starting_directory"], operation="get_root_node")
                self.current_node = self.tree.get_node(by='name', node_name=current_node)

            self.check_current_node()

            self.update_node()
            self.move_window()

        else:
            current_node = tree.clean(self.config["starting_directory"], operation="get_root_node")
            self.current_node = self.tree.get_node(by='name', node_name=current_node)

            self.check_current_node()

            self.update_node()
            self.move_window()

    def update_node(self):
        self.level_length = len(self.tree.tree_dict[f"level_{self.current_node.level}"])
        self.status_bar.showMessage(f"{self.current_node.name} [{self.current_node.position + 1}/{self.level_length}, {self.current_node.level + 1}/{self.tree_length}]")
        if self.current_node.type == "file":
            current_node_extension = os.path.splitext(self.current_node.name)[-1]

            if current_node_extension in extensions.image_extensions:
                # current_node_image = self.tree.get_node_path(self.current_node)
                current_node_image = self.current_node.path

                self.clear_layout()
                self.load_image(current_node_image)
                self.update_window()
                self.move_window()
                self.file_type_state = 'file'
        else:
            if self.file_type_state == 'file':
                self.clear_layout()
                self.update_window(operation='blank_window')
                self.move_window()
                self.file_type_state = 'dir'

    def update_window(self, operation=None):
        if operation == "blank_window" or self.config['fit_to_image'] is False:
            self.setFixedSize(self.window_w, self.window_h)
            # self.layout.setContentsMargins(self.config['image_margin'], self.config['image_margin'], self.config['image_margin'], self.config['image_margin'])

        elif self.config['fit_to_image']:
            self.setFixedSize(self.image.width, self.image.height)
            self.layout.setContentsMargins(self.config['image_margin'], self.config['image_margin'], self.config['image_margin'], self.config['image_margin'])

    def move_window(self, special=False):
        window_width = self.size().width()
        window_height = self.size().height()

        window_x = self.screen_size.width() - window_width
        window_y = self.screen_size.height() - window_height

        self.window_position_x = int((int(self.config['window_position_x'].strip('%'))/100) * window_x)
        self.window_position_y = int((int(self.config['window_position_y'].strip('%'))/100) * window_y)

        self.move(self.window_position_x, self.window_position_y)

    def load_image(self, image):
        self.label = QLabel()
        self.qpixmap = QPixmap(image)
        self.label.setPixmap(self.qpixmap)
        self.image = Image.open(image)
        self.layout.addWidget(self.label)

    def clear_layout(self):
        for i in reversed(range(self.layout.count())):
            self.layout.itemAt(i).widget().setParent(None)

    def check_current_node(self):
        if self.current_node is None:
            raise Exception("Current node is None")


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    import sys

    pyrefer_app = QApplication(sys.argv)

    screen = pyrefer_app.primaryScreen()
    screen_size = screen.availableGeometry()

    pyrefer_win = Window(screen_size)

    sys.exit(pyrefer_app.exec_())

import builtins
import inspect
import io
import keyword
import platform
import re
import sys
import os
import tempfile
import traceback
import threading
import subprocess
import types

import qdarkstyle
from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QFont, QColor, QTextCursor, QIcon, QStandardItem, \
    QStandardItemModel
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QTextEdit, QListWidget,
    QDockWidget, QStatusBar, QWidget, QVBoxLayout, QPushButton,
    QFileDialog, QHBoxLayout, QInputDialog, QMessageBox,
    QLineEdit, QListWidgetItem, QStyle, QPlainTextEdit, QComboBox, QLabel, QCompleter, QStyledItemDelegate
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject, QRegExp, QProcess, QTimer, QSettings, QStringListModel, \
    QAbstractListModel, QModelIndex, QRect, QSize

from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtGui import QTextCursor
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal, QObject

class VenvWorker(QObject):
    finished = pyqtSignal(str)  # передає повідомлення про завершення


    def __init__(self, venv_dir):
        super().__init__()
        self.venv_dir = venv_dir

    def run(self):
        import time, subprocess, shutil, os
        python_path = shutil.which("python") or shutil.which("python3")

        # Спеціальний флаг для Windows, щоб не відкривалось нове консольне вікно
        creation_flags = 0
        if os.name == 'nt':
            creation_flags = subprocess.CREATE_NO_WINDOW

        try:
            start = time.time()
            subprocess.check_call(
                ["py", "-m", "venv", self.venv_dir],
                creationflags=creation_flags
            )
            end = time.time()
            elapsed = round(end - start, 2)
            self.finished.emit(f"Venv створено за {elapsed} секунд.")
        except Exception as e:
            self.finished.emit(f"Помилка: {e}")


import keyword
import builtins
import traceback
import re
from PyQt5.QtWidgets import QTextEdit, QCompleter
from PyQt5.QtGui import QFont, QTextCursor
from PyQt5.QtCore import Qt
'''class SuggestionDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        text = index.data(Qt.DisplayRole)
        icon = index.data(Qt.DecorationRole)
        category = index.data(Qt.UserRole)

        painter.save()

        if option.state & QStyle.State_Selected:
            painter.fillRect(option.rect, QColor("#2a2d30"))
        else:
            painter.fillRect(option.rect, QColor("#21252b"))

        # Іконка
        if icon:
            icon_rect = QRect(option.rect.left() + 4, option.rect.top() + 4, 20, 20)
            icon.paint(painter, icon_rect)
            x_offset = 28
        else:
            x_offset = 4

        # Текст
        text_rect = QRect(option.rect.left() + x_offset, option.rect.top(), option.rect.width(), option.rect.height() // 2)
        painter.setPen(Qt.white)
        painter.setFont(QFont("Consolas", 12))
        painter.drawText(text_rect, Qt.AlignVCenter, text)

        # Category
        if category:
            cat_rect = QRect(option.rect.left() + x_offset, option.rect.top() + option.rect.height() // 2, option.rect.width(), option.rect.height() // 2)
            painter.setPen(QColor("#6c757d"))
            painter.setFont(QFont("Consolas", 10, QFont.StyleItalic))
            painter.drawText(cat_rect, Qt.AlignVCenter, category)

        painter.restore()

    def sizeHint(self, option, index):
        return QSize(200, 28)
class SuggestionModel(QAbstractListModel):
    def __init__(self, items, parent=None):
        super().__init__(parent)
        self.items = items

    def rowCount(self, parent=QModelIndex()):
        return len(self.items)

    def data(self, index, role):
        if not index.isValid():
            return None

        item = self.items[index.row()]

        if role == Qt.DisplayRole:
            return item.text
        elif role == Qt.DecorationRole:
            return item.icon
        elif role == Qt.UserRole:
            return item.category
        return None
def generate_suggestions():
    suggestions = []

    for word in keyword.kwlist:
        suggestions.append(SuggestionItem(word, "icons/keyword.svg", "keyword"))

    for name in dir(builtins):
        obj = getattr(builtins, name)
        if inspect.isclass(obj):
            suggestions.append(SuggestionItem(name, "icons/class.svg", "builtins class"))
        elif isinstance(obj, types.BuiltinFunctionType):
            suggestions.append(SuggestionItem(name, "icons/function.svg", "builtins function"))
        else:
            suggestions.append(SuggestionItem(name, "icons/variable.svg", "builtins"))
    return suggestions
class SuggestionItem:
    def __init__(self, text, icon_path=None, category=""):
        self.text = text
        self.icon_path = icon_path
        self.category = category'''
def get_icon_for_completion(name, user_functions, module_aliases, direct_imports):
    icon_path = None

    if name in user_functions:
        icon_path = "Icons/functions.png"
    elif name in direct_imports:
        for modname in module_aliases.values():
            if hasattr(modname, name):
                obj = getattr(modname, name)
                if inspect.isclass(obj):
                    icon_path = "Icons/class.png"
                elif inspect.isfunction(obj) or inspect.isbuiltin(obj):
                    icon_path = "Icons/functions.png"
                break
        if not icon_path:
            icon_path = "Icons/python.png"
    elif name in dir(builtins):
        obj = getattr(builtins, name, None)
        if inspect.isclass(obj):
            icon_path = "Icons/class.png"
        elif inspect.isbuiltin(obj):
            icon_path = "Icons/python.png"
        elif inspect.isfunction(obj):
            icon_path = "Icons/functions.png"
    else:
        for mod in module_aliases.values():
            if hasattr(mod, name):
                obj = getattr(mod, name)
                if inspect.isclass(obj):
                    icon_path = "Icons/class.png"
                elif inspect.isfunction(obj) or inspect.isbuiltin(obj):
                    icon_path = "Icons/functions.png"
                break

    return QIcon(icon_path) if icon_path and os.path.exists(icon_path) else QIcon()

class CodeTextEdit(QTextEdit):
    def __init__(self):
        super().__init__()

        self.setFont(QFont("Consolas", 14))
        self.setTabStopDistance(4 * self.fontMetrics().horizontalAdvance(' '))

        self.default_words = sorted(set(keyword.kwlist + dir(builtins)))
        self.user_functions = set()

        self.module_aliases = {}     # alias -> module object
        self.module_attributes = {}  # alias -> list of attributes (dir(module))
        self.direct_imports = set()  # names imported via 'from module import *'

        self.completer = QCompleter(self.default_words, self)
        self.completer.setWidget(self)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.activated.connect(self.insert_completion)

        popup = self.completer.popup()
        popup.setStyleSheet("""
            QListView {
                background-color: #2b2b2b;
                color: white;
                font-size: 16pt;
                selection-background-color: #555;
            }
        """)
        popup.setFont(QFont("Consolas", 16))

        self.last_completion_prefix = ""

        self.language = "python"

    def insert_completion(self, completion):
        tc = self.textCursor()
        prefix = self.last_completion_prefix

        if not prefix:
            tc.insertText(completion)
            self.setTextCursor(tc)
            return

        if '.' in prefix:
            left, right = prefix.rsplit('.', 1)
            replace_length = len(right)
        else:
            replace_length = len(prefix)

        for _ in range(replace_length):
            tc.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor)

        tc.removeSelectedText()
        tc.insertText(completion)
        self.setTextCursor(tc)

    def keyPressEvent(self, event):
        key = event.key()
        cursor = self.textCursor()

        # Якщо показано підказки
        if self.completer.popup().isVisible():
            if key in (Qt.Key_Up, Qt.Key_Down):
                return  # дозволити QCompleter обробити
            elif key in (Qt.Key_Enter, Qt.Key_Return, Qt.Key_Tab):
                index = self.completer.popup().currentIndex()
                if index.isValid():
                    completion = index.data()
                    self.insert_completion(completion)
                self.completer.popup().hide()
                return
            elif key == Qt.Key_Escape:
                self.completer.popup().hide()
                return

        # Автопари
        pairs = {'(': ')', '[': ']', '{': '}', '"': '"', "'": "'"}
        opening = event.text()
        if opening in pairs:
            cursor = self.textCursor()
            if cursor.hasSelection():
                selected = cursor.selectedText()
                cursor.insertText(opening + selected + pairs[opening])
                return
            else:
                super().keyPressEvent(event)
                cursor.insertText(pairs[opening])
                cursor.movePosition(QTextCursor.Left)
                self.setTextCursor(cursor)
                return

        # Видалення автопари
        if key == Qt.Key_Backspace:
            pos = cursor.position()
            if pos > 0:
                prev_char = self.document().characterAt(pos - 1)
                next_char = self.document().characterAt(pos)
                if prev_char in pairs and next_char == pairs[prev_char]:
                    cursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor)
                    cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, 2)
                    cursor.removeSelectedText()
                    return

        # Заміна Tab на пробіли
        if key == Qt.Key_Tab:
            cursor.insertText("    ")
            return

        super().keyPressEvent(event)

        # Оновити імена функцій та імпорти
        self.extract_function_names()
        self.parse_imports()

        prefix = self.text_under_cursor()
        self.last_completion_prefix = prefix

        if not prefix or not (prefix[-1].isalnum() or prefix[-1] == '.'):
            self.completer.popup().hide()
            return

        suggestions = self.get_suggestions(prefix)
        if len(prefix) >= 1 and suggestions:
            # Створюємо модель з іконками
            model = QStandardItemModel()

            for word in sorted(suggestions):
                item = QStandardItem(word)
                icon = get_icon_for_completion(word, self.user_functions, self.module_aliases, self.direct_imports)
                item.setIcon(icon)
                model.appendRow(item)

            self.completer.setModel(model)

            if '.' in prefix:
                _, right = prefix.rsplit('.', 1)
                self.completer.setCompletionPrefix(right)
            else:
                self.completer.setCompletionPrefix(prefix)

            popup = self.completer.popup()
            popup.setCurrentIndex(self.completer.completionModel().index(0, 0))
            cr = self.cursorRect()
            cr.setWidth(popup.sizeHintForColumn(0) + popup.verticalScrollBar().sizeHint().width())
            self.completer.complete(cr)
        else:
            self.completer.popup().hide()

    def text_under_cursor(self):
        cursor = self.textCursor()
        pos = cursor.position()
        text = self.toPlainText()[:pos]
        match = re.search(r'([\w_][\w\d_\.]*)$', text)
        return match.group(1) if match else ''

    def extract_function_names(self):
        lines = self.toPlainText().splitlines()
        new_funcs = set()
        for line in lines:
            if line.strip().startswith("def "):
                match = re.match(r'def (\w+)', line.strip())
                if match:
                    new_funcs.add(match.group(1))
        self.user_functions = new_funcs

    def parse_imports(self):
        lines = self.toPlainText().splitlines()
        self.module_aliases.clear()
        self.module_attributes.clear()
        self.direct_imports.clear()

        for line in lines:
            line = line.strip()
            try:
                if line.startswith("from ") and "import" in line:
                    parts = line.split()
                    module = parts[1]
                    mod = __import__(module, fromlist=['*'])
                    # Збираємо всі імпорти з цього модуля у direct_imports
                    for name in dir(mod):
                        self.direct_imports.add(name)

                elif line.startswith("import "):
                    imports = line.replace("import", "").strip().split(",")
                    for imp in imports:
                        imp = imp.strip()
                        if " as " in imp:
                            modname, alias = [x.strip() for x in imp.split(" as ")]
                            mod = __import__(modname)
                            self.module_aliases[alias] = mod
                            self.module_attributes[alias] = dir(mod)
                        else:
                            mod = __import__(imp)
                            self.module_aliases[imp] = mod
                            self.module_attributes[imp] = dir(mod)

            except Exception as e:
                print(f"[Import Error]: {e}\n{traceback.format_exc()}")

    def get_object_by_chain(self, chain):
        """
        За ланцюжком імен (список рядків) повертає Python-об'єкт (модуль, клас, функцію і т.д.)
        Якщо об'єкт не знайдено — повертає None.
        """
        if not chain:
            return None
        # Перший елемент — alias або імпортоване ім'я
        first = chain[0]

        # Перевіряємо псевдоніми модулів
        if first in self.module_aliases:
            obj = self.module_aliases[first]
        elif first in self.direct_imports:
            obj = getattr(builtins, first, None)
        else:
            obj = None

        # Проходимо по ланцюжку і шукаємо вкладені атрибути
        for attr in chain[1:]:
            if obj is None:
                return None
            try:
                obj = getattr(obj, attr)
            except AttributeError:
                return None
        return obj

    def get_attributes_chain(self, chain):
        """
        Повертає список атрибутів Python-об'єкта, визначеного ланцюжком імен.
        """
        obj = self.get_object_by_chain(chain)
        if obj is None:
            return []
        try:
            return dir(obj)
        except Exception:
            return []

    def get_suggestions(self, prefix):
        if self.language == "css":
            return []  # пропускаємо CSS тут

        # Якщо є крапки, ділимо на ланцюжок
        if '.' in prefix:
            parts = prefix.split('.')
            attrs = self.get_attributes_chain(parts[:-1])
            last_part = parts[-1]
            return [a for a in attrs if a.startswith(last_part)]

        # Якщо без крапок — пропонуємо ключові слова, функції, direct_imports та aliases
        all_words = self.default_words + list(self.user_functions) + list(self.direct_imports) + list(
            self.module_aliases.keys())
        return [w for w in all_words if w.startswith(prefix)]
    def get_suggestions(self, prefix):
        if self.language == "css":
            # Твій CSS код — опустимо тут для стислості
            return []

        all_words = self.default_words + list(self.user_functions) + list(self.direct_imports)

        if '.' in prefix:
            chain = prefix.split('.')
            attrs = self.get_attributes_chain(chain[:-1])
            last_part = chain[-1]
            return [a for a in attrs if a.startswith(last_part)]

        return [w for w in all_words if w.startswith(prefix)]




highlight_dict = {
    "purple": [name for name in dir(builtins) if callable(getattr(builtins, name))],
    "#C76738": keyword.kwlist,
    "#B1076C": [name for name in dir(object) if name.startswith('__') and name.endswith('__')],  # магічні методи
}

class SimpleHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.rules = []
        for color, words in highlight_dict.items():
            fmt = QTextCharFormat()
            fmt.setForeground(QColor(color))
            fmt.setFontWeight(QFont.Bold)
            for word in words:
                pattern = QRegExp(rf'\b{word}\b')
                self.rules.append((pattern, fmt))


        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#5CAA5B"))
        self.rules.append((QRegExp(r'"[^"\\]*(\\.[^"\\]*)*"'), string_format))
        self.rules.append((QRegExp(r"'[^'\\]*(\\.[^'\\]*)*'"), string_format))

        number_format = QTextCharFormat()
        number_format.setForeground(QColor(86, 156, 214))
        self.rules.append((QRegExp(r'\b\d+(\.\d+)?\b'), number_format))

        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#7A7E85"))
        self.rules.append((QRegExp(r'#.*'), comment_format))

        multiline_format = QTextCharFormat()
        multiline_format.setForeground(QColor("#4A7F62"))
        self.rules.append((QRegExp(r"'''[^']*'''"), multiline_format))
        self.rules.append((QRegExp(r'"""[^"]*"""'), multiline_format))

        # Формат для имени функции
        self.funcname_format = QTextCharFormat()
        self.funcname_format.setForeground(QColor(86, 156, 214))  # светло-синий

    def highlightBlock(self, text):
        # Спочатку підсвічуємо ім’я функції після def (до першої дужки)
        match = re.search(r'\bdef\s+([A-Za-z_]\w*)', text)
        if match:
            func_name = match.group(1)
            if not re.fullmatch(r'__\w+__', func_name):  # виключаємо дандери (__init__, __str__, ...)
                start = match.start(1)
                length = len(func_name)
                self.setFormat(start, length, self.funcname_format)

        # Потім застосовуємо всі інші правила
        for pattern, fmt in self.rules:
            index = pattern.indexIn(text)
            while index >= 0:
                length = pattern.matchedLength()
                if length > 0:
                    self.setFormat(index, length, fmt)
                index = pattern.indexIn(text, index + length)

# --- Клас для виконання Python коду у окремому потоці ---
class CodeExecutor(QObject):
    output_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)
    input_request_signal = pyqtSignal()
    finished_signal = pyqtSignal()

    def __init__(self, code, venv_path=None):
        super().__init__()
        self.code = code
        self.venv_path = venv_path  # шлях до venv/bin/python або venv\Scripts\python.exe
        self.process = None
        self.input_queue = []
        self._lock = threading.Lock()

    def send_input(self, text):
        with self._lock:
            if self.process and self.process.stdin:
                try:
                    self.process.stdin.write((text + '\n').encode())
                    self.process.stdin.flush()
                except Exception as e:
                    self.error_signal.emit(str(e))

    def run(self):
        def reader(stream, signal):
            for line in iter(stream.readline, b''):
                decoded = line.decode(errors='ignore')
                signal.emit(decoded)
                if 'input' in decoded.lower():
                    self.input_request_signal.emit()
            stream.close()

        python_executable = sys.executable  # за замовчуванням
        if self.venv_path:
            # Використовуємо python із venv
            if os.name == 'nt':
                python_executable = os.path.join(self.venv_path, 'Scripts', 'python.exe')
            else:
                python_executable = os.path.join(self.venv_path, 'bin', 'python')

        # Записуємо код у тимчасовий файл
        import tempfile
        with tempfile.NamedTemporaryFile('w', delete=False, suffix='.py') as tmpfile:
            tmpfile.write(self.code)
            tmp_path = tmpfile.name

        try:
            self.process = subprocess.Popen(
                [python_executable, tmp_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=0
            )

            threading.Thread(target=reader, args=(self.process.stdout, self.output_signal), daemon=True).start()
            threading.Thread(target=reader, args=(self.process.stderr, self.error_signal), daemon=True).start()

            self.process.wait()
        except Exception as e:
            self.error_signal.emit(str(e))
        finally:
            self.finished_signal.emit()

# --- Вбудований Python консольний вивід ---
class PythonConsole(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)

    def append_output(self, text):
        self.setReadOnly(False)
        self.moveCursor(self.textCursor().End)
        self.insertPlainText(text)
        self.setReadOnly(True)
        self.moveCursor(self.textCursor().End)


# --- Клас PowerShell терміналу з живим вводом/виводом ---
class PowerShellTerminal(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setStyleSheet("background-color: black; color: white; font-family: Consolas; font-size: 12pt;")
        layout.addWidget(self.output)

        self.input_line = QLineEdit()
        self.input_line.setPlaceholderText("Введіть команду та натисніть Enter")
        self.input_line.returnPressed.connect(self.send_command)
        layout.addWidget(self.input_line)

        self.process = QProcess(self)

        self.process.setProgram("powershell.exe")

        self.process.setArguments([
            "-NoExit",
            "-ExecutionPolicy", "Bypass",
            "-Command", f'cd "{os.getcwd()}"'
        ])

        self.process.setProcessChannelMode(QProcess.MergedChannels)
        self.process.readyReadStandardOutput.connect(self.read_output)
        self.process.started.connect(lambda: self.output.append("[PowerShell запущений]"))
        self.process.finished.connect(lambda code, status: self.output.append(f"[Завершено з кодом {code}]"))

        self.process.start()

    def read_output(self):
        try:
            output = self.process.readAllStandardOutput().data().decode("utf-8", errors="ignore")
            self.output.append(output)
            self.output.moveCursor(self.output.textCursor().End)  # Автоматично скролити вниз
        except Exception as e:
            self.output.append(f"<span style='color:red;'>[Output Error]: {e}</span>")

    def send_command(self, command=None):
        if command is None:
            command = self.input_line.text()
            self.input_line.clear()
        self.output.append(f"> {command}")

        if self.process.state() == QProcess.Running:
            try:
                self.process.write((command + '\n').encode("utf-8"))
            except Exception as e:
                self.output.append(f"<span style='color:red;'>[Error sending command]: {e}</span>")
        else:
            self.output.append("<span style='color:red;'>[Error]: PowerShell не запущений</span>")

    def set_working_directory(self, path):
        if self.process.state() == QProcess.Running:
            try:
                # Виконуємо команду зміни директорії у PowerShell/basн
                if platform.system() == "Windows":
                    self.process.write(f'cd "{path}"\n'.encode("utf-8"))
                else:
                    self.process.write(f'cd "{path}"\n'.encode("utf-8"))
                self.output.append(f"[Directory changed to]: {path}")
            except Exception as e:
                self.output.append(f"<span style='color:red;'>[Directory error]: {e}</span>")
        else:
            self.output.append("<span style='color:red;'>[Error]: Немає активного процесу PowerShell</span>")



# --- Головне вікно PyCharm-подібного IDE ---
class PyCharmClone(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyFlow")
        self.resize(1200, 800)
        self.current_folder = ""
        self.opened_files = {}
        self.current_opened_file = None
        self.executor_thread = None
        self.executor = None
        self.last_tab_index = -1

        self.code_te = None
        self.make_file_btn = None
        self.open_folder_btn = None
        self.fails_lw = None
        self.terminal_console_te = None
        self.terminal_console_le = None
        self.venv_path = None
        self.init_ui()

        self.watch_timer = QTimer()
        self.watch_timer.timeout.connect(self.check_for_file_changes)
        self.watch_timer.start(3000)  # кожні 3 секунди
        self.last_file_set = set()
    def init_ui(self):
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.save_previous_tab_on_switch)

        top_bar = QWidget()
        top_layout = QHBoxLayout(top_bar)

        run_btn = QPushButton("▶ Виконати код")
        run_btn.clicked.connect(self.run_code)

        self.make_file_btn = QPushButton("📄 Створити файл")
        self.make_file_btn.clicked.connect(self.create_new_file)

        self.open_folder_btn = QPushButton("📂 Відкрити папку")
        self.open_folder_btn.clicked.connect(self.open_folder)

        delete_btn = QPushButton("🗑️ Видалити")
        delete_btn.clicked.connect(self.delete_selected_item)

        self.settings = QSettings("MyCompany", "MyApp")

        self.theme_combo = QComboBox()
        self.theme_combo.addItems([
            "Світла",
            "Темна (QDarkStyle)",
            "Темна (Моя)",
            "Темна (VSCode)",
            "Темна (Solarized Dark)",
            "Темна (Monokai)",
            "Синя",
            "Червона",
            "Зелена"
        ])
        self.theme_combo.currentIndexChanged.connect(self.change_theme)
        top_layout.addWidget(QLabel("Тема:"))
        top_layout.addWidget(self.theme_combo)

        # Застосувати збережену тему
        saved_index = self.settings.value("theme_index", 0, int)
        self.theme_combo.setCurrentIndex(saved_index)
        self.change_theme(saved_index)

        top_layout.addWidget(run_btn)
        top_layout.addWidget(self.make_file_btn)
        top_layout.addWidget(self.open_folder_btn)
        top_layout.addWidget(delete_btn)
        top_layout.addStretch()

        top_container = QWidget()
        layout = QVBoxLayout(top_container)
        layout.addWidget(top_bar)
        layout.addWidget(self.tabs)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(top_container)

        self.fails_lw = QListWidget()
        self.fails_lw.itemDoubleClicked.connect(self.file_double_clicked)

        file_widget = QWidget()
        file_layout = QVBoxLayout(file_widget)
        file_layout.addWidget(self.fails_lw)

        self.file_explorer = QDockWidget("Project")
        self.file_explorer.setWidget(file_widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.file_explorer)

        self.bottom_tabs = QTabWidget()

        self.terminal = PowerShellTerminal()
        self.terminal_console_te = self.terminal.output
        self.terminal_console_le = self.terminal.input_line
        self.bottom_tabs.addTab(self.terminal, "PowerShell Terminal")

        self.python_console = PythonConsole()
        python_console_widget = QWidget()
        py_console_layout = QVBoxLayout(python_console_widget)

        self.python_console_input = QLineEdit()
        self.python_console_input.setPlaceholderText("Введіть input і натисніть Enter")
        self.python_console_input.returnPressed.connect(self.python_console_input_entered)
        self.python_console_input.hide()

        py_console_layout.addWidget(self.python_console)
        py_console_layout.addWidget(self.python_console_input)

        self.bottom_tabs.addTab(python_console_widget, "Python Console")

        self.terminal_dock = QDockWidget("Bottom")
        self.terminal_dock.setWidget(self.bottom_tabs)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.terminal_dock)

        self.setStatusBar(QStatusBar())

    def change_theme(self, index):
        self.settings.setValue("theme_index", index)

        if index == 0:
            self.setStyleSheet("")
        elif index == 1:
            self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        elif index == 2:
            self.setStyleSheet("""
                QWidget {
                    background-color: #2b2b2b;
                    color: #dcdcdc;
                    font-family: Consolas;
                    font-size: 14px;
                }
                QPushButton {
                    background-color: #3c3f41;
                    color: white;
                    border: 1px solid #555;
                    padding: 4px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #4c5052;
                }
                QLineEdit, QTextEdit, QPlainTextEdit {
                    background-color: #1e1e1e;
                    color: #dcdcdc;
                    border: 1px solid #555;
                }
                QListWidget {
                    background-color: #252526;
                    color: #d4d4d4;
                }
                
                QTabWidget::pane {
                    border-top: 2px solid #3c3c3c;
                }
                
                QTabBar::tab {
                    background: #2d2d2d;
                    color: #d4d4d4;
                    padding: 6px;
                    border: 1px solid #3c3c3c;
                    border-bottom: none;
                    min-width: 100px;
                }
                
                QTabBar::tab:selected {
                    background: #1e1e1e;
                    border-bottom: 2px solid #0e639c;
                }
                
                QTabBar::tab:hover {
                    background: #383838;
                }
                
                QLabel, QComboBox {
                    color: #d4d4d4;
                }
                
                QPushButton {
                    background-color: #0e639c;
                    color: white;
                    border-radius: 3px;
                    padding: 4px;
                }

            """)
        elif index == 3:
            self.setStyleSheet("""
                QWidget {
                    background-color: #1e1e1e;
                    color: #d4d4d4;
                    font-family: Consolas;
                    font-size: 12px;
                }
                
                QTabWidget::pane {
                    border: 1px solid #3c3c3c;
                    top: -1px;
                }
                
                QTabBar::tab {
                    background: #2d2d2d;
                    color: #b0b0b0;              /* світло-сірий, але читаємий */
                    padding: 6px 12px;
                    border: 1px solid #3c3c3c;
                    border-bottom: none;
                    min-width: 100px;
                }
                
                QTabBar::tab:selected {
                    background: #007acc;
                    color: white;                /* Білий текст на активній вкладці */
                    font-weight: bold;
                }
                
                QTabBar::tab:hover {
                    background: #3e3e3e;
                    color: #e0e0e0;              /* Яскравіший при наведенні */
                }
                
                QPushButton {
                    background-color: #0e639c;
                    color: white;
                    border-radius: 3px;
                    padding: 5px 10px;
                    border: 1px solid #3c3c3c;
                }
                
                QPushButton:hover {
                    background-color: #1177bb;
                }
                
                QComboBox, QLabel, QLineEdit {
                    color: #ffffff;
                    background-color: #2e2e2e;
                    padding: 4px;
                    border: 1px solid #3c3c3c;
                }
                
                QPlainTextEdit, QTextEdit {
                    background-color: #1e1e1e;
                    color: #dcdcdc;
                    border: 1px solid #3c3c3c;
                }
                
                QScrollBar:vertical, QScrollBar:horizontal {
                    background: #2d2d2d;
                    width: 10px;
                    margin: 0px;
                }
                
                QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
                    background: #555;
                    min-height: 20px;
                    border-radius: 5px;
                }
                
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
                QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                    background: none;
                    border: none;
                }
                
                /* Важливо: якщо Terminal і Python Console — вкладки в QTabWidget, то саме цей стиль їх покращує */
                QTabBar::tab {
                    font-size: 13px;
                    text-transform: none;
                }
                
                /* Якщо вони кнопки, додамо явний стиль: */
                QPushButton#terminalButton, QPushButton#pythonConsoleButton {
                    color: white;
                    font-weight: bold;
                    background-color: #007acc;
                    border: 1px solid #005a9e;
                }
                
                QPushButton#terminalButton:hover, QPushButton#pythonConsoleButton:hover {
                    background-color: #005a9e;
                }
            """)
        elif index == 4:
            self.setStyleSheet("""
                QWidget {
                    background-color: #002b36; /* base03 - дуже темний фон */
                    color: #839496; /* base0 - світло-сірий текст */
                    font-family: Consolas, "Courier New", monospace;
                    font-size: 12px;
                }
                
                QTabWidget::pane {
                    border: 1px solid #073642; /* base02 */
                    top: -1px;
                }
                
                QTabBar::tab {
                    background: #073642; /* base02 */
                    color: #93a1a1; /* base1 */
                    padding: 6px 12px;
                    border: 1px solid #586e75; /* base01 */
                    border-bottom: none;
                    min-width: 100px;
                }
                
                QTabBar::tab:selected {
                    background: #268bd2; /* blue */
                    color: #fdf6e3; /* base3 - дуже світлий текст */
                    font-weight: bold;
                }
                
                QTabBar::tab:hover {
                    background: #2aa198; /* cyan */
                    color: #eee8d5; /* base2 */
                }
                
                QPushButton {
                    background-color: #b58900; /* yellow */
                    color: #002b36; /* base03 - темний текст */
                    border-radius: 3px;
                    padding: 5px 10px;
                    border: 1px solid #657b83; /* base00 */
                    font-weight: bold;
                }
                
                QPushButton:hover {
                    background-color: #cb4b16; /* orange */
                    color: #fdf6e3; /* base3 */
                }
                
                QComboBox, QLabel, QLineEdit {
                    color: #839496; /* base0 */
                    background-color: #073642; /* base02 */
                    padding: 4px;
                    border: 1px solid #586e75; /* base01 */
                }
                
                QPlainTextEdit, QTextEdit {
                    background-color: #002b36; /* base03 */
                    color: #839496; /* base0 */
                    border: 1px solid #586e75; /* base01 */
                }
                
                QScrollBar:vertical, QScrollBar:horizontal {
                    background: #073642; /* base02 */
                    width: 10px;
                    margin: 0px;
                }
                
                QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
                    background: #586e75; /* base01 */
                    min-height: 20px;
                    border-radius: 5px;
                }
                
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
                QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                    background: none;
                    border: none;
                }
                
                /* Спеціальний стиль для вкладок Terminal і Python Console */
                QTabBar::tab {
                    font-size: 13px;
                }
                
                /* Кнопки Terminal і Python Console */
                QPushButton#terminalButton, QPushButton#pythonConsoleButton {
                    color: #002b36; /* base03 */
                    background-color: #268bd2; /* blue */
                    border: 1px solid #073642; /* base02 */
                    font-weight: bold;
                }
                
                QPushButton#terminalButton:hover, QPushButton#pythonConsoleButton:hover {
                    background-color: #2aa198; /* cyan */
                    color: #fdf6e3; /* base3 */
                }
            """)
        elif index == 5:
            self.setStyleSheet("""
                QWidget {
                    background-color: #272822;
                    color: #f8f8f2;
                    font-family: Consolas, "Courier New", monospace;
                    font-size: 12px;
                }
                
                QTabWidget::pane {
                    border: 1px solid #555753;
                    top: -1px;
                }
                
                QTabBar::tab {
                    background: #3e3d32;
                    color: #f8f8f2; /* світлий текст */
                    padding: 6px 12px;
                    border: 1px solid #555753;
                    border-bottom: none;
                    min-width: 100px;
                }
                
                QTabBar::tab:selected {
                    background: #f92672; /* яскраво-рожевий */
                    color: white;
                    font-weight: bold;
                }
                
                QTabBar::tab:hover {
                    background: #49483e;
                    color: #f8f8f2;
                }
                
                QPushButton {
                    background-color: #66d9ef; /* яскравий блакитний */
                    color: #272822;           /* темний текст */
                    border-radius: 3px;
                    padding: 5px 10px;
                    border: 1px solid #a6e22e;
                    font-weight: bold;
                }
                
                QPushButton:hover {
                    background-color: #a1efe4;
                }
                
                QComboBox, QLabel, QLineEdit {
                    color: #f8f8f2;
                    background-color: #3e3d32;
                    padding: 4px;
                    border: 1px solid #555753;
                }
                
                QPlainTextEdit, QTextEdit {
                    background-color: #272822;
                    color: #f8f8f2;
                    border: 1px solid #555753;
                }
                
                QScrollBar:vertical, QScrollBar:horizontal {
                    background: #3e3d32;
                    width: 10px;
                    margin: 0px;
                }
                
                QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
                    background: #75715e;
                    min-height: 20px;
                    border-radius: 5px;
                }
                
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
                QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                    background: none;
                    border: none;
                }
                
                /* Спеціальний стиль для вкладок Terminal і Python Console */
                QTabBar::tab {
                    font-size: 13px;
                    text-transform: none;
                }
                
                /* Якщо Terminal і Python Console - кнопки з такими objectName */
                QPushButton#terminalButton, QPushButton#pythonConsoleButton {
                    color: #272822; /* темний текст */
                    background-color: #f92672; /* яскравий рожевий */
                    border: 1px solid #ae015e;
                    font-weight: bold;
                }
                
                QPushButton#terminalButton:hover, QPushButton#pythonConsoleButton:hover {
                    background-color: #ae015e;
                    color: #f8f8f2;
            """)
        elif index == 6:  # Синя
            self.setStyleSheet("""
                QWidget {
                    background-color: #001f3f;
                    color: #cce6ff;
                    font-family: Consolas;
                    font-size: 12px;
                }
                
                QTabWidget::pane {
                    border: 1px solid #0074d9;
                }
                
                QTabBar::tab {
                    background: #003366;
                    color: #ffffff;
                    padding: 6px;
                    border: 1px solid #0074d9;
                    border-bottom: none;
                }
                
                QTabBar::tab:selected {
                    background: #0074d9;
                    color: white;
                    font-weight: bold;
                }
                
                QPushButton {
                    background-color: #0074d9;
                    color: white;
                    border-radius: 3px;
                    padding: 5px 10px;
                }
                
                QComboBox, QLabel {
                    color: white;
                    background-color: #003366;
                    border: 1px solid #0074d9;
                }
            """)
        elif index == 7:  # Червона
            self.setStyleSheet("""
                QWidget {
                    background-color: #330000;
                    color: #ffcccc;
                    font-family: Consolas;
                    font-size: 12px;
                }
                
                QTabWidget::pane {
                    border: 1px solid #990000;
                }
                
                QTabBar::tab {
                    background: #660000;
                    color: #ffffff;
                    padding: 6px;
                    border: 1px solid #990000;
                    border-bottom: none;
                }
                
                QTabBar::tab:selected {
                    background: #cc0000;
                    color: white;
                    font-weight: bold;
                }
                
                QPushButton {
                    background-color: #cc0000;
                    color: white;
                    border-radius: 3px;
                    padding: 5px 10px;
                }
                
                QComboBox, QLabel {
                    color: white;
                    background-color: #660000;
                    border: 1px solid #990000;
                }

            """)
        elif index == 8:  # Зелена
            self.setStyleSheet("""
                QWidget {
                    background-color: #002b00;
                    color: #ccffcc;
                    font-family: Consolas;
                    font-size: 12px;
                }
                
                QTabWidget::pane {
                    border: 1px solid #00cc00;
                }
                
                QTabBar::tab {
                    background: #004d00;
                    color: #ffffff;
                    padding: 6px;
                    border: 1px solid #00cc00;
                    border-bottom: none;
                }
                
                QTabBar::tab:selected {
                    background: #00cc00;
                    color: white;
                    font-weight: bold;
                }
                
                QPushButton {
                    background-color: #00cc00;
                    color: white;
                    border-radius: 3px;
                    padding: 5px 10px;
                }
                
                QComboBox, QLabel {
                    color: white;
                    background-color: #004d00;
                    border: 1px solid #00cc00;
                }
            """)

    def set_dark_theme(self):
        dark_stylesheet = """
        QWidget {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        QPlainTextEdit, QTextEdit, QLineEdit, QListWidget {
            background-color: #3c3f41;
            color: #ffffff;
        }
        QTabWidget::pane {
            border: 1px solid #444;
        }
        QTabBar::tab {
            background: #2b2b2b;
            color: #aaa;
            padding: 6px;
        }
        QTabBar::tab:selected {
            background: #3c3f41;
            color: #fff;
        }
        QPushButton {
            background-color: #555;
            border: 1px solid #888;
            padding: 5px;
        }
        QPushButton:hover {
            background-color: #666;
        }
        QComboBox {
            background-color: #3c3f41;
            color: #fff;
        }
        QComboBox QAbstractItemView {
            background-color: #3c3f41;
            selection-background-color: #2b2b2b;
        }
        QDockWidget {
            titlebar-close-icon: url(none);
            titlebar-normal-icon: url(none);
        }
        """
        self.setStyleSheet(dark_stylesheet)
    def delete_selected_item(self):
        selected_items = self.fails_lw.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "Інформація", "Оберіть файл або папку для видалення.")
            return

        selected_item = selected_items[0]
        name = selected_item.text()
        full_path = os.path.join(self.current_folder, name)

        if not os.path.exists(full_path):
            QMessageBox.warning(self, "Помилка", "Файл або папку не знайдено.")
            return

        confirm = QMessageBox.question(
            self, "Підтвердження", f"Ви справді хочете видалити '{name}'?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            try:
                if os.path.isdir(full_path):
                    import shutil
                    shutil.rmtree(full_path)
                else:
                    os.remove(full_path)
                self.refresh_file_list()
            except Exception as e:
                QMessageBox.warning(self, "Помилка", f"Не вдалося видалити:\n{e}")

    def python_console_input_entered(self):
        text = self.python_console_input.text()
        self.python_console_input.clear()
        self.python_console_input.setEnabled(False)
        self.python_console_input.hide()
        self.python_console.append_output(text + "\n")
        if self.executor:
            self.executor.send_input(text)

    def run_code(self):
        current_widget = self.tabs.currentWidget()
        if isinstance(current_widget, QTextEdit):
            self.code_te = current_widget
            code = self.code_te.toPlainText()
            if self.executor_thread and self.executor_thread.isRunning():
                QMessageBox.warning(self, "Попередження", "Вже виконується код!")
                return

            self.python_console.clear()
            self.python_console.append_output(">>> Виконання коду...\n")

            self.executor = CodeExecutor(code)
            self.executor_thread = QThread()
            self.executor.moveToThread(self.executor_thread)

            self.executor.output_signal.connect(self.python_console.append_output)
            self.executor.input_request_signal.connect(self.show_input_lineedit)
            self.executor.error_signal.connect(self.show_error)
            self.executor.finished_signal.connect(self.executor_thread.quit)

            self.executor_thread.started.connect(self.executor.run)
            self.executor_thread.finished.connect(self.execution_finished)

            self.executor_thread.start()

    def show_input_lineedit(self):
        self.python_console_input.setEnabled(True)
        self.python_console_input.show()
        self.python_console_input.setFocus()

    def show_error(self, text):
        self.python_console.append_output("\nПомилка:\n" + text + "\n")

    def execution_finished(self):
        self.python_console.append_output("\n>>> Виконання завершено\n")
        self.python_console_input.hide()
        self.python_console_input.setEnabled(False)

    def create_new_file(self):
        type_options = ["Python file (.py)", "Folder"]
        choice, ok = QInputDialog.getItem(self, "Тип об'єкта", "Що створити:", type_options, 0, False)
        if not ok:
            return

        name, ok = QInputDialog.getText(self, "Ім'я", "Введіть ім'я:")
        if not ok or not name:
            return

        selected_items = self.fails_lw.selectedItems()
        if selected_items:
            selected_item = selected_items[0]
            selected_name = selected_item.text()
            full_path = os.path.join(self.current_folder, selected_name)

            if os.path.isfile(full_path):
                QMessageBox.warning(self, "Помилка", "Виберіть папку для створення файлу")
                return

            target_path = os.path.join(full_path, name)
        else:
            target_path = os.path.join(self.current_folder, name)

        if choice.startswith("Python"):
            if not target_path.endswith(".py"):
                target_path += ".py"
            try:
                with open(target_path, "w", encoding="utf-8") as f:
                    f.write("# Новий файл\n")
                self.refresh_file_list()
            except Exception as e:
                QMessageBox.warning(self, "Помилка", f"Не вдалося створити файл:\n{e}")
        else:
            try:
                os.makedirs(target_path, exist_ok=True)
                self.refresh_file_list()
            except Exception as e:
                QMessageBox.warning(self, "Помилка", f"Не вдалося створити папку:\n{e}")

    def open_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Оберіть папку")
        if folder:
            self.current_folder = folder
            self.handle_venv_check(folder)
            self.refresh_file_list()

            self.terminal.set_working_directory(self.current_folder)
            self.last_file_set = set(os.listdir(self.current_folder))

            # ➕ Спроба активувати venv, якщо він існує
            activate_script = os.path.join(self.current_folder, "venv", "Scripts", "Activate.ps1")
            if os.path.isfile(activate_script):
                activate_command = f'. .\\venv\\Scripts\\Activate.ps1'
                self.terminal.send_command(activate_command)
    def refresh_file_list(self):
        self.fails_lw.clear()
        if not self.current_folder:
            return

        parent_folder = os.path.dirname(self.current_folder)
        if parent_folder and parent_folder != self.current_folder:
            parent_item = QListWidgetItem("..")
            parent_item.setIcon(self.style().standardIcon(QStyle.SP_DirIcon))
            self.fails_lw.addItem(parent_item)

        try:
            for item in sorted(os.listdir(self.current_folder), key=str.lower):
                list_item = QListWidgetItem(item)
                full_path = os.path.join(self.current_folder, item)
                if os.path.isdir(full_path):
                    list_item.setIcon(self.style().standardIcon(QStyle.SP_DirIcon))
                else:
                    list_item.setIcon(self.style().standardIcon(QStyle.SP_FileIcon))
                self.fails_lw.addItem(list_item)
        except Exception as e:
            QMessageBox.warning(self, "Помилка", f"Не вдалося відобразити файли:\n{e}")

    def file_double_clicked(self, item: QListWidgetItem):
        filename = item.text()
        if filename == "..":
            new_folder = os.path.dirname(self.current_folder)
            if new_folder and new_folder != self.current_folder:
                self.current_folder = new_folder
                self.refresh_file_list()
            return

        full_path = os.path.join(self.current_folder, filename)
        if os.path.isdir(full_path):
            self.current_folder = full_path
            self.refresh_file_list()
            return

        if os.path.isfile(full_path):
            if full_path in self.opened_files:
                index = self.tabs.indexOf(self.opened_files[full_path])
                self.tabs.setCurrentIndex(index)
                self.current_opened_file = full_path
            else:
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        text = f.read()
                except Exception as e:
                    QMessageBox.warning(self, "Помилка", f"Не вдалося відкрити файл:\n{e}")
                    return

                editor = CodeTextEdit()
                editor.setPlainText(text)
                self.highlighter = SimpleHighlighter(editor.document())
                editor.setObjectName("code_te")
                editor.setFont(QFont("Fonts/JetBrainsMono-Regular.ttf", 16))
                self.tabs.addTab(editor, os.path.basename(full_path))
                self.tabs.setCurrentWidget(editor)
                self.opened_files[full_path] = editor
                self.current_opened_file = full_path
                self.code_te = editor

    def close_tab(self, index):
        widget = self.tabs.widget(index)
        if not widget:
            return

        for path, editor in list(self.opened_files.items()):
            if editor == widget:
                try:
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(editor.toPlainText())
                except Exception as e:
                    QMessageBox.warning(self, "Помилка збереження", f"Не вдалося зберегти файл:\n{e}")
                del self.opened_files[path]
                if self.current_opened_file == path:
                    self.current_opened_file = None
                break

        self.tabs.removeTab(index)

        if self.tabs.count() > 0:
            self.last_tab_index = self.tabs.currentIndex()
        else:
            self.last_tab_index = -1

    def save_previous_tab_on_switch(self, current_index):
        if self.last_tab_index == -1:
            self.last_tab_index = current_index
            return

        prev_widget = self.tabs.widget(self.last_tab_index)
        if prev_widget:
            for path, editor in self.opened_files.items():
                if editor == prev_widget:
                    try:
                        with open(path, "w", encoding="utf-8") as f:
                            f.write(editor.toPlainText())
                    except Exception as e:
                        QMessageBox.warning(self, "Помилка збереження", f"Не вдалося зберегти файл:\n{e}")
                    break

        self.last_tab_index = current_index

    def handle_venv_check(self, folder_path):
        venv_dir = os.path.join(folder_path, "venv")
        if os.path.exists(venv_dir):
            self.venv_path = venv_dir

            # Активуємо venv у терміналі
            activate_script = os.path.join(self.current_folder, "venv", "Scripts", "Activate.ps1")
            if os.path.isfile(activate_script):
                activate_command = f'. .\\venv\\Scripts\\Activate.ps1'
                self.terminal.send_command(activate_command)

            return

        # Якщо нема venv, пропонуємо створити
        choice = QMessageBox.question(
            self,
            "Віртуальне середовище",
            f"У папці '{os.path.basename(folder_path)}' не знайдено 'venv'.\n"
            "Хочете створити нове середовище?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if choice == QMessageBox.Yes:
            self.create_new_venv(venv_dir)
        else:
            other_venv = QFileDialog.getExistingDirectory(self, "Оберіть існуюче venv середовище")
            if other_venv:
                self.venv_path = other_venv
                # Активуємо вибране venv
                activate_script = os.path.join(self.venv_path, "Scripts", "Activate.ps1")
                if os.path.isfile(activate_script):
                    activate_command = f'. "{activate_script}"'
                    self.terminal.send_command(activate_command)

    def create_new_venv(self, venv_dir):
        self.setEnabled(False)
        self.statusBar().showMessage("Створення віртуального середовища...")

        self.worker = VenvWorker(venv_dir)
        self.worker_thread = QThread()
        self.worker.finished.connect(self.on_venv_finished)
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.run)
        self.worker_thread.start()
        activate_script = os.path.join(self.current_folder, "venv", "Scripts", "Activate.ps1")
        if os.path.isfile(activate_script):
            activate_command = f'. .\\venv\\Scripts\\Activate.ps1'
            self.terminal.send_command(activate_command)
    def on_venv_finished(self, message):
        self.setEnabled(True)
        self.statusBar().clearMessage()
        QMessageBox.information(self, "Готово", message)

        self.worker_thread.quit()
        self.worker_thread.wait()

        # Автоматично активувати venv у терміналі
        activate_script = os.path.join(self.current_folder, "venv", "Scripts", "Activate.ps1")
        if os.path.isfile(activate_script):
            activate_command = f'. .\\venv\\Scripts\\Activate.ps1'
            self.terminal.send_command(activate_command)

    def check_for_file_changes(self):
        if not self.current_folder:
            return

        try:
            current_file_set = set(os.listdir(self.current_folder))
            if current_file_set != self.last_file_set:
                self.refresh_file_list()
                self.last_file_set = current_file_set
        except Exception as e:
            print(f"[watch error] {e}")  # або логувати в IDE
if __name__=="__main__":
    try:
        app = QApplication(sys.argv)
        #app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        window = PyCharmClone()
        window.show()
        window.fails_lw.setFont(QFont("Fonts/JetBrainsMono-Regular.ttf", 16))
        sys.exit(app.exec_())
    except Exception as e:
        print(e)

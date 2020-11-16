import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, \
    QRadioButton, QLabel, QFrame, QComboBox, QButtonGroup, QLineEdit, QFileDialog
from PyQt5.QtCore import QRect
from PyQt5 import QtGui
import random
import sqlite3
import xlrd


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def get_unique_data(topic_id, answer):
    con = sqlite3.connect('quiz_db.db')
    cur = con.cursor()
    query = "SELECT * FROM qa WHERE topic_id = (?) and question NOT LIKE (?) GROUP BY (question)"
    args = (topic_id, answer)
    res = cur.execute(query, args).fetchall()
    con.commit()
    con.close()

    return res


def get_result(topic_id, qa_list):
    con = sqlite3.connect('quiz_db.db')
    cur = con.cursor()
    for qa in qa_list:
        query = "INSERT INTO qa (question, answer, topic_id) VALUES (?,?,?)"
        args = (qa[0], qa[1], topic_id)
        cur.execute(query, args)
        con.commit()
    con.close()


def get_data(topic_id):
    con = sqlite3.connect('quiz_db.db')
    cur = con.cursor()
    res = cur.execute("SELECT * FROM qa WHERE topic_id = ?", [topic_id]).fetchall()
    con.commit()
    con.close()

    return res


def save_score(user_id, topic_id, result):
    con = sqlite3.connect('quiz_db.db')
    cur = con.cursor()
    query = "INSERT INTO scoreboard (user_id, topic_id, result) VALUES (?,?,?)"
    args = (user_id, topic_id, result)
    cur.execute(query, args)
    con.commit()
    con.close()


def get_topics(subject_id=1):
    con = sqlite3.connect('quiz_db.db')
    cur = con.cursor()
    query = "SELECT id, name FROM topic WHERE subject_id = ?"
    args = [subject_id]
    res = cur.execute(query, args).fetchall()
    con.commit()
    con.close()

    return res


class Welcome(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 650, 300)
        self.setWindowTitle('Тест')

        self.welcometext = QLabel(self)
        self.welcometext.setGeometry(QRect(150, -70, 350, 250))
        self.welcometext.setText('электронный тренажёр ')
        self.welcometext.setFont(QtGui.QFont('Segoe Script', 18, 450))

        self.description = QLabel(self)
        self.description.setGeometry(QRect(90, -30, 500, 250))
        self.description.setText('самосовершенствуйся с помощью тестов!')
        self.description.setFont(QtGui.QFont('Segoe Script', 15))

        self.startquiz = QPushButton('Начать тест', self)
        self.startquiz.resize(150, 40)
        self.startquiz.move(100, 225)
        self.startquiz.clicked.connect(self.startquiz_func)

        self.makequiz = QPushButton('Создать тест', self)
        self.makequiz.resize(150, 40)
        self.makequiz.move(400, 225)
        self.makequiz.clicked.connect(self.makequiz_func)

    def startquiz_func(self):
        self.cl = Start()
        self.cl.show()
        self.close()

    def makequiz_func(self):
        self.cl = CreateQuiz()
        self.cl.show()
        self.close()


class CreateQuiz(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 650, 300)
        self.setWindowTitle('Тест')

        self.safe = QPushButton('Выбрать файл', self)
        self.safe.setDisabled(True)
        self.safe.resize(100, 23)
        self.safe.move(70, 100)
        self.safe.clicked.connect(self.file_selector)

        self.name = QLabel(self)
        self.name.setGeometry(QRect(70, 20, 250, 70))
        self.name.setText('Введите название теста.')
        self.name.setFont(QtGui.QFont('Arial', 12))

        self.input_name = QLineEdit(self)
        self.input_name.move(70, 70)
        self.input_name.resize(150, 23)
        self.input_name.textChanged.connect(self.disableButton)

    def disableButton(self):
        if len(self.input_name.text()) > 0:
            self.safe.setDisabled(False)

    def file_selector(self):
        filename = QFileDialog.getOpenFileName(self, "Select File", "")
        self.get_data_from_file(filename[0])

    def get_data_from_file(self, file_name):
        con = sqlite3.connect('quiz_db.db')
        cur = con.cursor()
        query = "INSERT INTO topic (name, subject_id) VALUES (?,?)"
        args = (self.input_name.text(), 1)
        result = cur.execute(query, args)
        topic_id = result.lastrowid
        con.commit()
        con.close()

        questions = []
        wb = xlrd.open_workbook(file_name)
        sheet = wb.sheet_by_index(0)

        sheet.cell_value(0, 0)
        i = 0
        while i < sheet.nrows:
            questions.append([sheet.cell_value(i, 0), sheet.cell_value(i, 1)])
            i += 1
        get_result(topic_id, questions)


class Start(QWidget):
    def __init__(self, user_id=0):
        super().__init__()
        self.user_id = user_id
        self.setup()
        self.initUI()
        self.workspace = None

    def initUI(self):
        self.setGeometry(100, 100, 650, 300)
        self.setWindowTitle('Тест')

    def setup(self):
        self.greeting = QLabel(self)
        self.greeting.setGeometry(QRect(70, -70, 250, 250))
        self.greeting.setText('Введите своё имя.')
        self.greeting.setFont(QtGui.QFont('Arial', 12))

        self.input_first = QLineEdit(self)
        self.input_first.move(70, 70)
        self.input_first.resize(150, 23)

        self.safe = QPushButton('Сохранить', self)
        self.safe.resize(100, 23)
        self.safe.move(70, 100)
        self.safe.clicked.connect(self.login)

    def login(self):
        user_name = self.input_first.text()
        con = sqlite3.connect('quiz_db.db')
        cur = con.cursor()
        query = cur.execute("INSERT OR IGNORE INTO users (name) VALUES (?)", [user_name])
        con.commit()
        if query.lastrowid == 0:
            query = cur.execute("SELECT * FROM users WHERE name = (?)", [user_name]).fetchone()
            self.user_id = query[0]
        else:
            self.user_id = query.lastrowid
        con.close()

        self.close()
        self.workspace = SelectQuiz(self.user_id)
        self.workspace.show()


class SelectQuiz(QWidget):
    def __init__(self, user_id=0):
        super().__init__()
        self.user_id = user_id
        self.setup()
        self.initUI()
        self.workspace = None

    def initUI(self):
        self.setGeometry(100, 100, 650, 300)
        self.setWindowTitle('Тест')

    def setup(self):
        self.greeting = QLabel(self)
        self.greeting.setGeometry(QRect(70, 30, 250, 50))
        self.greeting.setText('Выберите нужный тест.')
        self.greeting.setFont(QtGui.QFont('Arial', 12))

        self.cb = QComboBox(self)
        self.cb.move(70, 80)
        self.cb.setPlaceholderText('Выбрать тест:')

        for i in get_topics():
            self.cb.addItem(i[1], i[0])

        self.cb.currentIndexChanged.connect(self.selectionchange)

    def selectionchange(self):
        topic_id = self.cb.currentData()
        self.close()
        self.workspace = Test(topic_id, self.user_id)
        self.workspace.show()


class Test(QWidget):
    def __init__(self, topic_id, user_id):
        super().__init__()
        self.initUI()
        self.button_group = QButtonGroup()
        self.step = 0
        self.user_answers = []
        self.topic_id = topic_id
        self.user_id = user_id
        self.length = len(get_data(self.topic_id))

        self.test(self.step)

    def initUI(self):
        self.setGeometry(100, 100, 650, 300)
        self.setWindowTitle('Тест')

        self.input_first = QLabel(self)
        self.input_first.setGeometry(QRect(50, -10, 250, 100))
        self.input_first.setText('Вопрос')
        self.input_first.setFont(QtGui.QFont('Arial', 13))

        self.own_result = QLabel(self)
        self.question = QLabel(self)
        self.question.move(50, 70)
        self.layout = QFrame(self)
        self.init_button()

    def test(self, step):
        a = 0
        j = 0

        data = get_data(self.topic_id)

        correct = data[step]

        self.question.setText(correct[2])
        self.question.setGeometry(QRect(50, 52, 600, 80))
        font = QtGui.QFont()
        font.setPointSize(13)
        self.question.setFont(font)
        self.question.setWordWrap(True)

        numbers = (self.length - 1 if self.length < 4 else 3)
        failed = random.sample(get_unique_data(self.topic_id, correct[1]), numbers)
        for i in random.sample(failed + [correct], numbers + 1):
            a += 30
            j += 1
            button_name = "radioButton" + str(j)
            button_name = QRadioButton(self.layout)
            if correct[0] != i[0]:
                self.button_group.addButton(button_name, correct[0])
            else:
                self.button_group.addButton(button_name, 0)

            button_name.setGeometry(QRect(50, 100 + a, 255, 17))
            button_name.setObjectName("radioButton" + str(j))
            button_name.setText(i[1])
            button_name.toggled.connect(self.get_answer)
            button_name.show()

        self.input_first.setText('Вопрос № ' + str(self.step + 1) + ' из ' + str(self.length))

    def get_answer(self):
        self.btn.setEnabled(True)

    def init_button(self):
        self.btn = QPushButton('Перейти к следующему вопросу.', self)
        self.btn.setEnabled(False)
        self.btn.resize(200, 40)
        self.btn.move(50, 250)
        self.btn.clicked.connect(self.validate)

    def validate(self):
        for children in self.button_group.buttons():
            if children.isChecked() and self.button_group.id(children) > 0:
                self.user_answers.append(self.button_group.id(children))
            children.hide()

        self.btn.setEnabled(False)
        self.step += 1

        if self.step < self.length:
            self.test(self.step)
        else:
            if self.user_answers:
                self.input_first.setText('Ошибки:')
                self.conclusion()
            else:
                self.input_first.setText('Ошибок нет. Молодец!')
                self.conclusion()

    def conclusion(self):
        con = sqlite3.connect('quiz_db.db')
        cur = con.cursor()
        query = cur.execute("SELECT * FROM qa WHERE id in (%s)" %
                            (', '.join(str(i) for i in self.user_answers))).fetchall()
        con.commit()
        con.close()

        result = 99 + ((self.length - len(self.user_answers) * 100) // self.length)
        save_score(self.user_id, self.topic_id, result)
        text = ''
        for i in query:
            text += i[1] + ' — ' + i[2] + '\n'

        self.own_result.setGeometry(QRect(50, 175, 275, 100))
        self.own_result.setText('Ваш результат составляет: ' + str(result) + '%')
        self.own_result.setFont(QtGui.QFont('Arial', 13))

        self.question.setText(text)
        self.question.move(50, 75)
        self.btn.setText('Вернуться на главную страницу.')
        self.btn.setEnabled(True)
        self.btn.clicked.connect(self.restart)

    def restart(self):
        self.cl = SelectQuiz(self.user_id)
        self.cl.show()
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Welcome()
    ex.show()
    sys.exit(app.exec_())

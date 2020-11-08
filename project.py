import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QRadioButton, QLabel, QFrame, QComboBox, QButtonGroup
from PyQt5.QtCore import QRect
from PyQt5 import QtGui
import random
import csv
import sqlite3
import time
# import chardet


# with open('quiz.csv', 'rb') as file:
#     r = chardet.detect(file.read())
#     print(r)

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def get_data_from_file():
    questions = []
    with open('quiz.csv', 'r', encoding='IBM866', errors='ignore') as file:
        file = csv.reader(file, delimiter=";")
        for i in file:
            questions.append(i)
    return questions


def get_result():
    con = sqlite3.connect('quiz_db.db')
    cur = con.cursor()
    for qa in get_data_from_file():
        query = "INSERT INTO qa (question, answer, topic_id) VALUES (?,?,?)"
        args = (qa[0], qa[1], 1)
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


def get_topics(subject_id=1):
    con = sqlite3.connect('quiz_db.db')
    # con.row_factory = dict_factory
    cur = con.cursor()
    query = "SELECT id, name FROM topic WHERE subject_id = ?"
    args = [subject_id]
    res = cur.execute(query, args).fetchall()
    con.commit()
    con.close()

    return res


class Start(QWidget):
    def __init__(self):
        super().__init__()
        self.setup()
        self.initUI()
        self.workspace = None

    def initUI(self):
        self.setGeometry(100, 100, 650, 300)
        self.setWindowTitle('Тест')

    def setup(self):
        self.cb = QComboBox(self)
        self.cb.move(50, 60)
        self.cb.setPlaceholderText('выберите тест:')
        for i in get_topics():
            self.cb.addItem(i[1], i[0])
        self.cb.currentIndexChanged.connect(self.selectionchange)

    def selectionchange(self):
        topic_id = self.cb.currentData()
        self.close()
        self.workspace = Example(topic_id)
        self.workspace.show()


class Example(QWidget):
    def __init__(self, topic_id):
        super().__init__()
        self.initUI()
        self.button_group = QButtonGroup()
        self.step = 1
        self.user_answers = []
        self.topic_id = topic_id

        self.length = len(get_data(topic_id))

        self.test(self.step)

    def initUI(self):
        self.setGeometry(100, 100, 650, 300)
        self.setWindowTitle('Тест')
        self.input_first = QLabel(self)
        self.input_first.setText('Вопрос:')
        self.input_first.move(50, 40)
        self.question = QLabel(self)
        self.question.move(50, 60)

        self.layout = QFrame(self)
        self.init_button()

    def test(self, step):
        a = 0
        j = 0

        data = get_data(self.topic_id)

        self.question.setText(data[step][2])
        self.question.setGeometry(QRect(50, 60, 600, 70))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.question.setFont(font)
        self.question.setWordWrap(True)

        numbers = (self.length - 1 if self.length < 4 else 3)
        correct = data[step]
        del data[step]
        failed = random.sample(data, numbers)
        for i in random.sample(failed + [correct], numbers + 1):
            a += 30
            j += 1
            button_name = "radioButton" + str(j)
            button_name = QRadioButton(self.layout)
            if correct[0] != i[0]:
                self.button_group.addButton(button_name, correct[0])
            button_name.setGeometry(QRect(50, 100 + a, 255, 17))
            button_name.setObjectName("radioButton" + str(j))
            button_name.setText(i[1])
            button_name.toggled.connect(self.get_answer)

            button_name.show()

    def get_answer(self):
        self.btn.setEnabled(True)

    def init_button(self):
        self.btn = QPushButton('->', self)
        self.btn.setEnabled(False)
        self.btn.resize(40, 40)
        self.btn.move(60, 250)
        self.btn.clicked.connect(self.validate)

    def validate(self):
        for children in self.layout.children():
            if children.isChecked() and self.button_group.id(children) > 0:
                self.user_answers.append(self.button_group.id(children))
                self.layout.setStyleSheet("border: 1px solid green;")
            else:
                self.layout.setStyleSheet("border: 1px solid red;")
            children.hide()
            # self.button_group.removeButton(children)

        self.btn.setEnabled(False)
        self.step += 1
        if self.step < self.length:
            self.test(self.step)
        else:
            # print(self.user_answers)
            self.conclusion()

    def conclusion(self):
        con = sqlite3.connect('quiz_db.db')
        cur = con.cursor()
        query = cur.execute("SELECT * FROM qa WHERE id in (%s)" % (', '.join(str(id) for id in self.user_answers))).fetchall()
        con.commit()
        con.close()
        text = ''
        for i in query:
            text += i[1] + ' — ' + i[2] + '\n'
        self.question.setText(text)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Start()
    ex.show()
    sys.exit(app.exec_())

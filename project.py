import csv
import chardet


# with open('quiz.csv', 'rb') as file:
#     r = chardet.detect(file.read())
#     print(r)

def get_data():
    questions = []
    with open('quiz.csv', 'r', encoding='IBM866', errors='ignore') as file:
        file = csv.reader(file, delimiter=";")
        for i in file:
            questions.append(i)
    return questions


import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QRadioButton, QLabel, QFrame
from PyQt5.QtCore import QRect
from PyQt5 import QtGui
import random


class Example(QWidget):
    def __init__(self):
        super().__init__()
        # self.initUI()
        # data = get_data()
        self.step = 1
        self.initUI()
        self.test(1)

    def initUI(self):
        self.setGeometry(100, 100, 650, 300)
        self.setWindowTitle('Миникалькулятор')
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
        data = get_data()

        self.question.setText(data[step][1])
        self.question.setGeometry(QRect(50, 60, 600, 70))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.question.setFont(font)
        self.question.setWordWrap(True)

        radioButton = QRadioButton(self.layout)
        radioButton.setGeometry(QRect(50, 220, 255, 17))
        radioButton.setObjectName("radioButton" + str(5))
        radioButton.setText(data[step][0])
        radioButton.toggled.connect(self.get_answer)
        radioButton.show()

        for i in random.sample(data, 3):
            a += 30
            j += 1
            buttonname = "radioButton" + str(j)
            buttonname = QRadioButton(self.layout)

            buttonname.setGeometry(QRect(50, 100 + a, 255, 17))
            buttonname.setObjectName("radioButton" + str(j))
            buttonname.setText(i[0])
            buttonname.toggled.connect(self.get_answer)
            buttonname.show()

    def get_answer(self):
        rbtn = self.sender()
        self.btn.setEnabled(True)
        if rbtn.isChecked():
            print(rbtn.text())

    def init_button(self):
        self.btn = QPushButton('->', self)
        self.btn.setEnabled(False)
        self.btn.resize(40, 40)
        self.btn.move(60, 250)
        self.btn.clicked.connect(self.validate)

    def validate(self):
        for children in self.layout.children():
            children.hide()
        self.btn.setEnabled(False)
        self.step += 1
        self.test(self.step)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec_())

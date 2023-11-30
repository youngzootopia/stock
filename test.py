from PyQt5.QtWidgets import *
import sys

if __name__ == '__main__': # 중복 방지를 위해 사용
    app = QApplication(sys.argv)

    for i in range(9999):
        print("process {} {}".format(sys.argv, i))

    app.exec_()

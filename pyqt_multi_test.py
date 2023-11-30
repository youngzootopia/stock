from PyQt5.QtCore import QProcess

process = QProcess()

process.setProgram("/test.py")

process.setArguments(QStringList() << "인수1" << "인수2" << "인수3")
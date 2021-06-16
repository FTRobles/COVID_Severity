from PyQt5 import QtWidgets

from views.ViewerMainWindow import ViewerMainWindow

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    main_window = ViewerMainWindow()

    main_window.show()
    sys.exit(app.exec_())

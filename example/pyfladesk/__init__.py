import sys
from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtWebEngineWidgets import QWebEngineView
import socket


class ApplicationThread(QtCore.QThread):
    def __init__(self, application, port=5000):
        super(ApplicationThread, self).__init__()
        self.application = application
        self.port = port

    def __del__(self):
        self.wait()

    def run(self):
        self.application.run(port=self.port, threaded=True)


class WebPage(QWebEnginePage):
    def __init__(self, root_url):
        super(WebPage, self).__init__()
        self.root_url = root_url

    def home(self):
        self.load(QtCore.QUrl(self.root_url))

    def acceptNavigationRequest(self, url, kind, is_main_frame):
        """Open external links in browser and internal links in the webview"""
        ready_url = url.toEncoded().data().decode()
        is_clicked = kind == self.NavigationType.NavigationTypeLinkClicked
        if is_clicked and self.root_url not in ready_url:
            QtGui.QDesktopServices.openUrl(url)
            return False
        return super(WebPage, self).acceptNavigationRequest(url, kind, is_main_frame)


def init_gui(application, port=0, width=800, height=600,
             window_title="PyFladesk", icon="appicon.png", argv=None):
    if argv is None:
        argv = sys.argv

    if port == 0:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('localhost', 0))
        port = sock.getsockname()[1]
        sock.close()

    # Application Level
    qtapp = QtWidgets.QApplication(argv)
    webapp = ApplicationThread(application, port)
    webapp.start()
    qtapp.aboutToQuit.connect(webapp.terminate)

    # Main Window Level
    window = QtWidgets.QMainWindow()
    window.resize(width, height)
    window.setWindowTitle(window_title)
    window.setWindowIcon(QtGui.QIcon(icon))

    # WebView Level
    webView = QWebEngineView(window)
    window.setCentralWidget(webView)

    # WebPage Level
    page = WebPage('http://localhost:{}'.format(port))
    page.home()
    webView.setPage(page)

    window.show()
    return qtapp.exec_()

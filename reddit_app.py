from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal, QObject, pyqtSlot, QTimer
import sys
import reddit
import urllib.request
import json
import codecs
import time
import functools


class getPostsThread(QObject):
    def __init__(self, subreddits):
        QObject.__init__(self)
        super(getPostsThread, self).__init__()
        self.subreddits = subreddits
        self.count = 0

    def _get_top_post(self, subreddit):
        url = "https://www.reddit.com/r/{}.json?limit=1".format(subreddit)
        headers = {'User-Agent': 'nikolak@outlook.com tutorial code'}
        request = urllib.request.Request(url, headers=headers)
        reader = codecs.getreader('utf-8')
        response = urllib.request.urlopen(request)
        data = json.load(reader(response))
        top_post = data['data']['children'][0]['data']
        return "'{title}' by {author} in {subreddit}".format(**top_post)

    add_post = pyqtSignal(str, name='add_post')
    ended = pyqtSignal(name='ended')

    def run(self):
        print("being called")
        if self.count < len(self.subreddits):
            top_post = self._get_top_post(self.subreddits[self.count])
            self.add_post.emit(top_post)
            self.count += 1
        else:
            self.ended.emit()
            self.count = 0


class MainWindow(QtWidgets.QMainWindow, reddit.Ui_MainWindow):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        self.btn_start.clicked.connect(self.start_getting_top_posts)
        self.thread = QThread()
        self.get_thread = None
        self.timer = QTimer(self)

    def start_getting_top_posts(self):
        self.list_submissions.clear()

        subreddit_list = str(self.edit_subreddits.text()).split(',')
        if subreddit_list == ['']:  # since ''.split(',') == [''] we use that to check
            QtWidgets.QMessageBox.critical(self, "No subreddits",
                                           "You didn't enter any subreddits.",
                                           QtWidgets.QMessageBox.Ok)
            return

        self.progress_bar.setMaximum(len(subreddit_list))
        self.progress_bar.setValue(0)

        self.get_thread = getPostsThread(subreddit_list)
        self.get_thread.moveToThread(self.thread)

        self.get_thread.add_post.connect(self.add_post)
        self.get_thread.ended.connect(self.done)

        self.btn_stop.clicked.connect(self.done)

        self.thread.start()

        self.timer.timeout.connect(self.get_thread.run)
        self.timer.start(2000)  # 2 seconds

        self.btn_stop.setEnabled(True)

        self.btn_start.setEnabled(False)

    def add_post(self, post_text):
        self.list_submissions.addItem(post_text)
        self.progress_bar.setValue(self.progress_bar.value() + 1)

    def done(self):
        self.timer.stop()
        self.btn_stop.setEnabled(False)
        self.btn_start.setEnabled(True)
        self.progress_bar.setValue(0)
        QtWidgets.QMessageBox.information(self, "Done!", "Done fetching posts!")
        self.thread.quit()
        self.thread.wait()


def main():
    app = QtWidgets.QApplication(sys.argv)
    form = MainWindow()
    form.show()
    app.exec_()


if __name__ == '__main__':
    main()

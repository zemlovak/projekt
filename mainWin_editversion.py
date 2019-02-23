import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QSizePolicy, QPushButton,\
QFileDialog, QLabel, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout
from PyQt5.QtCore import Qt, pyqtSignal

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter

from filterWin import Filtrace


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.left = 10
        self.top = 10
        self.title = 'XRD data processing'
        self.width = 720
        self.height = 540

        self.layout = QVBoxLayout(self)

        self.button1 = QPushButton('Open file', self)
        self.label1 = QLabel('', self)

        self.tabs = QTabWidget(self)

        # setting the main tab
        self.tab1 = QWidget()
        self.label2 = QLabel('Specify theta', self)
        self.kanal = QLineEdit('', self)
        self.button2 = QPushButton('Next', self)
        self.m = PlotCanvas(self, width=6.9, height=2.5)
        self.m.move(15, 40)
        self.tools = NavigationToolbar(self.m, self)
        self.tools.move(15, 500)
        self.tools.resize(400, 30)

        # setting the secondary tab
        #self.tab2 = QWidget()
        #self.m2 = PlotCanvas(self, width=6.9, height=2.5)
        #self.m2.move(15, 40)
        #self.tools2 = NavigationToolbar(self.m2, self)
        #self.tools2.move(15, 500)
        #self.tools2.resize(400, 30)

        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setMaximumSize(720, 540)

        self.button1.setToolTip('Click to open data file')
        self.button1.move(5, 7)
        self.button1.resize(90, 26)
        self.button1.clicked.connect(self.file_fcn)

        self.label1.move(100, 6)
        self.label1.setText(" Current file:  None ")
        self.label1.setMinimumWidth(600)
        self.label1.setMaximumHeight(27)

        ## tabs
        self.tabs.resize(710, 500)
        self.tabs.move(5, 38)
        self.tabs.addTab(self.tab1, " Main ")
        #txt = " Theta "
        #self.tabs.addTab(self.tab2, txt)

        ## main tab
        self.button2.move(630, 501)
        self.button2.resize(75, 27)
        self.button2.clicked.connect(self.btn_fcn)

        self.label2.move(430, 500)
        self.label2.resize = (48, 27)

        self.kanal.setToolTip('Enter theta value')
        self.kanal.move(525, 500)
        self.kanal.resize(100, 30)

        self.buttons_layout = QHBoxLayout(self)
        self.buttons_layout.addWidget(self.button2)
        self.buttons_layout.addWidget(self.tools)
        self.buttons_layout.addWidget(self.label2)
        self.buttons_layout.addWidget(self.kanal)

        self.tab1.layout = QGridLayout(self)
        self.tab1.layout.addWidget(self.m)
        self.tab1.setLayout(self.tab1.layout)



        # secondary tab
        #self.tab2.layout = QGridLayout(self)
        #self.tab2.layout.addWidget(self.m2)
        #self.tab2.layout.addWidget(self.tools2)
        #self.tab2.setLayout(self.tab2.layout)

        ##
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

        self.show()

    def file_fcn(self):
        options = QFileDialog.Options()
        self.fileName, _ = QFileDialog.getOpenFileName(self, "Otevřít soubor - zpracování XRD dat", "",
                                                       "Data Files (*.dat);;All Files (*)", options=options)
        if self.fileName:
            self.data = np.genfromtxt(self.fileName)
            self.label1.setText(" Current file:   " + str(self.fileName))
            self.show()
            self.m.plotit(self.data)
        else:
            print("Error: File not selected")

    def btn_fcn(self):
        try:
            k = int(self.kanal.text())

        except ValueError:
            print("Not a number")

        self.my_channel = k
        self.newWin(self.data, self.my_channel)

    def newWin(self, data, channel):
        self.data = data
        self.my_channel = channel
        newWindow = Filtrace(data, channel, self)
        newWindow.show()


class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None, width=6.9, height=3.2, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def plotit(self, data_plt):
        self.data = data_plt
        ax = self.figure.add_subplot(111)
        ax.plot(data_plt)
        ax.autoscale(enable=True, axis='x, y', tight=bool)
        row = data_plt.shape[0]
        col = data_plt.shape[1]
        data_plt = data_plt[:, 7:col]
        x = np.arange(0, col - 7, 1)
        y = np.arange(0, row, 1)

        ax = self.figure.gca(projection='3d')
        x, y = np.meshgrid(x, y)
        surf = ax.plot_surface(x, y, data_plt, cmap=cm.gist_stern, linewidth=0, antialiased=False, vmin=np.amin(data_plt), vmax=np.amax(data_plt))

        self.figure.colorbar(surf)

        ax.set_xlabel('Theta (deg)')
        ax.set_ylabel('Time (s)')
        ax.set_zlabel('Intensity ()')

        self.draw()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTimer, QCoreApplication, QSize, Qt, QRect
from PyQt5.QtWidgets import (
    QMainWindow,
    QAction,
    QLabel,
    QPushButton,
    QRadioButton,
    QSpacerItem,
    QSizePolicy,
    QDoubleSpinBox,
    QSpinBox,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QMenuBar,
    QStatusBar,
    QMenu,
    QLineEdit,
    QProgressBar,
    QListWidget,
    QListWidgetItem,
    QAbstractItemView,
    QListView,
)

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from fgdosProcedure import fgdosProcedure
from dataLogger import dataLogger

# import pyqtgraph as pg
# from dvg_pyqtgraph_threadsafe import BufferedPlotCurve
SERIAL_PORT = "COM5"


class MainWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.setupUi()
        self.measurement_running = False
        self.app = app

    from gui_core_fgdos import (
        populate_serial_ports,
        set_plot,
        unset_plot,
        update_adc_measurement,
        update_plot,
        save_settings,
        load_settings,
        set_sensor,
        clear_message,
    )

    def setupUi(self):
        self.setObjectName("FGDOS GUI")
        self.resize(800, 800)
        self.actionSave = QAction(self)  # Provide appropriate text and parent widget
        self.actionSave.setObjectName("actionSave")
        self.actionLoad = QAction(self)  # Provide appropriate text and parent widget
        self.actionLoad.setObjectName("actionLoad")
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setEnabled(True)
        self.centralwidget.setContextMenuPolicy(QtCore.Qt.PreventContextMenu)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.mainFrame = QtWidgets.QFrame(self.centralwidget)
        self.mainFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.mainFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.mainFrame.setObjectName("mainFrame")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.mainFrame)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horLaySetADC = QtWidgets.QHBoxLayout()
        self.horLaySetADC.setObjectName("horLaySetADC")

        font = QtGui.QFont()
        font.setPointSize(10)

        self.labelADC = QLabel(self.mainFrame)
        self.labelADC.setObjectName("labelADC")

        self.horLaySetADC.addWidget(self.labelADC)

        self.setPlotOn = QPushButton(self.mainFrame)
        self.setPlotOn.setObjectName("setPlotOn")

        self.horLaySetADC.addWidget(self.setPlotOn)

        self.setPlotOff = QPushButton(self.mainFrame)
        self.setPlotOff.setObjectName("setPlotOff")

        self.horLaySetADC.addWidget(self.setPlotOff)

        self.radioADC = QRadioButton(self.mainFrame)
        self.radioADC.setObjectName(u"radioADC")
        self.radioADC.setChecked(True)
        self.radioADC.setCheckable(True)
        self.horLaySetADC.addWidget(self.radioADC)

        self.radioSMU = QRadioButton(self.mainFrame)
        self.radioSMU.setObjectName(u"radioSMU")
        self.radioSMU.setCheckable(True)
        self.radioSMU.setVisible(False)  ############################ HIDE RADIO SMU

        self.horLaySetADC.addWidget(self.radioSMU)

        self.labelNPLC = QLabel(self.mainFrame)
        self.labelNPLC.setObjectName(u"labelNPLC")
        self.labelNPLC.setVisible(False)  ############################ HIDE LABEL NPLC

        self.horLaySetADC.addWidget(self.labelNPLC)

        self.lineNPLC = QLineEdit(self.mainFrame)
        self.lineNPLC.setObjectName(u"lineNPLC")
        self.lineNPLC.setMaximumSize(QSize(40, 16777215))
        self.lineNPLC.setVisible(False)  ############################ HIDE LINE NPLC

        self.horLaySetADC.addWidget(self.lineNPLC)


        self.horizontalSpacerPlot = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horLaySetADC.addItem(self.horizontalSpacerPlot)

        self.labelSamplePeriod = QLabel(self.mainFrame)
        self.labelSamplePeriod.setObjectName("labelSamplePeriod")
        self.horLaySetADC.addWidget(self.labelSamplePeriod)

        self.sampleTime = QLineEdit(self.mainFrame)
        self.sampleTime.setObjectName("sampleTime")
        self.horLaySetADC.addWidget(self.sampleTime)

        self.labelBufferSize = QLabel(self.mainFrame)
        self.labelBufferSize.setObjectName("labelBufferSize")
        self.horLaySetADC.addWidget(self.labelBufferSize)
        self.bufferSize = QLineEdit(self.mainFrame)
        self.bufferSize.setObjectName("bufferSize")

        self.horLaySetADC.addWidget(self.bufferSize)

        self.verticalLayout.addLayout(self.horLaySetADC)

        self.horizontalChannel = QHBoxLayout()
        self.horizontalChannel.setObjectName("horizontalChannel")
        self.gridChargeDischarge = QGridLayout()
        self.gridChargeDischarge.setObjectName("gridChargeDischarge")
        self.spinChargeVoltage = QDoubleSpinBox(self.mainFrame)
        self.spinChargeVoltage.setObjectName("spinChargeVoltage")
        self.spinChargeVoltage.setFrame(True)
        self.spinChargeVoltage.setDecimals(1)
        self.spinChargeVoltage.setMaximum(12.000000000000000)
        self.spinChargeVoltage.setSingleStep(0.100000000000000)
        self.spinChargeVoltage.setValue(8.000000000000000)

        self.gridChargeDischarge.addWidget(self.spinChargeVoltage, 0, 1, 1, 1)

        self.spinDischargeVoltage = QDoubleSpinBox(self.mainFrame)
        self.spinDischargeVoltage.setObjectName("spinDischargeVoltage")
        self.spinDischargeVoltage.setFrame(True)
        self.spinDischargeVoltage.setDecimals(1)
        self.spinDischargeVoltage.setMinimum(-6.000000000000000)
        self.spinDischargeVoltage.setMaximum(0.000000000000000)
        self.spinDischargeVoltage.setSingleStep(0.100000000000000)
        self.spinDischargeVoltage.setValue(-3.000000000000000)

        self.gridChargeDischarge.addWidget(self.spinDischargeVoltage, 1, 1, 1, 1)

        self.buttonCharge = QPushButton(self.mainFrame)
        self.buttonCharge.setObjectName("buttonCharge")

        self.gridChargeDischarge.addWidget(self.buttonCharge, 0, 0, 1, 1)

        self.buttonDischarge = QPushButton(self.mainFrame)
        self.buttonDischarge.setObjectName("buttonDischarge")

        self.gridChargeDischarge.addWidget(self.buttonDischarge, 1, 0, 1, 1)

        self.horizontalChannel.addLayout(self.gridChargeDischarge)

        self.verticalPulses = QVBoxLayout()
        self.verticalPulses.setObjectName(u"verticalPulses")
        self.buttonPositivePulse = QPushButton(self.mainFrame)
        self.buttonPositivePulse.setObjectName(u"buttonPositivePulse")
        self.verticalPulses.addWidget(self.buttonPositivePulse)
        self.buttonNegativePulse = QPushButton(self.mainFrame)
        self.buttonNegativePulse.setObjectName(u"buttonDisableFeedback")
        self.verticalPulses.addWidget(self.buttonNegativePulse)
        self.horizontalChannel.addLayout(self.verticalPulses)

        self.labelSensor = QLabel(self.mainFrame)
        self.labelSensor.setObjectName("labelSensor")
        self.labelSensor.setLayoutDirection(Qt.LeftToRight)
        self.labelSensor.setAlignment(
            Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter
        )

        self.horizontalChannel.addWidget(self.labelSensor)

        self.spinSensor = QSpinBox(self.mainFrame)
        self.spinSensor.setObjectName("spinSensor")
        self.spinSensor.setMaximum(6)
        self.spinSensor.setWrapping(True)

        self.horizontalChannel.addWidget(self.spinSensor)

        self.verticalRWEnable = QVBoxLayout()
        self.verticalRWEnable.setObjectName("verticalRWEnable")
        self.buttonEnableReading = QPushButton(self.mainFrame)
        self.buttonEnableReading.setObjectName("buttonEnableReading")

        self.verticalRWEnable.addWidget(self.buttonEnableReading)

        self.buttonEnableWriting = QPushButton(self.mainFrame)
        self.buttonEnableWriting.setObjectName("buttonEnableWriting")

        self.verticalRWEnable.addWidget(self.buttonEnableWriting)

        self.horizontalChannel.addLayout(self.verticalRWEnable)

        self.verticalRWDisable = QVBoxLayout()
        self.verticalRWDisable.setObjectName("verticalRWDisable")
        self.buttonDisableReading = QPushButton(self.mainFrame)
        self.buttonDisableReading.setObjectName("buttonDisableReading")

        self.verticalRWDisable.addWidget(self.buttonDisableReading)

        self.buttonDisableWriting = QPushButton(self.mainFrame)
        self.buttonDisableWriting.setObjectName("buttonDisableWriting")

        self.verticalRWDisable.addWidget(self.buttonDisableWriting)

        self.horizontalChannel.addLayout(self.verticalRWDisable)

        self.verticalLayout.addLayout(self.horizontalChannel)

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_ylim([0, 3.3])
        self.ax.grid()
        # Initialize the line object
        (self.line,) = self.ax.plot([], [], "-")

        self.verticalLayout.addWidget(self.canvas)

        # self.canvas = pg.GraphicsLayoutWidget()
        # self.ax = self.canvas.addPlot()
        # self.curve = BufferedPlotCurve(capacity=100,linked_curve=self.ax.plot()
        #                                )
        
        # self.verticalLayout.addWidget(self.canvas)

        self.horLaSetLED = QtWidgets.QHBoxLayout()
        self.horLaSetLED.setObjectName("horLaSetLED")
        self.resetSensor = QtWidgets.QPushButton(self.mainFrame)
        

        self.resetSensor.setObjectName("resetSensor")
        self.horLaSetLED.addWidget(self.resetSensor)

        self.targetVoltage = QDoubleSpinBox(self.mainFrame)
        self.targetVoltage.setObjectName("targetVoltage")
        self.targetVoltage.setFrame(True)
        self.targetVoltage.setDecimals(1)
        self.targetVoltage.setMinimum(0.300000000000000)
        self.targetVoltage.setMaximum(3.000000000000000)
        self.targetVoltage.setSingleStep(0.100000000000000)
        self.targetVoltage.setValue(2.800000000000000)
        self.horLaSetLED.addWidget(self.targetVoltage)

        self.chargeSensor = QtWidgets.QPushButton(self.mainFrame)
        self.chargeSensor.setObjectName("chargeSensor")
        self.horLaSetLED.addWidget(self.chargeSensor)

        self.verticalLayout.addLayout(self.horLaSetLED)
        self.horLaySerial = QtWidgets.QHBoxLayout()
        self.horLaySerial.setObjectName("horLaySerial")
        self.buttonSetMetalShieldBias = QtWidgets.QPushButton(self.mainFrame)

        self.buttonSetMetalShieldBias.setObjectName("buttonSetMetalShieldBias")
        self.horLaySerial.addWidget(self.buttonSetMetalShieldBias)

        self.spinMetalShieldBias = QDoubleSpinBox(self.mainFrame)
        self.spinMetalShieldBias.setObjectName("spinMetalShieldBias")
        self.spinMetalShieldBias.setFrame(True)
        self.spinMetalShieldBias.setDecimals(1)
        self.spinMetalShieldBias.setMinimum(-12.000000000000000)
        self.spinMetalShieldBias.setMaximum(12.000000000000000)
        self.spinMetalShieldBias.setSingleStep(0.100000000000000)
        self.spinMetalShieldBias.setValue(0.000000000000000)
        self.horLaySerial.addWidget(self.spinMetalShieldBias)
        # self.comboBoxSerialPort = QtWidgets.QComboBox(self.mainFrame)
        
        #self.comboBoxSerialPort.setObjectName("comboBoxSerialPort")
        #self.horLaySerial.addWidget(self.comboBoxSerialPort)
        self.buttonChargeAll = QtWidgets.QPushButton(self.mainFrame)

        self.buttonChargeAll.setObjectName("buttonChargeAll")
        self.horLaySerial.addWidget(self.buttonChargeAll)

        self.verticalLayout.addLayout(self.horLaySerial)

        self.horizontalDatalog = QHBoxLayout()
        self.horizontalDatalog.setObjectName(u"horizontalDatalog")
        # self.spacerDatalog = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        # self.horizontalDatalog.addItem(self.spacerDatalog)

        self.labelNameToDatalog = QLabel(self.mainFrame)
        self.labelNameToDatalog.setObjectName(u"labelNameToDatalog")
        self.horizontalDatalog.addWidget(self.labelNameToDatalog)

        self.lineNameToDatalog = QLineEdit(self.mainFrame)
        self.lineNameToDatalog.setObjectName("lineNameToDatalog")
        self.horizontalDatalog.addWidget(self.lineNameToDatalog)

        self.labelSensorsToDatalog = QLabel(self.mainFrame)
        self.labelSensorsToDatalog.setObjectName(u"labelSensorsToDatalog")
        self.horizontalDatalog.addWidget(self.labelSensorsToDatalog)

        self.listSensorsToDatalog = QListWidget(self.mainFrame)
        QListWidgetItem(self.listSensorsToDatalog)
        QListWidgetItem(self.listSensorsToDatalog)
        QListWidgetItem(self.listSensorsToDatalog)
        QListWidgetItem(self.listSensorsToDatalog)
        QListWidgetItem(self.listSensorsToDatalog)
        QListWidgetItem(self.listSensorsToDatalog)
        QListWidgetItem(self.listSensorsToDatalog)
        self.listSensorsToDatalog.setObjectName(u"listSensorsToDatalog")
        self.listSensorsToDatalog.setMaximumSize(QSize(180, 24))
        # self.listSensorsToDatalog.setAlternatingRowColors(False)
        self.listSensorsToDatalog.setSelectionMode(QAbstractItemView.MultiSelection)
        self.listSensorsToDatalog.setFlow(QListView.LeftToRight)
        # self.listSensorsToDatalog.setSelectionRectVisible(False)
        # self.listSensorsToDatalog.setSortingEnabled(False)
        self.horizontalDatalog.addWidget(self.listSensorsToDatalog)
        self.labelDatalogging = QLabel(self.mainFrame)
        self.labelDatalogging.setObjectName(u"labelDatalogging")
        self.horizontalDatalog.addWidget(self.labelDatalogging)
        self.buttonDatalogOn = QPushButton(self.mainFrame)
        self.buttonDatalogOn.setObjectName(u"buttonDatalogOn")
        self.horizontalDatalog.addWidget(self.buttonDatalogOn)
        self.buttonDatalogPause = QPushButton(self.mainFrame)
        self.buttonDatalogPause.setObjectName(u"buttonDatalogPause")
        self.horizontalDatalog.addWidget(self.buttonDatalogPause)
        self.buttonDatalogOff = QPushButton(self.mainFrame)
        self.buttonDatalogOff.setObjectName(u"buttonDatalogOff")
        self.horizontalDatalog.addWidget(self.buttonDatalogOff)
        self.progressBarDatalog = QProgressBar(self.mainFrame)
        self.progressBarDatalog.setObjectName(u"progressBarDatalog")
        self.progressBarDatalog.setMaximumSize(QSize(20, 16777215))
        self.progressBarDatalog.setValue(100)
        self.progressBarDatalog.setTextVisible(False)
        self.horizontalDatalog.addWidget(self.progressBarDatalog)
        self.verticalLayout.addLayout(self.horizontalDatalog)

        self.horizontalFeedback = QHBoxLayout()
        self.horizontalFeedback.setObjectName(u"horizontalFeedback")
        self.buttonEnableFeedback = QPushButton(self.mainFrame)
        self.buttonEnableFeedback.setObjectName(u"buttonEnableFeedback")
        self.horizontalFeedback.addWidget(self.buttonEnableFeedback)
        self.labelVref = QLabel(self.mainFrame)
        self.labelVref.setObjectName(u"labelVref")
        self.horizontalFeedback.addWidget(self.labelVref)
        self.spinVref = QDoubleSpinBox(self.mainFrame)
        self.spinVref.setObjectName(u"spinVref")
        self.spinVref.setDecimals(1)
        self.spinVref.setMaximum(3.300000000000000)
        self.spinVref.setSingleStep(0.100000000000000)
        self.spinVref.setValue(2.800000000000000)
        self.horizontalFeedback.addWidget(self.spinVref)
        self.buttonDisableFeedback = QPushButton(self.mainFrame)
        self.buttonDisableFeedback.setObjectName(u"buttonDisableFeedback")
        self.horizontalFeedback.addWidget(self.buttonDisableFeedback)
        self.verticalLayout.addLayout(self.horizontalFeedback)

        self.verticalLayout_2.addWidget(self.mainFrame)
        self.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(self)
        self.menubar.setObjectName("menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 26))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)
        
        try:
            self.fgdos = fgdosProcedure(
                device=SERIAL_PORT,
                spinbox_sensor=self.spinSensor,
                spinbox_metalshield=self.spinMetalShieldBias,
                update_plot=self.update_plot,
                update_gui=app.processEvents,
            )
            self.fgdos.set_enable_output(1)
        except:
            self.fgdos = None
            print("RP2040 not connected")

        self.logger = dataLogger(
            mode="adp",
            pauseButton=self.buttonDatalogPause,
            progressBarDatalog=self.progressBarDatalog,
            sensor_list=self.listSensorsToDatalog,
            fgdos=self.fgdos,
            filename_prefix=self.lineNameToDatalog,
        )

        self.menubar.addAction(self.menuFile.menuAction())
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionLoad)

        self.retranslateUi(self)
        self.buttonChargeAll.clicked.connect(lambda: self.fgdos.auto_charge_all())  # type: ignore
        self.buttonSetMetalShieldBias.clicked.connect(
            lambda: self.fgdos.setup_shield_bias(self.spinMetalShieldBias.value())
        )
        self.resetSensor.clicked.connect(
            lambda: self.fgdos.reset_sensor(self.spinSensor.value())
        )
        self.chargeSensor.clicked.connect(lambda: self.fgdos.auto_charge(self.spinSensor.value(),self.targetVoltage.value()))
        self.setPlotOn.clicked.connect(self.set_plot)
        self.setPlotOff.clicked.connect(self.unset_plot)
        self.actionSave.triggered.connect(self.save_settings)
        self.actionLoad.triggered.connect(self.load_settings)
        self.buttonEnableReading.clicked.connect(
            lambda: self.fgdos.set_enable_output(1)
        )
        self.buttonDisableReading.clicked.connect(
            lambda: self.fgdos.set_enable_output(0)
        )
        self.spinSensor.valueChanged.connect(self.set_sensor)
        self.buttonEnableWriting.clicked.connect(
            lambda: self.fgdos.set_enable_input(1)
        )
        self.buttonDisableWriting.clicked.connect(
            lambda: self.fgdos.set_enable_input(0)
        )

        self.buttonCharge.clicked.connect(
            lambda: self.fgdos.setup_charge(
                self.spinSensor.value(), "in", self.spinChargeVoltage.value()
            )
        )
        self.buttonDischarge.clicked.connect(
            lambda: self.fgdos.setup_charge(
                self.spinSensor.value(), "out", self.spinDischargeVoltage.value()
            )
        )

        self.buttonDatalogOn.clicked.connect(lambda: self.logger.start_log_data())
        self.buttonDatalogPause.clicked.connect(lambda: self.logger.toggle_log_data())
        self.buttonDatalogOff.clicked.connect(lambda: self.logger.stop_log_data())

        self.buttonPositivePulse.clicked.connect(
            lambda: self.fgdos.positive_pulse(self.spinSensor.value(), self.spinChargeVoltage.value())
        )
        self.buttonNegativePulse.clicked.connect(
            lambda: self.fgdos.negative_pulse(self.spinSensor.value(), self.spinDischargeVoltage.value())
        )
        
        self.buttonEnableFeedback.clicked.connect(
            lambda: self.fgdos.enable_feedback(self.spinVref.value())
        )
        # self.spinSensor.valueChanged.connect(self.fgdos.set_voltage())

        QtCore.QMetaObject.connectSlotsByName(self)

        #self.serial_port = QSerialPort()
        #self.populate_serial_ports()
        self.load_settings()
        self.timer = QTimer()
        self.timerPlot = QTimer()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.labelADC.setText(QCoreApplication.translate("MainWindow", "Plot:", None))
        self.setPlotOn.setText(QCoreApplication.translate("MainWindow", "On", None))
        self.setPlotOff.setText(QCoreApplication.translate("MainWindow", "Off", None))
        self.radioADC.setText(QCoreApplication.translate("MainWindow", u"ADC", None))
        self.radioSMU.setText(QCoreApplication.translate("MainWindow", u"SMU", None))
        self.labelNPLC.setText(QCoreApplication.translate("MainWindow", u"NPLC:", None))
        self.labelSamplePeriod.setText(
            QCoreApplication.translate("MainWindow", "Sample Period (ms):", None)
        )
        self.labelBufferSize.setText(
            QCoreApplication.translate("MainWindow", "Buffer Size (samples):", None)
        )
        self.sampleTime.setText(QCoreApplication.translate("MainWindow", "100", None))
        self.bufferSize.setText(QCoreApplication.translate("MainWindow", "5", None))
        self.resetSensor.setText(_translate("MainWindow", "Reset Sensor"))
        self.chargeSensor.setText(_translate("MainWindow", "Auto-Charge Sensor"))
        self.buttonSetMetalShieldBias.setText(_translate("MainWindow", "Metal Shield Bias"))
        self.buttonChargeAll.setText(_translate("MainWindow", "Charge All"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.actionSave.setText(QCoreApplication.translate("MainWindow", "Save", None))
        self.actionSave.setShortcut(
            QCoreApplication.translate("MainWindow", "Ctrl+S", None)
        )
        self.actionLoad.setText(QCoreApplication.translate("MainWindow", "Load", None))
        self.actionLoad.setShortcut(
            QCoreApplication.translate("MainWindow", "Ctrl+L", None)
        )

        self.spinChargeVoltage.setSuffix(
            QCoreApplication.translate("MainWindow", " V", None)
        )
        self.spinDischargeVoltage.setSuffix(
            QCoreApplication.translate("MainWindow", " V", None)
        )
        self.buttonCharge.setText(
            QCoreApplication.translate("MainWindow", "Setup Charge", None)
        )
        self.buttonDischarge.setText(
            QCoreApplication.translate("MainWindow", "Setup Discharge", None)
        )
        self.labelSensor.setText(
            QCoreApplication.translate("MainWindow", "Channel:", None)
        )
        self.buttonEnableReading.setText(
            QCoreApplication.translate("MainWindow", "Enable Reading", None)
        )
        self.buttonEnableWriting.setText(
            QCoreApplication.translate("MainWindow", "Enable Writing", None)
        )
        self.buttonDisableReading.setText(
            QCoreApplication.translate("MainWindow", "Disable Reading", None)
        )
        self.buttonDisableWriting.setText(
            QCoreApplication.translate("MainWindow", "Disable Writing", None)
        )

        self.labelSensorsToDatalog.setText(
            QCoreApplication.translate("MainWindow", u"Sensor:", None)
        )

        ___qlistwidgetitem = self.listSensorsToDatalog.item(0)
        ___qlistwidgetitem.setText(QCoreApplication.translate("MainWindow", u"0", None))
        ___qlistwidgetitem1 = self.listSensorsToDatalog.item(1)
        ___qlistwidgetitem1.setText(QCoreApplication.translate("MainWindow", u"1", None))
        ___qlistwidgetitem2 = self.listSensorsToDatalog.item(2)
        ___qlistwidgetitem2.setText(QCoreApplication.translate("MainWindow", u"2", None))
        ___qlistwidgetitem3 = self.listSensorsToDatalog.item(3)
        ___qlistwidgetitem3.setText(QCoreApplication.translate("MainWindow", u"3", None))
        ___qlistwidgetitem4 = self.listSensorsToDatalog.item(4)
        ___qlistwidgetitem4.setText(QCoreApplication.translate("MainWindow", u"4", None))
        ___qlistwidgetitem5 = self.listSensorsToDatalog.item(5)
        ___qlistwidgetitem5.setText(QCoreApplication.translate("MainWindow", u"5", None))
        ___qlistwidgetitem6 = self.listSensorsToDatalog.item(6)
        ___qlistwidgetitem6.setText(QCoreApplication.translate("MainWindow", u"6", None))

        self.labelDatalogging.setText(
            QCoreApplication.translate("MainWindow", u"Datalogging:", None)
        )
        self.buttonDatalogOn.setText(QCoreApplication.translate("MainWindow", u"New", None))
        self.buttonDatalogPause.setText(
            QCoreApplication.translate("MainWindow", u"Pause", None)
        )
        self.buttonDatalogOff.setText(
            QCoreApplication.translate("MainWindow", u"Disable", None)
        )
        self.progressBarDatalog.setValue(0)

        self.buttonEnableFeedback.setText(
            QCoreApplication.translate("MainWindow", u"Enable Feedback", None)
        )
        self.labelVref.setText(QCoreApplication.translate("MainWindow", u"Vref:", None))
        self.spinVref.setSuffix(QCoreApplication.translate("MainWindow", u"V", None))
        self.buttonDisableFeedback.setText(QCoreApplication.translate("MainWindow", u"Disable Feedback", None))
        self.buttonPositivePulse.setText(QCoreApplication.translate("MainWindow", u"Positive Pulse", None))
        self.buttonNegativePulse.setText(QCoreApplication.translate("MainWindow", u"Negative Pulse", None))
        self.labelNameToDatalog.setText(QCoreApplication.translate("MainWindow", u"File Name:", None))
        self.lineNameToDatalog.setText(QCoreApplication.translate("MainWindow", u"", None))

    def closeEvent(self, event):
        self.save_settings()  # Call the save_settings() method on the Ui_MainWindow instance
        # self.send_message(b"set_adc off\n")

        # quit_msg = "Are you sure you want to exit the program?"
        # reply = QMessageBox.question(self, 'Message',
        #                 quit_msg, QMessageBox.Yes, QMessageBox.No)

        # if reply == QMessageBox.Yes:
        #     event.accept()
        # else:
        #     event.ignore()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindow(app)

    mainWindow.show()
    sys.exit(app.exec_())

# Form implementation generated from reading ui file 'src/GUI_QtDesigner/turbine_simulator_window.ui'
#
# Created by: PyQt6 UI code generator 6.7.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1280, 720)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.treeWidget = QtWidgets.QTreeWidget(parent=self.centralwidget)
        self.treeWidget.setGeometry(QtCore.QRect(10, 10, 261, 651))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.treeWidget.setFont(font)
        self.treeWidget.setExpandsOnDoubleClick(False)
        self.treeWidget.setObjectName("treeWidget")
        item_0 = QtWidgets.QTreeWidgetItem(self.treeWidget)
        item_1 = QtWidgets.QTreeWidgetItem(item_0)
        item_2 = QtWidgets.QTreeWidgetItem(item_1)
        item_2 = QtWidgets.QTreeWidgetItem(item_1)
        item_2 = QtWidgets.QTreeWidgetItem(item_1)
        item_2 = QtWidgets.QTreeWidgetItem(item_1)
        item_1 = QtWidgets.QTreeWidgetItem(item_0)
        item_2 = QtWidgets.QTreeWidgetItem(item_1)
        item_2 = QtWidgets.QTreeWidgetItem(item_1)
        item_2 = QtWidgets.QTreeWidgetItem(item_1)
        item_1 = QtWidgets.QTreeWidgetItem(item_0)
        self.plainTextEdit = QtWidgets.QPlainTextEdit(parent=self.centralwidget)
        self.plainTextEdit.setGeometry(QtCore.QRect(280, 570, 991, 91))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.plainTextEdit.setFont(font)
        self.plainTextEdit.setObjectName("plainTextEdit")
        self.tabWidget = QtWidgets.QTabWidget(parent=self.centralwidget)
        self.tabWidget.setEnabled(True)
        self.tabWidget.setGeometry(QtCore.QRect(280, 10, 991, 551))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.tabWidget.setFont(font)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.CoverImage = QtWidgets.QLabel(parent=self.tab)
        self.CoverImage.setGeometry(QtCore.QRect(10, 150, 961, 243))
        self.CoverImage.setObjectName("CoverImage")
        self.label = QtWidgets.QLabel(parent=self.tab)
        self.label.setGeometry(QtCore.QRect(350, 10, 281, 41))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.tabWidget.addTab(self.tab, "")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1280, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Turbine Simulator"))
        self.treeWidget.headerItem().setText(0, _translate("MainWindow", "Project"))
        __sortingEnabled = self.treeWidget.isSortingEnabled()
        self.treeWidget.setSortingEnabled(False)
        self.treeWidget.topLevelItem(0).setText(0, _translate("MainWindow", "Case"))
        self.treeWidget.topLevelItem(0).child(0).setText(0, _translate("MainWindow", "Turbine Hydraulics"))
        self.treeWidget.topLevelItem(0).child(0).child(0).setText(0, _translate("MainWindow", "Load Data"))
        self.treeWidget.topLevelItem(0).child(0).child(1).setText(0, _translate("MainWindow", "Sizing"))
        self.treeWidget.topLevelItem(0).child(0).child(2).setText(0, _translate("MainWindow", "Surface Fit Settings"))
        self.treeWidget.topLevelItem(0).child(0).child(3).setText(0, _translate("MainWindow", "Output Options"))
        self.treeWidget.topLevelItem(0).child(1).setText(0, _translate("MainWindow", "Performance Simulator"))
        self.treeWidget.topLevelItem(0).child(1).child(0).setText(0, _translate("MainWindow", "Maximised Output"))
        self.treeWidget.topLevelItem(0).child(1).child(1).setText(0, _translate("MainWindow", "Manual/Automatic Control"))
        self.treeWidget.topLevelItem(0).child(1).child(2).setText(0, _translate("MainWindow", "Output Options"))
        self.treeWidget.topLevelItem(0).child(2).setText(0, _translate("MainWindow", "Turbine Loads"))
        self.treeWidget.setSortingEnabled(__sortingEnabled)
        self.plainTextEdit.setPlainText(_translate("MainWindow", "Welcome to the Turbine Simulator. Use the menu on the left to get started. Status updates will be shown here."))
        self.CoverImage.setText(_translate("MainWindow", "CoverImage"))
        self.label.setText(_translate("MainWindow", "Turbine Simulator Tool"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())


# Form implementation generated from reading ui file 'src/GUI_QtDesigner/manual-automatic_control_widget.ui'
#
# Created by: PyQt6 UI code generator 6.7.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_FormManualAutomaticControl(object):
    def setupUi(self, FormManualAutomaticControl):
        FormManualAutomaticControl.setObjectName("FormManualAutomaticControl")
        FormManualAutomaticControl.resize(461, 690)
        font = QtGui.QFont()
        font.setPointSize(11)
        FormManualAutomaticControl.setFont(font)
        self.lineEdit_H_t = QtWidgets.QLineEdit(parent=FormManualAutomaticControl)
        self.lineEdit_H_t.setGeometry(QtCore.QRect(40, 120, 141, 22))
        self.lineEdit_H_t.setObjectName("lineEdit_H_t")
        self.label_H_t = QtWidgets.QLabel(parent=FormManualAutomaticControl)
        self.label_H_t.setGeometry(QtCore.QRect(40, 90, 101, 31))
        self.label_H_t.setObjectName("label_H_t")
        self.label_T_t_rate = QtWidgets.QLabel(parent=FormManualAutomaticControl)
        self.label_T_t_rate.setGeometry(QtCore.QRect(200, 90, 141, 31))
        self.label_T_t_rate.setObjectName("label_T_t_rate")
        self.lineEdit_H_t_rate = QtWidgets.QLineEdit(parent=FormManualAutomaticControl)
        self.lineEdit_H_t_rate.setGeometry(QtCore.QRect(200, 120, 141, 22))
        self.lineEdit_H_t_rate.setObjectName("lineEdit_H_t_rate")
        self.label_Q = QtWidgets.QLabel(parent=FormManualAutomaticControl)
        self.label_Q.setGeometry(QtCore.QRect(40, 30, 101, 31))
        self.label_Q.setObjectName("label_Q")
        self.lineEdit_Q_rate = QtWidgets.QLineEdit(parent=FormManualAutomaticControl)
        self.lineEdit_Q_rate.setGeometry(QtCore.QRect(200, 60, 141, 22))
        self.lineEdit_Q_rate.setObjectName("lineEdit_Q_rate")
        self.lineEdit_Q = QtWidgets.QLineEdit(parent=FormManualAutomaticControl)
        self.lineEdit_Q.setGeometry(QtCore.QRect(40, 60, 141, 22))
        self.lineEdit_Q.setObjectName("lineEdit_Q")
        self.label_Q_rate = QtWidgets.QLabel(parent=FormManualAutomaticControl)
        self.label_Q_rate.setGeometry(QtCore.QRect(200, 30, 151, 31))
        self.label_Q_rate.setObjectName("label_Q_rate")
        self.label_blade_angle = QtWidgets.QLabel(parent=FormManualAutomaticControl)
        self.label_blade_angle.setGeometry(QtCore.QRect(40, 150, 101, 31))
        self.label_blade_angle.setObjectName("label_blade_angle")
        self.lineEdit_blade_angle = QtWidgets.QLineEdit(parent=FormManualAutomaticControl)
        self.lineEdit_blade_angle.setGeometry(QtCore.QRect(40, 180, 141, 22))
        self.lineEdit_blade_angle.setObjectName("lineEdit_blade_angle")
        self.label_n = QtWidgets.QLabel(parent=FormManualAutomaticControl)
        self.label_n.setGeometry(QtCore.QRect(40, 210, 101, 31))
        self.label_n.setObjectName("label_n")
        self.lineEdit_n = QtWidgets.QLineEdit(parent=FormManualAutomaticControl)
        self.lineEdit_n.setGeometry(QtCore.QRect(40, 240, 141, 22))
        self.lineEdit_n.setObjectName("lineEdit_n")
        self.lineEdit_blade_angle_rate = QtWidgets.QLineEdit(parent=FormManualAutomaticControl)
        self.lineEdit_blade_angle_rate.setGeometry(QtCore.QRect(200, 180, 141, 22))
        self.lineEdit_blade_angle_rate.setObjectName("lineEdit_blade_angle_rate")
        self.label_blade_angle_rate = QtWidgets.QLabel(parent=FormManualAutomaticControl)
        self.label_blade_angle_rate.setGeometry(QtCore.QRect(200, 150, 141, 31))
        self.label_blade_angle_rate.setObjectName("label_blade_angle_rate")
        self.lineEdit_n_rate = QtWidgets.QLineEdit(parent=FormManualAutomaticControl)
        self.lineEdit_n_rate.setGeometry(QtCore.QRect(200, 240, 141, 22))
        self.lineEdit_n_rate.setObjectName("lineEdit_n_rate")
        self.label_n_rate = QtWidgets.QLabel(parent=FormManualAutomaticControl)
        self.label_n_rate.setGeometry(QtCore.QRect(200, 210, 141, 31))
        self.label_n_rate.setObjectName("label_n_rate")
        self.checkBox = QtWidgets.QCheckBox(parent=FormManualAutomaticControl)
        self.checkBox.setGeometry(QtCore.QRect(360, 120, 75, 20))
        self.checkBox.setObjectName("checkBox")
        self.groupBox = QtWidgets.QGroupBox(parent=FormManualAutomaticControl)
        self.groupBox.setGeometry(QtCore.QRect(20, 10, 421, 271))
        self.groupBox.setObjectName("groupBox")
        self.checkBox_2 = QtWidgets.QCheckBox(parent=self.groupBox)
        self.checkBox_2.setGeometry(QtCore.QRect(340, 170, 75, 20))
        self.checkBox_2.setObjectName("checkBox_2")
        self.pushButtonApply = QtWidgets.QPushButton(parent=FormManualAutomaticControl)
        self.pushButtonApply.setGeometry(QtCore.QRect(360, 290, 81, 31))
        self.pushButtonApply.setObjectName("pushButtonApply")
        self.groupBox_2 = QtWidgets.QGroupBox(parent=FormManualAutomaticControl)
        self.groupBox_2.setGeometry(QtCore.QRect(20, 350, 421, 211))
        self.groupBox_2.setObjectName("groupBox_2")
        self.label_blade_angle_max = QtWidgets.QLabel(parent=self.groupBox_2)
        self.label_blade_angle_max.setGeometry(QtCore.QRect(190, 80, 111, 31))
        self.label_blade_angle_max.setObjectName("label_blade_angle_max")
        self.label_Kp = QtWidgets.QLabel(parent=self.groupBox_2)
        self.label_Kp.setGeometry(QtCore.QRect(20, 140, 101, 31))
        self.label_Kp.setObjectName("label_Kp")
        self.lineEdit_Ki = QtWidgets.QLineEdit(parent=self.groupBox_2)
        self.lineEdit_Ki.setGeometry(QtCore.QRect(130, 170, 91, 22))
        self.lineEdit_Ki.setObjectName("lineEdit_Ki")
        self.label_n_min = QtWidgets.QLabel(parent=self.groupBox_2)
        self.label_n_min.setGeometry(QtCore.QRect(20, 20, 101, 31))
        self.label_n_min.setObjectName("label_n_min")
        self.lineEdit_blade_angle_max = QtWidgets.QLineEdit(parent=self.groupBox_2)
        self.lineEdit_blade_angle_max.setGeometry(QtCore.QRect(190, 110, 141, 22))
        self.lineEdit_blade_angle_max.setObjectName("lineEdit_blade_angle_max")
        self.label_n_max = QtWidgets.QLabel(parent=self.groupBox_2)
        self.label_n_max.setGeometry(QtCore.QRect(190, 20, 111, 31))
        self.label_n_max.setObjectName("label_n_max")
        self.label_Ki = QtWidgets.QLabel(parent=self.groupBox_2)
        self.label_Ki.setGeometry(QtCore.QRect(130, 140, 111, 31))
        self.label_Ki.setObjectName("label_Ki")
        self.lineEdit_n_max = QtWidgets.QLineEdit(parent=self.groupBox_2)
        self.lineEdit_n_max.setGeometry(QtCore.QRect(190, 50, 141, 22))
        self.lineEdit_n_max.setObjectName("lineEdit_n_max")
        self.label_Kd = QtWidgets.QLabel(parent=self.groupBox_2)
        self.label_Kd.setGeometry(QtCore.QRect(240, 140, 101, 31))
        self.label_Kd.setObjectName("label_Kd")
        self.lineEdit_blade_angle_min = QtWidgets.QLineEdit(parent=self.groupBox_2)
        self.lineEdit_blade_angle_min.setGeometry(QtCore.QRect(20, 110, 141, 22))
        self.lineEdit_blade_angle_min.setObjectName("lineEdit_blade_angle_min")
        self.lineEdit_Kd = QtWidgets.QLineEdit(parent=self.groupBox_2)
        self.lineEdit_Kd.setGeometry(QtCore.QRect(240, 170, 91, 22))
        self.lineEdit_Kd.setObjectName("lineEdit_Kd")
        self.label_blade_angle_min = QtWidgets.QLabel(parent=self.groupBox_2)
        self.label_blade_angle_min.setGeometry(QtCore.QRect(20, 80, 101, 31))
        self.label_blade_angle_min.setObjectName("label_blade_angle_min")
        self.lineEdit_n_min = QtWidgets.QLineEdit(parent=self.groupBox_2)
        self.lineEdit_n_min.setGeometry(QtCore.QRect(20, 50, 141, 22))
        self.lineEdit_n_min.setObjectName("lineEdit_n_min")
        self.lineEdit_Kp = QtWidgets.QLineEdit(parent=self.groupBox_2)
        self.lineEdit_Kp.setGeometry(QtCore.QRect(20, 170, 91, 22))
        self.lineEdit_Kp.setObjectName("lineEdit_Kp")
        self.pushButtonApply_2 = QtWidgets.QPushButton(parent=FormManualAutomaticControl)
        self.pushButtonApply_2.setGeometry(QtCore.QRect(360, 570, 81, 31))
        self.pushButtonApply_2.setObjectName("pushButtonApply_2")
        self.pushButtonStop = QtWidgets.QPushButton(parent=FormManualAutomaticControl)
        self.pushButtonStop.setGeometry(QtCore.QRect(360, 640, 81, 31))
        self.pushButtonStop.setObjectName("pushButtonStop")
        self.pushButtonStart = QtWidgets.QPushButton(parent=FormManualAutomaticControl)
        self.pushButtonStart.setGeometry(QtCore.QRect(260, 640, 81, 31))
        self.pushButtonStart.setObjectName("pushButtonStart")
        self.groupBox.raise_()
        self.lineEdit_H_t.raise_()
        self.label_H_t.raise_()
        self.label_T_t_rate.raise_()
        self.lineEdit_H_t_rate.raise_()
        self.label_Q.raise_()
        self.lineEdit_Q_rate.raise_()
        self.lineEdit_Q.raise_()
        self.label_Q_rate.raise_()
        self.label_blade_angle.raise_()
        self.lineEdit_blade_angle.raise_()
        self.label_n.raise_()
        self.lineEdit_n.raise_()
        self.lineEdit_blade_angle_rate.raise_()
        self.label_blade_angle_rate.raise_()
        self.lineEdit_n_rate.raise_()
        self.label_n_rate.raise_()
        self.checkBox.raise_()
        self.pushButtonApply.raise_()
        self.pushButtonApply_2.raise_()
        self.pushButtonStop.raise_()
        self.pushButtonStart.raise_()
        self.groupBox_2.raise_()

        self.retranslateUi(FormManualAutomaticControl)
        QtCore.QMetaObject.connectSlotsByName(FormManualAutomaticControl)

    def retranslateUi(self, FormManualAutomaticControl):
        _translate = QtCore.QCoreApplication.translate
        FormManualAutomaticControl.setWindowTitle(_translate("FormManualAutomaticControl", "Form"))
        self.label_H_t.setText(_translate("FormManualAutomaticControl", "Target H [m]"))
        self.label_T_t_rate.setText(_translate("FormManualAutomaticControl", "Rate of Change [1/s]"))
        self.label_Q.setText(_translate("FormManualAutomaticControl", "Q [m³/s]"))
        self.label_Q_rate.setText(_translate("FormManualAutomaticControl", "Rate of Change [1/s]"))
        self.label_blade_angle.setText(_translate("FormManualAutomaticControl", "Blade Angle [°]"))
        self.label_n.setText(_translate("FormManualAutomaticControl", "n [rpm]"))
        self.label_blade_angle_rate.setText(_translate("FormManualAutomaticControl", "Rate of Change [1/s]"))
        self.label_n_rate.setText(_translate("FormManualAutomaticControl", "Rate of Change [1/s]"))
        self.checkBox.setText(_translate("FormManualAutomaticControl", "Activate"))
        self.groupBox.setTitle(_translate("FormManualAutomaticControl", "Input Parameters"))
        self.checkBox_2.setText(_translate("FormManualAutomaticControl", "Lock"))
        self.pushButtonApply.setText(_translate("FormManualAutomaticControl", "Apply"))
        self.groupBox_2.setTitle(_translate("FormManualAutomaticControl", "Settings"))
        self.label_blade_angle_max.setText(_translate("FormManualAutomaticControl", "Blade Angle max [°]"))
        self.label_Kp.setText(_translate("FormManualAutomaticControl", "Kp"))
        self.label_n_min.setText(_translate("FormManualAutomaticControl", "n min [rpm]"))
        self.label_n_max.setText(_translate("FormManualAutomaticControl", "n max [rpm]"))
        self.label_Ki.setText(_translate("FormManualAutomaticControl", "Ki"))
        self.label_Kd.setText(_translate("FormManualAutomaticControl", "Kd"))
        self.label_blade_angle_min.setText(_translate("FormManualAutomaticControl", "Blade Angle min [°]"))
        self.pushButtonApply_2.setText(_translate("FormManualAutomaticControl", "Apply"))
        self.pushButtonStop.setText(_translate("FormManualAutomaticControl", "Stop"))
        self.pushButtonStart.setText(_translate("FormManualAutomaticControl", "Start"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    FormManualAutomaticControl = QtWidgets.QWidget()
    ui = Ui_FormManualAutomaticControl()
    ui.setupUi(FormManualAutomaticControl)
    FormManualAutomaticControl.show()
    sys.exit(app.exec())


# Form implementation generated from reading ui file 'src/GUI_QtDesigner/maximise_output_widget.ui'
#
# Created by: PyQt6 UI code generator 6.7.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_MaximiseOutput(object):
    def setupUi(self, MaximiseOutput):
        MaximiseOutput.setObjectName("MaximiseOutput")
        MaximiseOutput.resize(450, 550)
        font = QtGui.QFont()
        font.setPointSize(11)
        MaximiseOutput.setFont(font)
        self.groupBox_Q = QtWidgets.QGroupBox(parent=MaximiseOutput)
        self.groupBox_Q.setGeometry(QtCore.QRect(20, 10, 411, 91))
        self.groupBox_Q.setObjectName("groupBox_Q")
        self.lineEdit_Q_step = QtWidgets.QLineEdit(parent=self.groupBox_Q)
        self.lineEdit_Q_step.setGeometry(QtCore.QRect(280, 50, 113, 22))
        self.lineEdit_Q_step.setObjectName("lineEdit_Q_step")
        self.label_Q_Step = QtWidgets.QLabel(parent=self.groupBox_Q)
        self.label_Q_Step.setGeometry(QtCore.QRect(280, 20, 101, 31))
        self.label_Q_Step.setObjectName("label_Q_Step")
        self.lineEdit_Q_start = QtWidgets.QLineEdit(parent=self.groupBox_Q)
        self.lineEdit_Q_start.setGeometry(QtCore.QRect(20, 50, 113, 22))
        self.lineEdit_Q_start.setObjectName("lineEdit_Q_start")
        self.label_Q_Stop = QtWidgets.QLabel(parent=self.groupBox_Q)
        self.label_Q_Stop.setGeometry(QtCore.QRect(150, 20, 111, 31))
        self.label_Q_Stop.setObjectName("label_Q_Stop")
        self.lineEdit_Q_stop = QtWidgets.QLineEdit(parent=self.groupBox_Q)
        self.lineEdit_Q_stop.setGeometry(QtCore.QRect(150, 50, 113, 22))
        self.lineEdit_Q_stop.setObjectName("lineEdit_Q_stop")
        self.label_Q_Start = QtWidgets.QLabel(parent=self.groupBox_Q)
        self.label_Q_Start.setGeometry(QtCore.QRect(20, 20, 101, 31))
        self.label_Q_Start.setObjectName("label_Q_Start")
        self.pushButtonStart = QtWidgets.QPushButton(parent=MaximiseOutput)
        self.pushButtonStart.setGeometry(QtCore.QRect(350, 500, 81, 31))
        self.pushButtonStart.setObjectName("pushButtonStart")
        self.groupBox_n = QtWidgets.QGroupBox(parent=MaximiseOutput)
        self.groupBox_n.setGeometry(QtCore.QRect(20, 130, 411, 91))
        self.groupBox_n.setObjectName("groupBox_n")
        self.lineEdit_n_step = QtWidgets.QLineEdit(parent=self.groupBox_n)
        self.lineEdit_n_step.setGeometry(QtCore.QRect(280, 50, 113, 22))
        self.lineEdit_n_step.setObjectName("lineEdit_n_step")
        self.label_n_Step = QtWidgets.QLabel(parent=self.groupBox_n)
        self.label_n_Step.setGeometry(QtCore.QRect(280, 20, 101, 31))
        self.label_n_Step.setObjectName("label_n_Step")
        self.lineEdit_n_start = QtWidgets.QLineEdit(parent=self.groupBox_n)
        self.lineEdit_n_start.setGeometry(QtCore.QRect(20, 50, 113, 22))
        self.lineEdit_n_start.setObjectName("lineEdit_n_start")
        self.label_n_Stop = QtWidgets.QLabel(parent=self.groupBox_n)
        self.label_n_Stop.setGeometry(QtCore.QRect(150, 20, 111, 31))
        self.label_n_Stop.setObjectName("label_n_Stop")
        self.lineEdit_n_stop = QtWidgets.QLineEdit(parent=self.groupBox_n)
        self.lineEdit_n_stop.setGeometry(QtCore.QRect(150, 50, 113, 22))
        self.lineEdit_n_stop.setObjectName("lineEdit_n_stop")
        self.label_n_Start = QtWidgets.QLabel(parent=self.groupBox_n)
        self.label_n_Start.setGeometry(QtCore.QRect(20, 20, 101, 31))
        self.label_n_Start.setObjectName("label_n_Start")
        self.groupBox_blade_angle = QtWidgets.QGroupBox(parent=MaximiseOutput)
        self.groupBox_blade_angle.setGeometry(QtCore.QRect(20, 250, 411, 91))
        self.groupBox_blade_angle.setObjectName("groupBox_blade_angle")
        self.lineEdit_blade_angle_step = QtWidgets.QLineEdit(parent=self.groupBox_blade_angle)
        self.lineEdit_blade_angle_step.setGeometry(QtCore.QRect(280, 50, 113, 22))
        self.lineEdit_blade_angle_step.setObjectName("lineEdit_blade_angle_step")
        self.label_blade_angle_Step = QtWidgets.QLabel(parent=self.groupBox_blade_angle)
        self.label_blade_angle_Step.setGeometry(QtCore.QRect(290, 20, 101, 31))
        self.label_blade_angle_Step.setObjectName("label_blade_angle_Step")
        self.lineEdit_blade_angle_start = QtWidgets.QLineEdit(parent=self.groupBox_blade_angle)
        self.lineEdit_blade_angle_start.setGeometry(QtCore.QRect(20, 50, 113, 22))
        self.lineEdit_blade_angle_start.setObjectName("lineEdit_blade_angle_start")
        self.label_blade_angle_Stop = QtWidgets.QLabel(parent=self.groupBox_blade_angle)
        self.label_blade_angle_Stop.setGeometry(QtCore.QRect(150, 20, 111, 31))
        self.label_blade_angle_Stop.setObjectName("label_blade_angle_Stop")
        self.lineEdit_blade_angle_stop = QtWidgets.QLineEdit(parent=self.groupBox_blade_angle)
        self.lineEdit_blade_angle_stop.setGeometry(QtCore.QRect(150, 50, 113, 22))
        self.lineEdit_blade_angle_stop.setObjectName("lineEdit_blade_angle_stop")
        self.label_blade_angle_Start = QtWidgets.QLabel(parent=self.groupBox_blade_angle)
        self.label_blade_angle_Start.setGeometry(QtCore.QRect(20, 20, 101, 31))
        self.label_blade_angle_Start.setObjectName("label_blade_angle_Start")
        self.groupBox_H = QtWidgets.QGroupBox(parent=MaximiseOutput)
        self.groupBox_H.setGeometry(QtCore.QRect(20, 370, 411, 91))
        self.groupBox_H.setObjectName("groupBox_H")
        self.lineEdit_H_min = QtWidgets.QLineEdit(parent=self.groupBox_H)
        self.lineEdit_H_min.setGeometry(QtCore.QRect(20, 50, 113, 22))
        self.lineEdit_H_min.setObjectName("lineEdit_H_min")
        self.label_H_max = QtWidgets.QLabel(parent=self.groupBox_H)
        self.label_H_max.setGeometry(QtCore.QRect(150, 20, 111, 31))
        self.label_H_max.setObjectName("label_H_max")
        self.lineEdit_H_max = QtWidgets.QLineEdit(parent=self.groupBox_H)
        self.lineEdit_H_max.setGeometry(QtCore.QRect(150, 50, 113, 22))
        self.lineEdit_H_max.setObjectName("lineEdit_H_max")
        self.label_H_min = QtWidgets.QLabel(parent=self.groupBox_H)
        self.label_H_min.setGeometry(QtCore.QRect(20, 20, 101, 31))
        self.label_H_min.setObjectName("label_H_min")

        self.retranslateUi(MaximiseOutput)
        QtCore.QMetaObject.connectSlotsByName(MaximiseOutput)

    def retranslateUi(self, MaximiseOutput):
        _translate = QtCore.QCoreApplication.translate
        MaximiseOutput.setWindowTitle(_translate("MaximiseOutput", "Form"))
        self.groupBox_Q.setTitle(_translate("MaximiseOutput", "Range of Q [m³/s]"))
        self.label_Q_Step.setText(_translate("MaximiseOutput", "Step"))
        self.label_Q_Stop.setText(_translate("MaximiseOutput", "Stop"))
        self.label_Q_Start.setText(_translate("MaximiseOutput", "Start"))
        self.pushButtonStart.setText(_translate("MaximiseOutput", "Start"))
        self.groupBox_n.setTitle(_translate("MaximiseOutput", "Range of n [rpm]"))
        self.label_n_Step.setText(_translate("MaximiseOutput", "Step"))
        self.label_n_Stop.setText(_translate("MaximiseOutput", "Stop"))
        self.label_n_Start.setText(_translate("MaximiseOutput", "Start"))
        self.groupBox_blade_angle.setTitle(_translate("MaximiseOutput", "Range of Blade Angles [°]"))
        self.label_blade_angle_Step.setText(_translate("MaximiseOutput", "Step"))
        self.label_blade_angle_Stop.setText(_translate("MaximiseOutput", "Stop"))
        self.label_blade_angle_Start.setText(_translate("MaximiseOutput", "Start"))
        self.groupBox_H.setTitle(_translate("MaximiseOutput", "Limits of H [m]"))
        self.label_H_max.setText(_translate("MaximiseOutput", "Max."))
        self.label_H_min.setText(_translate("MaximiseOutput", "Min."))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MaximiseOutput = QtWidgets.QWidget()
    ui = Ui_MaximiseOutput()
    ui.setupUi(MaximiseOutput)
    MaximiseOutput.show()
    sys.exit(app.exec())


# Form implementation generated from reading ui file 'src/GUI_QtDesigner/sizing_widget.ui'
#
# Created by: PyQt6 UI code generator 6.7.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_Sizing(object):
    def setupUi(self, Sizing):
        Sizing.setObjectName("Sizing")
        Sizing.resize(240, 421)
        font = QtGui.QFont()
        font.setPointSize(11)
        Sizing.setFont(font)
        self.label_input_1 = QtWidgets.QLabel(parent=Sizing)
        self.label_input_1.setGeometry(QtCore.QRect(40, 230, 171, 31))
        self.label_input_1.setObjectName("label_input_1")
        self.lineEdit_input_1 = QtWidgets.QLineEdit(parent=Sizing)
        self.lineEdit_input_1.setGeometry(QtCore.QRect(40, 260, 161, 22))
        self.lineEdit_input_1.setObjectName("lineEdit_input_1")
        self.label_input_2 = QtWidgets.QLabel(parent=Sizing)
        self.label_input_2.setGeometry(QtCore.QRect(40, 290, 171, 31))
        self.label_input_2.setObjectName("label_input_2")
        self.lineEdit_input_2 = QtWidgets.QLineEdit(parent=Sizing)
        self.lineEdit_input_2.setGeometry(QtCore.QRect(40, 320, 161, 22))
        self.lineEdit_input_2.setObjectName("lineEdit_input_2")
        self.groupBox = QtWidgets.QGroupBox(parent=Sizing)
        self.groupBox.setGeometry(QtCore.QRect(20, 10, 201, 351))
        self.groupBox.setObjectName("groupBox")
        self.checkBox_2 = QtWidgets.QCheckBox(parent=self.groupBox)
        self.checkBox_2.setGeometry(QtCore.QRect(20, 100, 171, 20))
        self.checkBox_2.setObjectName("checkBox_2")
        self.label = QtWidgets.QLabel(parent=self.groupBox)
        self.label.setGeometry(QtCore.QRect(20, 20, 101, 31))
        self.label.setObjectName("label")
        self.checkBox_1 = QtWidgets.QCheckBox(parent=self.groupBox)
        self.checkBox_1.setGeometry(QtCore.QRect(20, 60, 171, 20))
        self.checkBox_1.setObjectName("checkBox_1")
        self.checkBox_3 = QtWidgets.QCheckBox(parent=self.groupBox)
        self.checkBox_3.setGeometry(QtCore.QRect(20, 140, 171, 20))
        self.checkBox_3.setObjectName("checkBox_3")
        self.checkBox_4 = QtWidgets.QCheckBox(parent=self.groupBox)
        self.checkBox_4.setGeometry(QtCore.QRect(20, 180, 171, 20))
        self.checkBox_4.setObjectName("checkBox_4")
        self.pushButton = QtWidgets.QPushButton(parent=Sizing)
        self.pushButton.setGeometry(QtCore.QRect(140, 370, 81, 31))
        self.pushButton.setObjectName("pushButton")
        self.groupBox.raise_()
        self.label_input_1.raise_()
        self.lineEdit_input_1.raise_()
        self.label_input_2.raise_()
        self.lineEdit_input_2.raise_()
        self.pushButton.raise_()

        self.retranslateUi(Sizing)
        QtCore.QMetaObject.connectSlotsByName(Sizing)

    def retranslateUi(self, Sizing):
        _translate = QtCore.QCoreApplication.translate
        Sizing.setWindowTitle(_translate("Sizing", "Form"))
        self.label_input_1.setText(_translate("Sizing", "Input value 1"))
        self.label_input_2.setText(_translate("Sizing", "Input value 2"))
        self.groupBox.setTitle(_translate("Sizing", "Input Parameters"))
        self.checkBox_2.setText(_translate("Sizing", "Flow rate Q [m³/h]"))
        self.label.setText(_translate("Sizing", "Select Two:"))
        self.checkBox_1.setText(_translate("Sizing", "Head H [m]"))
        self.checkBox_3.setText(_translate("Sizing", "Rotational speed n [rpm]"))
        self.checkBox_4.setText(_translate("Sizing", "Runner diameter D [m]"))
        self.pushButton.setText(_translate("Sizing", "Apply"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Sizing = QtWidgets.QWidget()
    ui = Ui_Sizing()
    ui.setupUi(Sizing)
    Sizing.show()
    sys.exit(app.exec())


# Form implementation generated from reading ui file 'src/GUI_QtDesigner/surface_fitting_widget.ui'
#
# Created by: PyQt6 UI code generator 6.7.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_SurfaceFitting(object):
    def setupUi(self, SurfaceFitting):
        SurfaceFitting.setObjectName("SurfaceFitting")
        SurfaceFitting.resize(331, 440)
        font = QtGui.QFont()
        font.setPointSize(11)
        SurfaceFitting.setFont(font)
        self.groupBox = QtWidgets.QGroupBox(parent=SurfaceFitting)
        self.groupBox.setGeometry(QtCore.QRect(20, 280, 291, 91))
        self.groupBox.setObjectName("groupBox")
        self.label_input_1 = QtWidgets.QLabel(parent=self.groupBox)
        self.label_input_1.setGeometry(QtCore.QRect(20, 20, 231, 31))
        self.label_input_1.setObjectName("label_input_1")
        self.lineEdit_min_efficiency_limit = QtWidgets.QLineEdit(parent=self.groupBox)
        self.lineEdit_min_efficiency_limit.setGeometry(QtCore.QRect(20, 50, 81, 22))
        self.lineEdit_min_efficiency_limit.setObjectName("lineEdit_min_efficiency_limit")
        self.pushButton = QtWidgets.QPushButton(parent=SurfaceFitting)
        self.pushButton.setGeometry(QtCore.QRect(170, 390, 81, 31))
        self.pushButton.setObjectName("pushButton")
        self.groupBox_2 = QtWidgets.QGroupBox(parent=SurfaceFitting)
        self.groupBox_2.setGeometry(QtCore.QRect(20, 20, 291, 241))
        self.groupBox_2.setObjectName("groupBox_2")
        self.checkBox_extrapolate_n11 = QtWidgets.QCheckBox(parent=self.groupBox_2)
        self.checkBox_extrapolate_n11.setGeometry(QtCore.QRect(20, 30, 251, 20))
        self.checkBox_extrapolate_n11.setObjectName("checkBox_extrapolate_n11")
        self.checkBox_extrapolate_blade_angle = QtWidgets.QCheckBox(parent=self.groupBox_2)
        self.checkBox_extrapolate_blade_angle.setGeometry(QtCore.QRect(20, 150, 251, 20))
        self.checkBox_extrapolate_blade_angle.setObjectName("checkBox_extrapolate_blade_angle")
        self.label_n11_min = QtWidgets.QLabel(parent=self.groupBox_2)
        self.label_n11_min.setGeometry(QtCore.QRect(20, 50, 171, 31))
        self.label_n11_min.setObjectName("label_n11_min")
        self.lineEdit_n11_min = QtWidgets.QLineEdit(parent=self.groupBox_2)
        self.lineEdit_n11_min.setGeometry(QtCore.QRect(20, 80, 71, 22))
        self.lineEdit_n11_min.setObjectName("lineEdit_n11_min")
        self.label_n11_max = QtWidgets.QLabel(parent=self.groupBox_2)
        self.label_n11_max.setGeometry(QtCore.QRect(110, 50, 71, 31))
        self.label_n11_max.setObjectName("label_n11_max")
        self.lineEdit_n11_max = QtWidgets.QLineEdit(parent=self.groupBox_2)
        self.lineEdit_n11_max.setGeometry(QtCore.QRect(110, 80, 71, 22))
        self.lineEdit_n11_max.setObjectName("lineEdit_n11_max")
        self.label_n11_pts = QtWidgets.QLabel(parent=self.groupBox_2)
        self.label_n11_pts.setGeometry(QtCore.QRect(200, 50, 171, 31))
        self.label_n11_pts.setObjectName("label_n11_pts")
        self.lineEdit_n11_pts = QtWidgets.QLineEdit(parent=self.groupBox_2)
        self.lineEdit_n11_pts.setGeometry(QtCore.QRect(200, 80, 71, 22))
        self.lineEdit_n11_pts.setObjectName("lineEdit_n11_pts")
        self.lineEdit_blade_angle_max = QtWidgets.QLineEdit(parent=self.groupBox_2)
        self.lineEdit_blade_angle_max.setGeometry(QtCore.QRect(110, 200, 71, 22))
        self.lineEdit_blade_angle_max.setObjectName("lineEdit_blade_angle_max")
        self.lineEdit_blade_angle_pts = QtWidgets.QLineEdit(parent=self.groupBox_2)
        self.lineEdit_blade_angle_pts.setGeometry(QtCore.QRect(200, 200, 71, 22))
        self.lineEdit_blade_angle_pts.setObjectName("lineEdit_blade_angle_pts")
        self.label_blade_angle_min = QtWidgets.QLabel(parent=self.groupBox_2)
        self.label_blade_angle_min.setGeometry(QtCore.QRect(20, 170, 171, 31))
        self.label_blade_angle_min.setObjectName("label_blade_angle_min")
        self.lineEdit_blade_angle_min = QtWidgets.QLineEdit(parent=self.groupBox_2)
        self.lineEdit_blade_angle_min.setGeometry(QtCore.QRect(20, 200, 71, 22))
        self.lineEdit_blade_angle_min.setObjectName("lineEdit_blade_angle_min")
        self.label_blade_angle_max = QtWidgets.QLabel(parent=self.groupBox_2)
        self.label_blade_angle_max.setGeometry(QtCore.QRect(110, 170, 71, 31))
        self.label_blade_angle_max.setObjectName("label_blade_angle_max")
        self.label_blade_angle_pts = QtWidgets.QLabel(parent=self.groupBox_2)
        self.label_blade_angle_pts.setGeometry(QtCore.QRect(200, 170, 171, 31))
        self.label_blade_angle_pts.setObjectName("label_blade_angle_pts")

        self.retranslateUi(SurfaceFitting)
        QtCore.QMetaObject.connectSlotsByName(SurfaceFitting)

    def retranslateUi(self, SurfaceFitting):
        _translate = QtCore.QCoreApplication.translate
        SurfaceFitting.setWindowTitle(_translate("SurfaceFitting", "Form"))
        self.groupBox.setTitle(_translate("SurfaceFitting", "Surface Trim Options"))
        self.label_input_1.setText(_translate("SurfaceFitting", "Minimum efficiency trim limit"))
        self.lineEdit_min_efficiency_limit.setText(_translate("SurfaceFitting", "0.2"))
        self.pushButton.setText(_translate("SurfaceFitting", "Fit Surface"))
        self.groupBox_2.setTitle(_translate("SurfaceFitting", "Data Interpolation/Extrapolation Options"))
        self.checkBox_extrapolate_n11.setText(_translate("SurfaceFitting", "Extrapolate unit speed n11 [rpm]"))
        self.checkBox_extrapolate_blade_angle.setText(_translate("SurfaceFitting", "Extrapolate Blade Angles [°]"))
        self.label_n11_min.setText(_translate("SurfaceFitting", "Min."))
        self.lineEdit_n11_min.setText(_translate("SurfaceFitting", "60"))
        self.label_n11_max.setText(_translate("SurfaceFitting", "Max."))
        self.lineEdit_n11_max.setText(_translate("SurfaceFitting", "200"))
        self.label_n11_pts.setText(_translate("SurfaceFitting", "No. of Pts"))
        self.lineEdit_n11_pts.setText(_translate("SurfaceFitting", "10"))
        self.lineEdit_blade_angle_max.setText(_translate("SurfaceFitting", "26"))
        self.lineEdit_blade_angle_pts.setText(_translate("SurfaceFitting", "10"))
        self.label_blade_angle_min.setText(_translate("SurfaceFitting", "Min."))
        self.lineEdit_blade_angle_min.setText(_translate("SurfaceFitting", "3"))
        self.label_blade_angle_max.setText(_translate("SurfaceFitting", "Max."))
        self.label_blade_angle_pts.setText(_translate("SurfaceFitting", "No. of Pts"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    SurfaceFitting = QtWidgets.QWidget()
    ui = Ui_SurfaceFitting()
    ui.setupUi(SurfaceFitting)
    SurfaceFitting.show()
    sys.exit(app.exec())



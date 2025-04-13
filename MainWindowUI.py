# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MainWindow.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        # 表格整体布局
        Form.setObjectName("Form")
        Form.resize(440, 720)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        Form.setFont(font)

        # 输入手牌布局
        self.hand_input = QtWidgets.QLineEdit(Form)
        self.hand_input.setGeometry(QtCore.QRect(10, 260, 421, 41))  # 设置位置和大小

        # 底牌输入布局
        self.landlord_input = QtWidgets.QLineEdit(Form)
        self.landlord_input.setGeometry(QtCore.QRect(10, 300, 421, 41))  # 设置位置和大小

        # 位置输入布局
        self.role_combo = QtWidgets.QComboBox(Form)
        self.role_combo.setGeometry(QtCore.QRect(10, 340, 421, 41))  # 设置位置和大小

        
        # 胜率布局
        self.WinRate = QtWidgets.QLabel(Form)
        self.WinRate.setGeometry(QtCore.QRect(225, 180, 200, 61))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.WinRate.setFont(font)
        self.WinRate.setAlignment(QtCore.Qt.AlignCenter)
        self.WinRate.setObjectName("WinRate")


        # 开始按钮布局
        self.InitCard = QtWidgets.QPushButton(Form)
        self.InitCard.setGeometry(QtCore.QRect(60, 400, 121, 41))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.InitCard.setFont(font)
        self.InitCard.setStyleSheet("")
        self.InitCard.setObjectName("InitCard")


        #手牌位置布局
        self.UserHandCards = QtWidgets.QLabel(Form)
        self.UserHandCards.setGeometry(QtCore.QRect(10, 300, 421, 41))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.UserHandCards.setFont(font)
        self.UserHandCards.setAlignment(QtCore.Qt.AlignCenter)
        self.UserHandCards.setObjectName("UserHandCards")

        #左侧（上家）玩家布局
        self.LPlayer = QtWidgets.QFrame(Form)
        self.LPlayer.setGeometry(QtCore.QRect(10, 80, 201, 61))
        self.LPlayer.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.LPlayer.setFrameShadow(QtWidgets.QFrame.Raised)
        self.LPlayer.setObjectName("LPlayer")
        
        #左侧（上家）显示布局
        self.LPlayedCard = QtWidgets.QLabel(self.LPlayer)
        self.LPlayedCard.setGeometry(QtCore.QRect(-15, 0, 230, 61))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.LPlayedCard.setFont(font)
        self.LPlayedCard.setAlignment(QtCore.Qt.AlignCenter)
        self.LPlayedCard.setObjectName("LPlayedCard")

        #右侧（下家）手牌布局
        self.RPlayer = QtWidgets.QFrame(Form)
        self.RPlayer.setGeometry(QtCore.QRect(215, 80, 201, 61))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.RPlayer.setFont(font)
        self.RPlayer.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.RPlayer.setFrameShadow(QtWidgets.QFrame.Raised)
        self.RPlayer.setObjectName("RPlayer")

        #右侧（下家）显示布局
        self.RPlayedCard = QtWidgets.QLabel(self.RPlayer)
        self.RPlayedCard.setGeometry(QtCore.QRect(0, 0, 230, 61))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.RPlayedCard.setFont(font)
        self.RPlayedCard.setAlignment(QtCore.Qt.AlignCenter)
        self.RPlayedCard.setObjectName("RPlayedCard")

        #玩家布局
        self.Player = QtWidgets.QFrame(Form)
        self.Player.setGeometry(QtCore.QRect(40, 180, 171, 61))
        self.Player.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.Player.setFrameShadow(QtWidgets.QFrame.Raised)
        self.Player.setObjectName("Player")

        #预测牌布局
        self.PredictedCard = QtWidgets.QLabel(self.Player)
        self.PredictedCard.setGeometry(QtCore.QRect(-30, 0, 220, 61))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.PredictedCard.setFont(font)
        self.PredictedCard.setAlignment(QtCore.Qt.AlignCenter)
        self.PredictedCard.setObjectName("PredictedCard")

        #底牌显示布局
        self.ThreeLandlordCards = QtWidgets.QLabel(Form)
        self.ThreeLandlordCards.setGeometry(QtCore.QRect(125, 10, 210, 41))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.ThreeLandlordCards.setFont(font)
        self.ThreeLandlordCards.setAlignment(QtCore.Qt.AlignCenter)
        self.ThreeLandlordCards.setObjectName("ThreeLandlordCards")

        #停止按钮布局
        self.Stop = QtWidgets.QPushButton(Form)
        self.Stop.setGeometry(QtCore.QRect(260, 400, 111, 41))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.Stop.setFont(font)
        self.Stop.setStyleSheet("")
        self.Stop.setObjectName("Stop")
        self.retranslateUi(Form)

        # 开始结束按钮监听器
        self.InitCard.clicked.connect(Form.on_input_confirm)
        self.Stop.clicked.connect(Form.stop)
        QtCore.QMetaObject.connectSlotsByName(Form)

        # # 开始按钮注册器
        # self.inputBtn = QtWidgets.QPushButton(Form)
        # self.inputBtn.setObjectName("inputBtn")
        # self.inputBtn.setGeometry(QtCore.QRect(20, 20, 100, 30))

        # 历史出牌记录
        self.HistoryLabel = QtWidgets.QLabel(Form)
        self.HistoryLabel.setGeometry(QtCore.QRect(20, 470, 200, 20))
        self.HistoryLabel.setText("History Cards Records")

        self.HistoryList = QtWidgets.QListWidget(Form)
        self.HistoryList.setGeometry(QtCore.QRect(20, 490, 400, 100))

        # 剩余牌数
        self.RemainingCardsLabel = QtWidgets.QLabel(Form)
        self.RemainingCardsLabel.setGeometry(QtCore.QRect(20, 600, 200, 20))
        self.RemainingCardsLabel.setText("Cards Remain")

        self.RemainingCardsText = QtWidgets.QLabel(Form)
        self.RemainingCardsText.setGeometry(QtCore.QRect(20, 590, 400, 160))

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Happy Landlord"))
        self.WinRate.setText(_translate("Form", "Win Rate：--%"))
        self.InitCard.setText(_translate("Form", "Start"))
        
        self.hand_input.setPlaceholderText(_translate("Form","Initial Hand Input"))
        self.landlord_input.setPlaceholderText(_translate("Form","Bottom Cards Input"))
        self.role_combo.addItems(["Upper Neighbour", "Landlord", "Lower Neighbour"]) 

        self.UserHandCards.hide()
        self.UserHandCards.setText(_translate("Form", "Initial Cards"))
        self.LPlayedCard.setText(_translate("Form", "Upper Cards"))
        self.RPlayedCard.setText(_translate("Form", "Lower Cards"))
        self.PredictedCard.setText(_translate("Form", "Perdiction"))
        self.ThreeLandlordCards.setText(_translate("Form", "Bottom cards"))
        self.Stop.setText(_translate("Form", "Stop"))

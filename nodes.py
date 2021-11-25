from lxml import etree
from owlready2 import *
from classes import *
import random

import re

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication,QGraphicsView, QGraphicsScene, QGraphicsEllipseItem,QGroupBox,QTreeWidgetItem
from PyQt5.QtCore import Qt, QPointF



class EntityRepresentation(QGroupBox):
    def __init__(self,x):
        super().__init__(x)
        self.attrib_list = None

    def add_attribute(self,text,data):

        attrib = QtWidgets.QListWidgetItem(parent= self.attrib_list)
        attrib.setText(text)








class Ui_MainWindow(object):
    def setupUi(self, MainWindow,app):

        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1527, 920)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(5)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.treeWidget = QtWidgets.QTreeWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.treeWidget.sizePolicy().hasHeightForWidth())
        self.treeWidget.setSizePolicy(sizePolicy)
        self.treeWidget.setMaximumSize(QtCore.QSize(14000, 16777215))
        self.treeWidget.setObjectName("treeWidget")
        self.treeWidget.headerItem().setText(0, "1")
        self.horizontalLayout.addWidget(self.treeWidget)
        self.rule_view = QtWidgets.QGroupBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(3)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.rule_view.sizePolicy().hasHeightForWidth())
        self.rule_view.setSizePolicy(sizePolicy)
        self.rule_view.setObjectName("rule_view")
        self.horizontalLayout.addWidget(self.rule_view)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1527, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)


        self.initialize()



    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.rule_view.setTitle(_translate("MainWindow", "RuleName"))


    def initialize(self):

        self.init_tree()
        self.entity_list = []


        pass

    def init_tree(self):
        self.treeWidget.setColumnCount(1)



        for concept_root in ConceptRoot.instances():
            item = QTreeWidgetItem([concept_root.has_for_name])
            item.data = concept_root
            self.treeWidget.addTopLevelItem(item)

            for concept in concept_root.has_concepts:
                child = QTreeWidgetItem([concept.has_for_name])
                child.data = concept
                item.addChild(child)

        self.treeWidget.itemClicked.connect(self.on_tree_clicked)


    def on_tree_clicked(self,item):

        obj = item.data
        for el in self.entity_list:
            el.setParent(None)

        self.entity_list= []

        if ConceptRoot.__instancecheck__(obj):
            pass

        if Concept.__instancecheck__(obj):
            self.rule_view.setTitle(obj.has_for_name)

            for rules in obj.has_template_rules:

                for rule in rules.has_template_rules:
                    print(rule)
                    paths = rule.path_list
                    self.import_visuals(paths)


    def import_visuals(self,paths):

        path = paths[-1]

        entity = None

        for element in path:
            if(ConceptTemplate.__instancecheck__(element)):

                entity = self.add_entity(element.has_for_applicable_entity,element)

                pass
            elif(EntityRule.__instancecheck__(element)):
                entity = self.add_entity(element.has_for_entity_name,element)
                pass
            elif(AttributeRule.__instancecheck__(element)):

                entity.add_attribute(element.has_for_attribute_name,element)


            else:
                self.add_label(element)
                pass


    def add_entity(self,name,data):





        el = self.entity_list

        entity =EntityRepresentation(self.rule_view)

        width = 200
        heigth = 75

        xpos = 25+len(el)*(width+25)
        ypos = 25



        entity.setGeometry(QtCore.QRect(xpos, ypos, width, heigth))
        entity.setObjectName(name)
        entity.setTitle(name)


        grid = QtWidgets.QGridLayout(entity)
        grid.setObjectName("internes_grid")
        entity.attrib_list = QtWidgets.QListWidget(entity)
        entity.attrib_list.setObjectName("Liste")
        grid.addWidget(entity.attrib_list, 0, 0, 1, 1)


        entity.show()

        self.entity_list.append(entity)





        return entity


    def add_label(self,inhalt):

        text = str(inhalt)

        entity_list = self.entity_list


        label = QtWidgets.QLabel(self.rule_view)

        label.setText(text)
        width = 200
        height = 50
        xpos = 25 + len(entity_list) * (width + 25)
        ypos = 50



        label.setGeometry(xpos,ypos,width,height)
        label.show()

        print(bool.__instancecheck__(inhalt))


        if bool.__instancecheck__(inhalt):
            if inhalt == True:
                color = "solid green"
            elif inhalt == False:
                color = "solid red"
            else:
                color = "solid blue"
        else:
            color = "solid black"

        label.setStyleSheet("border :3px "+color+";")



        entity_list.append(label)

        print(str(label.x())+":"+str(label.y()))



if __name__ == "__main__":
    import sys

    doc = "mvdXML_V1.1.xsd"
    file = "mvdXML_V1-1-Final-Documentation.xml"
    file2 = "bimq_rules.mvdxml"
    file3 = "RelAssociatesMaterial.mvdxml"
    mvd = MvdXml()
    #
    #
    mvd.import_xml(file=file3, doc=doc, validation=False)






    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow,app)
    MainWindow.show()
    sys.exit(app.exec_())


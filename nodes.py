from lxml import etree
from owlready2 import *
from classes import *
import random

import re

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication,QGraphicsView, QGraphicsScene, QGraphicsEllipseItem,QGroupBox,QTreeWidgetItem
from PyQt5.QtCore import Qt, QPointF


class connector(QtGui.QPainterPath):

    def __init__(self,x1,y1,x2,y2):
        super().__init__()

        self.x1 = x1
        self.x2=x2
        self.y1=y1
        self.y2=y2

    pass


class drag_box(QtWidgets.QGraphicsProxyWidget):

    def __init__(self,widget):
        super().__init__()
        self.setAcceptHoverEvents(True)
        self.setWidget(widget)
        self.connected_entities=[]


    def connect_to_entity(self,entity):

        if entity is not None:
            self.connected_entities.append(entity)

            scene = self.scene()
            rect1 = self.windowFrameGeometry()
            rect2 = entity.windowFrameGeometry()


            print(rect1)
            print(rect2)


            p1 = QPointF()
            p2 = QPointF()
            p1.setX(rect1.left())
            p1.setY(rect1.top()+rect1.height()/2)



            p2.setX(rect2.right())
            p2.setY(rect2.top()+rect2.height()/2)




            path = QtGui.QPainterPath()
            path.moveTo(p1)
            path.lineTo(p2)
            scene.addPath(path)

    def hoverEnterEvent(self,event):
        app.instance().setOverrideCursor(QtCore.Qt.OpenHandCursor)

    def hoverLeaveEvent(self,event):
        app.instance().restoreOverrideCursor()

    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        rect1 = self.windowFrameRect()
        print(rect1)

        # rect = self.windowFrameGeometry()
        #
        # center_left = (rect.bottomLeft()-rect.topLeft())/2
        # scene = self.scene()
        #
        # print(rect)
        # print(center_left)
        #
        # path = QtGui.QPainterPath()
        # path.currentPosition()
        # p1 = QPointF()
        # p2 = QPointF()
        # p1.setX(rect.left())
        # p1.setY(rect.top()+rect.height()/2)
        #
        # path.lineTo(p1)
        # scene.addPath(path)

        pass

    def mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        orig_cursor_position = event.lastScenePos()
        updated_cursor_position = event.scenePos()

        orig_position = self.scenePos()
        updated_cursor_x = updated_cursor_position.x() - orig_cursor_position.x()+orig_position.x()
        updated_cursor_y = updated_cursor_position.y() - orig_cursor_position.y()+orig_position.y()

        self.setPos(QPointF(updated_cursor_x,updated_cursor_y))



        pass

    def mouseReleaseEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
            pass

    pass

class EntityRepresentation(QGroupBox):

    def __init__(self,):
        super().__init__()
        self.attrib_list = None

    def add_attribute(self,text,data):

        attrib = QtWidgets.QListWidgetItem(parent= self.attrib_list)
        attrib.setText(text)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow,app):


        ### Fenster Aufbau

        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1920, 1080)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.base_layout = QtWidgets.QGridLayout(self.centralwidget)
        self.base_layout.setObjectName("baseLayout")

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
        self.treeWidget.setObjectName("RuleBrowser")
        self.treeWidget.headerItem().setText(0, "1")
        self.horizontalLayout.addWidget(self.treeWidget)

        self.rule_view = QtWidgets.QGroupBox()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(3)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.rule_view.sizePolicy().hasHeightForWidth())
        self.rule_view.setSizePolicy(sizePolicy)
        self.rule_view.setObjectName("rule_view")

        self.rule_view_grid = QtWidgets.QGridLayout(self.rule_view)
        self.rule_view_grid.setObjectName("rule_view_grid")


        self.scene = QGraphicsScene()
        self.graphicsView = QtWidgets.QGraphicsView(self.scene)
        self.graphicsView.setObjectName("graphicsView")
        self.rule_view_grid.addWidget(self.graphicsView, 0, 0, 1, 1)



        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.graphicsView.sizePolicy().hasHeightForWidth())
        self.graphicsView.setSizePolicy(sizePolicy)



        #print(self.graphicsView.width())







        self.horizontalLayout.addWidget(self.rule_view)
        self.base_layout.addLayout(self.horizontalLayout, 0, 0, 1, 1)
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
        MainWindow.show()

        width, height = self.rule_view.width()-50, self.rule_view.height()-50

        self.scene.setSceneRect(0, 0, width, height)

        self.init_tree()
        self.entity_list = []
        print(self.rule_view.width())

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
                    paths = rule.path_list
                    self.import_visuals(paths)


    def import_visuals(self,paths):

        path = paths[-1]

        entity = None
        proxy = None

        for element in path:
            if(ConceptTemplate.__instancecheck__(element)):

                proxy,entity = self.add_entity(element.has_for_applicable_entity,element,proxy)

                pass
            elif(EntityRule.__instancecheck__(element)):
                proxy,entity = self.add_entity(element.has_for_entity_name,element,proxy)
                pass
            elif(AttributeRule.__instancecheck__(element)):

                entity.add_attribute(element.has_for_attribute_name,element)


            else:
                self.add_label(element,proxy)
                pass


    def add_entity(self,name,data,old_proxy):

        el = self.entity_list

        entity =EntityRepresentation()

        proxy = drag_box(entity)






        self.scene.addItem(proxy)



        width = 200
        heigth = 50

        xpos = 25+len(el)*(width+25)
        ypos = 25

        proxy.setPos((QPointF(xpos,ypos)))
        proxy.resize(width,heigth)
        entity.setObjectName(name)
        entity.setTitle(name)

        proxy.connect_to_entity(old_proxy)

        grid = QtWidgets.QGridLayout(entity)
        grid.setObjectName("internes_grid")
        entity.attrib_list = QtWidgets.QListWidget(entity)
        entity.attrib_list.setObjectName("Liste")
        grid.addWidget(entity.attrib_list, 0, 0, 1, 1)


        entity.show()
        self.entity_list.append(entity)
        return proxy,entity


    def add_label(self,inhalt,old_proxy):

        text = str(inhalt)

        entity_list = self.entity_list


        label = QtWidgets.QLabel()
        proxy = drag_box(label)


        self.scene.addItem(proxy)
        label.setText(text)
        width = 200
        height = 50
        xpos = 25 + len(entity_list) * (width + 25)
        ypos = 50



        label.setGeometry(xpos,ypos,width,height)
        proxy.show()
        label.show()

        proxy.connect_to_entity(old_proxy)

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

        return proxy,label



if __name__ == "__main__":
    import sys

    doc = "mvdXML_V1.1.xsd"
    file = "Examples/mvdXML_V1-1-Final-Documentation.xml"
    file2 = "Examples/bimq_rules.mvdxml"
    file3 = "Examples/RelAssociatesMaterial.mvdxml"
    mvd = MvdXml()
    #
    #
    mvd.import_xml(file=file3, doc=doc, validation=False)






    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow,app)
    #MainWindow.show()
    sys.exit(app.exec_())


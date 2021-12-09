from lxml import etree
from owlready2 import *
from classes import *
import random

import re

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGroupBox, \
    QTreeWidgetItem
from PyQt5.QtCore import Qt, QPointF


class Attribute(QtWidgets.QLabel):

    def __init__(self):
        super().__init__()
        self.connections = []


class Connection():

    def __init__(self, attribute, right_proxy):
        self.scene = right_proxy.scene()
        self.attribute = attribute
        self.right_proxy = right_proxy

        self.points = self.get_pos()

        self.path = QtGui.QPainterPath()
        self.path.moveTo(self.points[0])
        self.path.cubicTo(self.points[1], self.points[2], self.points[3])

        self.line = QtWidgets.QGraphicsPathItem()
        self.line.setPath(self.path)
        self.scene.addItem(self.line)

    def get_pos(self):
        rectangle_right = self.right_proxy.windowFrameGeometry()

        attribute = self.attribute
        groupbox = attribute.parent()

        attribute_frame = attribute.geometry()
        groupbox_frame = groupbox.frameGeometry()

        x1 = groupbox_frame.x() + attribute_frame.x()
        y1 = groupbox_frame.y() + attribute_frame.y()

        rectangle_left = QtCore.QRectF(x1, y1, attribute_frame.width(), attribute_frame.height())

        pstart = QPointF()
        p2 = QPointF()
        p3 = QPointF()
        pend = QPointF()

        pstart.setX(rectangle_left.right())
        pstart.setY(rectangle_left.top() + rectangle_left.height() / 2)
        pend.setX(rectangle_right.left())
        pend.setY(rectangle_right.top() + rectangle_right.height() / 2)

        p2.setX(rectangle_left.right() + (rectangle_right.left() - rectangle_left.right()) / 2)
        p2.setY(pstart.y())

        p3.setX(p2.x())
        p3.setY(pend.y())

        return [pstart, p2, p3, pend]

    def update_line(self):
        self.points = self.get_pos()

        for i, el in enumerate(self.points):
            self.path.setElementPositionAt(i, el.x(), el.y())

        self.line.setPath(self.path)

    pass


class drag_box(QtWidgets.QGraphicsProxyWidget):

    def __init__(self, widget):
        super().__init__()
        self.setAcceptHoverEvents(True)
        self.setWidget(widget)
        self.connections = []
        self.lines = []

    def resizeEvent(self, event):
        try:
            for el in self.connections:
                el.update_line()
        except:
            pass

    def connect_to_entity(self, entity):

        if entity is not None:
            con = Connection(entity, self)
            self.connections.append(con)
            entity.parent().graphicsProxyWidget().connections.append(con)

    def hoverEnterEvent(self, event):
        app.instance().setOverrideCursor(QtCore.Qt.OpenHandCursor)

    def hoverLeaveEvent(self, event):
        app.instance().restoreOverrideCursor()

    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        rect1 = self.windowFrameRect()
        groupbox = self.widget()
        print(groupbox.frameGeometry())
        pass

    def mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        orig_cursor_position = event.lastScenePos()
        updated_cursor_position = event.scenePos()

        orig_position = self.scenePos()
        updated_cursor_x = updated_cursor_position.x() - orig_cursor_position.x() + orig_position.x()
        updated_cursor_y = updated_cursor_position.y() - orig_cursor_position.y() + orig_position.y()

        self.setPos(QPointF(updated_cursor_x, updated_cursor_y))

        for el in self.connections:
            el.update_line()

        pass

    def mouseReleaseEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        pass

    pass


class EntityRepresentation(QGroupBox):

    def __init__(self, ):
        super().__init__()
        self.qlayout = QtWidgets.QVBoxLayout()
        self.connections = []
        self.setLayout(self.qlayout)

    def add_attribute(self, text, data):
        attrib = Attribute()
        attrib.setText(text)
        self.qlayout.addWidget(attrib)
        attrib.setFrameStyle(1)

        return attrib


class Ui_MainWindow(object):

    def setupUi(self, MainWindow, app):

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
        self.treeWidget.headerItem().setText(0, "Regeln")
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
        width, height = self.rule_view.width() - 50, self.rule_view.height() - 50

        self.scene.setSceneRect(0, 0, width, height)

        self.init_tree()
        self.entity_list = []

        pass

    def init_tree(self):
        self.treeWidget.setColumnCount(1)

        for concept_root in ConceptRoot.instances():

            name = concept_root.has_for_name

            if name == "":
                name = "undefined"

            item = QTreeWidgetItem([name])
            item.data = concept_root
            self.treeWidget.addTopLevelItem(item)

            for concept in concept_root.has_concepts:
                child = QTreeWidgetItem([concept.has_for_name])
                child.data = concept
                item.addChild(child)

        self.treeWidget.itemClicked.connect(self.on_tree_clicked)

    def on_tree_clicked(self, item):

        obj = item.data

        for el in self.scene.items():
            self.scene.removeItem(el)

        if ConceptRoot.__instancecheck__(obj):
            pass

        if Concept.__instancecheck__(obj):
            self.rule_view.setTitle(obj.has_for_name)

            for rules in obj.has_template_rules:

                for i, rule in enumerate(rules.has_template_rules):
                    if i == 0:  # TODO: Iteration entfernen
                        self.entity_list = []
                        paths = rule.path_list
                        self.import_visuals(paths, i)

    def import_visuals(self, paths, index):

        created_entities = []
        proxy_dict = {}
        entity_dict = {}
        for path in paths:
            for i, element in enumerate(path):

                last_item_index = i - 1
                if last_item_index >= 0:
                    last_item = path[last_item_index]
                else:
                    last_item = None

                if element not in created_entities:
                    proxy = proxy_dict.get(last_item)

                    if (ConceptTemplate.__instancecheck__(element)):

                        proxy_dict[element] = self.add_entity(element.has_for_applicable_entity, element, proxy, 0)

                        pass
                    elif (EntityRule.__instancecheck__(element)):
                        proxy_dict[element] = self.add_entity(element.has_for_entity_name, element, proxy, 0)
                        pass
                    elif (AttributeRule.__instancecheck__(element)):

                        proxy_dict[element] = proxy.widget().add_attribute(element.has_for_attribute_name, element)


                    else:
                        proxy_dict[element] = self.add_label(element, proxy, 0)
                        pass

                    created_entities.append(element)

        for proxy in proxy_dict:

            proxy = proxy_dict[proxy]
            if drag_box.__instancecheck__(proxy):
                for child in proxy.widget().children():
                    print(child.geometry())

            for connection in proxy.connections:
                connection.update_line()

    def add_entity(self, name, data, old_proxy, index):

        el = self.entity_list
        proxy = drag_box(EntityRepresentation())
        self.scene.addItem(proxy)

        ## size ##
        width = 200
        heigth = 50
        xpos = 25 + len(el) * (width + 25)
        ypos = 25 + index * 200

        proxy.setPos((QPointF(xpos, ypos)))
        proxy.resize(width, heigth)

        proxy.widget().setObjectName(name)
        proxy.widget().setTitle(name)

        self.entity_list.append(proxy.widget())
        proxy.connect_to_entity(old_proxy)
        return proxy

    def add_label(self, inhalt, old_proxy, index):

        text = str(inhalt)

        entity_list = self.entity_list

        label = QtWidgets.QLabel()
        label.setText(text)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred,
                                           type=QtWidgets.QSizePolicy.Label)
        label.setSizePolicy(sizePolicy)
        proxy = drag_box(label)

        self.scene.addItem(proxy)
        width = 200
        height = 50
        xpos = 25 + len(entity_list) * (width + 25)
        ypos = 50 + index * 200

        label.setGeometry(xpos, ypos, width, height)

        if bool.__instancecheck__(inhalt):
            if inhalt == True:
                color = "solid green"
            elif inhalt == False:
                color = "solid red"
            else:
                color = "solid blue"
        else:
            color = "solid black"

        label.setStyleSheet("border :3px " + color + ";")

        entity_list.append(label)

        proxy.connect_to_entity(old_proxy)

        return proxy


if __name__ == "__main__":
    import sys

    doc = "mvdXML_V1.1.xsd"
    file = "Examples/mvdXML_V1-1-Final-Documentation.xml"
    file2 = "Examples/bimq_rules.mvdxml"
    file3 = "Examples/RelAssociatesMaterial.mvdxml"
    mvd = MvdXml()
    #
    #
    mvd.import_xml(file=file, doc=doc, validation=False)

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow, app)
    # MainWindow.show()

    sys.exit(app.exec_())

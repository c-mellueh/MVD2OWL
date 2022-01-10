from lxml import etree
from owlready2 import *
from classes import *
import random

import re

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGroupBox, \
    QTreeWidgetItem,QTreeWidget
from PySide6.QtCore import Qt, QPointF



class Template_Rule_Rectangle(QGraphicsView):
    def __init__(self,parent_scene,paths,metrics,index):

        scene = QGraphicsScene()
        super().__init__(scene)
        self.setContentsMargins(0,0,0,0)


        self.setObjectName("Template Rule {0}".format(index))

        self.parent_scene = parent_scene
        self.import_visuals(paths,metrics,index)
        parent_scene.addWidget(self)
        print(self.pos())

        self.move(50,50)
        print(self.rect())
        self.add_title(self.objectName())

        #self.setAcceptHoverEvents(True)



    pass

    def import_visuals(self, paths,metrics, index):

        created_entities = []
        graphical_items_dict = {}

        template_rule_scene =self.scene()


        for k,path in enumerate(paths):
            metric = metrics[k]
            last_item = None

            for i, path_item in enumerate(path):

                if path_item not in created_entities:
                    last_block = graphical_items_dict.get(last_item)

                    if (isinstance(path_item, (ConceptTemplate, EntityRule))):
                        block = self.add_block(template_rule_scene,path_item,last_block)
                        graphical_items_dict[path_item] = block
                        created_entities.append(path_item)
                        pass

                    elif isinstance(path_item,AttributeRule):
                        groupbox = last_block.widget()
                        attribute_label = groupbox.add_attribute(path_item) # returns QLabel housed in QGroupBox
                        graphical_items_dict[path_item] = attribute_label
                        created_entities.append(path_item)

                    else:
                        graphical_items_dict[path_item] = self.add_label(template_rule_scene,path_item, last_block, metric)

                last_item =path_item

    def add_block(self,scene, data,last_block):

        if isinstance(data, ConceptTemplate):
            name = data.has_for_applicable_entity
        elif isinstance(data, EntityRule):
            name = data.has_for_entity_name

        block = DragBox(EntityRepresentation(name),self)


        ## size ##
        if last_block is not None:
            xpos = last_block.parent().pos().x()+220
        else:
            xpos = 25
        ypos = 50

        block.setPos((QPointF(xpos, ypos)))
        scene.addItem(block)

        block.connect_to_entity(last_block)

        return block

    def add_label(self,scene, inhalt, old_proxy, metric):

        text = str(inhalt)


        label = LabelRepresentation()
        label.setText(text)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred,
                                           type=QtWidgets.QSizePolicy.Label)
        label.setSizePolicy(sizePolicy)
        proxy = DragBox(label,self)

        scene.addItem(proxy)
        width = 100
        height = 50
        xpos = old_proxy.parent().pos().x()+225
        ypos = 150

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


        proxy.connect_to_entity(old_proxy,metric)

        return proxy

    def add_title(self,title):

        scene_rect = self.sceneRect()
        width = scene_rect.width()
        pos = self.pos()
        self.top_rect = self.title_block(pos.x(),pos.y()-25,width
                             ,25,self)

        brush = QtGui.QBrush()
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        color = QtGui.QColor("grey")
        brush.setColor(color)
        self.top_rect.setBrush(brush)

        self.parent_scene.addItem(self.top_rect)

    class title_block(QtWidgets.QGraphicsRectItem):
        def __init__(self,x,y,w,h,view: QGraphicsView):
            super().__init__(x,y,w,h)
            self.setAcceptHoverEvents(True)
            self.graphical_view=view
        pass

        def hoverEnterEvent(self, event):
            app.instance().setOverrideCursor(QtCore.Qt.OpenHandCursor)

        def hoverLeaveEvent(self, event):
            app.instance().restoreOverrideCursor()

        def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
            pass

        def mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
            orig_cursor_position = event.lastScenePos()
            updated_cursor_position = event.scenePos()

            x_dif = updated_cursor_position.x() - orig_cursor_position.x()
            y_dif= updated_cursor_position.y() - orig_cursor_position.y()

            self.graphical_view.move(self.graphical_view.pos().x()+x_dif,self.graphical_view.pos().y()+y_dif)
            self.moveBy(x_dif,y_dif)
            print(x_dif,y_dif)

        def mouseReleaseEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
            pass



class Attribute(QtWidgets.QLabel):

    def __init__(self,text):
        super().__init__()
        self.setText(text)
        self.connections = []
        self.setFrameStyle(1)

    def __str__(self):
        return "[Attribut] {0}".format(self.text())

class Connection():

    def __init__(self, attribute, right_proxy,metric):

        self.label = None
        self.attribute = attribute
        self.right_proxy = right_proxy
        self.metric = metric
        self.scene = self.right_proxy.scene()

        self.create_line()
        self.create_text()

    def __str__(self):
        return "{0}->{1}".format(self.attribute,self.right_proxy)

    def create_line(self):
        self.points = self.get_pos()
        self.path = QtGui.QPainterPath()
        self.path.moveTo(self.points[0])
        self.path.cubicTo(self.points[1], self.points[2], self.points[3])
        self.line = QtWidgets.QGraphicsPathItem()
        self.line.setPath(self.path)
        self.scene.addItem(self.line)

    def create_text(self):
        if self.metric != "":
            self.center = self.path.boundingRect().center()
            self.label =QtWidgets.QGraphicsTextItem()
            self.label.setHtml("<div style='background-color:#FFFFFF;'>" + str(self.metric)+ "</div>")


            self.scene.addItem(self.label)
            width = self.label.boundingRect().width()
            height = self.label.boundingRect().height()
            movement = QPointF(width,height)/2
            self.label.setPos(self.center-movement)


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

    def update(self):
        ## Update Curve Position
        self.points = self.get_pos()

        for i, el in enumerate(self.points):
            self.path.setElementPositionAt(i, el.x(), el.y())

        self.line.setPath(self.path)

        ## Update Label
        if self.label is not None:
            self.center = self.path.boundingRect().center()
            width = self.label.boundingRect().width()
            height = self.label.boundingRect().height()
            movement = QPointF(width,height)/2
            self.label.setPos(self.center-movement)

    pass


class DragBox(QtWidgets.QGraphicsProxyWidget):
    #is needed to house QGroupBoxy (EntityRepresentation)

    def __init__(self, widget,top):
        super().__init__()
        self.setAcceptHoverEvents(True)
        self.setWidget(widget)
        self.connections = []
        self.top =top

    def __str__(self):
        return str(self.widget())

    def connect_to_entity(self, attribute,metric = ""):

        if attribute is not None:
            con = Connection(attribute,self,metric)

            self.connections.append(con)
            attribute.parent().graphicsProxyWidget().connections.append(con)

    def hoverEnterEvent(self, event):
        app.instance().setOverrideCursor(QtCore.Qt.OpenHandCursor)

    def hoverLeaveEvent(self, event):
        app.instance().restoreOverrideCursor()

    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        pass

    def mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        orig_cursor_position = event.lastScenePos()
        updated_cursor_position = event.scenePos()

        orig_position = self.scenePos()
        updated_cursor_x = updated_cursor_position.x() - orig_cursor_position.x() + orig_position.x()
        updated_cursor_y = updated_cursor_position.y() - orig_cursor_position.y() + orig_position.y()


        # if updated_cursor_y <0:
        #     updated_cursor_y=0
        # if updated_cursor_x <0:
        #     updated_cursor_x=0
        #
        # if updated_cursor_y+self.geometry().height()>self.scene().height():
        #     updated_cursor_y=self.scene().height()-self.geometry().height()
        # if updated_cursor_x+self.geometry().width()>self.scene().width():
        #     updated_cursor_x=self.scene().width()-self.geometry().width()

        self.setPos(QPointF(updated_cursor_x, updated_cursor_y))

        for el in self.connections:
            el.update()
        #
        # view = self.scene().views()[0]
        # bound = view.scene().itemsBoundingRect()
        # bound.setWidth(bound.width()+50)
        # bound.setHeight(bound.height()+50)
        # view.centerOn(bound.center())

        # print("{0}:{1}".format(bound.width(),bound.height()))
        # view.resize(bound.width(),bound.height())



    def mouseReleaseEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        pass

    pass

class EntityRepresentation(QGroupBox):

    """ Widget in DragBox"""

    def __init__(self, title):

        super().__init__()
        self.qlayout = QtWidgets.QVBoxLayout()  #Layout for lining up all the Attributes
        self.setLayout(self.qlayout)
        self.setTitle(title)
        self.alignment()
        self.setStyleSheet('QGroupBox:title {'
                 'subcontrol-origin: margin;'
                 'subcontrol-position: top center;'
                 'padding-left: 10px;'
                 'padding-right: 10px; }')

    def __str__(self):
        return "Entity:{0}".format(self.title())

    def add_attribute(self, data):

        text = data.has_for_attribute_name
        attrib = Attribute(text)
        self.qlayout.addWidget(attrib)
        attrib.show()
        return attrib

class LabelRepresentation(QtWidgets.QLabel):
    def __str__(self):
        return "[Label] {0}".format(self.text())

class Ui_MainWindow(object):

    def setupUi(self, MainWindow, app):

        ### Fenster Aufbau

        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1920, 1080)

        # Base for Columns
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.base_layout = QtWidgets.QGridLayout(self.centralwidget)
        self.base_layout.setObjectName("baseLayout")
        MainWindow.setCentralWidget(self.centralwidget)

        # Columns Layout for Treelist nad Object window
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(5)
        self.horizontalLayout.setObjectName("horizontalLayout")

        # Inhalt in Fenster hinzufügen
        self.base_layout.addLayout(self.horizontalLayout, 0, 0, 1, 1)

        # Tree Widget
        self.treeWidget = QtWidgets.QTreeWidget(self.centralwidget)

        # Set Size Policy for TreeWidget
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.treeWidget.sizePolicy().hasHeightForWidth())
        self.treeWidget.setSizePolicy(sizePolicy)
        self.treeWidget.setObjectName("RuleBrowser")
        self.treeWidget.headerItem().setText(0, "Regeln")

        self.horizontalLayout.addWidget(self.treeWidget)

        # Object Window
        self.scene = QGraphicsScene()
        self.graphicsView = QtWidgets.QGraphicsView(self.scene)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(3)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.graphicsView.sizePolicy().hasHeightForWidth())
        self.graphicsView.setSizePolicy(sizePolicy)
        self.graphicsView.setObjectName("graphicsView")

        self.horizontalLayout.addWidget(self.graphicsView)

        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1527, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)

        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        MainWindow.show()
        self.initialize()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MVD2Onto"))

    def initialize(self):
        width, height = self.graphicsView.width(), self.graphicsView.height()
        self.scene.setSceneRect(0, 0, width, height)
        self.init_tree()

    def init_tree(self):
        self.treeWidget.setColumnCount(1)

        items = []
        for concept_root in ConceptRoot.instances():
            name = concept_root.has_for_name
            print(name)

            if name == "":
                name = "undefined"


            item = QTreeWidgetItem(self.treeWidget,[name])
            item.konzept = concept_root
            self.treeWidget.addTopLevelItem(item)

            for concept in concept_root.has_concepts:
                child = QTreeWidgetItem(item,[concept.has_for_name])
                child.konzept = concept

        self.treeWidget.itemClicked.connect(self.on_tree_clicked)

    def on_tree_clicked(self, item):

        obj = item.konzept
        print("Hier",type(obj))
        for el in self.scene.items():
            self.scene.removeItem(el)

        rect = QtWidgets.QGraphicsRectItem(0,0,self.scene.width(),self.scene.height())
        self.scene.addItem(rect)

        if isinstance(obj,ConceptRoot):
            pass

        if isinstance(obj,Concept):

            for rules in obj.has_template_rules:

                for i, rule in enumerate(rules.has_template_rules):
                    if i == 0:  # TODO: Iteration entfernen
                        paths,metrics = rule.get_linked_rules()
                        graphicsView = Template_Rule_Rectangle(self.scene, paths, metrics, i)





if __name__ == "__main__":
    import sys

    doc = "mvdXML_V1.1.xsd"
    file = "Examples/mvdXML_V1-1-Final-Documentation.xml"
    file2 = "Examples/bimq_rules.mvdxml"
    file3 = "Examples/RelAssociatesMaterial.xml"
    mvd = MvdXml()
    mvd.import_xml(file=file3, doc=doc, validation=False)

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow, app)

    sys.exit(app.exec_())

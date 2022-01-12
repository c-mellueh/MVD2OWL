from core import *
from typing import Union
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtWidgets import *
from PySide6.QtCore import QPointF
from random import random

# Constants 
BORDER = 5


class testView(QGraphicsView):


    def wheelEvent(self, event:QtGui.QWheelEvent) -> None:
        point = event.angleDelta() / 4
        val = point.y()

        modifier = QApplication.keyboardModifiers()

        if bool(modifier==QtCore.Qt.ControlModifier):


            if val <0:
                self.scale(0.9,0.9)
            else:
                self.scale(1.1,1.1)

        elif bool(modifier==QtCore.Qt.ShiftModifier):


            hor = self.horizontalScrollBar()
            hor.setValue(hor.value() - val)

        else:

            ver = self.verticalScrollBar()


            ver.setValue(ver.value() -val)

        self.update()


class TemplateRuleRectangle(QGraphicsView):
    def __init__(self, parent_scene, paths, metrics, position: QPointF,data: TemplateRule):

        super().__init__()
        scene = QGraphicsScene()
        self.setScene(scene)
        self.move(position)

        self.data =data
        self.parent_scene = parent_scene
        self.import_visuals(paths, metrics)

        width = self.sceneRect().width() + 20
        height = self.sceneRect().height() + 20

        self.setGeometry(position.x(), position.y(), width, height)
        self.setSceneRect(-10, -10, width, height)
        self.add_title()
        self.turn_off_scrollbar()

    def import_visuals(self, paths, metrics):

        created_entities = []
        graphical_items_dict = {}

        template_rule_scene = self.scene()

        # for k, path in enumerate(paths):


        for k,path in enumerate(paths):

            metric = metrics[k]
            last_item = None

            for i, path_item in enumerate(path):

                if path_item not in created_entities:
                    last_block = graphical_items_dict.get(last_item)

                    if isinstance(path_item, (ConceptTemplate, EntityRule)):

                        block = self.add_block(template_rule_scene, path_item, last_block)
                        template_rule_scene.addItem(block)
                        block.connect_to_entity(last_block)

                        graphical_items_dict[path_item] = block
                        created_entities.append(path_item)
                        pass

                    elif isinstance(path_item, AttributeRule):
                        groupbox = last_block.widget()
                        attribute_label = groupbox.add_attribute(path_item)  # returns QLabel housed in QGroupBox
                        graphical_items_dict[path_item] = attribute_label
                        created_entities.append(path_item)

                    else:
                        graphical_items_dict[path_item] = self.add_label(template_rule_scene, path_item, last_block,
                                                                         metric)

                last_item = path_item



    def add_block(self, scene, data, last_block):

        name = "undefined"

        if isinstance(data, ConceptTemplate):
            name = data.has_for_applicable_entity
        elif isinstance(data, EntityRule):
            name = data.has_for_entity_name

        block = DragBox(EntityRepresentation(name), self)

        # size
        if last_block is not None and not isinstance(last_block, DragBox):
            xpos = last_block.parent().pos().x() + 220
        elif isinstance(last_block, DragBox):
            xpos = last_block.pos().x() + 220
        else:
            xpos = 0
        ypos = 0

        block.setPos((QPointF(xpos, ypos)))
        return block

    def add_label(self, scene, inhalt, old_proxy, metric):

        text = str(inhalt)
        label_ = LabelRepresentation()
        label_.setText(text)
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred,
                                            type=QtWidgets.QSizePolicy.Label)
        label_.setSizePolicy(size_policy)
        proxy = DragBox(label_, self)
        scene.addItem(proxy)
        width = 100
        height = 50
        xpos = old_proxy.parent().pos().x() + 225
        ypos = 150

        label_.setGeometry(xpos, ypos, width, height)

        if isinstance(inhalt, bool):
            if inhalt:
                color = "solid green"
            else:
                color = "solid red"
        else:
            color = "solid blue"

        label_.setStyleSheet("border :2px " + color + ";")
        proxy.connect_to_entity(old_proxy, metric)

        return proxy

    def add_title(self):

        scene_rect = self.sceneRect()
        width = scene_rect.width()
        pos = self.pos()
        self.TitleBlock = TitleBlock(pos.x(), pos.y() - 25, width, 25, self, "TemplateRule")

        brush = QtGui.QBrush()
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        color = QtGui.QColor("grey")
        brush.setColor(color)
        self.TitleBlock.setBrush(brush)
        self.parent_scene.addItem(self.TitleBlock)
        return self.TitleBlock

    def turn_off_scrollbar(self):
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)


class TemplateRulesRectangle(QGraphicsView):

    def __init__(self, parent_scene: QGraphicsScene, position: QPointF, data: TemplateRules):

        scene = QGraphicsScene()
        super().__init__()
        self.setScene(scene)
        self.setContentsMargins(0, 0, 0, 0)
        self.move(position)
        self.data = data
        self.operator = self.data.has_for_operator
        self.parent_scene = parent_scene

        self.turn_off_scrollbar()



    def add_title(self):

        scene_rect = self.sceneRect()
        width = scene_rect.width()
        pos = self.pos()
        self.TitleBlock = TitleBlock(pos.x(), pos.y() - 25, width, 25, self, self.operator)

        brush = QtGui.QBrush()
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)

        if self.operator == "or":
            color = "blue"
        elif self.operator == "and":
            color = "green"
        elif self.operator == "nor":
            color = "red"
        else:
            color = "grey"

        brush.setColor(QtGui.QColor(color))
        pen = QtGui.QPen()

        pen.setColor(color)
        view = self.scene().views()[0]

        view.setFrameStyle(QFrame.Box)
        view.setLineWidth(2)
        style = "border: 2px solid {};".format(color)
        view.setStyleSheet(style)

        self.TitleBlock.setBrush(brush)
        self.TitleBlock.setZValue(0)

        self.parent_scene.addItem(self.TitleBlock)
        return self.TitleBlock

    def turn_off_scrollbar(self):
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

    def wheelEvent(self, event:QtGui.QWheelEvent) -> None:
        ui.graphicsView.wheelEvent(event)

        pass


class TitleBlock(QtWidgets.QGraphicsRectItem):
    def __init__(self, x, y, w, h, view: Union[TemplateRulesRectangle, TemplateRuleRectangle], text: str):
        super().__init__(x, y, w, h)
        self.setAcceptHoverEvents(True)
        self.graphical_view = view

        self.text = QtWidgets.QGraphicsTextItem(text.upper())

        self.graphical_view.parent_scene.addItem(self.text)
        self.text.setPos(x, y)
        self.text.setDefaultTextColor("white")

        font = QtGui.QFont()
        font.setBold(True)

        self.text.setFont(font)
        self.text.setZValue(1)

    pass

    def hoverEnterEvent(self, event):
        application.instance().setOverrideCursor(QtCore.Qt.OpenHandCursor)

    def hoverLeaveEvent(self, event):
        application.instance().restoreOverrideCursor()

    def mousePressEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        application.instance().setOverrideCursor(QtCore.Qt.OpenHandCursor)
        pass

    def mouseMoveEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        orig_cursor_position = event.lastScenePos()
        updated_cursor_position = event.scenePos()

        x_dif = updated_cursor_position.x() - orig_cursor_position.x()
        y_dif = updated_cursor_position.y() - orig_cursor_position.y()

        self.graphical_view.move(self.graphical_view.pos().x() + x_dif, self.graphical_view.pos().y() + y_dif)
        self.moveBy(x_dif, y_dif)
        self.text.moveBy(x_dif, y_dif)

    def mouseReleaseEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        application.instance().restoreOverrideCursor()

        pass


class Attribute(QtWidgets.QLabel):

    def __init__(self, text):
        super().__init__()
        self.setText(text)
        self.connections = []
        self.setFrameStyle(1)

    def __str__(self):
        return "[Attribut] {0}".format(self.text())


class Connection:

    liste =[]

    def __init__(self, attribute, right_proxy, metric):


        self.label = None
        self.attribute = attribute
        self.right_proxy = right_proxy
        self.metric = metric
        self.scene = self.right_proxy.scene()

        self.create_line()
        self.create_text()

        Connection.liste.append(self)


    def __str__(self):
        return "Connection [{0}->{1}]".format(self.attribute, self.right_proxy)

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
            self.label = QtWidgets.QGraphicsTextItem()
            self.label.setHtml("<div style='background-color:#FFFFFF;'>" + str(self.metric) + "</div>")

            self.scene.addItem(self.label)
            width = self.label.boundingRect().width()
            height = self.label.boundingRect().height()
            movement = QPointF(width, height) / 2
            self.label.setPos(self.center - movement)

    def get_pos(self):
        rectangle_right = self.right_proxy.windowFrameGeometry()
        attribute = self.attribute
        if isinstance(attribute, DragBox):
            rectangle_left = attribute.windowFrameGeometry()
        else:
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
        pend.setY(rectangle_right.top() + 15)

        p2.setX(rectangle_left.right() + (rectangle_right.left() - rectangle_left.right()) / 2)
        p2.setY(pstart.y())

        p3.setX(p2.x())
        p3.setY(pend.y())

        return [pstart, p2, p3, pend]

    def update(self):
        # Update Curve Position
        self.points = self.get_pos()

        for i, el in enumerate(self.points):
            self.path.setElementPositionAt(i, el.x(), el.y())

        self.line.setPath(self.path)

        # Update Label
        if self.label is not None:
            self.center = self.path.boundingRect().center()
            width = self.label.boundingRect().width()
            height = self.label.boundingRect().height()
            movement = QPointF(width, height) / 2
            self.label.setPos(self.center - movement)

        return self.points


class DragBox(QtWidgets.QGraphicsProxyWidget):
    # is needed to house QGroupBoxy (EntityRepresentation)

    def __init__(self, widget, top):
        super().__init__()

        if isinstance(widget,EntityRepresentation):
            widget.helper=self

        self.setAcceptHoverEvents(True)
        self.setWidget(widget)
        self.connections = []
        self.top = top

    def __str__(self):
        w = self.widget()
        return "[Dragbox: {}]".format(w)

    def connect_to_entity(self, attribute, metric=""):

        if attribute is not None:
            con = Connection(attribute, self, metric)
            self.connections.append(con)
            if isinstance(attribute, DragBox):
                 attribute.connections.append(con)
            else:
                 par = attribute.parent()
                 proxy = par.helper
                 proxy.connections.append(con)

    def hoverEnterEvent(self, event):
        application.instance().setOverrideCursor(QtCore.Qt.OpenHandCursor)

    def hoverLeaveEvent(self, event):
        application.instance().restoreOverrideCursor()

    def mousePressEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        application.instance().setOverrideCursor(QtCore.Qt.OpenHandCursor)
        pass

    def mouseMoveEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        orig_cursor_position = event.lastScenePos()
        updated_cursor_position = event.scenePos()

        orig_position = self.scenePos()
        updated_cursor_x = updated_cursor_position.x() - orig_cursor_position.x() + orig_position.x()
        updated_cursor_y = updated_cursor_position.y() - orig_cursor_position.y() + orig_position.y()

        if self.check_for_exit(updated_cursor_x, "x"):
            updated_cursor_x = orig_position.x()
        if self.check_for_exit(updated_cursor_y, "y"):
            updated_cursor_y = orig_position.y()

        self.setPos(QPointF(updated_cursor_x, updated_cursor_y))

        for el in self.connections:
            el.update()

    def check_for_exit(self, value, direction: str):

        if not (direction == "x" or direction == "y"):
            raise (AttributeError("Direction needs to be 'x' or 'y'"))

        if value < 0:
            return True
        elif direction == "x":
            if value > self.scene().width() - self.geometry().width():
                return True
        elif direction == "y":
            if value > self.scene().height() - self.geometry().height():
                return True
        else:
            return False

    def mouseReleaseEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        application.instance().restoreOverrideCursor()

    pass


class EntityRepresentation(QFrame):
    """ Widget in DragBox"""

    def __init__(self, title:str):
        super().__init__()
        self.helper =None
        self.title = title
        self.setLayout(QtWidgets.QVBoxLayout())
        self.setStyleSheet('QGroupBox:title {'
                           'subcontrol-origin: margin;'
                           'subcontrol-position: top center;'
                           'padding-left: 10px;'
                           'padding-right: 10px; }')

        self.setObjectName(str(random()*1000))

        self.title_widget = QtWidgets.QLabel(self.title)
        self.layout().addWidget(self.title_widget)

    def __str__(self):
        return "[EntityRepresentation: {}]".format(self.title)

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        #self.update_title(self.title)
        pass

    def add_attribute(self, data):

        text = data.has_for_attribute_name
        attrib = Attribute(text)
        self.layout().addWidget(attrib)
        attrib.show()
        return attrib

    def update_title(self, title):
        self.title = title


class LabelRepresentation(QtWidgets.QLabel):
    def __str__(self):
        return "[Label: {0}]".format(self.text())


class UiMainWindow(object):


    def setup_ui(self, main_window):

        # Fenster Aufbau

        main_window.setObjectName("MainWindow")
        main_window.resize(1920, 1080)

        # Base for Columns
        self.centralwidget = QtWidgets.QWidget(main_window)
        self.centralwidget.setObjectName("centralwidget")
        self.base_layout = QtWidgets.QGridLayout(self.centralwidget)
        self.base_layout.setObjectName("baseLayout")
        main_window.setCentralWidget(self.centralwidget)

        # Columns Layout for Treelist nad Object window
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(5)
        self.horizontalLayout.setObjectName("horizontalLayout")

        # Inhalt in Fenster hinzufügen
        self.base_layout.addLayout(self.horizontalLayout, 0, 0, 1, 1)

        # Tree Widget
        self.treeWidget = QtWidgets.QTreeWidget(self.centralwidget)

        # Set Size Policy for TreeWidget
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        size_policy.setHorizontalStretch(1)
        size_policy.setVerticalStretch(1)
        size_policy.setHeightForWidth(self.treeWidget.sizePolicy().hasHeightForWidth())
        self.treeWidget.setSizePolicy(size_policy)
        self.treeWidget.setObjectName("RuleBrowser")
        self.treeWidget.headerItem().setText(0, "Regeln")

        self.horizontalLayout.addWidget(self.treeWidget)

        # Object Window
        self.scene = QGraphicsScene()
        self.graphicsView = testView(self.scene)
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        size_policy.setHorizontalStretch(3)
        size_policy.setVerticalStretch(1)
        size_policy.setHeightForWidth(self.graphicsView.sizePolicy().hasHeightForWidth())
        self.graphicsView.setSizePolicy(size_policy)
        self.graphicsView.setObjectName("graphicsView")

        self.horizontalLayout.addWidget(self.graphicsView)

        self.menubar = QtWidgets.QMenuBar(main_window)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1527, 22))
        self.menubar.setObjectName("menubar")
        main_window.setMenuBar(self.menubar)

        self.statusbar = QtWidgets.QStatusBar(main_window)
        self.statusbar.setObjectName("statusbar")
        main_window.setStatusBar(self.statusbar)

        self.retranslate_ui(main_window)
        QtCore.QMetaObject.connectSlotsByName(main_window)

        main_window.show()

        self.initialize()

    @staticmethod
    def retranslate_ui(main_window):
        _translate = QtCore.QCoreApplication.translate
        main_window.setWindowTitle(_translate("MainWindow", "MVD2Onto"))

    def initialize(self):
        self.treeWidget.setColumnCount(1)
        for concept_root in ConceptRoot.instances():
            name = concept_root.has_for_name

            if name == "":
                name = "undefined"

            item = QTreeWidgetItem(self.treeWidget, [name])
            item.konzept = concept_root
            self.treeWidget.addTopLevelItem(item)

            for concept in concept_root.has_concepts:
                child = QTreeWidgetItem(item, [concept.has_for_name])
                child.konzept = concept

        self.treeWidget.itemClicked.connect(self.on_tree_clicked)


    def on_tree_clicked(self, item):

        obj = item.konzept
        self.scene.clear()

        if isinstance(obj, ConceptRoot):
            pass

        if isinstance(obj, Concept):

            for index, rules in enumerate(obj.has_template_rules):
                self.loop_through_rules(rules, self.scene)

        for el in Connection.liste:
            print("HIER",el)
            print(el.update())


    def print_tree(self):
        for gv in self.scene.items():
            if not isinstance(gv, TitleBlock | QtWidgets.QGraphicsTextItem | QtWidgets.QGraphicsProxyWidget):
                print("{} Other Element {}".format("", gv))
            if isinstance(gv,TitleBlock):

                title_text = gv.text.toPlainText()

            if isinstance(gv,QtWidgets.QGraphicsProxyWidget):
                gv = gv.widget()

                self.print_scenes(gv,"",title_text)
        print("----------------------------")


    def print_scenes(self, gv:TemplateRulesRectangle ,text,title_text):


        print("{} {} Graphic View {}".format(text,title_text,gv))
        text += "   "

        title_text =""

        for el in  gv.scene().items():

            if not isinstance(el,TitleBlock|QtWidgets.QGraphicsTextItem|QtWidgets.QGraphicsProxyWidget):
                print("{} Other Element {}".format(text, el))

            if isinstance(el,TitleBlock):

                title_text = el.text.toPlainText()

            if isinstance(el,QtWidgets.QGraphicsProxyWidget) and isinstance(el.widget(), TemplateRulesRectangle):
                el = el.widget()

                if el is not None:
                    pass
                    #self.print_scenes(el,text,title_text)

            elif(isinstance(el,QtWidgets.QGraphicsProxyWidget)):
                if isinstance(el.widget(),TemplateRuleRectangle):
                    el = el.widget()
                    print("{}TEMPRULE {}".format(text,el.data.has_for_plain_text))
                    print_template_rule_items(el,text)
                else:
                    print("{}PROXYWIDGET {}".format(text, el.widget()))



    def loop_through_rules(self, rules: Union[TemplateRule, TemplateRules], parent_scene):
        bbox = parent_scene.itemsBoundingRect()

        item_count = int(len(parent_scene.items())/3)    #For every Rule exists 3 items (header,rule,title)

        position = QtCore.QPoint(BORDER, bbox.height() + (item_count+1) * BORDER + 25)

        if isinstance(rules, TemplateRule):
            paths = rules.path_list
            metrics = rules.metric_list

            template_rule_rectangle = TemplateRuleRectangle(parent_scene, paths, metrics, position,rules)
            return template_rule_rectangle

        elif isinstance(rules,TemplateRules):
            trr = TemplateRulesRectangle(parent_scene, position, rules)

            for i, rule in enumerate(rules.has_template_rules):
                template_rule = self.loop_through_rules(rule, trr.scene())

                if template_rule is not None:
                    trr.scene().addWidget(template_rule)

            trr.parent_scene.addWidget(trr)

            width = trr.scene().itemsBoundingRect().width() + BORDER * 2
            height = trr.scene().itemsBoundingRect().height() + BORDER * 2

            trr.setGeometry(position.x(), position.y(), width, height)
            trr.setSceneRect(-BORDER / 2, -BORDER / 2, width, height)
            trr.add_title()

            trr.centerOn(trr.sceneRect().center())

def print_template_rule_items(tr: TemplateRuleRectangle, text):
    text += " -->"

    items = tr.scene().items()

    text_list = []
    path_list = []
    else_list = []

    for el in items:

        if isinstance(el, QtWidgets.QGraphicsTextItem):
            text_list.append(el)
        elif isinstance(el, QtWidgets.QGraphicsPathItem):
            path_list.append(el)
        else:

            else_list.append(el)
    printall=False
    if printall:

        print("{} TEXTITEMS {} Stck.".format(text[:-3], len(text_list)))

        for el in text_list:
            print("   {} [TextItem] {}".format(text, el.toPlainText()))

        print("{} PATHITEMS {} Stck.".format(text[:-3], len(path_list)))

        for el in path_list:
            print("   {} [PathItem] {}".format(text, ""))

    print("{} ELSEITEMS {} Stck.".format(text[:-3], len(else_list)))
    for el in else_list:
        print("   {} {}".format(text, el))


def main ():
    global application
    global ui
    doc = "mvdXML_V1.1.xsd"
    file = "../Examples/mvdXML_V1-1-Final-Documentation.xml"
    file2 = "../Examples/Prüfregeln.mvdxml"
    file3 = "../Examples/RelAssociatesMaterial.xml"
    mvd = MvdXml(file=file2, doc=doc, validation=False)

    application = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()
    ui = UiMainWindow()
    ui.setup_ui(window)

    sys.exit(application.exec())

if __name__ == "__main__":
    exit(main())

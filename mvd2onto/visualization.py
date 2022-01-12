from core import *
from typing import Union
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QTreeWidgetItem, QFrame
from PySide6.QtCore import QPointF

# Constants 
BORDER = 5


class TemplateRuleRectangle(QGraphicsView):
    def __init__(self, parent_scene, paths, metrics, index, position: QPointF):

        scene = QGraphicsScene()
        super().__init__(scene)
        self.move(position)

        self.setObjectName("Template Rule {0}".format(index))
        self.parent_scene = parent_scene
        self.import_visuals(paths, metrics)

        width = self.sceneRect().width() + 20
        height = self.sceneRect().height() + 20

        self.setGeometry(position.x(), position.y(), width, height)
        self.setSceneRect(-10, -10, width, height)
        self.add_title()

        parent_scene.addWidget(self)
        self.turn_off_scrollbar()

    def import_visuals(self, paths, metrics):

        created_entities = []
        graphical_items_dict = {}

        template_rule_scene = self.scene()

        # for k, path in enumerate(paths):
        metric = metrics
        last_item = None

        for i, path_item in enumerate(paths):

            if path_item not in created_entities:
                last_block = graphical_items_dict.get(last_item)

                if isinstance(path_item, (ConceptTemplate, EntityRule)):
                    block = self.add_block(template_rule_scene, path_item, last_block)
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
        scene.addItem(block)

        # if not isinstance(last_block,DragBox):
        block.connect_to_entity(last_block)

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

    def __init__(self, parent_scene: QGraphicsScene, index: int, position: QPointF, data: TemplateRules):

        scene = QGraphicsScene()
        super().__init__()
        self.setScene(scene)
        self.setContentsMargins(0, 0, 0, 0)
        self.move(position)
        self.data = data
        self.operator = self.data.has_for_operator
        self.setObjectName("Template Rules {0}".format(index))
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

    def __init__(self, attribute, right_proxy, metric):

        self.label = None
        self.attribute = attribute
        self.right_proxy = right_proxy
        self.metric = metric
        self.scene = self.right_proxy.scene()

        self.create_line()
        self.create_text()

    def __str__(self):
        return "{0}->{1}".format(self.attribute, self.right_proxy)

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

    pass


class DragBox(QtWidgets.QGraphicsProxyWidget):
    # is needed to house QGroupBoxy (EntityRepresentation)

    def __init__(self, widget, top):
        super().__init__()
        self.setAcceptHoverEvents(True)
        self.setWidget(widget)
        self.connections = []
        self.top = top

    def __str__(self):
        return str(self.widget())

    def connect_to_entity(self, attribute, metric=""):

        if attribute is not None:
            con = Connection(attribute, self, metric)

            self.connections.append(con)
            if isinstance(attribute, DragBox):
                attribute.connections.append(con)
            else:
                attribute.parent().graphicsProxyWidget().connections.append(con)

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

    pass


class EntityRepresentation(QFrame):
    """ Widget in DragBox"""

    def __init__(self, title):
        super().__init__()
        self.qlayout = QtWidgets.QVBoxLayout()  # Layout for lining up all the Attributes
        self.setLayout(self.qlayout)
        self.setStyleSheet('QGroupBox:title {'
                           'subcontrol-origin: margin;'
                           'subcontrol-position: top center;'
                           'padding-left: 10px;'
                           'padding-right: 10px; }')
        self.title_text = title
        self.title = QtWidgets.QLabel(self.title_text)
        self.qlayout.addWidget(self.title)

    def __str__(self):
        pass

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        self.update_title(self.title_text)
        pass

    def add_attribute(self, data):
        text = data.has_for_attribute_name
        attrib = Attribute(text)
        self.qlayout.addWidget(attrib)
        attrib.show()
        return attrib

    def update_title(self, title):
        self.title_text = title


class LabelRepresentation(QtWidgets.QLabel):
    def __str__(self):
        return "[Label] {0}".format(self.text())


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
        self.graphicsView = QtWidgets.QGraphicsView(self.scene)
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
        width, height = self.graphicsView.width(), self.graphicsView.height()
        self.scene.setSceneRect(0, 0, width, height)
        self.init_tree()

    def init_tree(self):
        self.treeWidget.setColumnCount(1)
        print(ConceptRoot.instances())
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
        for el in self.scene.items():
            print("Delete Scene {}".format(el))
            self.scene.removeItem(el)

        print()

        if isinstance(obj, ConceptRoot):
            pass

        if isinstance(obj, Concept):

            for index, rules in enumerate(obj.has_template_rules):
                self.loop_through_rules(rules, self.scene, index)

    def loop_through_rules(self, rules: Union[TemplateRule, TemplateRules], parent_scene, index):
        bbox = parent_scene.itemsBoundingRect()
        position = QtCore.QPoint(BORDER, bbox.height() + (index + 1) * BORDER + 25)

        if isinstance(rules, TemplateRule):
            paths, metrics = rules.get_linked_rules()
            return TemplateRuleRectangle(parent_scene, paths, metrics, index, position)
        else:
            trr = TemplateRulesRectangle(parent_scene, index, position, rules)
            for i, rule in enumerate(rules.has_template_rules):
                self.loop_through_rules(rule, trr.scene(), i)

            trr.parent_scene.addWidget(trr)

            width = trr.scene().itemsBoundingRect().width() + BORDER * 2
            height = trr.scene().itemsBoundingRect().height() + BORDER * 2

            trr.setGeometry(position.x(), position.y(), width, height)
            trr.setSceneRect(-BORDER / 2, -BORDER / 2, width, height)
            trr.add_title()

            trr.centerOn(trr.sceneRect().center())

def main ():
    global application
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

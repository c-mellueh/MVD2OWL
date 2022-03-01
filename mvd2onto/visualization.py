from core import *
from typing import Union
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtWidgets import *
from PySide6.QtCore import QPointF, QPoint
from random import random
import constants

class MainView(QGraphicsView):

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        point = event.angleDelta() / 4
        val = point.y()

        modifier = QApplication.keyboardModifiers()

        if bool(modifier == QtCore.Qt.ControlModifier):

            if val < 0:
                self.scale(1-constants.SCALING_FACTOR, 1-constants.SCALING_FACTOR)
            else:
                self.scale(1+constants.SCALING_FACTOR, 1+constants.SCALING_FACTOR)

        elif bool(modifier == QtCore.Qt.ShiftModifier):

            hor = self.horizontalScrollBar()
            hor.setValue(hor.value() - val)

        else:

            ver = self.verticalScrollBar()

            ver.setValue(ver.value() - val)

        self.update()


class RuleRectangle(QGraphicsView):
    """parent class of TemplateRuleRectangle & TemplateRulesRectangle"""

    def __init__(self, position: QPointF, data: Union[TemplateRule, TemplateRules], parent_scene: QGraphicsScene):
        super().__init__()
        scene = QGraphicsScene()
        self.setScene(scene)
        self.move(position)
        self.data = data
        self.parent_scene = parent_scene
        self.turn_off_scrollbar()
        self.movable_elements = []
        self.color = "grey"
        self.resize_elements = []
        self.view = self.scene().views()[0]
        self.view.setFrameStyle(QFrame.Box)


    def add_title(self, text):
        width = self.sceneRect().width()
        self.title_block = TitleBlock(self.pos().x(), self.pos().y() - 25,
                                      width, 25, self, text)

        # Brush
        brush = QtGui.QBrush()
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        brush.setColor(QtGui.QColor(self.color))

        self.title_block.setBrush(brush)
        self.title_block.setZValue(0)

        self.parent_scene.addItem(self.title_block)
        self.movable_elements.append(self.title_block)
        self.movable_elements.append(self.title_block.text)

        return self.title_block

    def turn_off_scrollbar(self):
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

    def change_border_color(self, color):

        self.view.setLineWidth(2)
        style = "border: 2px solid {};".format(color)
        self.view.setStyleSheet(style)

    def resizeEvent(self, event):

        if self.title_block is not None:


            rec = self.title_block.rect()
            bar_height = rec.height()
            width = self.size().width()
            rec.setWidth(width)
            self.title_block.setRect(rec)

            gpw = self.graphicsProxyWidget()
            scene_pos = gpw.scenePos()
            gpw_rect = gpw.rect()

            shift = QPointF(0, -bar_height)
            self.top_left = scene_pos + gpw_rect.topLeft() + shift
            self.top_right = rec.topRight() + shift
            self.bottom_left = scene_pos + gpw_rect.bottomLeft()
            self.bottom_right = scene_pos + gpw_rect.bottomRight()

            for el in self.movable_elements:
                if isinstance(el, ResizeBorder):
                    if el.orientation == "top" or el.orientation == "bottom":
                        rect = el.rect()
                        rect.setWidth(self.width())
                        el.setRect(rect)
                    if el.orientation == "left" or el.orientation == "right":
                        rect = el.rect()
                        rect.setHeight(self.height() + self.title_block.rect().height())
                        el.setRect(rect)

    def add_resize_elements(self):

        gpw = self.graphicsProxyWidget()

        pos = self.title_block.rect().topLeft()
        self.resize_elements.append(ResizeEdge(self, self.parent_scene, pos, "top_left"))
        self.resize_elements.append(ResizeBorder(self, self.parent_scene, pos, "top"))
        self.resize_elements.append(ResizeBorder(self, self.parent_scene, pos, "left"))

        pos = self.title_block.rect().topRight()
        self.resize_elements.append(ResizeEdge(self, self.parent_scene, pos, "top_right"))
        self.resize_elements.append(ResizeBorder(self, self.parent_scene, pos, "right"))

        pos = gpw.scenePos() + gpw.rect().bottomLeft()
        self.resize_elements.append(ResizeEdge(self, self.parent_scene, pos, "bottom_left"))
        self.resize_elements.append(ResizeBorder(self, self.parent_scene, pos, "bottom"))

        pos = gpw.scenePos() + gpw.rect().bottomRight()
        self.resize_elements.append(ResizeEdge(self, self.parent_scene, pos, "bottom_right"))

        color = QtGui.QColor("black")
        color.setAlpha(0)
        pen = QtGui.QPen()
        pen.setColor(color)

        for el in self.resize_elements:
            self.movable_elements.append(el)
            el.setPen(pen)

    def resize_top(self, y_dif):
        proxy = self.graphicsProxyWidget()

        for el in self.movable_elements:
            if not isinstance(el, (ResizeEdge, ResizeBorder)):
                el.moveBy(0, y_dif)

            elif isinstance(el, ResizeEdge):
                if el.orientation == "top_right" or el.orientation == "top_left":
                    el.moveBy(0, y_dif)

            elif isinstance(el, ResizeBorder):
                if not el.orientation == "bottom":
                    el.moveBy(0, y_dif)

        proxy.moveBy(0, y_dif)

        size = proxy.size()
        size.setHeight(size.height() - y_dif)
        proxy.resize(size)

        for items in self.scene().items():
            items.moveBy(0, -y_dif)

    def resize_bottom(self,y_dif,):
        proxy = self.graphicsProxyWidget()
        for el in self.movable_elements:

            if isinstance(el, ResizeEdge):
                if el.orientation == "bottom_right" or el.orientation == "bottom_left":
                    el.moveBy(0, y_dif)

            if isinstance(el,ResizeBorder):
                if el.orientation =="bottom":
                    el.moveBy(0,y_dif)

        size = proxy.size()
        size.setHeight(size.height() + y_dif)
        proxy.resize(size)

    def resize_left(self,x_dif):
        proxy:QtWidgets.QGraphicsProxyWidget = self.graphicsProxyWidget()

        for el in self.movable_elements:
            if not isinstance(el, (ResizeEdge, ResizeBorder)):
                el.moveBy(x_dif, 0)

            elif isinstance(el, ResizeEdge):
                if el.orientation == "bottom_left" or el.orientation == "top_left":
                    el.moveBy(x_dif, 0)

            elif isinstance(el, ResizeBorder):
                if not el.orientation == "right":
                    el.moveBy(x_dif, 0)


        proxy.moveBy(x_dif, 0)

        size = proxy.size()
        size.setWidth(size.width() - x_dif)
        proxy.resize(size)

        for items in self.scene().items():
            items.moveBy(-x_dif, 0)

    def resize_right(self,x_dif):
        proxy: QtWidgets.QGraphicsProxyWidget = self.graphicsProxyWidget()

        for el in self.movable_elements:

            if isinstance(el, ResizeEdge):
                if el.orientation == "bottom_right" or el.orientation == "top_right":
                    el.moveBy(x_dif, 0)
            if isinstance(el,ResizeBorder):
                if el.orientation =="right":
                    el.moveBy(x_dif,0)


        size = proxy.size()
        size.setWidth(size.width() + x_dif)
        proxy.resize(size)

    def resize_scene(self,x_dif,y_dif):
        proxy = self.graphicsProxyWidget()
        item: TemplateRuleRectangle = proxy.widget()
        rec = item.scene().sceneRect()
        rec.setWidth(rec.width() + x_dif)
        rec.setHeight(rec.height() + y_dif)
        item.scene().setSceneRect(rec)


class TemplateRuleRectangle(RuleRectangle):
    def __init__(self, parent_scene, position: QPointF, data: TemplateRule):

        super().__init__(position, data, parent_scene)

        self.import_visuals(data)

        width = self.sceneRect().width() + 20
        height = self.sceneRect().height() + 20

        self.setGeometry(position.x(), position.y(), width, height)
        #self.setSceneRect(0, 0, width, height)
        self.add_title("TemplateRule")
        self.turn_off_scrollbar()

    def import_visuals(self, data: TemplateRule):

        created_entities = []
        graphical_items_dict = {}
        template_rule_scene = self.scene()

        for parameter in data.has_for_parameters:
            path = parameter.path
            metric = parameter.metric
            operator = parameter.operator

            last_item = None

            for path_item in path:

                if path_item not in created_entities:
                    last_block = graphical_items_dict.get(last_item)

                    if isinstance(path_item, (ConceptTemplate, EntityRule, ConceptRoot)):

                        block = self.add_block(path_item, last_block)
                        template_rule_scene.addItem(block)
                        block.solve_collisions()
                        block.connect_to_entity(last_block)
                        graphical_items_dict[path_item] = block
                        created_entities.append(path_item)
                        pass

                    elif isinstance(path_item, AttributeRule):
                        groupbox = last_block.widget()
                        attribute_label = groupbox.add_attribute(path_item)  # returns QLabel housed in QGroupBox
                        graphical_items_dict[path_item] = attribute_label
                        created_entities.append(path_item)

                last_item = path_item

            last_block = graphical_items_dict.get(last_item)
            self.add_label(template_rule_scene, parameter.value, last_block,str(metric + operator))

    def add_block(self, data, last_block):

        name = "undefined"

        if isinstance(data, ConceptTemplate):
            name = data.has_for_applicable_entity
        elif isinstance(data, EntityRule):
            name = data.has_for_entity_name
        elif isinstance(data, ConceptRoot):
            name = data.has_for_applicable_root_entity

        block = DragBox(EntityRepresentation(name), self)

        # size
        if last_block is not None and not isinstance(last_block, DragBox):
            xpos = last_block.parent().pos().x() + 220
            ypos = last_block.y()
        elif isinstance(last_block, DragBox):
            xpos = last_block.pos().x() + 220
            ypos = 0

        else:
            xpos = 0
            ypos = 0

        block.setPos((QPointF(xpos, ypos)))
        return block

    def add_label(self, scene, inhalt, old_proxy, metric):

        if isinstance(old_proxy, DragBox):
            connect_item = old_proxy
        else:
            connect_item = old_proxy.parent()

        text = str(inhalt)
        label_ = LabelRepresentation()
        label_.setText(text)
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred,
                                            type=QtWidgets.QSizePolicy.Label)
        label_.setSizePolicy(size_policy)
        proxy = DragBox(label_, self)
        scene.addItem(proxy)
        width = label_.width()+20
        height = label_.height()
        xpos = connect_item.pos().x() + 225
        ypos = old_proxy.y()-10

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


class TemplateRulesRectangle(RuleRectangle):

    def __init__(self, parent_scene: QGraphicsScene, position: QPointF, data: TemplateRules) -> object:
        """

        :param parent_scene:
        :type parent_scene:
        :param position:
        :type position:
        :param data:
        :type data:
        """

        super().__init__(position, data, parent_scene)

        self.operator = self.data.has_for_operator
        self.color = self.get_color()
        self.change_border_color(self.color)

        self.title_block = None

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        ui.graphics_view.wheelEvent(event)

        pass

    def get_color(self):
        if self.operator == "or":
            color = "blue"
        elif self.operator == "and":
            color = "green"
        elif self.operator == "nor":
            color = "red"
        else:
            color = "grey"
        return color


class ResizeEdge(QtWidgets.QGraphicsRectItem):

    def __init__(self, graphics_view: TemplateRulesRectangle, parent: QGraphicsScene, position: QPointF,
                 orientation: str):

        self.orientation = orientation
        self.graphical_view = graphics_view

        movement = QPoint(constants.RESIZE_BORDER_WIDTH / 2, constants.RESIZE_BORDER_WIDTH / 2)

        position = position - movement
        super().__init__(position.x(), position.y(), constants.RESIZE_BORDER_WIDTH, constants.RESIZE_BORDER_WIDTH)
        self.setAcceptHoverEvents(True)

        self.setZValue(100)
        parent.addItem(self)

    def hoverEnterEvent(self, event):

        if self.orientation == "top_left" or self.orientation == "bottom_right":
            application.instance().setOverrideCursor(QtCore.Qt.SizeFDiagCursor)
        elif self.orientation == "top_right" or self.orientation == "bottom_left":
            application.instance().setOverrideCursor(QtCore.Qt.SizeBDiagCursor)

    def hoverLeaveEvent(self, event):
        application.instance().restoreOverrideCursor()

    def mousePressEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        if self.orientation == "top_left" or self.orientation == "bottom_right":
            application.instance().setOverrideCursor(QtCore.Qt.SizeFDiagCursor)
        elif self.orientation == "top_right" or self.orientation == "bottom_left":
            application.instance().setOverrideCursor(QtCore.Qt.SizeBDiagCursor)

    def mouseMoveEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        orig_cursor_position = event.lastScenePos()
        updated_cursor_position = event.scenePos()

        x_dif = updated_cursor_position.x() - orig_cursor_position.x()
        y_dif = updated_cursor_position.y() - orig_cursor_position.y()

        gv = self.graphical_view
        self.scene().update()

        if self.orientation == "top_left":
            gv.resize_left(x_dif)
            gv.resize_top(y_dif)

        elif self.orientation == "top_right":
            gv.resize_top(y_dif)
            gv.resize_right(x_dif)

        elif self.orientation == "bottom_left":
            gv.resize_bottom(y_dif)
            gv.resize_left(x_dif)

        elif self.orientation == "bottom_right":
            gv.resize_bottom(y_dif)
            gv.resize_right(x_dif)

        gv.resize_scene(x_dif,y_dif)

    def mouseReleaseEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        application.instance().restoreOverrideCursor()

        pass


class ResizeBorder(QtWidgets.QGraphicsRectItem):

    def __init__(self, graphics_view: TemplateRulesRectangle, parent: QGraphicsScene, position: QPointF,
                 orientation: str):

        self.orientation = orientation
        self.graphical_view = graphics_view

        self.graphical_view.height()

        self.width = 10

        if self.orientation == "top" or self.orientation == "bottom":
            position.setY(position.y() - self.width / 2)
            super().__init__(position.x(), position.y(), self.graphical_view.width(), self.width)

        elif self.orientation == "left" or self.orientation == "right":
            position.setX(position.x() - self.width / 2)
            super().__init__(position.x(), position.y(), self.width,
                             self.graphical_view.height() + self.graphical_view.title_block.rect().height())

        self.setAcceptHoverEvents(True)

        parent.addItem(self)

    def hoverEnterEvent(self, event):

        if self.orientation == "top" or self.orientation == "bottom":
            application.instance().setOverrideCursor(QtCore.Qt.SizeVerCursor)
        elif self.orientation == "left" or self.orientation == "right":
            application.instance().setOverrideCursor(QtCore.Qt.SizeHorCursor)

    def hoverLeaveEvent(self, event):
        application.instance().restoreOverrideCursor()

    def mousePressEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        if self.orientation == "top" or self.orientation == "bottom":
            application.instance().setOverrideCursor(QtCore.Qt.SizeVerCursor)
        elif self.orientation == "left" or self.orientation == "right":
            application.instance().setOverrideCursor(QtCore.Qt.SizeHorCursor)



    def mouseMoveEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        orig_cursor_position = event.lastScenePos()
        updated_cursor_position = event.scenePos()

        x_dif = updated_cursor_position.x() - orig_cursor_position.x()
        y_dif = updated_cursor_position.y() - orig_cursor_position.y()

        gv = self.graphical_view

        self.scene().update()

        if self.orientation == "top":
            gv.resize_top(y_dif)
            x_dif = x_dif =0.0

        if self.orientation == "bottom":
            gv.resize_bottom(y_dif)
            x_dif = 0.0

        elif self.orientation == "left":
            gv.resize_left(x_dif)
            y_dif = 0.0
        elif self.orientation == "right":
            gv.resize_right(x_dif)
            y_dif = 0.0

        gv.resize_scene(x_dif,y_dif)

    def mouseReleaseEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        application.instance().restoreOverrideCursor()

        pass


class TitleBlock(QtWidgets.QGraphicsRectItem):
    def __init__(self, x, y, w, h, view: Union[TemplateRulesRectangle, TemplateRuleRectangle], text: str):
        super().__init__(x, y, w, h)
        self.setAcceptHoverEvents(True)
        self.graphical_view = view

        if text == None:
            text = ""

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
        application.instance().setOverrideCursor(QtCore.Qt.ClosedHandCursor)
        pass

    def mouseMoveEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        orig_cursor_position = event.lastScenePos()
        updated_cursor_position = event.scenePos()

        x_dif = updated_cursor_position.x() - orig_cursor_position.x()
        y_dif = updated_cursor_position.y() - orig_cursor_position.y()

        for el in self.graphical_view.movable_elements:
            el.moveBy(x_dif, y_dif)

        proxy = self.graphical_view.graphicsProxyWidget()
        proxy.moveBy(x_dif, y_dif)

    def mouseReleaseEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        application.instance().restoreOverrideCursor()

        pass


class Attribute(QtWidgets.QLabel):

    def __init__(self, text):
        super().__init__()
        self.setText(text)
        self.connections = []
        self.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)

    def __str__(self):
        return "[Attribut] {0}".format(self.text())


class Connection:
    liste = []

    def __init__(self, attribute, right_proxy, text):

        self.label = None
        self.attribute = attribute
        self.right_proxy :DragBox = right_proxy
        self.text = text
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
        if self.text != "":
            self.center = self.path.boundingRect().center()
            self.label = QtWidgets.QGraphicsTextItem()
            self.label.setHtml("<div style='background-color:#FFFFFF;'>" + str(self.text) + "</div>")

            self.scene.addItem(self.label)
            width = self.label.boundingRect().width()
            height = self.label.boundingRect().height()
            movement = QPointF(width, height) / 2
            self.label.setPos(self.center - movement)

    def get_pos(self)->list[QPointF]:
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
        self.line.setPos(0.0,0.0)

        # Update Label
        if self.label is not None:
            self.center = self.path.boundingRect().center()
            width = self.label.boundingRect().width()
            height = self.label.boundingRect().height()
            movement = QPointF(width, height) / 2
            self.label.setPos(self.center - movement)

        return self.points


class DragBox(QtWidgets.QGraphicsProxyWidget):
    # is needed to house QGroupBox (EntityRepresentation)

    def __init__(self, widget, top):
        super().__init__()

        if isinstance(widget, EntityRepresentation):
            widget.helper = self

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
        application.instance().setOverrideCursor(QtCore.Qt.ClosedHandCursor)
        pass

    def mouseMoveEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:

        orig_cursor_position = event.lastScenePos()
        updated_cursor_position = event.scenePos()
        orig_position = self.scenePos()

        x_dif = updated_cursor_position.x() - orig_cursor_position.x()
        y_dif = updated_cursor_position.y() - orig_cursor_position.y()

        if self.check_for_exit(x_dif + orig_position.x(), "x"):
            x_dif = 0
        if self.check_for_exit( y_dif + orig_position.y(), "y"):
            y_dif = 0


        updated_cursor_x = x_dif + orig_position.x()
        updated_cursor_y = y_dif + orig_position.y()



        self.setPos(QPointF(updated_cursor_x, updated_cursor_y))

        for el in self.connections:
            el.update()

    def check_for_exit(self, value, direction: str):

        x_right = value+self.geometry().width()
        y_bottom = value+self.geometry().height()
        if value < 0:
            return True
        elif direction == "x":
            if x_right > self.scene().width():
                return True
        elif direction == "y":
            if y_bottom > self.scene().height():
                return True
        else:
            return False

    def mouseReleaseEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        application.instance().restoreOverrideCursor()

    def solve_collisions(self):

        collisions = self.collidingItems()

        t_bool = False

        if any(isinstance(x,DragBox) for x in collisions):
            t_bool = True

        while any(isinstance(x,DragBox) for x in collisions):
            self.moveBy(0.0,5.0)
            collisions = self.collidingItems()

        if t_bool:
            self.moveBy(0,10)

class EntityRepresentation(QFrame):
    """ Widget in DragBox"""

    def __init__(self, title: str):
        super().__init__()
        self.helper = None
        self.title = title
        self.setLayout(QtWidgets.QVBoxLayout())
        self.setStyleSheet('QGroupBox:title {'
                           'subcontrol-origin: margin;'
                           'subcontrol-position: top center;'
                           'padding-left: 10px;'
                           'padding-right: 10px; }')

        self.setObjectName(str(random() * 1000))

        self.title_widget = QtWidgets.QLabel(self.title)
        self.layout().addWidget(self.title_widget)

    def __str__(self):
        return "[EntityRepresentation: {}]".format(self.title)

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        # self.update_title(self.title)
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
    def __init__(self):
        super().__init__()
        self.setAlignment(QtCore.Qt.AlignCenter)

    def __str__(self):
        return "[Label: {0}]".format(self.text())


class UiMainWindow(object):

    def setup_ui(self, main_window):

        # Fenster Aufbau

        self.main_window = main_window

        self.main_window.setObjectName("MainWindow")
        self.main_window.resize(1920, 1080)

        # Base for Columns
        self.central_widget = QtWidgets.QWidget(main_window)
        self.central_widget.setObjectName("central_widget")
        self.base_layout = QtWidgets.QGridLayout(self.central_widget)
        self.base_layout.setObjectName("baseLayout")
        self.main_window.setCentralWidget(self.central_widget)

        # Columns Layout for Treelist nad Object window
        self.horizontal_layout = QtWidgets.QHBoxLayout()
        self.horizontal_layout.setSpacing(5)
        self.horizontal_layout.setObjectName("horizontal_layout")

        # Inhalt in Fenster hinzufügen
        self.base_layout.addLayout(self.horizontal_layout, 0, 0, 1, 1)

        # Tree Widget
        self.tree_widget = QtWidgets.QTreeWidget(self.central_widget)

        # Set Size Policy for TreeWidget
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        size_policy.setHorizontalStretch(1)
        size_policy.setVerticalStretch(1)
        size_policy.setHeightForWidth(self.tree_widget.sizePolicy().hasHeightForWidth())
        self.tree_widget.setSizePolicy(size_policy)
        self.tree_widget.setObjectName("tree_widget")
        self.tree_widget.headerItem().setText(0, "Regeln")

        self.horizontal_layout.addWidget(self.tree_widget)

        # Object Window
        self.scene = QGraphicsScene()
        self.graphics_view = MainView(self.scene)
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        size_policy.setHorizontalStretch(3)
        size_policy.setVerticalStretch(1)
        size_policy.setHeightForWidth(self.graphics_view.sizePolicy().hasHeightForWidth())
        self.graphics_view.setSizePolicy(size_policy)
        self.graphics_view.setObjectName("graphics_view")

        self.horizontal_layout.addWidget(self.graphics_view)

        self.menubar = QtWidgets.QMenuBar(main_window)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1527, 22))
        self.menubar.setObjectName("menubar")
        main_window.setMenuBar(self.menubar)

        self.statusbar = QtWidgets.QStatusBar(main_window)
        self.statusbar.setObjectName("statusbar")
        main_window.setStatusBar(self.statusbar)

        self.retranslate_ui(main_window)
        QtCore.QMetaObject.connectSlotsByName(main_window)



    def retranslate_ui(self,main_window):
        _translate = QtCore.QCoreApplication.translate
        main_window.setWindowTitle(_translate("MainWindow", "MVD2Onto"))
        self.initialize()


    def initialize(self):
        self.import_mvd()
        self.main_window.show()
        self.tree_widget.setColumnCount(1)
        for concept_root in ConceptRoot.instances():
            name = concept_root.has_for_name

            if name == "":
                name = constants.UNDEFINED_ROOT_NAME

            item = QTreeWidgetItem(self.tree_widget, [name])
            item.konzept = concept_root
            self.tree_widget.addTopLevelItem(item)

            for concept in concept_root.has_concepts:
                child = QTreeWidgetItem(item, [concept.has_for_name])
                child.konzept = concept

        self.tree_widget.itemClicked.connect(self.on_tree_clicked)

    def import_mvd(self):
        file_path = QtWidgets.QFileDialog.getOpenFileName(caption="mvdXML Datei", filter="mvdXML (*xml);;All files (*.*)",
                                               selectedFilter="mvdXML (*xml)")[0]

        #file_path = "../Examples/RelAssociatesMaterial.xml"

        self.mvd =  MvdXml(file=file_path, validation=False)

    def on_tree_clicked(self, item):

        obj = item.konzept
        self.scene.clear()

        if isinstance(obj, ConceptRoot):
            pass

        if isinstance(obj, Concept):

            for index, rules in enumerate(obj.has_template_rules):
                self.loop_through_rules(rules, self.scene)

    def loop_through_rules(self, rules: Union[TemplateRule, TemplateRules], parent_scene):
        bbox = parent_scene.itemsBoundingRect()

        item_count = int(len(parent_scene.items()) / 3)  # For every Rule exists 3 items (header,rule,title)

        position = QtCore.QPoint(constants.BORDER, bbox.height() + (item_count + 1) * constants.BORDER + 25)

        if isinstance(rules, TemplateRule):
            template_rule_rectangle = TemplateRuleRectangle(parent_scene, position, rules)
            return template_rule_rectangle

        elif isinstance(rules, TemplateRules):
            trr = TemplateRulesRectangle(parent_scene, position, rules)

            for i, rule in enumerate(rules.has_template_rules):
                template_rule = self.loop_through_rules(rule, trr.scene())

                if template_rule is not None:
                    trr.scene().addWidget(template_rule)
                    template_rule.add_resize_elements()

            trr.parent_scene.addWidget(trr)

            width = trr.scene().itemsBoundingRect().width() + constants.BORDER * 2
            height = trr.scene().itemsBoundingRect().height() + constants.BORDER * 2

            trr.setGeometry(position.x(), position.y(), width, height)
            trr.setSceneRect(-constants.BORDER, -constants.BORDER, width, height)
            trr.add_title(trr.operator)
            trr.add_resize_elements()

            trr.centerOn(trr.sceneRect().center())


def main():
    global application
    global ui
    application = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()
    ui = UiMainWindow()
    ui.setup_ui(window)

    sys.exit(application.exec())


if __name__ == "__main__":
    exit(main())

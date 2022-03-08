import time

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
                self.scale(1 - constants.SCALING_FACTOR, 1 - constants.SCALING_FACTOR)
            else:
                self.scale(1 + constants.SCALING_FACTOR, 1 + constants.SCALING_FACTOR)

        elif bool(modifier == QtCore.Qt.ShiftModifier):
            hor = self.horizontalScrollBar()
            hor.setValue(hor.value() - val)

        else:
            ver = self.verticalScrollBar()
            ver.setValue(ver.value() - val)
        self.update()


class RuleGraphicsView(QGraphicsView):
    """parent class of TemplateRuleGraphicsView & TemplateRulesGraphicsView"""

    def __init__(self, data: Union[TemplateRule, TemplateRules]):
        super().__init__()
        scene = QGraphicsScene()
        self.setScene(scene)
        self.data = data
        self.parent_scene: QGraphicsScene = None
        self.turn_off_scrollbar()
        self.setFrameStyle(QFrame.Box)
        self.frame_color = constants.FRAME_COLOR_DICT["ELSE"]
        self.infill_color = constants.INFILL_COLOR_DICT["ELSE"]

        # lists
        self.movable_elements = []
        self.resize_elements: list(Union[ResizeEdge, ResizeBorder]) = []
        self.title_block: TitleBlock = None

    def add_title_block(self):
        self.title_block = TitleBlock(self)

        # Brush
        brush = QtGui.QBrush()
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        brush.setColor(QtGui.QColor(self.frame_color[0], self.frame_color[1], self.frame_color[2]))

        self.title_block.setBrush(brush)

        self.parent_scene.addItem(self.title_block)
        self.movable_elements.append(self.title_block)
        self.movable_elements.append(self.title_block.text)

        return self.title_block

    def turn_off_scrollbar(self):
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

    def update_style(self, border_color:tuple[int,int,int], infill_color:tuple[int,int,int]):

        self.setLineWidth(2)
        style = "border: 2px solid rgb{}; " \
                "background-color: rgb{}; " \
                "border-bottom-left-radius: {}px; " \
                "border-bottom-right-radius: {}px;".format(border_color, infill_color, constants.BORDER_RADIUS,
                                                           constants.BORDER_RADIUS)
        self.setStyleSheet(style)

    def add_to_scene(self, scene: QGraphicsScene):
        self.parent_scene = scene
        bbox = scene.itemsBoundingRect()
        scene.addWidget(self)
        self.graphicsProxyWidget().setY(constants.TITLE_BLOCK_HEIGHT)
        self.add_title_block()
        self.moveBy(0, bbox.height())
        self.add_resize_elements()

    def resizeEvent(self, event):
        if self.title_block is not None:

            rec = self.title_block.rect()
            bar_height = rec.height()
            width = self.size().width()
            rec.setWidth(width)
            self.title_block.setRect(rec)

            gpw: QGraphicsProxyWidget = self.graphicsProxyWidget()
            gpw.setMinimumHeight(0)
            gpw.setMinimumWidth(0)

            for el in self.movable_elements:
                if isinstance(el, ResizeBorder):
                    if el.orientation == ResizeBorder.TOP or el.orientation == ResizeBorder.BOTTOM:
                        rect = el.rect()
                        rect.setWidth(self.width())
                        el.setRect(rect)
                    if el.orientation == ResizeBorder.LEFT or el.orientation == ResizeBorder.RIGHT:
                        rect = el.rect()
                        rect.setHeight(self.height() + self.title_block.rect().height())
                        el.setRect(rect)

    def add_resize_elements(self):

        for el in ResizeEdge.POSSIBLE_ORIENTATIONS:
            edge = ResizeEdge(self, el)
            self.resize_elements.append(edge)

        for el in ResizeBorder.POSSIBLE_ORIENTATIONS:
            border = ResizeBorder(self, el)
            self.resize_elements.append(border)

        color = QtGui.QColor("black")
        color.setAlpha(0)  # Turn Invisible
        pen = QtGui.QPen()
        pen.setColor(color)

        for el in self.resize_elements:
            self.movable_elements.append(el)
            el.setPen(pen)

    def resize_top(self, y_dif):
        proxy: QGraphicsProxyWidget = self.graphicsProxyWidget()
        proxy.setMinimumHeight(0)
        new_height = proxy.size().height() - y_dif

        min_items = min(item.y() for item in self.items())

        if min_items < 0 and y_dif > 0:
            pass

        elif new_height > constants.MIN_RECT_SIZE:
            for el in self.movable_elements:
                if not isinstance(el, (ResizeEdge, ResizeBorder)):
                    el.moveBy(0, y_dif)

                elif isinstance(el, ResizeEdge):
                    if el.orientation == ResizeEdge.TOP_RIGHT or el.orientation == ResizeEdge.TOP_LEFT:
                        el.moveBy(0, y_dif)


                elif isinstance(el, ResizeBorder):
                    if not el.orientation == ResizeBorder.BOTTOM:
                        el.moveBy(0, y_dif)

            proxy.moveBy(0, y_dif)

            size = proxy.size()
            size.setHeight(size.height() - y_dif)
            proxy.resize(size)

            for items in self.scene().items():
                items.moveBy(0, -y_dif)

    def resize_bottom(self, y_dif):
        proxy = self.graphicsProxyWidget()
        proxy.setMinimumHeight(0)
        new_height = proxy.size().height() + y_dif

        max_y = []
        for item in self.items():
            if isinstance(item, ResizeEdge):

                scene_pos = item.mapToScene(item.rect().bottomLeft())
                max_y.append(scene_pos.y() + constants.RESIZE_BORDER_WIDTH)

            elif isinstance(item, DragBox):
                scene_pos = item.mapToScene(item.rect().bottomLeft())
                max_y.append(scene_pos.y() + constants.RESIZE_BORDER_WIDTH)

        max_items = max(max_y)

        if new_height > constants.MIN_RECT_SIZE and new_height > max_items:
            for el in self.movable_elements:

                if isinstance(el, ResizeEdge):
                    if el.orientation == ResizeEdge.BOTTOM_RIGHT or el.orientation == ResizeEdge.BOTTOM_LEFT:
                        el.moveBy(0, y_dif)

                if isinstance(el, ResizeBorder):
                    if el.orientation == ResizeBorder.BOTTOM:
                        el.moveBy(0, y_dif)

            size = proxy.size()
            size.setHeight(size.height() + y_dif)
            proxy.resize(size)

    def resize_left(self, x_dif):
        proxy: QtWidgets.QGraphicsProxyWidget = self.graphicsProxyWidget()
        proxy.setMinimumWidth(0)
        new_width = proxy.size().width() - x_dif

        min_items = min(item.x() for item in self.items())

        if min_items < 0 and x_dif > 0:
            pass

        elif new_width > constants.MIN_RECT_SIZE:
            for el in self.movable_elements:
                if not isinstance(el, (ResizeEdge, ResizeBorder)):
                    el.moveBy(x_dif, 0)

                elif isinstance(el, ResizeEdge):
                    if el.orientation == ResizeEdge.BOTTOM_LEFT or el.orientation == ResizeEdge.TOP_LEFT:
                        el.moveBy(x_dif, 0)

                elif isinstance(el, ResizeBorder):
                    if not el.orientation == ResizeBorder.RIGHT:
                        el.moveBy(x_dif, 0)

            proxy.moveBy(x_dif, 0)

            size = proxy.size()
            size.setWidth(size.width() - x_dif)
            proxy.resize(size)

            for items in self.scene().items():
                items.moveBy(-x_dif, 0)

    def resize_right(self, x_dif):
        proxy: QtWidgets.QGraphicsProxyWidget = self.graphicsProxyWidget()
        proxy.setMinimumWidth(0)

        new_width = proxy.size().width() + x_dif

        max_x = []
        for item in self.items():
            if isinstance(item, ResizeEdge):

                scene_pos = item.mapToScene(item.rect().bottomRight())
                max_x.append(scene_pos.x() + constants.RESIZE_BORDER_WIDTH)

            elif isinstance(item, DragBox):
                scene_pos = item.mapToScene(item.rect().bottomRight())
                max_x.append(scene_pos.x() + constants.RESIZE_BORDER_WIDTH)

        max_items = max(max_x)

        if new_width > constants.MIN_RECT_SIZE and new_width > max_items:
            for el in self.movable_elements:

                if isinstance(el, ResizeEdge):
                    if el.orientation == ResizeEdge.BOTTOM_RIGHT or el.orientation == ResizeEdge.TOP_RIGHT:
                        el.moveBy(x_dif, 0)
                if isinstance(el, ResizeBorder):
                    if el.orientation == ResizeBorder.RIGHT:
                        el.moveBy(x_dif, 0)

            size = proxy.size()
            size.setWidth(size.width() + x_dif)
            proxy.resize(size)

    def moveBy(self, x_dif, y_dif):

        for el in self.movable_elements:
            el.moveBy(x_dif, y_dif)
        proxy = self.graphicsProxyWidget()
        proxy.moveBy(x_dif, y_dif)

    def bring_to_front(self):

        gpwidget: QGraphicsProxyWidget = self.graphicsProxyWidget()

        max_z = max(items.zValue() for items in gpwidget.scene().items())

        if gpwidget.zValue() < max_z - 2:

            self.title_block.setZValue(max_z)
            self.title_block.text.setZValue(max_z + 1)
            gpwidget.setZValue(max_z)

            for el in self.resize_elements:
                if isinstance(el, ResizeBorder):
                    el.setZValue(max_z + 1)
                elif isinstance(el, ResizeEdge):
                    el.setZValue(max_z + 2)

    def get_bottom_left(self):
        gpw: QGraphicsProxyWidget = self.graphicsProxyWidget()
        bottom_left = gpw.scenePos() + gpw.rect().bottomLeft()
        return bottom_left

    def get_bottom_right(self):
        gpw: QGraphicsProxyWidget = self.graphicsProxyWidget()
        bottom_right = gpw.scenePos() + gpw.rect().bottomRight()
        return bottom_right

    def get_top_left(self):
        gpw: QGraphicsProxyWidget = self.graphicsProxyWidget()

        top_left = gpw.scenePos() + QtCore.QPointF(0, -constants.TITLE_BLOCK_HEIGHT)
        return top_left

    def get_top_right(self):
        gpw: QGraphicsProxyWidget = self.graphicsProxyWidget()
        top_right = gpw.scenePos() + gpw.rect().topRight() + QtCore.QPointF(0, -constants.TITLE_BLOCK_HEIGHT)
        return top_right

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        ui.graphics_view.wheelEvent(event)
        pass

class TemplateRuleGraphicsView(RuleGraphicsView):
    def __init__(self, data: TemplateRule):

        super().__init__(data)

        self.setObjectName(str(data))
        self.import_visuals(data)
        self.turn_off_scrollbar()
        new_rec = QtCore.QRectF(self.sceneRect().x(), self.sceneRect().y(), self.sceneRect().width() + constants.BORDER,
                                self.sceneRect().height() + constants.BORDER)
        self.setSceneRect(new_rec)
        self.title = constants.TEMPLATE_RULE_TITLE
        self.update_style(self.frame_color, self.infill_color)

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
            self.add_label(template_rule_scene, parameter.value, last_block, str(metric + operator))

        for el in DragBox._registry:
            wid: EntityRepresentation = el.widget()

            if isinstance(wid, EntityRepresentation):
                wid.update_line()

    def add_block(self, data, last_block):

        name = "undefined"

        if isinstance(data, ConceptTemplate):
            name = data.has_for_applicable_entity
        elif isinstance(data, EntityRule):
            name = data.has_for_entity_name
        elif isinstance(data, ConceptRoot):
            name = data.has_for_applicable_root_entity

        block = DragBox(EntityRepresentation(name))

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
        proxy = DragBox(label_)
        scene.addItem(proxy)
        width = label_.width() + 20
        height = label_.height()
        xpos = connect_item.pos().x() + 225
        ypos = old_proxy.y() - 10

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


class TemplateRulesGraphicsView(RuleGraphicsView):

    def __init__(self, data: TemplateRules) -> object:
        """

        :param parent_scene:
        :type parent_scene:
        :param position:
        :type position:
        :param data:
        :type data:
        """

        super().__init__(data)
        self.setObjectName(str(data))
        self.operator = self.data.has_for_operator
        self.frame_color, self.infill_color = self.get_color(self.operator)
        self.update_style(self.frame_color, self.infill_color)

        if self.operator is None:
            self.title = "Operator does not Exist"
        else:
            self.title = self.operator

        self.title_block = None



    def get_color(self, text:str):

        if text is None:
            text = ""
        text = text.upper()

        frame_color = constants.FRAME_COLOR_DICT.get(text)
        infill_color = constants.INFILL_COLOR_DICT.get(text)

        if frame_color is None:
            frame_color = constants.FRAME_COLOR_DICT["ELSE"]
            infill_color = constants.INFILL_COLOR_DICT["ELSE"]

        return frame_color, infill_color


class ResizeEdge(QtWidgets.QGraphicsRectItem):
    TOP_LEFT = 7
    TOP_RIGHT = 4
    BOTTOM_LEFT = 8
    BOTTOM_RIGHT = 5

    POSSIBLE_ORIENTATIONS = [TOP_LEFT, TOP_RIGHT, BOTTOM_LEFT, BOTTOM_RIGHT]

    def __init__(self, graphics_view: RuleGraphicsView, orientation: int, orientation_2: int = 0):

        self.orientation = orientation + orientation_2
        if self.orientation not in self.POSSIBLE_ORIENTATIONS:
            raise ValueError("orientation not allowed")

        if self.orientation == self.TOP_LEFT:
            position = graphics_view.get_top_left()

        elif self.orientation == self.TOP_RIGHT:
            position = graphics_view.get_top_right()

        elif self.orientation == self.BOTTOM_LEFT:
            position = graphics_view.get_bottom_left()

        elif self.orientation == self.BOTTOM_RIGHT:
            position = graphics_view.get_bottom_right()

        self.graphical_view = graphics_view

        movement = QPoint(constants.RESIZE_BORDER_WIDTH / 2, constants.RESIZE_BORDER_WIDTH / 2)

        position = position - movement
        super().__init__(position.x(), position.y(), constants.RESIZE_BORDER_WIDTH, constants.RESIZE_BORDER_WIDTH)
        self.setAcceptHoverEvents(True)

        self.setZValue(10)
        graphics_view.parent_scene.addItem(self)

    def hoverEnterEvent(self, event):

        if self.orientation == self.TOP_LEFT or self.orientation == self.BOTTOM_RIGHT:
            application.instance().setOverrideCursor(QtCore.Qt.SizeFDiagCursor)
        elif self.orientation == self.TOP_RIGHT or self.orientation == self.BOTTOM_LEFT:
            application.instance().setOverrideCursor(QtCore.Qt.SizeBDiagCursor)

    def hoverLeaveEvent(self, event):
        application.instance().restoreOverrideCursor()

    def mousePressEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        if self.orientation == self.TOP_LEFT or self.orientation == self.BOTTOM_RIGHT:
            application.instance().setOverrideCursor(QtCore.Qt.SizeFDiagCursor)
        elif self.orientation == self.TOP_RIGHT or self.orientation == self.BOTTOM_LEFT:
            application.instance().setOverrideCursor(QtCore.Qt.SizeBDiagCursor)

    def mouseMoveEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        orig_cursor_position = event.lastScenePos()
        updated_cursor_position = event.scenePos()

        x_dif = updated_cursor_position.x() - orig_cursor_position.x()
        y_dif = updated_cursor_position.y() - orig_cursor_position.y()

        gv = self.graphical_view
        # self.scene().update()

        if self.orientation == self.TOP_LEFT:
            gv.resize_left(x_dif)
            gv.resize_top(y_dif)

        elif self.orientation == self.TOP_RIGHT:
            gv.resize_top(y_dif)
            gv.resize_right(x_dif)

        elif self.orientation == self.BOTTOM_LEFT:
            gv.resize_bottom(y_dif)
            gv.resize_left(x_dif)

        elif self.orientation == self.BOTTOM_RIGHT:
            gv.resize_bottom(y_dif)
            gv.resize_right(x_dif)

        gv.scene().update()
        gv.update()

    def mouseReleaseEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        application.instance().restoreOverrideCursor()
        pass


class ResizeBorder(QtWidgets.QGraphicsRectItem):
    TOP = 1
    RIGHT = 3
    BOTTOM = 2
    LEFT = 6

    POSSIBLE_ORIENTATIONS = [TOP, RIGHT, LEFT, BOTTOM]

    def __init__(self, graphics_view: TemplateRulesGraphicsView, orientation: int):

        self.orientation = orientation
        if self.orientation not in self.POSSIBLE_ORIENTATIONS:
            raise ValueError("orientation not allowed")

        self.width = constants.RESIZE_BORDER_WIDTH
        self.graphics_view = graphics_view
        position = self.get_pos()

        if self.orientation == self.TOP or self.orientation == self.BOTTOM:
            super().__init__(position.x(), position.y(), self.graphics_view.width(), self.width)

        elif self.orientation == self.LEFT or self.orientation == self.RIGHT:
            super().__init__(position.x(), position.y(), self.width,
                             self.graphics_view.height() + self.graphics_view.title_block.rect().height())

        self.setAcceptHoverEvents(True)
        self.graphics_view.parent_scene.addItem(self)

    def get_pos(self) -> QtCore.QPointF:
        position = None
        if self.orientation == self.TOP or self.orientation == self.LEFT:
            position = self.graphics_view.get_top_left()

        elif self.orientation == self.BOTTOM:
            position = self.graphics_view.get_bottom_left()

        elif self.orientation == self.RIGHT:
            position = self.graphics_view.get_top_right()

        if self.orientation == self.TOP or self.orientation == self.BOTTOM:
            position.setY(position.y() - self.width / 2)

        elif self.orientation == self.LEFT or self.orientation == self.RIGHT:
            position.setX(position.x() - self.width / 2)

        return position

    def hoverEnterEvent(self, event):

        if self.orientation == self.TOP or self.orientation == self.BOTTOM:
            application.instance().setOverrideCursor(QtCore.Qt.SizeVerCursor)
        elif self.orientation == self.LEFT or self.orientation == self.RIGHT:
            application.instance().setOverrideCursor(QtCore.Qt.SizeHorCursor)

    def hoverLeaveEvent(self, event):
        application.instance().restoreOverrideCursor()

    def mousePressEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        if self.orientation == self.TOP or self.orientation == self.BOTTOM:
            application.instance().setOverrideCursor(QtCore.Qt.SizeVerCursor)
        elif self.orientation == self.LEFT or self.orientation == self.RIGHT:
            application.instance().setOverrideCursor(QtCore.Qt.SizeHorCursor)

    def mouseMoveEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        orig_cursor_position = event.lastScenePos()
        updated_cursor_position = event.scenePos()

        x_dif = updated_cursor_position.x() - orig_cursor_position.x()
        y_dif = updated_cursor_position.y() - orig_cursor_position.y()

        gv = self.graphics_view

        self.scene().update()

        if self.orientation == self.TOP:
            gv.resize_top(y_dif)
            x_dif = 0.0

        if self.orientation == self.BOTTOM:
            gv.resize_bottom(y_dif)
            x_dif = 0.0

        elif self.orientation == self.LEFT:
            gv.resize_left(x_dif)
            y_dif = 0.0
        elif self.orientation == self.RIGHT:
            gv.resize_right(x_dif)
            y_dif = 0.0

        # gv.resize_scene(x_dif,y_dif)
        self.scene().update()
        self.graphics_view.update()

    def mouseReleaseEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        application.instance().restoreOverrideCursor()
        pass


class TitleBlock(QtWidgets.QGraphicsRectItem):
    def __init__(self, graphics_view: Union[TemplateRulesGraphicsView, TemplateRuleGraphicsView]):
        super().__init__(0, 0, graphics_view.width(), constants.TITLE_BLOCK_HEIGHT)

        self.setAcceptHoverEvents(True)
        self.graphics_view = graphics_view

        if graphics_view.title == None:
            self.text = QtWidgets.QGraphicsTextItem("")
        else:
            self.text = QtWidgets.QGraphicsTextItem(graphics_view.title.upper())

        graphics_view.parent_scene.addItem(self.text)
        self.text.setPos(0, 0)
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
        self.graphics_view.bring_to_front()

        orig_cursor_position = event.lastScenePos()
        updated_cursor_position = event.scenePos()

        x_dif = updated_cursor_position.x() - orig_cursor_position.x()
        y_dif = updated_cursor_position.y() - orig_cursor_position.y()

        self.graphics_view.moveBy(x_dif, y_dif)

    def mouseReleaseEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        application.instance().restoreOverrideCursor()

        pass


class Attribute(QtWidgets.QLabel):

    def __init__(self, text):
        super().__init__()
        self.setText(text)
        self.connections = []
        self.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.setStyleSheet("border-color: black; border-width: 1px; border-style: solid;border-radius:0px;")

    def __str__(self):
        return "[Attribut] {0}".format(self.text())


class Connection:
    liste = []

    def __init__(self, attribute, right_proxy, text):

        self.label = None
        self.attribute = attribute
        self.right_proxy: DragBox = right_proxy
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

    def get_pos(self) -> list[QPointF]:
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
        self.line.setPos(0.0, 0.0)

        # Update Label
        if self.label is not None:
            self.center = self.path.boundingRect().center()
            width = self.label.boundingRect().width()
            height = self.label.boundingRect().height()
            movement = QPointF(width, height) / 2
            self.label.setPos(self.center - movement)

        return self.points


class DragBox(QtWidgets.QGraphicsProxyWidget):
    _registry = []

    # is needed to house QGroupBox (EntityRepresentation)

    def __init__(self, widget):
        super().__init__()
        self._registry.append(self)
        self.setAcceptHoverEvents(True)
        self.setWidget(widget)
        self.connections = []

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
                par:EntityRepresentation = attribute.parent()
                proxy = par.graphicsProxyWidget()
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

        x_dif, y_dif = self.check_for_exit(x_dif, y_dif)

        self.moveBy(x_dif, y_dif)

        for el in self.connections:
            el.update()

    def check_for_exit(self, x_dif, y_dif):

        top_left = self.mapToScene(self.rect().topLeft())
        bottom_right = self.mapToScene(self.rect().bottomRight())

        visible_width = self.scene().views()[0].graphicsProxyWidget().rect().width()
        visible_height = self.scene().views()[0].graphicsProxyWidget().rect().height()

        if top_left.x() < 0 and x_dif < 0:
            x_dif = 0
        if top_left.y() < 0 and y_dif < 0:
            y_dif = 0

        if bottom_right.x() > visible_width and x_dif > 0:
            x_dif = 0

        if bottom_right.y() > visible_height and y_dif > 0:
            y_dif = 0

        return x_dif, y_dif

    def mouseReleaseEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        application.instance().restoreOverrideCursor()

    def solve_collisions(self):

        collisions = self.collidingItems()

        t_bool = False

        if any(isinstance(x, DragBox) for x in collisions):
            t_bool = True

        while any(isinstance(x, DragBox) for x in collisions):
            self.moveBy(0.0, 5.0)
            collisions = self.collidingItems()

        if t_bool:
            self.moveBy(0, 10)


class EntityRepresentation(QFrame):
    """ Widget in DragBox"""

    def __init__(self, title: str):
        super().__init__()

        self.title = title
        self.setLayout(QtWidgets.QVBoxLayout())

        layout: QVBoxLayout = self.layout()

        self.setLineWidth(2)
        self.setFrameStyle(QFrame.Raised)

        style = """subcontrol-origin:margin; 
                           subcontrol-position: top center; 
                           padding-left: 0px; 
                           padding-right: 0px; 
                           border-color: black; 
                           border-width: 1px; 
                           border-style: solid;
                           border-radius:10px;
                           background-color:{}""".format(constants.INFILL_COLOR_DICT["ELSE"])

        self.setStyleSheet(style)

        self.setObjectName(self.title)

        self.title_widget = QtWidgets.QLabel(self.title)

        self.title_widget.setStyleSheet("border-style: none")
        layout.setContentsMargins(10, 10, 5, 5)

        layout.addWidget(self.title_widget)
        self.horizontal_line = QFrame()
        self.horizontal_line.setFrameShape(QFrame.HLine)
        self.horizontal_line.setFrameShadow(QFrame.Sunken)
        self.horizontal_line.setLineWidth(3)
        self.horizontal_line.setStyleSheet("color: grey ;border-width: 2px; border-style: solid;")

        layout.addWidget(self.horizontal_line)

    def __str__(self):
        return "[EntityRepresentation: {}]".format(self.title)

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        pass

    def add_attribute(self, data: Union[TemplateRule,TemplateRules]):
        text = data.has_for_attribute_name
        attrib = Attribute(text)
        self.layout().addWidget(attrib)
        attrib.show()
        return attrib


    def update_line(self):
        geo = self.horizontal_line.geometry()
        geo.setWidth(self.graphicsProxyWidget().rect().width())
        geo.setX(0)
        self.horizontal_line.setGeometry(geo)


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
        self.horizontal_layout.setSpacing(constants.LAYOUT_SPACING)
        self.horizontal_layout.setObjectName("horizontal_layout")

        # Inhalt in Fenster hinzufügen
        self.base_layout.addLayout(self.horizontal_layout, 0, 0, 1, 1)

        # Tree Widget
        self.tree_widget = QtWidgets.QTreeWidget(self.central_widget)

        # Set Size Policy for TreeWidget
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(1)
        size_policy.setHeightForWidth(self.tree_widget.sizePolicy().hasHeightForWidth())
        self.tree_widget.setSizePolicy(size_policy)
        self.tree_widget.setObjectName("tree_widget")
        self.tree_widget.headerItem().setText(0, "ConceptRoot,Concept")

        self.horizontal_layout.addWidget(self.tree_widget)

        # Vertical Layout
        self.vertical_layout = QtWidgets.QVBoxLayout()
        self.vertical_layout.setSpacing(constants.LAYOUT_SPACING)
        self.vertical_layout.setObjectName("vertical_layout")
        self.horizontal_layout.addLayout(self.vertical_layout)

        # Title
        self.title = QtWidgets.QLabel()
        self.title.setText(""
                           )
        self.vertical_layout.addWidget(self.title)

        self.type = QtWidgets.QLabel()
        self.type.setText("")
        font = QtGui.QFont()
        font.setBold(True)
        font.setFamily("Open Sans")
        font.setPointSize(10)

        self.type.setFont(font)
        self.vertical_layout.addWidget(self.type)

        self.graphics_view = MainView()
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        size_policy.setHorizontalStretch(3)
        size_policy.setVerticalStretch(1)
        size_policy.setHeightForWidth(self.graphics_view.sizePolicy().hasHeightForWidth())
        self.graphics_view.setSizePolicy(size_policy)
        self.graphics_view.setObjectName("Mainview")
        self.vertical_layout.addWidget(self.graphics_view)

        self.menubar = QtWidgets.QMenuBar(main_window)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1527, 22))
        self.menubar.setObjectName("menubar")
        main_window.setMenuBar(self.menubar)

        self.statusbar = QtWidgets.QStatusBar(main_window)
        self.statusbar.setObjectName("statusbar")
        main_window.setStatusBar(self.statusbar)

        self.retranslate_ui(main_window)
        QtCore.QMetaObject.connectSlotsByName(main_window)

    def retranslate_ui(self, main_window):
        _translate = QtCore.QCoreApplication.translate
        main_window.setWindowTitle(_translate("MainWindow", "MVD2Onto"))

        icon_path = "../Graphics/icon.ico"
        main_window.setWindowIcon(QtGui.QIcon(icon_path))
        self.initialize()

    def initialize(self):
        self.import_mvd()
        self.main_window.show()
        self.tree_widget.setColumnCount(1)
        self.scene_dict = {}
        self.add_scene()

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

        # # file_path = "../Examples/RelAssociatesMaterial.xml"
        #
        # file_path = "../Examples/Prüfregeln.mvdxml"
        #
        #file_path = "../Examples/IFC4precast_V1.01.mvdxml"

        self.mvd = MvdXml(file=file_path, validation=False)

    def add_scene(self, item: QtWidgets.QTreeWidgetItem = None):

        scene = QGraphicsScene()
        if item is None:
            scene.setObjectName("Mainview")
        else:
            scene.setObjectName(item.text(0))

        self.graphics_view.setScene(scene)
        self.scene = scene
        self.scene_dict[item] = scene

        self.graphics_view.resetTransform()
        self.graphics_view.horizontalScrollBar().setValue(0)
        self.graphics_view.verticalScrollBar().setValue(0)

    def on_tree_clicked(self, item):
        obj = item.konzept

        known_scene: QGraphicsScene = self.scene_dict.get(item)

        if known_scene is None:
            self.add_scene(item)

            if isinstance(obj, ConceptRoot):
                applicability = obj.has_applicability

                if applicability is not None:
                    rule_type = constants.APPLICABILITY
                    for rules in applicability.has_template_rules:
                        self.loop_through_rules(rules, self.scene)
                else:
                    rule_type = constants.APPLICABILITYDNE

            else:
                for rules in obj.has_template_rules:
                    self.loop_through_rules(rules, self.scene)
                rule_type = constants.RULES

            self.title.setText(obj.has_for_name)
            self.type.setText(rule_type)

            self.graphics_view.setSceneRect(self.graphics_view.scene().itemsBoundingRect())

        else:
            self.graphics_view.setScene(known_scene)
            self.scene = known_scene

    def loop_through_rules(self, rule: Union[TemplateRule, TemplateRules], parent_scene):

        if isinstance(rule, TemplateRule):
            self.add_template_rule(rule, parent_scene)
        else:
            self.add_templates_rule(rule, parent_scene)

    def add_template_rule(self, rule, scene):
        graphics_view = TemplateRuleGraphicsView(rule)
        graphics_view.add_to_scene(scene)

    def add_templates_rule(self, rule, scene):
        graphics_view = TemplateRulesGraphicsView(rule)

        for sub_rule in rule.has_template_rules:
            if isinstance(sub_rule, TemplateRule):
                self.add_template_rule(sub_rule, graphics_view.scene())
            else:
                self.add_templates_rule(sub_rule, graphics_view.scene())
        graphics_view.add_to_scene(scene)

        wid: QGraphicsProxyWidget = graphics_view.graphicsProxyWidget()
        wid.setMinimumHeight(graphics_view.sceneRect().height())


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

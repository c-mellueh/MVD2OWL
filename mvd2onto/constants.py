"""constants for visualization"""


# text constants

UNDEFINED_ROOT_NAME = "undefined"
RULES = "Rules"
APPLICABILITY = "Applicability"
APPLICABILITYDNE = "Appilcability does not exist"
TEMPLATE_RULE_TITLE = "TemplateRule"
OPERATOR_DNE = "Operator Does not exists"
# geometrical constants
BORDER_RADIUS = 10
OUTER_BORDER = 50
BORDER = 5
RESIZE_BORDER_WIDTH = 10
SCALING_FACTOR =0.1
TITLE_BLOCK_HEIGHT = 25
RECTANGLE_SPACE = BORDER
LAYOUT_SPACING = 2
MIN_RECT_SIZE = 100

#Colors

FRAME_COLOR_DICT = {
    "AND" : (0, 110, 0),            #Green
    "NAND": (160,0,0),              #Red
    "OR": (0, 10, 160),             #Blue
    "NOR": (160,0,0),               #Red
    "XOR": (130,0,140),             #Violet
    "NXOR": (160,0,0),              #Red
    "ELSE": (140, 140, 140),        #Grey
}

INFILL_COLOR_DICT = {
    "AND" : (217, 255, 217),
    "NAND": (255, 217, 217),
    "OR": (217,220,255),
    "NOR": (255, 217, 217),
    "XOR": (255,217,255),
    "NXOR": (255, 217, 217),
    "ELSE": (235, 235, 235),
}

WIDGET_BORDER_COLOR = (120,0,0)
WIDGET_LINE_WIDTH = 2
WIDGET_FRAME_STYLE = 1
ICON_PATH = "Graphics/icon.png"
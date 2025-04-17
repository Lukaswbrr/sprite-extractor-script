from krita import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

def get_q_view(view):
    window = view.window()
    q_window = window.qwindow()
    q_stacked_widget = q_window.centralWidget()
    q_mdi_area = q_stacked_widget.findChild(QMdiArea)
    for v, q_mdi_view in zip(window.views(), q_mdi_area.subWindowList()):
        if v == view:
            return q_mdi_view.widget()


def get_q_canvas(q_view):
    scroll_area = q_view.findChild(QAbstractScrollArea)
    viewport = scroll_area.viewport()
    for child in viewport.children():
        cls_name = child.metaObject().className()
        if cls_name.startswith('Kis') and ('Canvas' in cls_name):
            return child


def get_transform(view):
    def _offset(scroller):
        mid = (scroller.minimum() + scroller.maximum()) / 2.0
        return -(scroller.value() - mid)
    canvas = view.canvas()
    document = view.document()
    q_view = get_q_view(view)
    area = q_view.findChild(QAbstractScrollArea)
    zoom = (canvas.zoomLevel() * 72.0) / document.resolution()
    transform = QTransform()
    transform.translate(
            _offset(area.horizontalScrollBar()),
            _offset(area.verticalScrollBar()))
    transform.rotate(canvas.rotation())
    transform.scale(zoom, zoom)
    return transform

def get_global_from_document_coords(doc_x, doc_y):
    app = Krita.instance()
    view = app.activeWindow().activeView()
    document = view.document()
    if document:
        q_view = get_q_view(view)
        q_canvas = get_q_canvas(q_view)
        transform = get_transform(view)
        
        # Calculate the center of the document
        centerCanvas = QPointF(0.5 * document.width(), 0.5 * document.height())
        
        #Convert document coordinates to coordinates relative to the center
        local_pos = QPointF(doc_x, doc_y) - centerCanvas
        
        # Apply the transformation to convert to canvas coordinates
        transformed_pos = transform.map(local_pos)
        
        # Find the center of the canvas
        center = q_canvas.rect().center()
        
        # Convert canvas coordinates to local widget coordinates
        widget_local_pos = transformed_pos + QPointF(center)
        
        return QPoint(int(widget_local_pos.x()), int(widget_local_pos.y()))



def click_canvas(x0, y0):
    pos0 = get_global_from_document_coords(x0, y0)
    app = Krita.instance()
    view = app.activeWindow().activeView()
    document = view.document()
    if document is None:
        return

    q_view = get_q_view(view)
    canvas = get_q_canvas(q_view)    

    global_pos = QPointF(canvas.mapToGlobal(pos0))
    device = QTabletEvent.Stylus
    pointer_type = QTabletEvent.Pen
    pressure = 1
    x_tilt = 0
    y_tilt = 0
    tangential_pressure = 0.0
    rotation = 0.0
    z_pos = 0
    key_state = Qt.NoModifier
    unique_id = 1234  # ???
    button = Qt.LeftButton
    buttons = Qt.LeftButton

    canvas.activateWindow()
    
    table_press = QTabletEvent(
        QEvent.TabletPress,
        pos0,
        global_pos,
        device,
        pointer_type,
        pressure,
        x_tilt,
        y_tilt,
        tangential_pressure,
        rotation,
        z_pos,
        key_state,
        unique_id,
        button,
        buttons)

    table_release = QTabletEvent(
        QEvent.TabletRelease,
        pos0,
        global_pos,
        device,
        pointer_type,
        pressure,
        x_tilt,
        y_tilt,
        tangential_pressure,
        rotation,
        z_pos,
        key_state,
        unique_id,
        button,
        buttons)

    QApplication.sendEvent(canvas, table_press)
    QApplication.sendEvent(canvas, table_release)


app = Krita.instance()
view = app.activeWindow().activeView()
document = view.document()


def check_actions():
    for k in app.actions():
        if "select" in k.objectName():
            print(k.objectName())

def make_selection():
    doc = app.activeDocument()
    
    width = doc.width()
    height = doc.height()
    middle = width // 2

    # Create a selection for the left half
    #selection = Selection()
    #selection.select(middle, 0, middle, height, 255)
    
    #doc.setSelection(selection)
    
    docselection = doc.selection()
    
    docselection.move(-middle, 0)
    doc.setSelection(docselection)
    
    app.activeDocument().refreshProjection()

def make_click():
    doc = app.activeDocument()
    
    width = doc.width()
    height = doc.height()
    middle = width // 2    
    
    click_canvas(middle + middle // 2, height // 2)
    #app.action("invert_selection").trigger()
    #app.action('edit_cut').trigger()
    
    app.activeDocument().refreshProjection()

def make_actions():
    app.action("invert_selection").trigger()
    app.action('edit_cut').trigger()

def make_resize():
    doc = app.activeDocument()
    
    width = doc.width()
    height = doc.height()
    middle = width // 2

    # Create a selection for the left half
    #selection = Selection()
    #selection.select(0, 0, middle, height, 255)
    
    #doc.setSelection(selection)
    
    doc.resizeImage(0, 0, middle, height)

    # Update the display
    doc.refreshProjection()

def clear_select():
    app.action("deselect").trigger()

make_click()
make_selection()
make_actions()
make_resize()
clear_select()
from PIL import Image
from PySide6.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, 
                               QVBoxLayout, QHBoxLayout, QTextEdit, QStackedLayout,
                               QFileDialog, QFileDialog, QFileIconProvider, 
                               QSizePolicy, QGraphicsView, QGraphicsScene, 
                               QGraphicsPixmapItem, QProgressBar, QSpacerItem, 
                               QDialog, QFrame, QGraphicsProxyWidget, QSlider,
                               QGraphicsPathItem)
from PySide6.QtGui import (QIcon, QPixmap, QPainter, QImage, QMouseEvent, 
                           QTransform, QMovie, QIcon, QDesktopServices, QColor,
                           QBrush, QPainterPath)
from PySide6.QtCore import Qt, QFileInfo, QThread, Signal, QPoint, QTimer, QSize, QUrl, QRectF

import os, sys
import drawing as dg

class MainWindow(QWidget):
    def __init__(self, app):
        super().__init__()
        
        self.app = app
        self.resize(1100, 700)
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.draggable_area = self.rect()
        self.offset = QPoint()
        self.dragging = False
        self.draggable = True

        home = os.path.expanduser("~")
        home = home.replace("\\", '/')
        self.default_path = home +"/"+ "Downloads/"

        self.initialize_settings()
        self.initialize_ui()
        self.initialize_loading()
        self.reset_settings()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton and self.draggable and self.draggable_area.contains(event.position().toPoint()):
            self.dragging = True
            self.offset = event.position().toPoint()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.dragging:
            self.move(self.mapToParent(event.position().toPoint() - self.offset))

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton and self.dragging:
            self.dragging = False

    def initialize_ui(self):
        self.setStyleSheet(
                                """
                                QWidget 
                                {
                                    background-color: #282828;
                                }
                                """
                            )

        titlebar = self.titlebar_ui()
        self.draggable_area = titlebar.rect()
        
        self.viewer = Viewport(self)
        viewport_toolbar  = self.viewport_ui()
        toolbar = self.toolbar_ui()

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.central_layout = QHBoxLayout()
        self.central_layout.setContentsMargins(10, 5, 10, 10)
        self.central_layout.addWidget(self.viewer)
        self.central_layout.addWidget(viewport_toolbar)
        self.central_layout.addWidget(toolbar)

        self.main_layout.addWidget(titlebar)
        self.main_layout.setAlignment(titlebar, Qt.AlignTop)
        self.main_layout.addLayout(self.central_layout)

        self.setLayout(self.main_layout)

    def initialize_loading(self):
        self.loading_icon = RotatingImage(self, "Files/Icons/loading.png", 128, 128, -1, 2)
        self.loading_icon.setAlignment(Qt.AlignCenter)
        self.loading_icon.setFixedSize(300, 300)
        self.loading_icon.move(400, 200)
        self.loading_icon.hide()
        self.loading_icon.setStyleSheet(
            """
                QGraphicsView
                {
                    border: 0px;
                }
            """
        )

    def initialize_settings(self):
        self.loading = False
        self.resize_factor = 1.5
        self.rasterize_edge = 2
        self.shadow_threshold = 72
        self.prewitt_threshold = 164

    def reset_settings(self):
        self.resize_factor = 1.5
        self.scaling_slider.setValue(15)

        self.rasterize_edge = 2
        self.rasterize_slider.setValue(20)

        self.shadow_threshold = 72
        self.shadow_slider.setValue(72)

        self.prewitt_threshold = 164
        self.prewitt_slider.setValue(164)

    def titlebar_ui(self) -> QWidget:
        app_icon = QPixmap("Files/Icons/icon.png")
        app_icon = app_icon.scaled(30, 30, Qt.AspectRatioMode.KeepAspectRatio, Qt.SmoothTransformation)

        icon_label = QLabel()
        icon_label.setPixmap(app_icon)
        icon_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        title_label = QLabel("Dijkstra")
        title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        title_label.setStyleSheet(
                                    """
                                    QLabel
                                    {
                                        color: #CCCCCC; 
                                        font-size: 16px; 
                                        font-weight: 550;
                                    }
                                    """
                                )

        close_icon = QPixmap("Files/Icons/close.png")

        close_button = QPushButton()
        close_button.setIcon(close_icon)
        close_button.setFixedSize(20, 20)
        close_button.clicked.connect(self.close)
        close_button.setStyleSheet(
                                    """
                                    QPushButton {
                                        font-size: 15px;
                                        font-weight: 800;
                                        padding: 8px 8px;
                                        border-radius: 5px;

                                        background-color: #151515;
                                        border: 1px solid #555555;
                                        color: #CCCCCC;
                                    }
                                    
                                    QPushButton:hover {
                                        background-color: #AA4040;
                                        border: 0px solid #555555;
                                        color: #101010;
                                    }
                                    
                                    QPushButton:pressed {
                                        background-color: #444444;
                                        border: 2px solid #777777;
                                        color: #CCCCCC;
                                    }
                                    """
                                )

        minimize_icon = QPixmap("Files/Icons/minimize.png")

        minimize_button = QPushButton()
        minimize_button.setIcon(minimize_icon)
        minimize_button.setFixedSize(20, 20)
        minimize_button.clicked.connect(self.showMinimized)
        minimize_button.setStyleSheet(
                                    """
                                    QPushButton {
                                        font-size: 15px;
                                        font-weight: 800;
                                        padding: 8px 8px;
                                        border-radius: 5px;

                                        background-color: #151515;
                                        border: 1px solid #555555;
                                        color: #CCCCCC;
                                    }
                                    
                                    QPushButton:hover {
                                        background-color: #80AA80;
                                        border: 0px solid #555555;
                                        color: #101010;
                                    }
                                    
                                    QPushButton:pressed {
                                        background-color: #444444;
                                        border: 2px solid #777777;
                                        color: #CCCCCC;
                                    }
                                    """
                                )

        title_layout = QHBoxLayout()
        title_layout.addWidget(icon_label)
        title_layout.setAlignment(icon_label, Qt.AlignRight | Qt.AlignVCenter)
        title_layout.addSpacing(5)
        title_layout.addWidget(title_label)
        title_layout.setAlignment(title_label, Qt.AlignLeft | Qt.AlignVCenter)

        button_layout = QHBoxLayout()
        button_layout.addWidget(minimize_button)
        button_layout.setAlignment(minimize_button, Qt.AlignRight | Qt.AlignVCenter)
        button_layout.addSpacing(5)
        button_layout.addWidget(close_button)
        button_layout.setAlignment(close_button, Qt.AlignLeft | Qt.AlignVCenter)

        titlebar_layout = QHBoxLayout()
        titlebar_layout.addSpacing(5)
        titlebar_layout.addLayout(title_layout)
        titlebar_layout.setAlignment(title_layout, Qt.AlignLeft | Qt.AlignVCenter)
        titlebar_layout.addLayout(button_layout)
        titlebar_layout.setAlignment(button_layout, Qt.AlignRight | Qt.AlignVCenter)
        titlebar_layout.addSpacing(5)

        titlebar_widget = QWidget()
        titlebar_widget.setFixedSize(1100, 40)
        titlebar_widget.setLayout(titlebar_layout)
        titlebar_widget.setStyleSheet(
                                        """
                                            QWidget {
                                                border-radius: 0px;
                                                background-color: #151515;
                                            }
                                        """
                                    )

        return titlebar_widget
    
    def toolbar_ui(self):
        open_button = QPushButton('OPEN')
        open_button.setFixedSize(205, 40)
        open_button.setToolTip("Open an image")
        open_button.clicked.connect(self.open_file)
        open_button.setStyleSheet(
                                    """
                                    QPushButton {
                                        font-size: 15px;
                                        font-weight: 800;
                                        padding: 8px 8px;
                                        border-radius: 5px;

                                        background-color: #151515;
                                        border: 1px solid #555555;
                                        color: #CCCCCC;
                                    }
                                    
                                    QPushButton:hover {
                                        background-color: #8080AA;
                                        border: 0px solid #555555;
                                        color: #101010;
                                    }
                                    
                                    QPushButton:pressed {
                                        background-color: #444444;
                                        border: 2px solid #777777;
                                        color: #CCCCCC;
                                    }
                                    """
                                )
        
        export_button = QPushButton('EXPORT')
        export_button.setToolTip("Saves the current image")
        export_button.setFixedSize(205, 40)
        # export_button.clicked.connect(self.export_file)
        export_button.setStyleSheet(
                                    """
                                    QPushButton {
                                        font-size: 15px;
                                        font-weight: 800;
                                        padding: 8px 8px;
                                        border-radius: 5px;

                                        background-color: #151515;
                                        border: 1px solid #555555;
                                        color: #CCCCCC;
                                    }
                                    
                                    QPushButton:hover {
                                        background-color: #8080AA;
                                        border: 0px solid #555555;
                                        color: #101010;
                                    }
                                    
                                    QPushButton:pressed {
                                        background-color: #444444;
                                        border: 2px solid #777777;
                                        color: #CCCCCC;
                                    }
                                    """
                                )

        button_icon = QIcon("Files/Icons/button.png")

        self.shadow_button = QPushButton()
        self.shadow_button.setIcon(button_icon)
        self.shadow_button.setEnabled(False)
        self.shadow_button.setToolTip("Re-renders the shadow layer")
        self.shadow_button.setIconSize(QSize(20, 20))
        self.shadow_button.setFixedSize(35, 35)
        self.shadow_button.clicked.connect(self.change_shadow)
        self.shadow_button.setStyleSheet(
                                    """
                                    QPushButton {
                                        font-size: 15px;
                                        font-weight: 800;
                                        padding: 8px 8px;
                                        border-radius: 5px;

                                        background-color: #151515;
                                        border: 1px solid #555555;
                                        color: #CCCCCC;
                                    }
                                    
                                    QPushButton:hover {
                                        background-color: #8080AA;
                                        border: 0px solid #555555;
                                        color: #101010;
                                    }
                                    
                                    QPushButton:pressed {
                                        background-color: #444444;
                                        border: 2px solid #777777;
                                        color: #CCCCCC;
                                    }

                                    QPushButton:disabled {
                                        background-color: #303030;
                                        border: 1px solid #505050;
                                        color: #707070;
                                    }
                                    """
                                )

        shadow_caption = QLabel("Shadow")
        shadow_caption.setAlignment(Qt.AlignRight)
        shadow_caption.setToolTip("Changes the amount of shadow in drawing")
        shadow_caption.setFixedWidth(100)
        shadow_caption.setStyleSheet(
                                    """
                                    QLabel
                                    {
                                        color: #A0A0A0; 
                                        font-size: 17px; 
                                        font-weight: 600;
                                    }
                                    """
                                )

        self.shadow_slider = SliderInt(255)

        shadow_layout = QHBoxLayout()
        shadow_layout.addSpacing(5)
        shadow_layout.addWidget(shadow_caption)
        shadow_layout.setAlignment(shadow_caption, Qt.AlignVCenter)
        shadow_layout.addWidget(self.shadow_slider)
        shadow_layout.addWidget(self.shadow_button)
        shadow_layout.addSpacing(5)

        self.prewitt_button = QPushButton()
        self.prewitt_button.setIcon(button_icon)
        self.prewitt_button.setEnabled(False)
        self.prewitt_button.setToolTip("Re-renders the prewitt(edge) layer")
        self.prewitt_button.setIconSize(QSize(20, 20))
        self.prewitt_button.setFixedSize(35, 35)
        self.prewitt_button.clicked.connect(self.change_prewitt)
        self.prewitt_button.setStyleSheet(
                                    """
                                    QPushButton {
                                        font-size: 15px;
                                        font-weight: 800;
                                        padding: 8px 8px;
                                        border-radius: 5px;

                                        background-color: #151515;
                                        border: 1px solid #555555;
                                        color: #CCCCCC;
                                    }
                                    
                                    QPushButton:hover {
                                        background-color: #8080AA;
                                        border: 0px solid #555555;
                                        color: #101010;
                                    }
                                    
                                    QPushButton:pressed {
                                        background-color: #444444;
                                        border: 2px solid #777777;
                                        color: #CCCCCC;
                                    }

                                    QPushButton:disabled {
                                        background-color: #303030;
                                        border: 1px solid #505050;
                                        color: #707070;
                                    }
                                    """
                                )

        prewitt_caption = QLabel("Edge")
        prewitt_caption.setAlignment(Qt.AlignRight)
        prewitt_caption.setToolTip("Changes the amount of egdes in the drawing")
        prewitt_caption.setFixedWidth(100)
        prewitt_caption.setStyleSheet(
                                    """
                                    QLabel
                                    {
                                        color: #A0A0A0; 
                                        font-size: 17px; 
                                        font-weight: 600;
                                    }
                                    """
                                )

        self.prewitt_slider = SliderInt(255)

        prewitt_layout = QHBoxLayout()
        prewitt_layout.addSpacing(5)
        prewitt_layout.addWidget(prewitt_caption)
        prewitt_layout.setAlignment(prewitt_caption, Qt.AlignVCenter)
        prewitt_layout.addWidget(self.prewitt_slider)
        prewitt_layout.addWidget(self.prewitt_button)
        prewitt_layout.addSpacing(5)

        scaling_caption = QLabel("Scaling")
        scaling_caption.setAlignment(Qt.AlignRight)
        scaling_caption.setToolTip("Factor to which the image is rescaled for drawing(change only matter while openning an image)")
        scaling_caption.setFixedWidth(100)
        scaling_caption.setStyleSheet(
                                    """
                                    QLabel
                                    {
                                        color: #A0A0A0; 
                                        font-size: 17px; 
                                        font-weight: 600;
                                    }
                                    """
                                )

        self.scaling_slider = SliderFloat(50, 10)
        self.scaling_slider.valueChange.connect(self.change_scaling)

        scaling_layout = QHBoxLayout()
        scaling_layout.addSpacing(5)
        scaling_layout.addWidget(scaling_caption)
        scaling_layout.setAlignment(scaling_caption, Qt.AlignVCenter)
        scaling_layout.addWidget(self.scaling_slider)
        scaling_layout.addSpacing(5)

        rasterize_caption = QLabel("Rasterization")
        rasterize_caption.setAlignment(Qt.AlignRight)
        rasterize_caption.setToolTip("Controls how much rasterized the edges are(a higher value might result in lower performance)")
        rasterize_caption.setFixedWidth(100)
        rasterize_caption.setStyleSheet(
                                    """
                                    QLabel
                                    {
                                        color: #A0A0A0; 
                                        font-size: 17px; 
                                        font-weight: 600;
                                    }
                                    """
                                )

        self.rasterize_slider = SliderFloat(50, 10)
        self.rasterize_slider.valueChange.connect(self.change_rasterization)

        rasterize_layout = QHBoxLayout()
        rasterize_layout.addSpacing(5)
        rasterize_layout.addWidget(rasterize_caption)
        rasterize_layout.setAlignment(rasterize_caption, Qt.AlignVCenter)
        rasterize_layout.addWidget(self.rasterize_slider)
        rasterize_layout.addSpacing(5)

        reset_button = QPushButton('RESET')
        reset_button.setFixedSize(120, 40)
        reset_button.setToolTip("Resets the parameters to default")
        reset_button.clicked.connect(self.reset_settings)
        reset_button.setStyleSheet(
                                    """
                                    QPushButton {
                                        font-size: 15px;
                                        font-weight: 800;
                                        padding: 8px 8px;
                                        border-radius: 5px;

                                        background-color: #151515;
                                        border: 1px solid #555555;
                                        color: #CCCCCC;
                                    }
                                    
                                    QPushButton:hover {
                                        background-color: #8080AA;
                                        border: 0px solid #555555;
                                        color: #101010;
                                    }
                                    
                                    QPushButton:pressed {
                                        background-color: #444444;
                                        border: 2px solid #777777;
                                        color: #CCCCCC;
                                    }
                                    """
                                )

        central_layout = QVBoxLayout()
        central_layout.addLayout(scaling_layout)
        central_layout.addLayout(rasterize_layout)
        central_layout.addLayout(shadow_layout)
        central_layout.addLayout(prewitt_layout)
        central_layout.addSpacing(20)
        central_layout.addWidget(reset_button)
        central_layout.setAlignment(reset_button, Qt.AlignHCenter)

        button_layout = QHBoxLayout()
        button_layout.addWidget(open_button)
        button_layout.setAlignment(open_button, Qt.AlignRight)
        button_layout.addSpacing(10)
        button_layout.addWidget(export_button)
        button_layout.setAlignment(export_button, Qt.AlignLeft)

        description = "The compile time depends on the size of the image and the parameters set."

        description_caption = QLabel(description)
        description_caption.setAlignment(Qt.AlignCenter)
        description_caption.setWordWrap(True)
        description_caption.setFixedSize(300, 50)
        description_caption.setStyleSheet(
                                    """
                                    QLabel
                                    {
                                        color: #606060; 
                                        font-size: 15px; 
                                        font-weight: 500;
                                        padding: 4px 4px;
                                    }
                                    """
                                )

        self.run_button = QPushButton('RUN')
        self.run_button.setEnabled(False)
        self.run_button.setFixedHeight(40)
        self.run_button.setToolTip("Runs the drawing algorithm")
        self.run_button.clicked.connect(self.run_algorithm)
        self.run_button.setStyleSheet(
                                    """
                                    QPushButton {
                                        font-size: 15px;
                                        font-weight: 800;
                                        padding: 8px 8px;
                                        border-radius: 5px;

                                        background-color: #151515;
                                        border: 1px solid #555555;
                                        color: #CCCCCC;
                                    }
                                    
                                    QPushButton:hover {
                                        background-color: #8080AA;
                                        border: 0px solid #555555;
                                        color: #101010;
                                    }
                                    
                                    QPushButton:pressed {
                                        background-color: #444444;
                                        border: 2px solid #777777;
                                        color: #CCCCCC;
                                    }

                                    QPushButton:disabled {
                                        background-color: #303030;
                                        border: 1px solid #505050;
                                        color: #707070;
                                    }
                                    """
                                )
        
        toolbar_layout = QVBoxLayout()
        toolbar_layout.addSpacing(10)
        toolbar_layout.addLayout(button_layout)
        toolbar_layout.setAlignment(button_layout, Qt.AlignTop)
        toolbar_layout.addSpacing(64)
        toolbar_layout.addLayout(central_layout)
        toolbar_layout.setAlignment(central_layout, Qt.AlignTop)
        toolbar_layout.addItem(QSpacerItem(100, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        toolbar_layout.addWidget(description_caption)
        toolbar_layout.setAlignment(description_caption, Qt.AlignBottom | Qt.AlignHCenter)
        toolbar_layout.addWidget(self.run_button)
        toolbar_layout.setAlignment(self.run_button, Qt.AlignBottom)

        toolbar_widget = QWidget()
        toolbar_widget.setLayout(toolbar_layout)

        return toolbar_widget

    def viewport_ui(self):
        refresh_icon = QIcon("Files/Icons/reset.png")

        reset_viewport_button = QPushButton()
        reset_viewport_button.setToolTip("Resets the view to fit the viewport")
        reset_viewport_button.setIcon(refresh_icon)
        reset_viewport_button.setIconSize(QSize(20, 20))
        reset_viewport_button.setFixedSize(35, 35)
        reset_viewport_button.clicked.connect(self.viewer.fitInView)
        reset_viewport_button.setStyleSheet(
                                    """
                                    QPushButton {
                                        font-size: 15px;
                                        font-weight: 800;
                                        padding: 8px 8px;
                                        border-radius: 5px;

                                        background-color: #151515;
                                        border: 1px solid #555555;
                                        color: #CCCCCC;
                                    }
                                    
                                    QPushButton:hover {
                                        background-color: #8080AA;
                                        border: 0px solid #555555;
                                        color: #101010;
                                    }
                                    
                                    QPushButton:pressed {
                                        background-color: #444444;
                                        border: 2px solid #777777;
                                        color: #CCCCCC;
                                    }
                                    """
                                )
        
        viewport_layout = QVBoxLayout()
        viewport_layout.addWidget(reset_viewport_button)
        viewport_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        viewport_widget = QWidget()
        viewport_widget.setLayout(viewport_layout)
        viewport_widget.setStyleSheet(
            """
                QWidget
                {
                    border: 1px solid #404040;
                    background-color: #303030; 
                    border-radius: 8px;
                }
            """
        )

        return viewport_widget
    
    def start_loading(self):
        self.loading = True
        self.loading_icon.start_animation()
        self.loading_icon.show()

    def stop_loading(self):
        self.loading = False
        self.loading_icon.stop_animation()
        self.loading_icon.hide()

    #worker thread
    def open_file(self):
        if not self.loading:
            path = QFileDialog.getOpenFileName(self, "Open File", self.default_path, "All Files (*);; PNG Files (*.png);; JPG Files (*.jpg)")
            
            if not path[0] == "":
                self.image = Image.open(path[0])
                self.image = dg.alpha_removal(self.image)

                pixmap = dg.pil_to_pixmap(self.image)
                self.viewer.setPhoto(pixmap)

                self.shadow = None
                self.prewitt = None

                self.run_button.setEnabled(True)
                self.shadow_button.setEnabled(False)
                self.prewitt_button.setEnabled(False)

    def refresh_viewer(self):
        pixmap = dg.pil_to_pixmap(self.drawing)
        self.viewer.setPhoto(pixmap)

    def create_shadow(self):
        self.shadow = dg.thresholding(self.image, self.shadow_threshold)
        self.shadow = dg.rasterize(self.shadow, self.rasterize_edge)

    def create_prewitt(self):
        self.prewitt = dg.thresholding(self.prewitt_edge, self.prewitt_threshold)
        self.prewitt = dg.rasterize(self.prewitt, self.rasterize_edge)

    def render_drawing(self):
        background = Image.new("L", self.image.size, 169)

        self.drawing = dg.addition(self.shadow, self.prewitt)
        self.drawing = dg.addition(background, self.drawing)

        self.refresh_viewer()

    #worker thread
    def change_shadow(self):
        if not self.loading:
            self.shadow_threshold = self.shadow_slider.getValue()
            self.create_shadow()
            self.render_drawing()
    
    #worker thread
    def change_prewitt(self):
        if not self.loading:
            self.prewitt_threshold = self.prewitt_slider.getValue()
            self.create_prewitt()
            self.render_drawing()

    def change_scaling(self, value: float):
        self.resize_factor = value
    
    def change_rasterization(self, value: float):
        self.rasterize_edge = value

    #worker thread
    def run_algorithm(self):
        if not self.loading:

            self.image = dg.resize(self.image, self.resize_factor)
            self.prewitt_edge = dg.prewitt(self.image, 1.5)

            self.create_shadow()
            self.create_prewitt()
            self.render_drawing()

            self.run_button.setEnabled(False)
            self.shadow_button.setEnabled(True)
            self.prewitt_button.setEnabled(True)

class Viewport(QGraphicsView):
    def __init__(self, parent):
        super(Viewport, self).__init__(parent)
        pixmap = QPixmap("Files/Icons/github.png")
        pixmap = pixmap.scaled(pixmap.width()/1.6, pixmap.height()/1.6, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        self._zoom = 0
        self._empty = True
        self._scene = QGraphicsScene(self)
        self._photo = QGraphicsPixmapItem()
        self._photo.setPixmap(pixmap)
        self._scene.addItem(self._photo)
        self.setRenderHint(QPainter.Antialiasing)

        self.setScene(self._scene)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QBrush(QColor(30, 30, 30)))
        self.setFrameShape(QFrame.NoFrame)
        self.setAcceptDrops(True)

    def hasPhoto(self):
        return not self._empty

    def fitInView(self, scale=True):
        rect = QRectF(self._photo.pixmap().rect())
        if not rect.isNull():
            self.setSceneRect(rect)
            if self.hasPhoto():
                unity = self.transform().mapRect(QRectF(0, 0, 1, 1))
                self.scale(1 / unity.width(), 1 / unity.height())
                viewrect = self.viewport().rect()
                scenerect = self.transform().mapRect(rect)
                factor = min(viewrect.width() / scenerect.width(),
                             viewrect.height() / scenerect.height())
                self.scale(factor, factor)
            self._zoom = 0

    def setPhoto(self, pixmap=None):
        self._zoom = 0
        if pixmap and not pixmap.isNull():
            self._empty = False
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self._photo.setPixmap(pixmap)
            self._size = self.size() 
        else:
            self._empty = True
            self.setDragMode(QGraphicsView.NoDrag)
            self._photo.setPixmap(QPixmap())
        self.fitInView()

    def wheelEvent(self, event):
        if self.hasPhoto():
            if event.angleDelta().y() > 0:
                self.zoomFactor = 1.1
                self._zoom += 1
            else:
                self.zoomFactor = 0.9
                self._zoom -= 1
            
            self.zoomCheck()

    def zoomIn(self):
        self.zoomFactor = 1.1
        self._zoom += 1
        self.zoomCheck()

    def zoomOut(self):
        self.zoomFactor = 0.9
        self._zoom -= 1
        self.zoomCheck()

    def zoomCheck(self):
        if self._zoom > 0:
            if self._zoom < 20:
                self.scale(self.zoomFactor, self.zoomFactor)
            else:
                self._zoom = 20
        elif self._zoom == 0:
            self.fitInView()
        else:
            if self._zoom > -20:
                self.scale(self.zoomFactor, self.zoomFactor)
            else:
                self._zoom = -20

    def toggleDragMode(self):
        if self.dragMode() == QGraphicsView.ScrollHandDrag:
            self.setDragMode(QGraphicsView.NoDrag)
        elif not self._photo.pixmap().isNull():
            self.setDragMode(QGraphicsView.ScrollHandDrag)

    def mousePressEvent(self, event: QMouseEvent):
        super(Viewport, self).mousePressEvent(event)

    def dragEnterEvent(self, event):
        if event.mimeData().hasImage:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasImage:
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasImage:
            event.setDropAction(Qt.CopyAction)
            event.accept()
            # Get the file path of the dropped image
            file_path = event.mimeData().urls()[0].toLocalFile()
            self.parent().openFile(file_path)
            self.setAcceptDrops(False)
        else:
            event.ignore()

class SliderInt(QWidget):
    valueChange = Signal(int)

    def __init__(self, maximum: int):
        super(SliderInt, self).__init__()
        layout = QHBoxLayout()
        self.setContentsMargins(0, 0, 0, 0)

        self.setStyleSheet("""
            QWidget {
                background: #282828;
            }
        """)

        self.slider = QSlider()
        self.slider.setOrientation(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(maximum)
        self.slider.setStyleSheet("""
            QSlider {
                border: 2px solid #505050;
                padding: 3px 5px;
                height: 20px;     
                border-radius: 10px;
            }
                                  
            QSlider::groove:horizontal {
                background: #505050;
                height: 12px;
                border-radius: 4px;
            }
            
            QSlider::handle:horizontal {
                background: #282828;
                border: 6px solid #505050;
                width: 14px;
                height: 14px;
                margin: -5px -3px;
                border-radius: 7px;
            }
        """)

        self.label = QLabel(str(self.slider.value()))
        self.label.setFixedWidth(30)
        self.label.setStyleSheet(
                                    """
                                    QLabel
                                    {
                                        color: #A0A0A0; 
                                        font-size: 17px; 
                                        font-weight: 600;
                                    }
                                    """
                                )
        self.slider.valueChanged.connect(self.onSliderValueChanged)

        layout.addWidget(self.slider)
        layout.addWidget(self.label)
        layout.setAlignment(self.label, Qt.AlignLeft | Qt.AlignVCenter)

        self.setLayout(layout)

    def onSliderValueChanged(self, value):
        self.label.setText(str(value))
        self.valueChange.emit(value)

    def setValue(self, value: int):
        self.label.setText(str(value))
        self.slider.setValue(value)

    def getValue(self) -> float:
        return self.slider.value()

class SliderFloat(QWidget):
    valueChange = Signal(float)

    def __init__(self, maximum: int, factor: float):
        super(SliderFloat, self).__init__()
        layout = QHBoxLayout()
        self.factor = factor
        self.setContentsMargins(0, 0, 0, 0)

        self.setStyleSheet("""
            QWidget {
                background: #282828;
            }
        """)

        self.slider = QSlider()
        self.slider.setOrientation(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(maximum)
        self.slider.setStyleSheet("""
            QSlider {
                border: 2px solid #505050;
                padding: 3px 5px;
                height: 20px;     
                border-radius: 10px;
            }
                                  
            QSlider::groove:horizontal {
                background: #505050;
                height: 12px;
                border-radius: 4px;
            }
            
            QSlider::handle:horizontal {
                background: #282828;
                border: 6px solid #505050;
                width: 14px;
                height: 14px;
                margin: -5px -3px;
                border-radius: 7px;
            }
        """)

        self.label = QLabel(str(self.slider.value() / self.factor))
        self.label.setFixedWidth(40)
        self.label.setStyleSheet(
                                    """
                                    QLabel
                                    {
                                        color: #A0A0A0; 
                                        font-size: 17px; 
                                        font-weight: 600;
                                    }
                                    """
                                )
        self.slider.valueChanged.connect(self.onSliderValueChanged)

        layout.addWidget(self.slider)
        layout.addWidget(self.label)
        layout.setAlignment(self.label, Qt.AlignLeft | Qt.AlignVCenter)

        self.setLayout(layout)

    def onSliderValueChanged(self, value):
        value = value / self.factor
        self.label.setText(str(value))
        self.valueChange.emit(value)

    def setValue(self, value: int):
        self.label.setText(str(value / self.factor))
        self.slider.setValue(value)

    def getValue(self) -> float:
        return self.slider.value() / self.factor

class RotatingImage(QGraphicsView):
    steps = 1
    interval = 10

    def __init__(self, parent, image: str, w: int, h: int, steps: float = None, interval: float = None):
        super().__init__(parent=parent)

        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

        if steps is not None:
            self.steps = steps

        if interval is not None:
            self.interval = interval

        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        rounded_rect = QPainterPath()
        rounded_rect.addRoundedRect(-35, -35, 200, 200, 30, 30)

        rectangle = QGraphicsPathItem(rounded_rect)
        stroke = QColor(0, 0, 0, 0)
        fill = QColor(0, 0, 0, 64)
        rectangle.setBrush(fill)
        rectangle.setPen(stroke)
        self.scene.addItem(rectangle)

        self.pixmap_item = QGraphicsPixmapItem()
        self.pixmap_item.setTransformationMode(Qt.SmoothTransformation)
        self.pixmap_item.setShapeMode(QGraphicsPixmapItem.BoundingRectShape)
        self.scene.addItem(self.pixmap_item)

        pixmap = QPixmap(image).scaled(w, h, Qt.AspectRatioMode.KeepAspectRatio, Qt.SmoothTransformation)
        self.pixmap_item.setPixmap(pixmap)

    def drawBackground(self, painter, rect):
        painter.setBrush(Qt.transparent)

    def start_animation(self):
        self.rotation_angle = 0
        self.rotation_timer = QTimer()
        self.rotation_timer.timeout.connect(self.update_rotation)
        self.rotation_timer.start(self.interval)

    def update_rotation(self):
        self.rotation_angle += self.steps
        pixmap_width = self.pixmap_item.pixmap().width()
        pixmap_height = self.pixmap_item.pixmap().height()
        transform = QTransform().translate(pixmap_width / 2, pixmap_height / 2).rotate(self.rotation_angle).translate(-pixmap_width / 2, -pixmap_height / 2)
        self.pixmap_item.setTransform(transform)

    def stop_animation(self):
        self.rotation_timer.stop()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow(app)
    window.show()
    app.exec()
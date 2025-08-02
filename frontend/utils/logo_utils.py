from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from frontend.constants import LOGO_PATH

def create_logo_label(height=60):
    """
    Create a logo label with the Pete logo or text.
    
    :param height: Height to scale the logo to
    :return: QLabel with logo or text
    """
    label = QLabel()
    pixmap = QPixmap(LOGO_PATH)
    
    if not pixmap.isNull():
        # Scale logo while maintaining aspect ratio
        pixmap = pixmap.scaledToHeight(height, Qt.SmoothTransformation)
        label.setPixmap(pixmap)
        label.setAlignment(Qt.AlignCenter)
    else:
        # Fallback text if logo not found
        label.setText('PETE')
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet('font-size: 32px; font-weight: bold; color: #1976d2;')
    
    return label 
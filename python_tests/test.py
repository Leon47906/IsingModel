import sys
import numpy as np
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QLabel,
    QSlider,
    QPushButton,
    QComboBox,
    QDoubleSpinBox,
)
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QImage, QPixmap
import isingmodel

width, height = 500, 500


class IsingWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ising Model")
        self.lattice = isingmodel.Lattice(width, height, 2.0, 0.0)
        self.running = True

        self.image_label = QLabel()
        self.info_label = QLabel()

        self.temp_slider = QSlider(Qt.Horizontal)
        self.temp_slider.setRange(0, 100)
        self.temp_slider.setValue(20)
        self.temp_slider.valueChanged.connect(self.on_temp_slider_changed)

        self.temp_spinbox = QDoubleSpinBox()
        self.temp_spinbox.setRange(0.0, 10.0)
        self.temp_spinbox.setSingleStep(0.1)
        self.temp_spinbox.setDecimals(2)
        self.temp_spinbox.setValue(2.0)
        self.temp_spinbox.valueChanged.connect(self.on_temp_spinbox_changed)

        self.reset_temp_button = QPushButton("Reset T")
        self.reset_temp_button.clicked.connect(self.reset_temperature)

        self.mag_slider = QSlider(Qt.Horizontal)
        self.mag_slider.setRange(-500, 500)
        self.mag_slider.setValue(0)
        self.mag_slider.valueChanged.connect(self.on_mag_slider_changed)

        self.mag_spinbox = QDoubleSpinBox()
        self.mag_spinbox.setRange(-5.0, 5.0)
        self.mag_spinbox.setSingleStep(0.1)
        self.mag_spinbox.setDecimals(2)
        self.mag_spinbox.setValue(0.0)
        self.mag_spinbox.valueChanged.connect(self.on_mag_spinbox_changed)

        self.reset_mag_button = QPushButton("Reset H_z")
        self.reset_mag_button.clicked.connect(self.reset_mag)

        self.pause_button = QPushButton("Pause")
        self.pause_button.clicked.connect(self.toggle_pause)

        self.algorithm_selector = QComboBox()
        self.algorithm_selector.addItems(["Metropolis", "Wolff"])
        self.algorithm_selector.currentTextChanged.connect(self.set_algorithm)
        self.algorithm = "Metropolis"

        controls = QHBoxLayout()
        controls.addWidget(QLabel("Temperature:"))
        controls.addWidget(self.temp_slider)
        controls.addWidget(self.temp_spinbox)
        controls.addWidget(self.reset_temp_button)
        controls.addWidget(QLabel("Magnetic field:"))
        controls.addWidget(self.mag_slider)
        controls.addWidget(self.mag_spinbox)
        controls.addWidget(self.reset_mag_button)
        controls.addWidget(self.pause_button)
        controls.addWidget(QLabel("Algorithm:"))
        controls.addWidget(self.algorithm_selector)

        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        layout.addWidget(self.info_label)
        layout.addLayout(controls)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_sim)
        self.timer.start(50)

    def set_algorithm(self, text):
        self.algorithm = text
        is_wolff = text == "Wolff"
        self.mag_slider.setEnabled(not is_wolff)
        self.mag_spinbox.setEnabled(not is_wolff)
        self.reset_mag_button.setEnabled(not is_wolff)
        if is_wolff and self.lattice.h_z != 0.0:
            self.reset_mag()

    def on_temp_slider_changed(self, value):
        temperature = value / 10.0
        self.lattice.temperature = temperature
        self.temp_spinbox.blockSignals(True)
        self.temp_spinbox.setValue(temperature)
        self.temp_spinbox.blockSignals(False)

    def on_temp_spinbox_changed(self, value):
        self.lattice.temperature = value
        self.temp_slider.blockSignals(True)
        self.temp_slider.setValue(int(value * 10))
        self.temp_slider.blockSignals(False)

    def reset_temperature(self):
        self.temp_spinbox.setValue(2.0)  # triggers on_temp_spinbox_changed

    def on_mag_slider_changed(self, value):
        h_z = value / 100.0
        self.lattice.h_z = h_z
        self.mag_spinbox.blockSignals(True)
        self.mag_spinbox.setValue(h_z)
        self.mag_spinbox.blockSignals(False)

    def on_mag_spinbox_changed(self, value):
        self.lattice.h_z = value
        self.mag_slider.blockSignals(True)
        self.mag_slider.setValue(int(value * 100))
        self.mag_slider.blockSignals(False)

    def reset_mag(self):
        self.mag_spinbox.setValue(0.0)  # triggers on_mag_spinbox_changed

    def toggle_pause(self):
        self.running = not self.running
        self.pause_button.setText("Resume" if not self.running else "Pause")

    def update_sim(self):
        if not self.running:
            return

        if self.algorithm == "Metropolis":
            for _ in range(1000):
                self.lattice.simulation_step()
        else:
            for _ in range(5):
                self.lattice.wolff_step()

        grid = np.array(self.lattice.as_array()).reshape(height, width)
        rgb = np.zeros((height, width, 3), dtype=np.uint8)
        rgb[grid == 1] = [220, 60, 60]
        rgb[grid == -1] = [60, 60, 220]

        qimg = QImage(rgb.data, width, height, 3 * width, QImage.Format_RGB888)
        self.image_label.setPixmap(QPixmap.fromImage(qimg).scaled(500, 500))

        energy = self.lattice.get_energy()
        mag = self.lattice.get_total_magnetization()
        avg_mag = mag / (width * height)
        self.info_label.setText(
            f"Energy: {energy:.2f}    Magnetization: {mag:.1f}    Avg. Magnetization: {avg_mag:.3f}"
        )


app = QApplication(sys.argv)
window = IsingWindow()
window.show()
sys.exit(app.exec())

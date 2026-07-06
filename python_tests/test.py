#import matplotlib
#matplotlib.use("TkAgg")  # must be set before importing pyplot
#
#import numpy as np
#import matplotlib.pyplot as plt
#import matplotlib.animation as animation
#import isingmodel
#
#width = 250
#height = 250
#temperature = 2.0
#h_z = 0.1
#
#lattice = isingmodel.Lattice(width, height, temperature, h_z)
#
#fig, ax = plt.subplots()
#plt.subplots_adjust(right=0.75)
#
#grid = np.array(lattice.as_array()).reshape(lattice.height, lattice.width)
#img = ax.imshow(grid, cmap="coolwarm", interpolation="nearest", vmin=-1, vmax=1)
#ax.set_title(f"Ising Model (T = {temperature}, H_z = {h_z})")
#
#info_text = fig.text(
#    0.78, 0.5, "", fontsize=11, verticalalignment="center",
#    bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
#)
#
#def update(frame):
#    for _ in range(1000):
#        lattice.simulation_step()
#
#    new_grid = np.array(lattice.as_array()).reshape(lattice.height, lattice.width)
#    img.set_data(new_grid)
#
#    energy = lattice.get_energy()
#    magnetization = lattice.get_total_magnetization()
#    n_sites = width * height
#    info_text.set_text(
#        f"Step: {frame * 1000}\n\n"
#        f"Total energy:\n{energy:.2f}\n\n"
#        f"Total magnetization:\n{magnetization}\n\n"
#        f"Avg. magnetization:\n{magnetization / n_sites:.4f}"
#    )
#
#    return [img, info_text]
#
#ani = animation.FuncAnimation(fig, update, frames=1000, interval=50, blit=False)
#plt.show()

import sys
import numpy as np
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QLabel, QSlider, QPushButton,
)
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QImage, QPixmap
import isingmodel

width, height = 250, 250

class IsingWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ising Model")
        self.lattice = isingmodel.Lattice(width, height, 2.0, 0.0)
        self.running = True

        self.image_label = QLabel()
        self.info_label = QLabel()

        self.temp_slider = QSlider(Qt.Horizontal)
        self.temp_slider.setRange(0, 20)
        self.temp_slider.setValue(2)
        self.temp_slider.valueChanged.connect(self.set_temperature)

        self.temp_label = QLabel(f"T = {self.lattice.temperature:.1f}")

        self.reset_temp_button = QPushButton("Reset T")
        self.reset_temp_button.clicked.connect(self.reset_temperature)

        self.mag_slider = QSlider(Qt.Horizontal)
        self.mag_slider.setRange(-5,5)
        self.mag_slider.setValue(0)
        self.mag_slider.valueChanged.connect(self.set_magnetic_field)

        self.mag_label = QLabel(f"H_z = {self.lattice.h_z:.1f}")

        self.reset_mag_button = QPushButton("Reset H_z")
        self.reset_mag_button.clicked.connect(self.reset_mag)

        self.pause_button = QPushButton("Pause")
        self.pause_button.clicked.connect(self.toggle_pause)

        controls = QHBoxLayout()
        controls.addWidget(QLabel("Temperature:"))
        controls.addWidget(self.temp_slider)
        controls.addWidget(self.temp_label)
        controls.addWidget(self.reset_temp_button)
        controls.addWidget(QLabel("Magnetic field:"))
        controls.addWidget(self.mag_slider)
        controls.addWidget(self.mag_label)
        controls.addWidget(self.reset_mag_button)
        controls.addWidget(self.pause_button)

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

    def set_temperature(self, value):
        self.lattice.temperature = value
        self.temp_label.setText(f"T = {self.lattice.temperature:.1f}")

    def reset_temperature(self):
        self.temp_slider.setValue(2)

    def set_magnetic_field(self, value):
        self.lattice.h_z = value
        self.mag_label.setText(f"H_z = {self.lattice.h_z:.1f}")

    def reset_mag(self):
        self.mag_slider.setValue(0)

    def toggle_pause(self):
        self.running = not self.running
        self.pause_button.setText("Resume" if not self.running else "Pause")

    def update_sim(self):
        if not self.running:
            return
        for _ in range(1000):
            self.lattice.simulation_step()

        grid = np.array(self.lattice.as_array()).reshape(height, width)
        rgb = np.zeros((height, width, 3), dtype=np.uint8)
        rgb[grid == 1] = [220, 60, 60]
        rgb[grid == -1] = [60, 60, 220]

        qimg = QImage(rgb.data, width, height, 3 * width, QImage.Format_RGB888)
        self.image_label.setPixmap(QPixmap.fromImage(qimg).scaled(500, 500))

        energy = self.lattice.get_energy()
        mag = self.lattice.get_total_magnetization()
        avg_mag = mag/(width * height)
        self.info_label.setText(f"Energy: {energy:.2f}    Magnetization: {mag:.1f}    Avg. Magnetization: {avg_mag:.3f}")

app = QApplication(sys.argv)
window = IsingWindow()
window.show()
sys.exit(app.exec())

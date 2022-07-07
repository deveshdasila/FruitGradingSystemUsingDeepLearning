# importing required libraries
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *
from PyQt5.QtCore import *
import os
import sys
import time
import cv2
import numpy as np
from loguru import logger
from keras.models import load_model

model = load_model(os.getcwd()+'\weights_best.hdf5')
model.compile(loss='binary_crossentropy', optimizer='rmsprop', metrics=['accuracy'])

imgPath = ''

grade = ["Unhealthy", "Healthy"]

# Main window class
class MainWindow(QMainWindow):

	# constructor
	def __init__(self):
		super().__init__()

		# setting geometry
		self.setGeometry(100, 100, 800, 600)

		# setting style sheet
		self.setStyleSheet("background : lightgrey;")

		# getting available cameras
		self.available_cameras = QCameraInfo.availableCameras()

		# if no camera found
		if not self.available_cameras:
			# exit the code
			sys.exit()

		# creating a status bar
		self.status = QStatusBar()

		# setting style sheet to the status bar
		self.status.setStyleSheet("background : white;")

		# adding status bar to the main window
		self.setStatusBar(self.status)

		# path to save
		self.save_path = os.getcwd()

		# creating a QCameraViewfinder object
		self.viewfinder = QCameraViewfinder()

		# showing this viewfinder
		self.viewfinder.show()

		# making it central widget of main window
		self.setCentralWidget(self.viewfinder)

		# Set the default camera.
		self.select_camera(0)

		# creating a tool bar
		toolbar = QToolBar("Camera Tool Bar")

		# adding tool bar to main window
		self.addToolBar(toolbar)

		# creating a photo action to take photo
		click_action = QAction("Click photo", self)

		# adding status tip to the photo action
		click_action.setStatusTip("This will capture picture")

		# adding tool tip
		click_action.setToolTip("Capture picture")


		# adding action to it
		# calling take_photo method
		click_action.triggered.connect(self.click_photo)

		# adding this to the tool bar
		toolbar.addAction(click_action)

		# creating a action to select image
		img_action = QAction("Image Select", self)

		# adding status tip to the image action
		img_action.setStatusTip("Select the saved image")

		# adding tool tip
		img_action.setToolTip("Image Select")

		# adding action to it
		# calling img_select method
		img_action.triggered.connect(self.img_select)

		# adding this to the tool bar
		toolbar.addAction(img_action)


		# creating a action to print result
		ai_action = QAction("Show Result", self)

		# adding status tip to the photo action
		ai_action.setStatusTip("This will print result")

		# adding tool tip
		ai_action.setToolTip("Show Result")

		# adding action to it
		# calling take_photo method
		ai_action.triggered.connect(self.show_result)

		# adding this to the tool bar
		toolbar.addAction(ai_action)

		# similarly creating action for changing save folder
		change_folder_action = QAction("Change save location", self)

		# adding status tip
		change_folder_action.setStatusTip("Change folder where picture will be saved saved.")

		# adding tool tip to it
		change_folder_action.setToolTip("Change save location")

		# setting calling method to the change folder action
		# when triggered signal is emitted
		change_folder_action.triggered.connect(self.change_folder)

		# adding this to the tool bar
		toolbar.addAction(change_folder_action)


		# creating a combo box for selecting camera
		camera_selector = QComboBox()

		# adding status tip to it
		camera_selector.setStatusTip("Choose camera to take pictures")

		# adding tool tip to it
		camera_selector.setToolTip("Select Camera")
		camera_selector.setToolTipDuration(2500)

		# adding items to the combo box
		camera_selector.addItems([camera.description()
								for camera in self.available_cameras])

		# adding action to the combo box
		# calling the select camera method
		camera_selector.currentIndexChanged.connect(self.select_camera)

		# adding this to tool bar
		toolbar.addWidget(camera_selector)

		# setting tool bar stylesheet
		toolbar.setStyleSheet("background : white;")


		# setting window title
		self.setWindowTitle("PyQt5 Cam")

		# showing the main window
		self.show()

	def img_select(self):
		global imgPath
		#Set the file path in name using the global variable
		# path = QFileDialog.getExistingDirectory(self, 'Open File')
		imgPath = QFileDialog.getOpenFileName(self, 'Select image')[0]
		print (f"Directory Path: {imgPath}")

	def show_result(self):
		global imgPath
		# imgPath = os.path.sep.join(('D:/Github/Final Year PRoject/GUI/output/','test2.jpg'))

		# print(imgPath)
		image = cv2.imread(imgPath)

		try:
			image = cv2.resize(image, (180, 180), interpolation=cv2.INTER_AREA)
			
			#save image after reshape
			#cv2.imwrite(imgPath, image)

			image = image * 1. / 255
			image = image.reshape(1, 180, 180, 3)

			# result=model.predict(image)
			pred = model.predict(image)
			pred = np.where(pred < 0.5, 0, 1)
			logger.critical(pred)

			logger.debug(pred)

			#pop up
			msg = QMessageBox()
			msg.setIcon(QMessageBox.Information)
			msg.setWindowTitle("Result box")
			msg.setText(f"Fruit is {grade[pred[0][0]]}.")
			#msg.setInformativeText()
			#msg.setDetailedText()
			msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
			msg.exec_()

		except Exception as e:
			print(str(e))

	# method to select camera
	def select_camera(self, i):

		# getting the selected camera
		self.camera = QCamera(self.available_cameras[i])

		# setting view finder to the camera
		self.camera.setViewfinder(self.viewfinder)

		# setting capture mode to the camera
		self.camera.setCaptureMode(QCamera.CaptureStillImage)

		# if any error occur show the alert
		self.camera.error.connect(lambda: self.alert(self.camera.errorString()))


		# start the camera
		self.camera.start()

		# creating a QCameraImageCapture object
		self.capture = QCameraImageCapture(self.camera)


		# showing alert if error occur
		self.capture.error.connect(lambda error_msg, error,
								msg: self.alert(msg))

		# when image captured showing message
		self.capture.imageCaptured.connect(lambda d,
										i: self.status.showMessage("Image captured : "
																	+ str(self.save_seq)))

		# getting current camera name
		self.current_camera_name = self.available_cameras[i].description()


		# initial save sequence
		self.save_seq = 0

	# method to take photo
	def click_photo(self):

		# time stamp
		timestamp = time.strftime("%d-%b-%Y-%H_%M_%S")

		# capture the image and save it on the save path
		imgId = self.capture.capture(os.path.join(self.save_path,
										"%s-%04d-%s.jpg" % (
			self.current_camera_name,
			self.save_seq,
			timestamp
		)))

		global imgPath
		imgPath = os.path.join(self.save_path, "%s-%04d-%s.jpg" % (self.current_camera_name, self.save_seq, timestamp))

		# increment the sequence
		self.save_seq += 1	

	# change folder method
	def change_folder(self):

		# open the dialog to select path
		path = QFileDialog.getExistingDirectory(self,
												"Picture Location", "")

		# if path is selected
		if path:

			# update the path
			self.save_path = path

			# update the sequence
			self.save_seq = 0

	# method for alerts
	def alert(self, msg):

		# error message
		error = QErrorMessage(self)

		# setting text to the error message
		error.showMessage(msg)

	def closeEvent(self, event):
		''' Close Popup'''
		reply = QMessageBox.question(self, 'Quit', 'Are you sure you want to quit?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
		if reply == QMessageBox.Yes:
			event.accept()
		else:
			event.ignore()

# Driver code
if __name__ == "__main__" :
	# create pyqt5 app
	App = QApplication(sys.argv)

	# create the instance of our Window
	window = MainWindow()

	window.show()

	# start the app
	sys.exit(App.exec())
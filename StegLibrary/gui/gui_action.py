# Builtin modules
from os import path
from webbrowser import open as webopen

# Internal modules
from StegLibrary import write_steg, extract_steg
from StegLibrary.helper import err_imp, raw_open
from StegLibrary.core.header import Header
from StegLibrary.core.errors import UnrecognisedHeaderError, SteganographyError
from StegLibrary.core.steg import extract_header
from StegLibrary.gui import Ui_MainWindow

# Non-builtin modules
try:
    from PIL import Image, UnidentifiedImageError
except ImportError:
    err_imp("Pillow")
    exit(1)

try:
from PyQt5 import QtWidgets


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs) -> None:
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.reset()
        self.register_logic()

    def reset(self):
        self.has_steg = False
        self.has_data = False
        self.has_image = False
        self.has_output = False

        self.input_filename = ""
        self.output_filename = ""
        self.image_filename = ""

        self.field_input.setText("")
        self.label_input_status.setText("Select input file")
        self.label_input_status.setStyleSheet("")
        self.field_image.setText("")
        self.label_image_status.setText("Not available")
        self.label_image_status.setStyleSheet("")
        self.field_output.setText("")
        self.label_output_status.setText("Not available")
        self.label_output_status.setStyleSheet("")
        self.field_authkey.setText("")
        self.spin_compress.setValue(9)
        self.spin_density.setValue(1)

        self.check_showim.setChecked(0)
        self.check_stdout.setChecked(0)

        self.text_output.clear()

    def register_logic(self):
        # Add function for Close button
        self.action_close.triggered.connect(self.close)

        # Add function for Help button
        self.action_help.triggered.connect(
            lambda: webopen("https://github.com/MunchDev/StegLibrary"))

        # Add function for Select (Input) button
        self.button_input.clicked.connect(self.select_input)

        # Add function for Select (Image) button
        self.button_image.clicked.connect(self.select_image)

        # Add function for Select (Output) button
        self.button_output.clicked.connect(self.select_output)

        # Add function for Create button
        self.button_create.clicked.connect(self.create)

        # Add function for Extract button
        self.button_extract.clicked.connect(self.extract)

        # Add function for Clear all button
        self.button_clear.clicked.connect(self.reset)
        pass

    def select_input(self):
        # Empty all other arguments
        self.reset()

        # Ask user to choose a file
        self.input_filename = QtWidgets.QFileDialog.getOpenFileName()[0]

        # If the user does not select any file
        # exit the routine
        if self.input_filename is None or len(self.input_filename) == 0:
            return

        # Display text output
        self.write_output("[User] File selected at: " + self.input_filename)

        # Show the path to file
        self.field_input.setText(self.input_filename)

        # Attempt to load the file into memory
        try:
            self.input_fileobject = raw_open(self.input_filename)
        except IOError as e:
            self.write_output("[System] " + str(e.strerror))
            return

        # Set correspongding status and text colours depending
        # on if it is a steganograph
        try:
            # Attempt to parse as an Image
            image_fileobject = Image.open(self.input_fileobject)

            # Attempt to extract the header
            header = extract_header(image_fileobject)
            self.write_output(
                "[System] File selected is a valid steganograph." +
                "Creation disabled!"
            )
            # Set text on label
            self.label_input_status.setText("Valid steganograph")
            # Set colour label
            self.label_input_status.setStyleSheet("QLabel { color : green; }")
            # Display compression and density
            self.spin_compress.setValue(header["compression"])
            self.spin_density.setValue(header["density"])
            # Enable widgets
            self.button_output.setEnabled(1)
            self.write_output("[System] Steganograph is ready for extraction")

            self.has_steg = True
        except UnidentifiedImageError or UnrecognisedHeaderError:
            # If it is a normal file
            self.write_output(
                "[System] File selected is not a steganograph. Extraction disabled!"
            )
            # Set text on label
            self.label_input_status.setText("Valid file")
            self.label_image_status.setText("Please select image")
            self.label_output_status.setText("Please select output file")
            # Set colour label
            self.label_input_status.setStyleSheet("QLabel { color : green; }")
            # Enable widgets
            self.button_image.setEnabled(1)
            self.button_output.setEnabled(1)
            self.write_output("[System] File is ready for creation")

            self.has_data = True
        self.enable_parametres()

    def select_image(self):
        # Ask user to choose a file
        self.image_filename = QtWidgets.QFileDialog.getOpenFileName()[0]

        # If the user does not select any file
        # exit the routine
        if self.image_filename is None or len(self.image_filename) == 0:
            return

        # Display text output
        self.write_output("[User] Image selected at: " + self.image_filename)

        # Show the path to file
        self.field_image.setText(self.image_filename)

        # Validate image
        try:
            steg.validate_image_file(self.image_file)
        except ImageFileValidationError as e:
            self.label_image_status.setText("Invalid image")
            self.label_image_status.setStyleSheet("QLabel { color: red; }")
            self.write_output("[System] " + str(e))
            self.disable_parametres()
        else:
            self.label_image_status.setText("Valid image")
            self.label_image_status.setStyleSheet("QLabel { color: green; }")
            self.write_output("[System] The image file is valid!")

            self.has_image = True
            self.enable_parametres()

    def select_output(self):
        # Ask user to choose a directory
        self.output_file = QtWidgets.QFileDialog.getExistingDirectory()

        # If the user does not select any file
        # exit the routine
        if self.output_file is None or len(self.output_file) == 0:
            return

        # Display text output
        self.write_output("[User] Output folder selected at: " +
                          self.output_file)

        # Create default output file
        self.output_file = path.join(
            self.output_file,
            path.splitext(path.split(self.input_file)[-1])[0])

        # Add numbering in case file already exists
        ext = "" if self.has_steg else ".png"
        if not steg.check_file_availability(self.output_file + ext):
            i = 1
            while not steg.check_file_availability(self.output_file + f"_{i}" +
                                                   ext):
                i += 1
            self.output_file += f"_{i}" + ext
        else:
            self.output_file += ext

        self.write_output("[System] Default output filename is: " +
                          self.output_file)

        # Show the path to file
        self.field_output.setText(self.output_file)

        self.label_output_status.setText("Valid file")
        self.label_output_status.setStyleSheet("QLabel { color: green; }")
        self.has_output = True
        self.enable_parametres()

    def create(self):
        self.print_system_status()
        self.write_output("[User] Start creating steganograph...")
        if len(self.field_authkey.text()) == 0:
            self.field_authkey.setText(Header.default_key)
        try:
            steg.write_steg(
                self.input_file,
                self.image_file,
                self.field_authkey.text(),
                self.spin_compress.value(),
                self.spin_density.value(),
                self.output_file,
            )
        except SteganographyError as e:
            self.write_output("[System] " + str(e))
            self.write_output("Operation will be cancelled.")
            return

        if self.check_showim.isChecked():
            im = Image.open(self.output_file)
            im.show()

        self.reset()

    def extract(self):
        self.print_system_status()
        self.write_output("[User] Start extracting steganograph...")
        if len(self.field_authkey.text()) == 0:
            self.field_authkey.setText(Header.default_key)
        try:
            steg.extract_steg(
                self.input_file,
                self.output_file,
                self.field_authkey.text(),
                False,
                False,
            )
        except SteganographyError as e:
            self.write_output("[System] " + str(e))
            self.write_output("Operation will be cancelled.")
            return

        if self.check_stdout.isChecked():
            with open(self.output_file, "r") as f:
                self.write_output(f.read())

        self.reset()

    def print_system_status(self):
        self.write_output(f"[System] Status report:")
        self.write_output(f"[System] Input file: {self.input_file}")
        self.write_output(f"[System] File is staganograph? {self.has_steg}")
        if not self.has_steg:
            self.write_output(f"[System] Image file: {self.image_file}")
        self.write_output(f"[System] Output file: {self.output_file}")
        if len(self.field_authkey.text()) == 0:
            self.write_output(
                f"[System] No authentication key given. Default key '{Header.default_key}' used instead."
            )
        else:
            self.write_output(f"[System] Authentication key is as given.")
        if self.has_steg:
            self.write_output(
                f"[System] Redirect output to stdout? {self.check_stdout.isChecked()}"
            )
        else:
            self.write_output(
                f"[System] Show image on creation? {self.check_showim.isChecked()}"
            )

    def enable_parametres(self):
        if self.has_steg and not self.has_output:
            return
        if not (self.has_steg or (self.has_image and self.has_output)):
            return

        self.write_output("[System] All files are valid!")

        if self.has_steg:
            self.field_authkey.setEnabled(1)
            self.check_stdout.setEnabled(1)
            self.button_extract.setEnabled(1)

            self.write_output(
                "[System] Please enter the authentication key used during creation."
            )
            self.write_output(
                "[System] Please check the appropriate options and click 'Extract' to start."
            )
        else:
            self.field_authkey.setEnabled(1)
            self.spin_compress.setEnabled(1)
            self.spin_density.setEnabled(1)
            self.check_showim.setEnabled(1)
            self.button_create.setEnabled(1)

            self.write_output(
                "[System] Please enter the authentication key for creation.")
            self.write_output(
                "[System] The key is required to extract data from the steganograph later."
            )
            self.write_output(
                "[System] Please choose a compression level and density for creation."
            )
            self.write_output(
                "[System] Please check the appropriate options and click 'Create' to start."
            )

    def disable_parametres(self):
        self.field_authkey.setDisabled(1)
        self.spin_compress.setDisabled(1)
        self.spin_density.setDisabled(1)
        self.check_showim.setDisabled(1)
        self.check_stdout.setDisabled(1)
        self.button_create.setDisabled(1)
        self.button_extract.setDisabled(1)

    def write_output(self, msg: str):
        self.text_output.appendPlainText(msg)
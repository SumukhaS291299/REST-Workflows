PYTHON := python
PYINSTALLER := pyinstaller
SCRIPT := main.py  # Change this to your script's name
EXECUTABLE := my_program  # Name of the final binary
DIST_DIR := dist
ROOT_DIR := .  # Root directory where the binary should be copied

all: build

build:
	@echo "Building binary..."
	$(PYINSTALLER) --onefile --name $(EXECUTABLE) $(SCRIPT)
	@echo "Copying binary to root folder..."
	mv $(DIST_DIR)/$(EXECUTABLE) $(ROOT_DIR)/

clean:
	@echo "Cleaning up..."
	rm -rf build __pycache__ $(EXECUTABLE).spec
	rm -rf $(DIST_DIR)

rebuild: clean build

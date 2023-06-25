# Photokiosk

This Python project is a NiceGUI / FastAPI app that allows users to view photos stored in the `/images` folder. It provides a user-friendly graphical interface for browsing and displaying images.

## Features

- Displays photos stored in the `/images` folder
- Supports various image formats (e.g., JPEG, PNG, GIF)
- Allows users to navigate through photos using previous and next buttons
- Displays the current image's filename

## Requirements

- Python 3.11 or higher
- NiceGUI library
- FastAPI library

## Installation

1. Clone the repository or download the source code:
   ```
   git clone https://github.com/yourusername/nicegui-fastapi-photo-viewer.git
   ```

2. Navigate to the project directory:
   ```
   cd nicegui-fastapi-photo-viewer
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Move your desired photos to the `/images` folder within the project directory.

2. Start the NiceGUI / FastAPI app:
   ```
   python main.py
   ```

3. Open your web browser and navigate to `http://localhost:8000`.

4. The app will display the first image in the `/images` folder. Use the previous and next buttons to navigate through the photos.

## Configuration

You can modify the behavior of the app by editing the `config.py` file. The available options are:

- `IMAGES_FOLDER`: Specifies the folder path where the images are stored.
- `PORT`: Specifies the port number on which the app will run.

## Contributions

Contributions to this project are welcome! If you find any issues or have suggestions for improvements, please feel free to open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

## To do:

- [ ] Add a way to delete photos
  - Should be easy, just add a button to the `/upload` page and use the `os` module to delete the file
  - Need to also allow videos to be deleted 
- [ ] Add a way to show videos
  - Shouldn't be too hard, just an `if/else` with showing `ui.image(...)` or `ui.video(...)` depending on the file extension
  - Need to also allow videos to be uploaded on the `/upload` page
- [ ] Newly uploaded photos should appear in their own section
- [ ] What do we do with portrait photos?
- [ ] Draggable cropping?
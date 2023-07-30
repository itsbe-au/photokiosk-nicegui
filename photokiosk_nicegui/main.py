import asyncio
import configparser
import os
import pickle

import sqlite3
from dotenv import load_dotenv
from nicegui import ui, app
from fastapi.staticfiles import StaticFiles
from nicegui.events import UploadEventArguments

from photokiosk_nicegui.layout import root_layout

load_dotenv(".env.local")
API_ROOT = os.getenv("API_ROOT")
API_TOKEN = os.getenv("API_TOKEN")

conn = sqlite3.connect("db.sqlite3")
cursor = conn.cursor()

app.add_static_files('/static', os.path.join(os.path.dirname(__file__), 'static'))

config_file = configparser.ConfigParser()


class Config:
    DISPLAY_TIME = 30


class Photoframe:
    def __init__(self) -> None:
        self.photos = os.listdir("images/")
        self.image = self.photos[0]
        self.filenames = cursor.execute(
            "SELECT caption,filename FROM PHOTOS"
        ).fetchall()
        self.caption = ""
        self.counter = 0

    def update_photo(self):
        self.image = self.photos[self.counter]
        self.caption = (
                cursor.execute(
                    f"SELECT caption FROM PHOTOS WHERE filename='{self.image}'"
                ).fetchone()
                or None
        )
        
        self.counter = next(iter(range(self.counter + 1, len(self.photos))), 0)
        
        if self.counter == 0:
            ui.open('/')
        else:
            self.photoframe.refresh()
    

    @ui.refreshable
    async def photoframe(self):
        ui.image(f"images/{self.image}").classes("rounded-xl m-auto").props("fit=contain")
        ui.label().bind_text(self, "caption").classes("text-4xl sm:text-6xl text-white absolute bottom-8 sm:py-4 sm:px-8 self-center max-w-screen-2xl rounded-xl text-center sm:backdrop-blur-lg mx-8")
        ui.link("Upload new photos", "/upload").props("icon=upload no-caps flat rounded").classes('self-center sm:hidden')


class CaptionCard:
    def __init__(self, image, caption=None) -> None:
        self.image = image
        self.caption = caption

    def render(self):
        with ui.card().tight().classes('w-auto sm:w-64 h-fit') as card:
            ui.image(f"images/{self.image}").classes("h-64 object-fit")
            with ui.card_section():
                ui.label(self.image).tailwind.font_weight('bold')
                ui.input(placeholder="Write a caption...").bind_value(self, 'caption').classes('w-full').props(
                    'filled dense label-stacked').on('blur', self.save_caption)

    def save_caption(self):
        # cursor.execute(f"INSERT INTO PHOTOS (filename, caption) VALUES ('{self.image.split('.')[0]}', '{self.caption}') ON CONFLICT(filename) DO UPDATE SET caption='{self.caption}'")

        sql = f"SELECT * FROM PHOTOS WHERE filename='{self.image}'"
        results = cursor.execute(sql).fetchone()
        if results:
            # Perform update
            sql = f"UPDATE PHOTOS SET caption='{self.caption}' WHERE filename='{self.image}'"
            result = cursor.execute(sql)
        else:
            # Perform insert
            sql = f"INSERT INTO PHOTOS (filename, caption) VALUES ('{self.image}', '{self.caption}')"
            result = cursor.execute(sql)

        print(sql)


class Upload:
    def __init__(self) -> None:
        self.files = os.listdir("images/")
        self.captions = cursor.execute(
            "SELECT filename, caption FROM PHOTOS"
        ).fetchall()
        self.card = {}
        self.time_changed = False

    def set_changed(self):
        self.time_changed = True

    def process_uploaded_files(self, file: UploadEventArguments):
        print(type(file))
        with open(f"images/{file.name}", "wb") as f:
            f.write(file.content.read())
        self.files.append(file.name)
        self.file_list.refresh()

    def caption(self, event):
        print(event)

    def time_change(self):
        ui.number("How many seconds to display each photo?", min=1, max=300).bind_value(Config, 'DISPLAY_TIME').props(
            'filled label-stacked').classes('sm:w-96 w-full')

    @ui.refreshable
    def file_list(self):
        with ui.element('div').classes('flex flex-wrap gap-8'):
            for file in self.files:
                captions = dict(self.captions)
                caption = captions.get(file)
                print(caption)
                CaptionCard(file, caption).render()

    def filepicker(self):
        ui.upload(
            label="Upload files",
            multiple=True,
            auto_upload=True,
            on_upload=lambda files: self.process_uploaded_files(files),
        ).props('no-thumbnails accept=".jpg, .png, image/*"').classes('sm:w-96 w-full')

    def save_all(self):
        try:
            conn.commit()
            ui.notify("Captions have been saved!", type="positive")
        except Exception as e:
            ui.notify(f"Error: {e}", type="negative")


@ui.page("/")
async def index():
    root_layout()

    page = Photoframe()

    if page.photos == []:
        ui.icon("camera").classes("text-9xl")
        return ui.markdown('''
                           # No photos found
                           ''')
    else:
        await page.photoframe()
        ui.timer(Config.DISPLAY_TIME, page.update_photo)



@ui.page("/upload")
def upload():
    time_changed = False
    root_layout(font_scheme='serif')


    page = Upload()
    with ui.element('div').classes('flex flex-col gap-8 justify-start'):
        ui.button("Back", on_click=lambda: ui.open("/")).props("icon=arrow_back no-caps flat rounded align=left")
        ui.markdown(
            """
            # Upload new photos here
            Please provide a caption for each photo.
            """
        )
        page.time_change()
        page.filepicker()
        page.file_list()
        ui.button("Save captions", on_click=page.save_all).props("icon=save no-caps rounded").classes('sticky w-fit bottom-4')


def startup():
    # Ensure db.sqlite3 exists, and create the PHOTOS table if it doesn't.
    if not os.path.exists("db.sqlite3"):
        print("Creating db.sqlite3")
        with open("db.sqlite3", "w") as f:
            pass

    cursor.execute(
        "CREATE TABLE IF NOT EXISTS PHOTOS (filename TEXT PRIMARY KEY, caption TEXT)"
    )
    conn.commit()
    read_config()


def read_config():
    # Read config.dat to get the display time.
    print("Reading config...")
    config_file.read("config.ini")

    if not config_file.has_section("display"):
        return

    Config.DISPLAY_TIME = config_file.getint("display", "DISPLAY_TIME")
    print(f"Display time set to {Config.DISPLAY_TIME} seconds")


def save_config():
    # Save the display time to config.dat
    print("Saving config...")

    config_file["display"] = {"DISPLAY_TIME": str(Config.DISPLAY_TIME)}

    with open("config.ini", "w") as f:
        config_file.write(f)


app.on_startup(startup)
app.on_shutdown(save_config)



if __name__ in ("__main__", "__mp_main__"):
    ui.run(title="Photokiosk",
           favicon="📸",
           port=7777,
           dark=True)

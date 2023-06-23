import asyncio
import os

import sqlite3
from dotenv import load_dotenv
from nicegui import ui, app
from fastapi.staticfiles import StaticFiles
from nicegui.events import UploadEventArguments

from photokiosk_nicegui.layout import root_layout

load_dotenv(".env.local")
API_ROOT = os.getenv("API_ROOT")
API_TOKEN = os.getenv("API_TOKEN")

conn = sqlite3.connect("db.sqlite3", check_same_thread=False)
cursor = conn.cursor()

app.add_static_files('/static', os.path.join(os.path.dirname(__file__), 'static'))


class Photoframe:
    def __init__(self) -> None:
        self.photos = os.listdir("images/")
        self.image = self.photos[0]
        self.filenames = cursor.execute(
            "SELECT caption,filename FROM PHOTOS"
        ).fetchall()
        self.caption = ""
        self.counter = 0

        print(self.photos)
        print(self.filenames)

    def update_photo(self):
        self.image = self.photos[self.counter]
        self.caption = (
            cursor.execute(
                f"SELECT caption FROM PHOTOS WHERE filename='{self.image}'"
            ).fetchone()
            or None
        )
        self.photoframe.refresh()
        self.counter = next(iter(range(self.counter + 1, len(self.photos))), 0)

    @ui.refreshable
    async def photoframe(self):
        ui.image(f"images/{self.image}").classes(
            "h-[calc(100vh-164px)] m-auto rounded-xl"
        )
        with ui.footer().classes("bg-dark"):
            label = (
                ui.label()
                .bind_text(self, "caption")
                .classes(
                    "transition-all duration-1000 opacity-0 text-center py-8 text-4xl w-full"
                )
            )
            await asyncio.sleep(0.1)
            label.classes(add="opacity-100", remove="opacity-0")
            
            
class CaptionCard:
    def __init__(self, image, caption = None) -> None:
        self.image = image
        self.caption = caption
        
    def render(self):
        with ui.card().tight().classes("w-64") as card:
            ui.image(f"images/{self.image}").classes("h-64 object-fit")
            with ui.card_section().classes('flex flex-col gap-4 items-center'):
                print(card.id)
                ui.label(self.image).tailwind.font_weight('bold')
                ui.input(placeholder="Write a caption...").bind_value_to(self, 'caption').classes('w-full').props('filled label-stacked').on('blur', self.save_caption)
                
    def save_caption(self):
        # cursor.execute(f"INSERT INTO PHOTOS (filename, caption) VALUES ('{self.image.split('.')[0]}', '{self.caption}') ON CONFLICT(filename) DO UPDATE SET caption='{self.caption}'")
        results = cursor.execute(f"SELECT * FROM PHOTOS WHERE filename='{self.image}'").fetchone()
        if results:
            # Perform update
            result = cursor.execute(f"UPDATE PHOTOS SET caption='{self.caption}' WHERE filename='{self.image}'")
            print(result)
        else:
            # Perform insert
            result = cursor.execute(f"INSERT INTO PHOTOS (filename, caption) VALUES ('{self.image}', '{self.caption}')")
        print(self.caption, self.image)


class Upload:
    def __init__(self) -> None:
        self.files = []
        self.card = {}

    def process_uploaded_files(self, file: UploadEventArguments):
        print(type(file))
        with open(f"images/{file.name}", "wb") as f:
            f.write(file.content.read())
        self.files.append(file.name)
        self.file_list.refresh()
        
    def caption(self, event):
        print(event)

    @ui.refreshable
    def file_list(self):
        # with ui.grid(columns=3).classes('w-screen-lg') as grid:
        with ui.row().classes("gap-8 rounded-md"):
            for file in self.files:        
                CaptionCard(file).render()
                

    def filepicker(self):
        ui.upload(
            label="Upload files",
            multiple=True,
            auto_upload=True,
            on_upload=lambda files: self.process_uploaded_files(files),
        ).props('no-thumbnails accept=".jpg, .png, image/*"')
        
    def save_all(self):
        try:
            conn.commit()
            ui.notify("Captions have been saved!", type="success")
        except Exception as e:
            ui.notify(f"Error: {e}", type="error")


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
        ui.timer(5, page.update_photo)


@ui.page("/upload")
def upload():
    root_layout(font_scheme='serif')
    ui.button("Back", on_click=lambda: ui.open("/")).props("icon=arrow_back no-caps flat rounded")
    ui.markdown(
        """
                # Upload new photos here
                Please provide a caption for each photo.
                """
    )

    page = Upload()
    page.filepicker()
    page.file_list()
    ui.button("Save captions", on_click=page.save_all).props("icon=save no-caps flat rounded")


ui.run(port=7777, dark=True)

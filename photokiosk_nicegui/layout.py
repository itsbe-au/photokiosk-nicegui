from nicegui import ui


def root_layout(font_scheme='cursive'):
    ui.add_head_html('<link rel="stylesheet" href="/static/style.css">')
    
    if font_scheme == 'serif':
        ui.query('body').classes(add='font-serif')
        
    return
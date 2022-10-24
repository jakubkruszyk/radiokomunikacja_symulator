import pyglet

window = pyglet.window.Window(1280, 720, resizable=True, caption="Test window")
label = pyglet.text.Label('Hello, world',
                          font_name='Times New Roman',
                          font_size=36,
                          x=window.width//2, y=window.height//2,
                          anchor_x='center', anchor_y='center')


@window.event
def on_draw():
    window.clear()
    label.draw()


@window.event
def on_resize(width, height):
    print('The window was resized to %dx%d' % (width, height))


pyglet.app.run()

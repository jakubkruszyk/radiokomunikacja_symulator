import pyglet
from pyglet import shapes


window = pyglet.window.Window(1280, 720, resizable=True, caption="Test window")

batch = pyglet.graphics.Batch()

# drawing sigle points
vertex_list = pyglet.graphics.vertex_list(2,
    ('v2i', (10, 15, 30, 35)),
    ('c3B', (0, 0, 255, 0, 255, 0))
)

# drawing rectangle
rect = shapes.Rectangle(x=100, y=100, width=100, height=50, color=(55, 55, 255), batch=batch)

# drawing line
line = shapes.Line(200, 100, 200, 500, width=4, color=(255, 255, 0), batch=batch)


@window.event
def on_draw():
    window.clear()
    vertex_list.draw(pyglet.gl.GL_POINTS)
    batch.draw()


pyglet.app.run()

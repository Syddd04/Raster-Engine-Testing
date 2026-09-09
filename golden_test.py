from rasterizer import Rasterizer
from graphics_lib import Vertex

rasterTest = Rasterizer()

a = Vertex(1, 2)
b = Vertex(2, 3)
c = Vertex(3, 2)

edge = rasterTest.edge(a, b, c.x, c.y)
dx = rasterTest.de_dx(a, b)
dy = rasterTest.de_dy(a, b)

area = edge / 2.0

print(f"Edge: {edge}\ndx: {dx}\ndy: {dy}\narea: {area}")

a = Vertex(1, 2)
b = Vertex(3, 2)
c = Vertex(2, 3)

edge = rasterTest.edge(a, b, c.x, c.y)
dx = rasterTest.de_dx(a, b)
dy = rasterTest.de_dy(a, b)

area = edge / 2.0

print(f"\nEdge: {edge}\ndx: {dx}\ndy: {dy}\narea: {area}")

a = Vertex(0, 0)
b = Vertex(500, 500)
c = Vertex(1000, 1000)

edge = rasterTest.edge(a, b, c.x, c.y)
dx = rasterTest.de_dx(a, b)
dy = rasterTest.de_dy(a, b)

area = edge / 2.0

print(f"\nEdge: {edge}\ndx: {dx}\ndy: {dy}\narea: {area}")

a = Vertex(-400, 1) #left point off
b = Vertex(10, 500)
c = Vertex(600, 250)

edge = rasterTest.edge(a, b, c.x, c.y)
dx = rasterTest.de_dx(a, b)
dy = rasterTest.de_dy(a, b)

area = edge / 2.0

print(f"\nEdge: {edge}\ndx: {dx}\ndy: {dy}\narea: {area}")

a = Vertex(0, 0)
b = Vertex(500, 500)
c = Vertex(1500, 300) #rightmost point off

edge = rasterTest.edge(a, b, c.x, c.y)
dx = rasterTest.de_dx(a, b)
dy = rasterTest.de_dy(a, b)

area = edge / 2.0

print(f"\nEdge: {edge}\ndx: {dx}\ndy: {dy}\narea: {area}")

a = Vertex(0, 0)
b = Vertex(500, 1100) #top point off
c = Vertex(1000, 1000) 

edge = rasterTest.edge(a, b, c.x, c.y)
dx = rasterTest.de_dx(a, b)
dy = rasterTest.de_dy(a, b)

area = edge / 2.0

print(f"\nEdge: {edge}\ndx: {dx}\ndy: {dy}\narea: {area}")

'''
a = Vertex(0, 0)
b = Vertex(500, 0)
c = Vertex(500, 1)

edge = rasterTest.edge(a, b, c.x, c.y)
dx = rasterTest.de_dx(a, b)
dy = rasterTest.de_dy(a, b)

area = edge / 2.0

print(f"\nEdge: {edge}\ndx: {dx}\ndy: {dy}\narea: {area}")

a = Vertex(0, 0)
b = Vertex(1024, 0)
c = Vertex(0, 768)

edge = rasterTest.edge(a, b, c.x, c.y)
dx = rasterTest.de_dx(a, b)
dy = rasterTest.de_dy(a, b)

area = edge / 2.0

print(f"\nEdge: {edge}\ndx: {dx}\ndy: {dy}\narea: {area}")

a = Vertex(0, 0)
b = Vertex(0, 768)
c = Vertex(1024, 0)


edge = rasterTest.edge(a, b, c.x, c.y)
dx = rasterTest.de_dx(a, b)
dy = rasterTest.de_dy(a, b)

area = edge / 2.0

print(f"\nEdge: {edge}\ndx: {dx}\ndy: {dy}\narea: {area}")
'''
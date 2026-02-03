import numpy as np
from graphics_lib import Vec3, Triangle, Projector
import matplotlib.pyplot as plt

def getNDC(project, vertex : Vec3):
    near_point = project.toNearPlane(vertex)
    ndc : Vec3 = project.toNDC(near_point)
    ndc.z = project.depth(ndc)
    return ndc

def project(project, vert):
    #Convert to NDC
    ndc = getNDC(project, vert)

    #Convert to screen space
    return project.toScreenSpace(ndc)

def edge(a, b, x, y):
    return (b.x - a.x) * (y - a.y) - (b.y - a.y) * (x - a.x)

#Set up machines

w = 1280
h = 720
projector = Projector(w, h, 1, 10) #width, height, near plane, far plane
screen = np.zeros((h,w))

#Get primitives

vertex1 = Vec3(-0.8, -0.6, -9)
vertex2 = Vec3( 0.8, -0.6, -9)
vertex3 = Vec3( 0.0,  0.6, -9)

triangle = Triangle(vertex1, vertex2, vertex3)

#Convert to screen space

ss_v1 = project(projector, triangle.A)
ss_v2 = project(projector, triangle.B)
ss_v3 = project(projector, triangle.C) 

ss_tri = Triangle(ss_v1, ss_v2, ss_v3)

ss_min = ss_tri.min().floor()
ss_max = ss_tri.max().ceil()

#Perform edge tests

print(ss_v1)
print(ss_v2)
print(ss_v3)
print(ss_min, ss_max)

area = edge(ss_tri.A, ss_tri.B, ss_tri.C.x, ss_tri.C.y)
if area < 0:
    ss_tri.B, ss_tri.C = ss_tri.C, ss_tri.B

for i in range(ss_min.y, ss_max.y):
    for j in range(ss_min.x, ss_max.x):
        x = j + 0.5
        y = i + 0.5

        edge1 = edge(ss_tri.A, ss_tri.B, x, y)
        edge2 = edge(ss_tri.B, ss_tri.C, x, y)
        edge3 = edge(ss_tri.C, ss_tri.A, x, y)
        
        if (edge1 >= 0 and edge2 >= 0 and edge3 >= 0):
            screen[i][j] = 1

plt.imshow(screen, cmap='gray', interpolation='nearest')
plt.axis('off')
plt.show()
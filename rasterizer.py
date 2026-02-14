import numpy as np
from graphics_lib import Triangle, Projector, Vertex
import matplotlib.pyplot as plt
from PIL import Image

#Set up machines
class Rasterizer():

    def getNDC(self, vertex : Vertex):
        near_point = self.projector.toNearPlane(vertex)
        ndc : Vertex = self.projector.toNDC(near_point)
        ndc.z = self.projector.depth(ndc)
        return ndc

    def project(self, vert):
        #Convert to NDC
        ndc = self.getNDC(vert)

        #Convert to screen space
        return self.projector.toScreenSpace(ndc)

    def edge(self, a, b, x, y):
        return (b.x - a.x) * (y - a.y) - (b.y - a.y) * (x - a.x)

    def validEdge (self, v0, v1):
        edge_vec = [v1.x - v0.x, v1.y - v0.y]
        top = edge_vec[1] == 0 and edge_vec[0] < 0  
        left = edge_vec[1] < 0                      
        return top or left

    def __init__(self, vx1, vy1, vz1, vx2, vy2, vz2, vx3, vy3, vz3, col1 = [[]], col2 = [[]], col3 = [[]], u1 = [], u2 = [], u3 = [], v1 = [], v2 = [], v3 = [], msaa = 0, w = 640, h = 480, near = 1, far = 10):
        #numpy arrays, all of them. Cols will be nx3x3 array
        self.vx1 = vx1
        self.vy1 = vy1
        self.vz1 = vz1
        
        self.vx2 = vx2
        self.vy2 = vy2
        self.vz2 = vz2

        self.vx3 = vx3
        self.vy3 = vy3
        self.vz3 = vz3

        self.col1 = col1
        self.col2 = col2
        self.col3 = col3

        self.u1 = u1
        self.u2 = u2
        self.u3 = u3
        
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3

        self.msaa = msaa
        self.w = w
        self.h = h

        self.projector = Projector(self.w, self.h, near, far) #width, height, near plane, far plane
        self.screen = np.zeros((h,w,3))
        self.z_buffer = np.full((h, w, 2), np.inf)

    def render(self):
        for i in range(0,len(self.vx1)):

            #Get primitives

            vertex1 = Vertex(self.vx1[i], self.vy1[i], self.vz1[i], self.col1[i])
            vertex2 = Vertex(self.vx2[i], self.vy2[i], self.vz2[i], self.col2[i])
            vertex3 = Vertex(self.vx3[i], self.vy3[i], self.vz3[i], self.col3[i])

            triangle = Triangle(vertex1, vertex2, vertex3)

            #Convert to screen space

            ss_v1 = self.project(triangle.A)
            ss_v2 = self.project(triangle.B)
            ss_v3 = self.project(triangle.C) 

            ss_tri = Triangle(ss_v1, ss_v2, ss_v3)

            ss_min = ss_tri.min().floor()
            ss_max = ss_tri.max().ceil()

            #Check winding.
            area = self.edge(ss_tri.A, ss_tri.B, ss_tri.C.x, ss_tri.C.y) / 2 #Edge equation is cross product, so divide by 2 to get area of triangle instead of parallelogram.
            if area < 0:
                ss_tri.B, ss_tri.C = ss_tri.C, ss_tri.B
                area = -area

            #Do edge testing
            for y in range(ss_min.y, ss_max.y):
                for j in range(ss_min.x, ss_max.x):
                    if area == 0:
                        continue
                    bx = j + 0.5
                    by = y + 0.5

                    check1 = 0 if self.validEdge(ss_tri.A, ss_tri.B) else -1e-12 #adjust for subtle fp errors
                    check2 = 0 if self.validEdge(ss_tri.B, ss_tri.C) else -1e-12
                    check3 = 0 if self.validEdge(ss_tri.C, ss_tri.A) else -1e-12

                    if (self.msaa == 2):
                        x0 = j + 0.25
                        y0 = y + 0.25

                        x1 = j + 0.75
                        y1 = y + 0.75

                        e0_1 = self.edge(ss_tri.A, ss_tri.B, x0, y0) / (2 * area)
                        e0_2 = self.edge(ss_tri.B, ss_tri.C, x0, y0) / (2 * area)
                        e0_3 = self.edge(ss_tri.C, ss_tri.A, x0, y0) / (2 * area)

                        e1_1 = self.edge(ss_tri.A, ss_tri.B, x1, y1) / (2 * area)
                        e1_2 = self.edge(ss_tri.B, ss_tri.C, x1, y1) / (2 * area)
                        e1_3 = self.edge(ss_tri.C, ss_tri.A, x1, y1) / (2 * area)

                        cov0 = 0
                        cov1 = 0

                        if ((e0_1 + check1 >= 0) and (e0_2 >= 0 + check2) and (e0_3 >= 0 + check3)):
                            cov0 = 1

                        if ((e1_1 >= 0 + check1) and (e1_2 >= 0 + check2) and (e1_3 >= 0 + check3)):
                            cov1 = 1

                        z0 = (ss_tri.A.z * e0_1 + ss_tri.B.z * e0_2 + ss_tri.C.z * e0_3)
                        z1 = (ss_tri.A.z * e1_1 + ss_tri.B.z * e1_2 + ss_tri.C.z * e1_3)

                        if ((cov0 or cov1) and (z0 <= self.z_buffer[y][j][0] or z1 <= self.z_buffer[y][j][1])):
                            r = 0
                            g = 0
                            b = 0

                            if (z0 <= self.z_buffer[y][j][0] and cov0):
                                self.z_buffer[y][j][0] = z0
                                r += ((ss_tri.A.R * e0_1 + ss_tri.B.R * e0_2 + ss_tri.C.R * e0_3))
                                g += ((ss_tri.A.G * e0_1 + ss_tri.B.G * e0_2 + ss_tri.C.G * e0_3))
                                b += ((ss_tri.A.B * e0_1 + ss_tri.B.B * e0_2 + ss_tri.C.B * e0_3))
                            elif(cov0):
                                r += self.screen[y][j][0]
                                g += self.screen[y][j][1]
                                b += self.screen[y][j][2]

                            if (z1 <= self.z_buffer[y][j][1] and cov1):
                                self.z_buffer[y][j][1] = z1
                                r += ((ss_tri.A.R * e1_1 + ss_tri.B.R * e1_2 + ss_tri.C.R * e1_3))
                                g += ((ss_tri.A.G * e1_1 + ss_tri.B.G * e1_2 + ss_tri.C.G * e1_3))
                                b += ((ss_tri.A.B * e1_1 + ss_tri.B.B * e1_2 + ss_tri.C.B * e1_3))
                            elif (cov1):
                                r += self.screen[y][j][0]
                                g += self.screen[y][j][1]
                                b += self.screen[y][j][2]

                            self.screen[y][j][0] = r / 2
                            self.screen[y][j][1] = g / 2
                            self.screen[y][j][2] = b / 2

                    else:
                        edge1 = self.edge(ss_tri.A, ss_tri.B, bx, by) / (2 * area) #Similar logic. Divide by 2 to get triangle area and then divide by area to normalize the result. The cross product above gives unnormalized barycentric coordinates. 
                        edge2 = self.edge(ss_tri.B, ss_tri.C, bx, by) / (2 * area)
                        edge3 = self.edge(ss_tri.C, ss_tri.A, bx, by) / (2 * area)

                        z = ss_tri.A.z * edge1 + ss_tri.B.z * edge2 + ss_tri.C.z * edge3

                        if ((edge1 + check1 >= 0) and (edge2 + check2 >= 0) and (edge3 + check3 >= 0) and z <= self.z_buffer[y][j][0]):
                            self.screen[y][j][0] = ss_tri.A.R * edge1 + ss_tri.B.R * edge2 + ss_tri.C.R * edge3
                            self.screen[y][j][1] = ss_tri.A.G * edge1 + ss_tri.B.G * edge2 + ss_tri.C.G * edge3
                            self.screen[y][j][2] = ss_tri.A.B * edge1 + ss_tri.B.B * edge2 + ss_tri.C.B * edge3

                            self.z_buffer[y][j][0] = z
                        else:
                            continue

    def showScreen(self):
        plt.imshow(self.screen)
        plt.axis('off')
        plt.show()

    def saveScreen(self):
        #Save image
        img_unit8 = (self.screen * 255).astype(np.uint8)
        img = Image.fromarray(img_unit8)
        img.save('lossless.png', mode='RGB')
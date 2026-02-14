from rasterizer import Rasterizer

vx1 = [-0.8, -1.4, 0.8]
vy1 = [-0.6, -0.4, -0.6]
vz1  = [-2,   -2,   -2]

vx2 = [0.8, -0.8, 1.4]
vy2 = [-0.6, -0.6, 0.4]
vz2  = [-2,   -2,   -2]

vx3 = [0.0, 0.0, -0.4]
vy3 = [0.6, 0.6, 1]
vz3  = [-2,  -2,  -3]

col1 = [[1,0,0], [0,0,1], [1,1,1]]
col2 = [[0,1,0], [0,1,0], [1,1,1]]
col3 = [[0,0,1], [1,0,0], [1,1,1]]

rasterEngine = Rasterizer(vx1, vy1, vz1, vx2, vy2, vz2, vx3, vy3, vz3, col1, col2, col3, msaa = 2, w = 1280, h = 720)
rasterEngine.render()
rasterEngine.showScreen()
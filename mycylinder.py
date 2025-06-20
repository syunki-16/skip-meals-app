# BN24250 上原駿希
import math
from Cylinder import Cylinder
a = Cylinder (1.0, 2.0)
a.print_info()
print('a.calvolume = ', a.calcvolume())
print('a.calcarea = ', a.calcarea())

b = Cylinder(1.0, 4.0, 2.0, 2.0, 4.0)
b.print_info()
print('b.calcvolume = ', b.calcvolume())
print('b.calcarea = ', b.calcarea())

dist = math.sqrt((a.cx - b.cx)**2 + (a.cy - b.cy)**2 + (a.cz - b.cz)**2)
print('distance a-b = ',dist)

# Circle a: 円柱体積　3.141592653589793, 円柱表面積　12.566370614359172
# Circle b: 円柱体積　50.26548245743669, 円柱表面積　75.39822368615503
# a, bの２中心間の距離(dist) 2.8284271247461903
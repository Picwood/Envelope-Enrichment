# ------------------------------------------------------------------------------
#
#  Gmsh Python tutorial 6
#
#  Transfinite meshes, deleting entities
#
# ------------------------------------------------------------------------------

import gmsh
import math
import sys

gmsh.initialize()

gmsh.model.add("t6")

# Copied from `t1.py'...
lc = 1e-2

# When the surface has only 3 or 4 points on its boundary the list of corners
# can be omitted in the `setTransfiniteSurface()' call:
gmsh.model.occ.addPoint(0.0, 1.0, 0, 1.0, 7)
gmsh.model.occ.addPoint(0.0, 0.0, 0, 1.0, 8)
gmsh.model.occ.addPoint(1.0, 1.0, 0, 1.0, 10)
gmsh.model.occ.addPoint(1.0, 0.0, 0, 1.0, 11)
gmsh.model.occ.addLine(8, 11, 10)
gmsh.model.occ.addLine(11, 10, 11)
gmsh.model.occ.addLine(10, 7, 12)
gmsh.model.occ.addLine(7, 8, 13)
gmsh.model.occ.addCurveLoop([13, 10, 11, 12], 14)
gmsh.model.occ.addPlaneSurface([14], 15)
#gmsh.model.occ.addSurfaceFilling([14],16)
gmsh.model.occ.synchronize()

#gmsh.model.occ.mesh.setTransfiniteSurface(15)

gmsh.model.occ.addPoint(0.2, 0.8, 0, 1.0, 4)
gmsh.model.occ.addPoint(0.2, 0.2, 0, 1.0, 1)
gmsh.model.occ.addPoint(0.8, 0.8, 0, 1.0, 3)
gmsh.model.occ.addPoint(0.8, 0.2, 0, 1.0, 2)
gmsh.model.occ.addLine(1, 2, 1)
gmsh.model.occ.addLine(2, 3, 2)
gmsh.model.occ.addLine(3, 4, 3)
gmsh.model.occ.addLine(4, 1, 4)
gmsh.model.occ.addCurveLoop([4, 1, 2, 3], 17)
gmsh.model.occ.addPlaneSurface([17], 18)
#gmsh.model.occ.addSurfaceFilling([17],19)

gmsh.model.occ.addPoint(0.3, 0.3, 0, 1.0, 20)
gmsh.model.occ.addPoint(0.7, 0.7, 0, 1.0, 21)
gmsh.model.occ.addPoint(0.3, 0.7, 0, 1.0, 22)
gmsh.model.occ.addPoint(0.7, 0.3, 0, 1.0, 23)
gmsh.model.occ.addPoint(0.3, 0.6, 0, 1.0, 24)
gmsh.model.occ.addPoint(0.6, 0.5, 0, 1.0, 25)
gmsh.model.occ.addLine(20, 21, 21)
gmsh.model.occ.addLine(22, 23, 22)
gmsh.model.occ.addLine(24, 25, 23)


print(gmsh.model.getEntities(2))

ov, ovv = gmsh.model.occ.fragment([(2, 15)], [(2, 18)])
gmsh.model.occ.synchronize()
print(ov)
ov, ovv = gmsh.model.occ.fragment([(2, 18)], [(1, 21)])
gmsh.model.occ.synchronize()
ov, ovv = gmsh.model.occ.fragment([(2, 18)], [(1, 22)])
gmsh.model.occ.synchronize()
ov, ovv = gmsh.model.occ.fragment([(2, 18)], [(1, 23)])
gmsh.model.occ.synchronize()
ite = 0
NN = 10
for c in gmsh.model.getEntities(1):
    if ite > 3:
        NN=20
    gmsh.model.mesh.setTransfiniteCurve(c[1], NN)
    ite = ite+1

#for i in range(10, 14):
#    gmsh.model.mesh.setTransfiniteCurve(i, 10)

# The way triangles are generated can be controlled by specifying "Left",
# "Right" or "Alternate" in `setTransfiniteSurface()' command. Try e.g.
#
#gmsh.model.mesh.setTransfiniteSurface(15, "Right")

gmsh.model.occ.synchronize()

# Finally we apply an elliptic smoother to the grid to have a more regular
# mesh:
gmsh.option.setNumber("Mesh.Smoothing", 100)

gmsh.model.mesh.generate(2)
gmsh.write("t6.msh")

# Launch the GUI to see the results:
if '-nopopup' not in sys.argv:
    gmsh.fltk.run()

gmsh.finalize()

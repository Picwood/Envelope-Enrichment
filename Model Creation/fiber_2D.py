import gmsh
import numpy as np
import json
import os
import matplotlib.pyplot as plt
import sys

def truncate_fiber(x1, y1, x2, y2, width, height):
    """Adjusts fiber endpoints to ensure they don't extend outside the RVE."""
    # Truncate at horizontal boundaries
    if x1 < 0:
        y1 = y1 + (0 - x1) * (y2 - y1) / (x2 - x1)
        x1 = 1
    elif x1 > width:
        y1 = y1 + (width - x1) * (y2 - y1) / (x2 - x1)
        x1 = width-1

    if x2 < 0:
        y2 = y2 + (0 - x2) * (y1 - y2) / (x1 - x2)
        x2 = 1
    elif x2 > width:
        y2 = y2 + (width - x2) * (y1 - y2) / (x1 - x2)
        x2 = width-1

    # Truncate at vertical boundaries
    if y1 < 0:
        x1 = x1 + (0 - y1) * (x2 - x1) / (y2 - y1)
        y1 = 1
    elif y1 > height:
        x1 = x1 + (height - y1) * (x2 - x1) / (y2 - y1)
        y1 = height-1

    if y2 < 0:
        x2 = x2 + (0 - y2) * (x1 - x2) / (y1 - y2)
        y2 = 1
    elif y2 > height:
        x2 = x2 + (height - y2) * (x1 - x2) / (y1 - y2)
        y2 = height-1

    return x1, y1, x2, y2

def create_2d_rve_with_fibers(ep, density, num_fibers, fiber_length, ref_angle, angle_spread, pos_spread, dist_type='uniform'):
    gmsh.initialize()
    gmsh.model.add("2D_RVE_with_Fibers")

    width = 100  # Example width of 100 units
    height = 100  # Example height of 100 units


    outer_box = gmsh.model.occ.addRectangle(-ep, -ep, 0, width + 2*ep, height + 2*ep)
    inner_box = gmsh.model.occ.addRectangle(0, 0, 0, width, height)
    gmsh.model.occ.synchronize()
    print(gmsh.model.getEntities(2))
    #outer_surf = gmsh.model.occ.addPlaneSurface([outer_box])
    #inner_surf = gmsh.model.occ.addPlaneSurface([inner_box])



    gmsh.option.setNumber("Geometry.OCCBoundsUseStl", 1)

    transfinite = True
    transfiniteAuto = True
    gmsh.model.mesh.setTransfiniteAutomatic()
    #if transfinite:
    ov, ovv = gmsh.model.occ.fragment([(2, outer_box)], [(2, inner_box)])

    gmsh.model.occ.synchronize()

    fibers = []
    fig, ax = plt.subplots()  # Set up the plot
    ax.set_aspect('equal', adjustable='box')
    ax.set_title('Fiber Distribution in 2D RVE')
    ax.set_xlabel('X Position')
    ax.set_ylabel('Y Position')
    gmsh.model.occ.synchronize()
    print(gmsh.model.getEntities(2))
    for _ in range(num_fibers):
        # Determine fiber orientation based on reference angle and spread
        if dist_type == 'uniform':
            angle = ref_angle + np.random.uniform(-angle_spread, angle_spread)
            center_x = width / 2 + np.random.uniform(-pos_spread, pos_spread)
            center_y = height / 2 + np.random.uniform(-pos_spread, pos_spread)
        elif dist_type == 'normal':
            angle = ref_angle + np.random.normal(0, angle_spread)
            center_x = width / 2 + np.random.normal(0, pos_spread)
            center_y = height / 2 + np.random.normal(0, pos_spread)

        # Calculate end points of the fiber line
        x1 = center_x + (fiber_length/2) * np.cos(angle)
        y1 = center_y + (fiber_length/2) * np.sin(angle)
        x2 = center_x - (fiber_length/2) * np.cos(angle)
        y2 = center_y - (fiber_length/2) * np.sin(angle)

        x1_adj, y1_adj, x2_adj, y2_adj = truncate_fiber(x1, y1, x2, y2, width, height)
        p1 = gmsh.model.occ.addPoint(x1_adj, y1_adj, 0)
        p2 = gmsh.model.occ.addPoint(x2_adj, y2_adj, 0)
        fiber_line = gmsh.model.occ.addLine(p1,p2)
        #gmsh.model.mesh.setSize([(1,fiber_line)], 0.05)
        #gmsh.model.mesh.embed(1, [fiber_line], 2, 2)
        gmsh.model.occ.synchronize()
        fibers.append({"id": fiber_line, "position": [center_x, center_y], "angle": angle, "length": fiber_length})
        ax.plot([x1_adj, x2_adj], [y1_adj, y2_adj], marker='o')

        if len(fibers) > 1:
            lines = gmsh.model.getEntities(1)
            sousseg = 1
            tool = [(1,fiber_line)]
            for i in range(len(lines)-9):
                try:
                    for j in range(sousseg):
                        ov2, ovv = gmsh.model.occ.fuse([lines[i+8]], [tool[-1-j]])
                        gmsh.model.occ.synchronize()

                except:
                    print("pas possible")
                else:
                    if len(ov2)>2:
                        sousseg = sousseg+1
                        tool = [ov2[-1],ov2[-2]]
                        print(tool)

    lines = gmsh.model.getEntities(1)
    for i in range(len(lines)-8):
        actual_surf = gmsh.model.getEntities(2)
        try:
            for ns in range(actual_surf):
                if ns != (2,3):
                    ov2, ovv = gmsh.model.occ.fragment([ns],[lines[i+8]])
                    gmsh.model.occ.synchronize()
        except:
            print("pas possible")

    gmsh.model.occ.synchronize()

    #NN = int(10/density)
    #ite = 0
    #for c in range(8):
        #if c > 3:
        #    NN=int(20/density)
        #points = gmsh.model.getBoundary([c])
        #gmsh.model.mesh.setTransfiniteCurve(c+1, NN)
    #for s in gmsh.model.getEntities(2):
    #    gmsh.model.mesh.setTransfiniteSurface(s[1])


    gmsh.option.setNumber('Mesh.SaveGroupsOfElements', -111)

    plt.show()
    plt.savefig('fiber_distribution.png')

    gmsh.option.setNumber("Mesh.Smoothing", 100)

    gmsh.model.mesh.generate(2)

    # Save fibers data to a JSON file for MATLAB analysis
    with open('fibers_data.json', 'w') as f:
        json.dump(fibers, f, indent=4)

    filepath_unv = os.path.join('C://Temp//%s-VER.unv')

    gmsh.write(filepath_unv)

    if '-nopopup' not in sys.argv:
        gmsh.fltk.run()

    gmsh.finalize()
plt.ion()
envelope_thickness = 20
mesh_density = 0.5
num_fibers = 20
fiber_length = 50
reference_angle = np.pi /4  # Example: 45 degrees as the reference angle
angle_spread = np.pi/6  # Example: ±10 degrees spread
position_spread = 50  # Example: Spread of 10 units from the center
distribution_type = 'uniform'  # Options: 'uniform' or 'normal'
create_2d_rve_with_fibers(envelope_thickness, mesh_density, num_fibers, fiber_length, reference_angle, angle_spread, position_spread, distribution_type)

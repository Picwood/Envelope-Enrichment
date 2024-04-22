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

    ov, ovv = gmsh.model.occ.fragment([(2, outer_box)], [(2, inner_box)])

    gmsh.option.setNumber("Geometry.OCCBoundsUseStl", 1)
    
    gmsh.model.addPhysicalGroup(2, [0], 1)
    gmsh.model.addPhysicalGroup(2, [1], 2)

    fibers = []

    fig, ax = plt.subplots()  # Set up the plot
    ax.set_aspect('equal', adjustable='box')
    ax.set_title('Fiber Distribution in 2D RVE')
    ax.set_xlabel('X Position')
    ax.set_ylabel('Y Position')
    
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
        gmsh.model.mesh.setSize([(1,fiber_line)], 0.05)
        gmsh.model.occ.synchronize()
        gmsh.model.mesh.embed(1, [fiber_line], 2, inner_box)
        fibers.append({"id": fiber_line, "position": [center_x, center_y], "angle": angle, "length": fiber_length})
        ax.plot([x1_adj, x2_adj], [y1_adj, y2_adj], marker='o')

    gmsh.model.occ.synchronize()
    if '-nopopup' not in sys.argv:
        gmsh.fltk.run()

    translation = [1, 0, 0, height+2*ep,    0, 1, 0, 0,     0, 0, 1, 0,    0, 0, 0, height+2*ep]
    gmsh.model.mesh.setPeriodic(1, [2], [1], translation)
    gmsh.model.mesh.setPeriodic(1, [4], [3],
                                [1, 0, 0, 0,   0, 1, 0, width+2*ep,   0, 0, 1, 0,   0, 0, 0, width+2*ep])
        
    transfinite = True
    transfiniteAuto = True
    
    if transfinite:
        NN = int(10/density)
        inte = 0
        for c in gmsh.model.getEntities(1):
            if inte >= 12:
                gmsh.model.mesh.setTransfiniteCurve(c[1], NN)
            inte = inte+1

    gmsh.model.occ.synchronize()
    gmsh.option.setNumber('Mesh.SaveGroupsOfElements', -111)

    plt.show()
    plt.savefig('fiber_distribution.png')
        
    gmsh.model.mesh.generate(2)

    # Save fibers data to a JSON file for MATLAB analysis
    with open('fibers_data.json', 'w') as f:
        json.dump(fibers, f, indent=4)

    filepath_unv = os.path.join('C://Temp//%s-VER.unv')
    
    gmsh.write(filepath_unv)

    gmsh.finalize()
plt.ion()
envelope_thickness = 5
mesh_density = 1
num_fibers = 100
fiber_length = 50
reference_angle = np.pi /4  # Example: 45 degrees as the reference angle
angle_spread = np.pi/6  # Example: ±10 degrees spread
position_spread = 50  # Example: Spread of 10 units from the center
distribution_type = 'uniform'  # Options: 'uniform' or 'normal'
create_2d_rve_with_fibers(envelope_thickness, mesh_density, num_fibers, fiber_length, reference_angle, angle_spread, position_spread, distribution_type)

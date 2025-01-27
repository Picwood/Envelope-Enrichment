import json
import gmsh
import sys
import os
import numpy as np

def load_rve_config(json_path):
    """Load particle configuration from JSON file."""
    with open(json_path, 'r') as f:
        data = json.load(f)
        # Convert the particle data from arrays to list of dictionaries
        particles = []
        for i in range(len(data['particles']['x'])):
            particles.append({
                'x': data['particles']['x'][i],
                'y': data['particles']['y'][i],
                'radius': data['particles']['radius'][i]
            })
        return particles, data['box_size']

def create_rve_mesh(particles, box_size, output_file):
    """Create RVE mesh with particles using gmsh."""
    gmsh.initialize()
    gmsh.model.add("RVE with Particles")

    # Set mesh parameters
    gmsh.option.setNumber("Mesh.Algorithm", 6)  # Frontal-Delaunay
    gmsh.option.setNumber("Mesh.CharacteristicLengthMin", box_size/25)
    gmsh.option.setNumber("Mesh.CharacteristicLengthMax", box_size/25)
    
    # Define padding for outer box (20% of box_size)
    padding = 0.2 * box_size
    
    # Create inner and outer boxes
    inner_box = gmsh.model.occ.addRectangle(0, 0, 0, box_size, box_size)
    outer_box = gmsh.model.occ.addRectangle(-padding, -padding, 0, box_size + 2*padding, box_size + 2*padding)
    
    # Fragment outer and inner boxes
    gmsh.model.occ.fragment([(2, outer_box)], [(2, inner_box)])
    gmsh.model.occ.synchronize()
    
    # Get the inner box for further fragmentation
    ov = [(2, inner_box)]
    ovtot = []
    
    # Add circles for each particle
    circle_loops = []
    for particle in particles:
        # Create circle curve
        circle = gmsh.model.occ.addCircle(
            particle['x'], 
            particle['y'], 
            0,  # z coordinate
            particle['radius']
        )
        
        # Create curve loop from circle
        loop = gmsh.model.occ.addCurveLoop([circle])
        
        # Create surface from the loop
        surface = gmsh.model.occ.addPlaneSurface([loop])
        circle_loops.append((2, surface))
    
    # Fragment with circles
    for circle in circle_loops:
        gmsh.model.occ.synchronize()
        if len(ov) == 3:
            ov, _ = gmsh.model.occ.fragment([ov[0]], [circle], removeObject=True, removeTool=True)
        elif len(ov) == 2:
            ov, _ = gmsh.model.occ.fragment([ov[-1]], [circle], removeObject=True, removeTool=True)
        elif len(ov) == 4:
            ov, _ = gmsh.model.occ.fragment([ov[1]], [circle], removeObject=True, removeTool=True)

        if len(ov) == 3:
            ovtot.append(ov[-1])
        elif len(ov) == 4:
            ovtot.append(ov[-2])
            ovtot.append(ov[-1])
    print(ovtot)

    gmsh.model.removeEntities(ovtot, True)  # Delete outside parts recursively

    
    gmsh.model.occ.synchronize()
    
    # Generate mesh
    gmsh.model.mesh.generate(2)
    
    # Save mesh
    gmsh.write(output_file)
    
    # Cleanup
    gmsh.finalize()

def process_rve_configs():
    # Base directories
    input_base_dir = r"D:/1-Recherche/Fiber META/STATISTICAL MODEL/RVE_definition"
    output_base_dir = r"D:/1-Recherche/Fiber META/STATISTICAL MODEL/RVE_model"
    
    # Process each config folder
    for i in range(1, 100):
        input_folder = f"config({i})"
        input_path = os.path.join(input_base_dir, input_folder)
        
        if not os.path.exists(input_path):
            print(f"Skipping {input_folder} - does not exist")
            continue
            
        print(f"Processing {input_folder}...")
        
        # Create output folder
        output_folder = os.path.join(output_base_dir, input_folder)
        os.makedirs(output_folder, exist_ok=True)
        
        # Process each JSON file in the folder
        for filename in os.listdir(input_path):
            if filename.endswith('.json'):
                json_path = os.path.join(input_path, filename)
                output_file = os.path.join(output_folder, filename.replace('.json', '.unv'))
                
                print(f"Processing {filename}...")
                try:
                    # Load particle configuration
                    particles, box_size = load_rve_config(json_path)
                    
                    # Create mesh
                    create_rve_mesh(particles, box_size, output_file)
                    
                    print(f"Successfully created mesh for {filename}")
                except Exception as e:
                    print(f"Error processing {filename}: {str(e)}")
                    print(f"Full error: {str(sys.exc_info())}")

if __name__ == "__main__":
    process_rve_configs()
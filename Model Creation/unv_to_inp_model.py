import os
import re
import numpy as np

class UnvData:
    def __init__(self):
        self.nodes = {}
        self.elements = []
        self.element_groups = {}
        self.minpos = [float('inf')] * 3
        self.maxpos = [float('-inf')] * 3
    
    def add_node(self, node_id, coordinates):
        """Add node and track min/max positions"""
        self.nodes[node_id] = coordinates
        coord = list(coordinates)
        for i in range(3):
            if self.minpos[i] > coord[i]:
                self.minpos[i] = coord[i]
            if self.maxpos[i] < coord[i]:
                self.maxpos[i] = coord[i]
    
    def add_element(self, elem_id, elem_type, nodes):
        """Add element definition"""
        self.elements.append({
            'id': elem_id,
            'type': elem_type,
            'nodes': nodes
        })
    
    def add_to_group(self, group_name, elem_id):
        """Add element to a named group"""
        if group_name not in self.element_groups:
            self.element_groups[group_name] = []
        self.element_groups[group_name].append(elem_id)

def parse_unv_file(unv_path):
    """Parse UNV file and extract nodes, elements, and groups"""
    unv_data = UnvData()
    
    # Regular expressions for each section
    node_pattern = re.compile(r'^\s*(\d+)\s+\d+\s+\d+\s+\d+\s*$')  # Matches node header line
    element_pattern = re.compile(r'^\s*(\d+)\s+(\d+)\s+\d+\s+\d+\s+\d+\s+\d+\s*$')  # Matches element header line
    # Pattern for group headers: any number at start, zeros in middle, any number at end
    group_header_pattern = re.compile(r'^\s*(\d+)\s+0\s+0\s+0\s+0\s+0\s+0\s+(\d+)\s*$')
    
    with open(unv_path, 'r') as f:
        lines = f.readlines()
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Look for section markers
            if line == '-1':
                i += 1
                if i >= len(lines):
                    break
                    
                section = lines[i].strip()
                
                # Node section (2411)
                if section == '2411':
                    i += 1
                    while i < len(lines):
                        if lines[i].strip() == '-1':
                            break
                        
                        match = node_pattern.match(lines[i].strip())
                        if match:
                            node_id = int(match.group(1))
                            i += 1
                            coords = lines[i].strip().replace('D', 'E').split()
                            coordinates = [float(coords[0]), float(coords[1]), float(coords[2])]
                            unv_data.add_node(node_id, coordinates)
                        i += 1
                
                # Element section (2412)
                elif section == '2412':
                    i += 1
                    while i < len(lines):
                        if lines[i].strip() == '-1':
                            break
                            
                        match = element_pattern.match(lines[i].strip())
                        if match:
                            elem_id = int(match.group(1))
                            elem_type = match.group(2)
                            i += 1
                            nodes = [int(x) for x in lines[i].strip().split()]
                            unv_data.add_element(elem_id, elem_type, nodes)
                        i += 1
                
                # Groups section (2477)
                elif section == '2477':
                    i += 1
                    # Special handling for 2477: skip additional -1 markers
                    while i < len(lines) and lines[i].strip() == '-1':
                        i += 1
                    
                    while i < len(lines):
                        if lines[i].strip() == '-1':
                            break
                            
                        # Look for group header pattern
                        if group_header_pattern.match(lines[i].strip()):
                            i += 1
                            # Next line contains the group name
                            group_name = lines[i].strip()
                            print(group_name)
                            i += 1
                            
                            # Only process if it's Matrix, Envelope, or Inclusion_*
                            if (group_name.strip() == "Matrix" or 
                                group_name.strip() == "Envelope" or 
                                group_name.strip().startswith("Inclusion_")):
                                
                                # Process elements until we hit next group header or section end
                                while (i < len(lines) and 
                                      lines[i].strip() != '-1' and 
                                      not group_header_pattern.match(lines[i].strip())):
                                    elements = lines[i].strip().split()
                                    # Process 8-field format: type, id, 0, 0, type, id, 0, 0
                                    for j in range(0, len(elements), 8):
                                        if j+1 < len(elements):
                                            elem_id = int(elements[j+1])  # Element ID is in second position
                                            unv_data.add_to_group(group_name, elem_id)
                                            
                                            # Check for second element in the same line
                                            if j+5 < len(elements):  # Make sure we have enough fields
                                                second_elem_id = int(elements[j+5])  # Second element ID
                                                unv_data.add_to_group(group_name, second_elem_id)
                                    i += 1
                            else:
                                # Skip non-matching group until next group header or section end
                                while (i < len(lines) and 
                                      lines[i].strip() != '-1' and 
                                      not group_header_pattern.match(lines[i].strip())):
                                    i += 1
                        else:
                            i += 1
            i += 1
    
    return unv_data

def convert_element_type(unv_type):
    """Convert UNV element types to Abaqus element types"""
    # UNV type 91 = linear triangle, 94 = linear quad
    type_mapping = {
        '91': 'CPS3',   # 2D triangle - plane stress
        '94': 'CPS4R',  # 2D quad - plane stress, reduced integration
        '111': 'C3D4',  # 3D tetra
        '115': 'C3D8'   # 3D hex
    }
    return type_mapping.get(unv_type, 'Unknown')

def write_inp_model(unv_data, output_path):
    """Write the INP model file in the required format"""
    # Find border nodes (using small tolerance for float comparison)
    tolerance = 1e-6
    nminx = []
    nmaxx = []
    nminy = []
    nmaxy = []
    
    for node_id, coords in unv_data.nodes.items():
        # Check X borders
        if abs(coords[0] - unv_data.minpos[0]) < tolerance:
            nminx.append(node_id)
        if abs(coords[0] - unv_data.maxpos[0]) < tolerance:
            nmaxx.append(node_id)
        # Check Y borders
        if abs(coords[1] - unv_data.minpos[1]) < tolerance:
            nminy.append(node_id)
        if abs(coords[1] - unv_data.maxpos[1]) < tolerance:
            nmaxy.append(node_id)

    with open(output_path, 'w') as f:
        # Header - matching Abaqus format exactly
        f.write("*Heading\n")
        f.write("** Job name: UNV_conversion Model name: Model-1\n")
        f.write("** Generated by: unv_to_inp_model.py\n")
        f.write("*Preprint, echo=NO, model=NO, history=NO, contact=NO\n")
        f.write("**\n** PARTS\n**\n")
        
        # Part definition - Note the uppercase RVEPLUS
        f.write("*Part, name=RVEPLUS\n")
        
        # Nodes - ensure proper formatting (2D coordinates only)
        f.write("*Node\n")
        for node_id, coords in sorted(unv_data.nodes.items()):
            # Format with proper spacing and precision, only X and Y coordinates
            f.write(f"{node_id:>8}, {coords[0]:>12.6f}, {coords[1]:>12.6f}\n")
        
        # After writing nodes and before elements, add the border node sets
        # Write node sets for borders
        
        # Separate elements by type
        triangles = []
        quads = []
        for elem in unv_data.elements:
            if elem['type'] == '91':  # Triangle elements
                triangles.append(elem)
            elif elem['type'] == '94':  # Quad elements
                quads.append(elem)
        
        # Write triangular elements (CPS3)
        if triangles:
            f.write("*Element, type=CPS3\n")
            for elem in sorted(triangles, key=lambda x: x['id']):
                nodes = elem['nodes'][:3]  # Ensure exactly 3 nodes
                nodes_str = ", ".join(f"{node:>8}" for node in nodes)
                f.write(f"{elem['id']:>8}, {nodes_str}\n")
        
        # Write quadrilateral elements (CPS4R)
        if quads:
            f.write("*Element, type=CPS4R\n")
            for elem in sorted(quads, key=lambda x: x['id']):
                nodes = elem['nodes'][:4]  # Ensure exactly 4 nodes
                nodes_str = ", ".join(f"{node:>8}" for node in nodes)
                f.write(f"{elem['id']:>8}, {nodes_str}\n")
        
        # Write element sets with standardized names
        matrix_elements = unv_data.element_groups.get('VOLUME2', []) or unv_data.element_groups.get('MATRIX', [])
        envelope_elements = unv_data.element_groups.get('VOLUME3', []) or unv_data.element_groups.get('ENVELOPE', [])
        
        # Write MATRIX set
        if matrix_elements:
            f.write("*Elset, elset=MATRIX\n")
            for i in range(0, len(matrix_elements), 16):
                line_elements = matrix_elements[i:i+16]
                f.write(", ".join(f"{elem:>8}" for elem in line_elements) + "\n")
        
        # Write ENVELOPE set
        if envelope_elements:
            f.write("*Elset, elset=ENVELOPE\n")
            for i in range(0, len(envelope_elements), 16):
                line_elements = envelope_elements[i:i+16]
                f.write(", ".join(f"{elem:>8}" for elem in line_elements) + "\n")

        # Create combined SET-1
        if matrix_elements or envelope_elements:
            f.write("*Elset, elset=SET-1, instance=RVEPLUS-1, generate\n")
            min_elem = min(matrix_elements) if matrix_elements else min(envelope_elements)
            max_elem = max(envelope_elements) if envelope_elements else max(matrix_elements)
            f.write(f"{min_elem:>8}, {max_elem:>8}, {1:>8}\n")

        f.write("*End Part\n")
        f.write("**\n")
        
        # Assembly
        f.write("** ASSEMBLY\n")
        f.write("**\n")
        f.write("*Assembly, name=Assembly\n")
        f.write("**\n")
        f.write("*Instance, name=RVEPLUS-1, part=RVEPLUS\n")
        f.write("*End Instance\n")
        f.write("**\n")
        
        # Reference points for boundary conditions
        # Calculate positions based on model dimensions
        long = unv_data.maxpos[0] - unv_data.minpos[0]
        f.write("*Node\n")
        f.write(f"      1, {unv_data.minpos[0]+1.2*long:>12.6f}, {unv_data.minpos[1]:>12.6f}\n")
        f.write(f"      2, {unv_data.minpos[0]+1.4*long:>12.6f}, {unv_data.minpos[1]:>12.6f}\n")
        f.write(f"      3, {unv_data.minpos[0]+1.6*long:>12.6f}, {unv_data.minpos[1]:>12.6f}\n")
        
        # Reference point sets
        f.write("*Nset, nset=REFMACRO1\n       1\n")
        f.write("*Nset, nset=REFMACRO2\n       2\n")
        f.write("*Nset, nset=REFMACRO3\n       3\n")
        
        # Create a combined set for all elements
        f.write("*Elset, elset=SET-1, instance=RVEPLUS-1, generate\n")
        all_elements = [elem['id'] for elem in (triangles + quads)]
        if all_elements:
            f.write(f"{min(all_elements):>8}, {max(all_elements):>8}, {1:>8}\n")

        for set_name, nodes in [
            ('NMINX', nminx),
            ('NMAXX', nmaxx),
            ('NMINY', nminy),
            ('NMAXY', nmaxy)
        ]:
            if nodes:
                f.write(f"*Nset, nset={set_name}, instance=RVEPLUS-1\n")
                # Write 16 nodes per line with proper spacing
                for i in range(0, len(nodes), 16):
                    line_nodes = nodes[i:i+16]
                    f.write(", ".join(f"{node:>8}" for node in line_nodes) + "\n")
        
        f.write("*End Assembly\n")

    # Create the .e2a file with model dimensions
    e2a_path = os.path.splitext(output_path)[0] + '.e2a'
    long = unv_data.maxpos[0] - unv_data.minpos[0]
    larg = unv_data.maxpos[1] - unv_data.minpos[1]
    haut = unv_data.maxpos[2] - unv_data.minpos[2]
    
    with open(e2a_path, 'w') as f:
        f.writelines(str(long)+'\n')
        f.writelines(str(larg)+'\n')
        f.writelines(str(0)+'\n')
        f.writelines(str(0)+'\n')  # ep value (set to 0 for now)
        f.writelines(str(unv_data.maxpos[0])+'\n')
        f.writelines(str(unv_data.minpos[0])+'\n')
        f.writelines(str(unv_data.maxpos[1])+'\n')
        f.writelines(str(unv_data.minpos[1])+'\n')
        f.writelines(str(0)+'\n')
        f.writelines(str(0)+'\n')

def main():
    # Get UNV file from user
    from tkinter import Tk
    from tkinter.filedialog import askopenfilename
    
    Tk().withdraw()
    unv_file = askopenfilename(filetypes=[('UNV files', '*.unv')])
    
    if not unv_file:
        print("No file selected")
        return
    
    # Parse UNV file
    print("Parsing UNV file...")
    unv_data = parse_unv_file(unv_file)
    
    # Create output path
    base_path = os.path.splitext(unv_file)[0]
    output_path = f"{base_path}-model.inp"
    
    # Write INP file
    print("Writing INP file...")
    write_inp_model(unv_data, output_path)
    print(f"Conversion complete. Output written to: {output_path}")

if __name__ == "__main__":
    main() 
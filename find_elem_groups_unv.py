import os
import json
import numpy as np
from multiprocessing import Pool, cpu_count

def load_rve_config(json_path):
    """Load particle configuration from JSON file."""
    with open(json_path, 'r') as f:
        data = json.load(f)
        particles = []
        for i in range(len(data['particles']['x'])):
            particles.append({
                'x': data['particles']['x'][i],
                'y': data['particles']['y'][i],
                'radius': data['particles']['radius'][i]
            })
        return particles, data['box_size']

def get_node_coordinates(unv_path):
    """Extract node coordinates from UNV file."""
    nodes = {}
    with open(unv_path, 'r') as f:
        lines = f.readlines()
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line == '2411':
                i += 1
                while i < len(lines) and lines[i].strip() != '-1':
                    node_data = lines[i].strip().split()
                    if len(node_data) >= 1:
                        node_id = int(node_data[0])
                        i += 1
                        coord_line = lines[i].strip().replace('D', 'E')
                        coords = coord_line.split()
                        if len(coords) >= 3:
                            nodes[node_id] = np.array([float(coords[0]), float(coords[1])])
                    i += 1
            i += 1
    return nodes

def is_point_in_sphere(point, sphere):
    """Check if point is inside a sphere (circle in 2D)."""
    return np.linalg.norm(np.array([point[0] - sphere['x'], point[1] - sphere['y']])) <= sphere['radius']

def is_point_outside_box(point, box_size):
    """Check if point is outside the bounding box."""
    return not (0 <= point[0] <= box_size and 0 <= point[1] <= box_size)

def process_unv_file(unv_path):
    """Process a single UNV file."""
    try:
        json_path = unv_path.replace('.unv', '.json').replace('RVE_model', 'RVE_definition')
        if not os.path.exists(json_path):
            return None

        particles, box_size = load_rve_config(json_path)
        nodes = get_node_coordinates(unv_path)
        groups = {}
        envelope_elements = []
        
        with open(unv_path, 'r') as f:
            lines = f.readlines()
            i = 0
            found_section = False
            while i < len(lines):
                line = lines[i].strip()
                if line == '2412':
                    found_section = True
                    i += 1
                    continue
                if line == '-1':
                    found_section = False
                
                if found_section:
                    try:
                        elem_data = line.split()
                        if len(elem_data) >= 6 and (elem_data[1] == '91' or elem_data[1] == '94'):
                            elem_id = int(elem_data[0])
                            elem_type = elem_data[1]
                            group_id = int(elem_data[2])
                            
                            i += 1
                            node_ids = [int(x) for x in lines[i].strip().split()]
                            node_coords = [nodes[node_id] for node_id in node_ids]
                            element_center = np.mean(node_coords, axis=0)
                            
                            is_envelope = (elem_type == '94' or 
                                         (elem_type == '91' and is_point_outside_box(element_center, box_size)))
                            
                            if is_envelope:
                                envelope_elements.append(elem_id)
                            else:
                                if group_id not in groups:
                                    groups[group_id] = {
                                        'elements': [],
                                        'sample_element_nodes': node_ids,
                                        'assigned_inclusion': None
                                    }
                                groups[group_id]['elements'].append(elem_id)
                    except (ValueError, IndexError):
                        pass
                i += 1

        final_groups = {}
        for group_id, group_data in groups.items():
            try:
                epicenter = np.mean([nodes[node_id] for node_id in group_data['sample_element_nodes']], axis=0)
                for i, sphere in enumerate(particles, 1):
                    if is_point_in_sphere(epicenter, sphere):
                        group_data['assigned_inclusion'] = i
                        break
            except KeyError:
                continue

        for inclusion_num in range(1, len(particles) + 1):
            inclusion_elements = []
            for group_data in groups.values():
                if group_data['assigned_inclusion'] == inclusion_num:
                    inclusion_elements.extend(group_data['elements'])
            if inclusion_elements:
                final_groups[inclusion_num] = {
                    'elements': inclusion_elements,
                    'name': f'Inclusion_{inclusion_num}'
                }

        matrix_elements = []
        for group_data in groups.values():
            if group_data['assigned_inclusion'] is None:
                matrix_elements.extend(group_data['elements'])

        if matrix_elements:
            final_groups[len(particles) + 1] = {
                'elements': matrix_elements,
                'name': 'Matrix'
            }

        if envelope_elements:
            final_groups[len(particles) + 2] = {
                'elements': envelope_elements,
                'name': 'Envelope'
            }

        write_2477_section(unv_path, final_groups)
        return unv_path
    except Exception as e:
        return f"Error processing {unv_path}: {str(e)}"

def write_2477_section(unv_path, groups):
    """Append Dataset 2477 section to the UNV file."""
    with open(unv_path, 'a') as f:
        f.write('    -1\n')
        f.write('  2477\n')
        for group_id, group_data in sorted(groups.items()):
            elements = group_data['elements']
            if not elements:
                continue
            
            f.write(f'{group_id:>10}{0:>10}{0:>10}{0:>10}{0:>10}{0:>10}{0:>10}{len(elements):>10}\n')
            f.write(f'{group_data["name"]:<80}\n')
            
            for i in range(0, len(elements), 2):
                line = ""
                for j in range(2):
                    if i + j < len(elements):
                        line += f'{8:>10}{elements[i + j]:>10}{0:>10}{0:>10}'
                f.write(f'{line}\n')
        
        f.write('    -1\n')

def main():
    base_dir = r"C:/temp/RVE_model"
    unv_files = []
    for root, _, files in os.walk(base_dir):
        unv_files.extend([os.path.join(root, f) for f in files if f.endswith('.unv')])
    
    with Pool(processes=cpu_count()) as pool:
        results = pool.map(process_unv_file, unv_files)
    
    # Minimal error reporting
    errors = [r for r in results if isinstance(r, str) and r.startswith('Error')]
    if errors:
        with open('processing_errors.log', 'w') as f:
            f.write('\n'.join(errors))

if __name__ == "__main__":
    main()
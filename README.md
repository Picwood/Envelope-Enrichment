# Homtools - Homogenization Tools for Abaqus

A Python-based toolset for automated homogenization analysis in Abaqus, featuring an iterative enrichment procedure.

## Overview

Homtools is a collection of Python scripts that automate the process of creating and analyzing Representative Volume Elements (RVEs) for material homogenization in Abaqus. The toolset includes:

- A GUI for model creation and parameter input
- Automated RVE envelope generation
- Periodic boundary conditions implementation
- Integration with Abaqus for analysis

## Project Structure

```
homtools-perso/
├── Model Creation/
│   ├── main_GUI.py           # Main graphical interface for model creation
│   ├── create_model_inp.py   # Model input file generation
│   ├── RVE_envlop_gene_custom_inp_nodeset.py  # RVE envelope generator
│   └── fiber_2D.py          # 2D fiber model utilities
├── abaqus_plugin/
│   ├── periodicBoundary_env.py    # Periodic boundary conditions implementation
│   ├── envelope_Enrichment_homtoolsDB.py  # Enrichment database management
│   └── envelope_Enrichment_homtools_plugin.py  # Abaqus plugin interface
```

## Features

1. **Model Creation**
   - Interactive GUI for parameter input
   - Support for multiple material types:
     - Elastic
     - Engineering Constants
     - Orthotropic
   - Automated mesh generation with periodic boundaries
   - Custom node set creation

2. **RVE Generation**
   - Automatic envelope creation around existing models
   - Support for 2D and 3D models
   - Customizable mesh density
   - Periodic boundary implementation

3. **Periodic Boundary Conditions**
   - Automated constraint equation generation
   - Tree-based algorithm to avoid duplicate DOFs
   - Support for reference points and node sets
   - Verification of master/slave node relationships

## Prerequisites

- Abaqus CAE with Python scripting enabled
- Python 2.7 (compatible with Abaqus)
- Required Python packages:
  - tkinter
  - numpy
  - gmsh

## Usage

1. **Model Creation**
   ```bash
   python main_GUI.py
   ```
   - Input material properties
   - Set mesh parameters
   - Define model dimensions

2. **RVE Generation**
   - Select input files (.inp format)
   - Specify envelope thickness
   - Choose mesh density
   - Define material properties for matrix and embedded phases

3. **Periodic Boundary Application**
   - Run through Abaqus plugin interface
   - Select node sets for periodic boundaries
   - Define reference points for loading
   - Execute analysis

## Implementation Details

### Main Components

1. **GUI (main_GUI.py)**
   - Material property input
   - Mesh control parameters
   - Model dimension settings

2. **RVE Generator (RVE_envlop_gene_custom_inp_nodeset.py)**
   - Uses GMSH for mesh generation
   - Creates periodic mesh
   - Generates node sets for boundaries

3. **Periodic Boundary Handler (periodicBoundary_env.py)**
   - Tree-based constraint equation management
   - Master/slave node relationship verification
   - Reference point integration

### Key Classes

1. **Tree**
   - Manages constraint equations
   - Prevents duplicate DOFs
   - Handles graph-based node relationships

2. **PeriodicBoundary**
   - Implements boundary conditions
   - Manages reference points
   - Handles node set creation

3. **NodeData**
   - Stores node coordinates
   - Tracks boundary positions
   - Manages mesh geometry

## Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Insert License Information]

## Contact

[Insert Contact Information] 
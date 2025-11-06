from pathlib import Path

def folder_parser(directory):
    for xyz_file in directory.rglob("*.xyz"):
        with open(xyz_file, "r") as file:
            content = file.readlines()
        atoms = []
        coordinates = []

        for line in content[2:]:
            parts = line.split()
            atoms.append(parts[0])
            coordinates.append([float(coordinate) for coordinate in parts[1:]])

        data = {"atoms": atoms, "coordinates": coordinates}
        print(data)

folder_parser(Path("data/geometries/transition-states"))
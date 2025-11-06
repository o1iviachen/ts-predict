import mysql.connector
import os
import rdkit
from pathlib import Path

base_dir = Path("data/geometries/transition-states")

for xyz_file in base_dir.rglob("*.xyz"):
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


# mydb = mysql.connector.connect(
#     host="localhost",
#     user="root",
#     password=os.environ.get("SQL_PW"),
#     database="ts-predict-db"
# )
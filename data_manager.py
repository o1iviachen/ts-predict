from pathlib import Path
import h5py
import json
import math


class DataManager():
    @staticmethod
    def xyz_file_parser(file_directory):
        with open(file_directory, "r") as file:
            content = file.readlines()
        
        atoms = []
        coordinates = []

        for line in content[2:]:
            parts = line.split()
            atoms.append(parts[0])
            coordinates.append([float(coordinate) for coordinate in parts[1:]])

        data = {"atoms": atoms, "coordinates": coordinates}

        return data
    
    @staticmethod
    def han_hdf5_file_parser(file_directory):
        reactions = []
        with h5py.File(file_directory, "r") as file:
            structure_keys = list(file.keys())
            number_of_reactions = len(file[structure_keys[0]]["atomic_numbers"])
            for i in range(number_of_reactions):
                reaction_dict = {}
                for key in structure_keys:
                    atomic_numbers = file[key]["atomic_numbers"][i].tolist()
                    structure = file[key]["cartesians"][i].tolist()
                    sql_structure = [
                        [None if math.isnan(coord) else coord for coord in atom_coords]
                        for atom_coords in structure
                    ]
                    reaction_dict[key] = json.dumps({"atoms": atomic_numbers, "coordinates": sql_structure})
                reactions.append(reaction_dict)
    
        return reactions
    
    def transition1x_hdf5_file_parser(file_directory):
        reactions = []
        with h5py.File(file_directory, "r") as file:
            longest_array = 0
            for molecule in file["data"]:
                sample_reaction_key = list(file["data"][molecule].keys())[0]
                sample_atoms = len(file["data"][molecule][sample_reaction_key]["atomic_numbers"])
                if sample_atoms > longest_array:
                    longest_array = sample_atoms
            for molecule in file["data"]:
                for reaction in file["data"][molecule]:
                    reaction_dict = {}
                    structures = ["product", "reactant", "transition_state"]
                    for structure in structures:
                        structure_dict = {"atoms": file["data"][molecule][reaction][structure]["atomic_numbers"][:].tolist(), "coordinates": file["data"][molecule][reaction][structure]["positions"][:].tolist()}
                        while len(structure_dict["atoms"]) < 23:
                            structure_dict["atoms"].append(0)
                            structure_dict["coordinates"].append([None, None, None])
                        reaction_dict[structure] = structure_dict
                    reactions.append(reaction_dict)
        
        return reactions
    
    @staticmethod
    def sql_insert_reactions(data, reaction_type_id, source_id, cursor):
        values = list(data[0].keys()) + ["reaction_type_id", "source_id"]
        script = f"""
            INSERT INTO reaction 
            ({", ".join(values)})
            VALUES ({", ".join(["%s"] * len(values))})
        """
        for reaction in data:
            reaction_dict = reaction | {"reaction_type_id": reaction_type_id, "source_id": source_id}
            reaction_tuple = tuple(
                json.dumps(value) if isinstance(value, dict) else value
                for value in reaction_dict.values()
            )
            cursor.execute(script, reaction_tuple)

print(DataManager.transition1x_hdf5_file_parser(Path("data/transition1x_dataset.h5")))
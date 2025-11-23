from pathlib import Path
import h5py
import json
import math


class DataManager():
    """
    Class for data management functions
        
    Methods
        xyz_file_parser(file_directory)
            parses xyz files 
        han_hdf5_file_parser(file_directory)
            parses hdf5 files with Han's datasets' format
        transition1x_hdf5_file_parser(file_directory):
            parses hdf5 files in the transition1x dataset format
        sql_insert_reactions(data, reaction_type_id, source_id, cursor)
            inserts reactions into SQL ts-predict-db database
    """
    
    @staticmethod
    def xyz_file_parser(file_directory):
        """
        Parses xyz files
        
        Arguments
            file_directory (Path): file directory to xyz file
        
        Returns
            data: dictionary of atoms and coordinates of a structure
        """

        # Read file content
        with open(file_directory, "r") as file:
            content = file.readlines()
        
        atoms = []
        coordinates = []

        # Loop through each line to slice atom and coordinates and append to corresponding lists
        for line in content[2:]:
            parts = line.split()
            atoms.append(parts[0])
            coordinates.append([float(coordinate) for coordinate in parts[1:]])

        data = {"atoms": atoms, "coordinates": coordinates}

        return data
    
    @staticmethod
    def han_hdf5_file_parser(file_directory):
        """
        Parses hdf5 files with Han's datasets' format
        
        Arguments
            file_directory (Path): file directory to hdf5 file
        
        Returns
            reaction: lists of dictionaries of atoms and coordinates of a structure
        """
        reactions = []

        with h5py.File(file_directory, "r") as file:

            # Get a list of the top layer's keys
            structures = list(file.keys())

            # Determine the number of reactions by retrieving the number of molecules
            number_of_reactions = len(file[structures[0]]["atomic_numbers"])

            # Loop through the reactions
            for i in range(number_of_reactions):

                # Create an empty dictionary representing a reaction
                reaction_dict = {}

                # Loop through each available structure
                for structure in structures:
                    atomic_numbers = file[structure]["atomic_numbers"][i].tolist()
                    coordinates = file[structure]["cartesians"][i].tolist()

                    # Convert NaN to None to render data compatible with SQL
                    sql_structure = [
                        [None if math.isnan(coord) else coord for coord in atom_coords]
                        for atom_coords in coordinates
                    ]

                    # Convert structure dictionary to JSON string to render data compatible with SQL and add to reaction dictionary
                    reaction_dict[structure] = json.dumps({"atoms": atomic_numbers, "coordinates": sql_structure})
                reactions.append(reaction_dict)
    
        return reactions
    
    def transition1x_hdf5_file_parser(file_directory):
        """
        Parses hdf5 files with Transition1x dataset's format
        
        Arguments
            file_directory (Path): file directory to hdf5 file
        
        Returns
            reaction: lists of dictionaries of atoms and coordinates of a structure
        """
        reactions = []
        with h5py.File(file_directory, "r") as file:

            # Use dummy atom masking
            longest_array = 0

            # Determine the molecules with the most atoms
            for molecule in file["data"]:

                # Retrieve sample reaction to retrieve atomic numbers of molecule
                sample_reaction_key = list(file["data"][molecule].keys())[0]
                number_of_atoms = len(file["data"][molecule][sample_reaction_key]["atomic_numbers"])

                # If number of atoms is higher than current highest, equal current highest to number of atoms
                if number_of_atoms > longest_array:
                    longest_array = number_of_atoms
            
            # Loop through each molecule
            for molecule in file["data"]:

                # Loop through each molecule's reactions
                for reaction in file["data"][molecule]:

                    # Create an empty dictionary representing a reaction
                    reaction_dict = {}
                    structures = ["product", "reactant", "transition_state"]

                    # For each structure, create a structure dictionary
                    for structure in structures:
                        atomic_numbers = file["data"][molecule][reaction][structure]["atomic_numbers"][:].tolist()
                        coordinates = file["data"][molecule][reaction][structure]["positions"][:][0].tolist()

                        # Employ dummy atom masking
                        while len(atomic_numbers) < longest_array:
                            atomic_numbers.append(0)
                            coordinates.append([None, None, None])
                        
                        # Convert structure dictionary to JSON string to render data compatible with SQL and add to reaction dictionary
                        reaction_dict[structure] = json.dumps({"atoms": atomic_numbers, "coordinates": coordinates})
                    reactions.append(reaction_dict)
        
        return reactions
    
    @staticmethod
    def sql_insert_reactions(data, reaction_type_id, source_id, cursor):
        """
        Inserts reactions into SQL ts-predict-db database
        
        Arguments
            data (list[dict[str, dict[str, list]]]): list of dictionaries representing reactions
            reaction_type_id (int): foreign key referencing characterisation table
            source_id (int): foreign key referencing source table
            cursor (MySQLCursor): executes insert command
        """

        # Prepare SQL script
        values = list(data[0].keys()) + ["reaction_type_id", "source_id"]
        script = f"""
            INSERT INTO reaction 
            ({", ".join(values)})
            VALUES ({", ".join(["%s"] * len(values))})
        """

        # Loop through reactions 
        for reaction in data:

            # Concatenate dictionaries and convert to tuple to execute insert command
            reaction_dict = reaction | {"reaction_type_id": reaction_type_id, "source_id": source_id}
            reaction_tuple = tuple(
                json.dumps(value) if isinstance(value, dict) else value
                for value in reaction_dict.values()
            )
            cursor.execute(script, reaction_tuple)

    @staticmethod
    def sql_parse_reactions(reactions, columns):
        reaction_dicts = []
        for reaction in reactions:
            reaction_dict = {}
            for i in range(len(reaction)):
                if isinstance(reaction[i], str):
                    value = json.loads(reaction[i])
                else:
                    value = reaction[i]
                reaction_dict[columns[i]] = value
            reaction_dicts.append(reaction_dict)
        
        return reaction_dicts
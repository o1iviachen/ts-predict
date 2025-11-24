class ModelManager():
    """
    Class for predictive models 
        
    Methods
        interpolate_model(reaction, fraction = 0.5)
            simple interpolation model, similar to Han's model
        error(reaction, predicted_ts)
            determines the total distance error between the actual and predicted transition states
    """
    @staticmethod
    def interpolate_model(reaction, fraction = 0.5): 
        """
        Simple interpolation model
        
        Arguments
            reaction (dict): dictionary representing a reaction
            fraction (float): the fraction of the distance added to the reactant coordinates
        
        Returns
            ts_dict: dictionary representing predicted transition state
        """
        ts_dict = {}
        
        # Set the predicted transition state's atoms as the reaction's atoms
        ts_dict["atoms"] = reaction["reactant"]["atoms"]

        # If origial data has reactant and product complexes, use corresponding coordinates
        if reaction["reactant_complex"] is not None and reaction["product_complex"] is not None:
            rc_coords = reaction["reactant_complex"]["coordinates"]
            pc_coords = reaction["product_complex"]["coordinates"]

        # Otherwise, use other the reactant and product's coordinates
        else:
            rc_coords = reaction["reactant"]["coordinates"]
            pc_coords = reaction["product"]["coordinates"]
        
        # Initialise list for predicted transition state's coordinates
        ts_coords = []

        # For each non-null coordinate, determine the midpoint and list above
        for i in range(len(rc_coords)):
            if rc_coords[i] != [None, None, None]:
                ts_coord = [rc_coords[i][j] + (rc_coords[i][j] - pc_coords[i][j])*fraction for j in range(len(rc_coords[i]))] 
            else:
                ts_coord = rc_coords[i]
            ts_coords.append(ts_coord)
        
        # Set the predicted transition state's coordinates
        ts_dict["coordinates"] = ts_coords

        return ts_dict
    
    @staticmethod
    def error(reaction, predicted_ts):
        """
        Calculates prediction error as sum of distances between actual and predicted transition state structures
        
        Arguments
            reaction (dict): dictionary representing a reaction
            predicted_ts (dict): dictionary representing predicted transition state
        
        Returns
            sum_structure_error: error value
        """
        # Get the actual and predicted transition states' coordinates
        ts_coords = reaction["transition_state"]["coordinates"]
        predicted_ts_coords = predicted_ts["coordinates"]

        sum_structure_error = 0

        # Loop through the actual and predicted transition states' coordinates
        for i in range(len(ts_coords)):
            component_difference = 0

            # For all the non-null coordinates, calculate the actual and predicted coordinates' distances 
            if ts_coords[i] != [None, None, None]:
                for j in range(len(ts_coords[i])):
                    component_difference += (ts_coords[i][j] - predicted_ts_coords[i][j])**2
                sum_structure_error += component_difference**0.5

            # If the coordinate is null, break out of the loop; all distances have been calculated
            else:
                break        
        
        return sum_structure_error
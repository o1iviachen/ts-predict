class ModelManager():
    @staticmethod
    def interpolate_model(reaction, fraction = 0.5): 
        ts_dict = {}
        
        ts_dict["atoms"] = reaction["reactant"]["atoms"]
        if reaction["reactant_complex"] is not None and reaction["product_complex"] is not None:
            rc_coords = reaction["reactant_complex"]["coordinates"]
            pc_coords = reaction["product_complex"]["coordinates"]
        else:
            rc_coords = reaction["reactant"]["coordinates"]
            pc_coords = reaction["product"]["coordinates"]
        
        ts_coords = []
        for i in range(len(rc_coords)):
            if rc_coords[i] != [None, None, None]:
                ts_coord = [rc_coords[i][j] + (rc_coords[i][j] - pc_coords[i][j])*fraction for j in range(len(rc_coords[i]))] 
            else:
                ts_coord = rc_coords[i]
            ts_coords.append(ts_coord)
        ts_dict["coordinates"] = ts_coords

        return ts_dict
    
    @staticmethod
    def error(reaction, predicted_ts):
        ts_coords = reaction["transition_state"]["coordinates"]
        predicted_ts_coords = predicted_ts["coordinates"]
        sum_structure_error = 0
        for i in range(len(ts_coords)):
            component_difference = 0
            if ts_coords[i] != [None, None, None]:
                for j in range(len(ts_coords[i])):
                    component_difference += (ts_coords[i][j] - predicted_ts_coords[i][j])**2
                sum_structure_error += component_difference**0.5
            else:
                break        
        
        return sum_structure_error
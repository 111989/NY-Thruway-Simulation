import pandas as pd
from main.Graph.GraphCreator import CONFIGS, ACCESS_POINTS
from tqdm import tqdm

PATH_2019 = '/home/capstone/Documents/AMS_553_Final_Project/2019_final.csv'
PATH_2018 = '/home/capstone/Documents/AMS_553_Final_Project/2018_final.csv'
PATH_2017 = '/home/capstone/Documents/AMS_553_Final_Project/2017_final.csv'
DATA_PATH = '/home/capstone/Documents/AMS_553_Final_Project/original_results_1.csv'
SAVE_PATH_19 = '/home/capstone/Documents/AMS_553_Final_Project/2019_analysis_3.csv'
SAVE_PATH_18 = '/home/capstone/Documents/AMS_553_Final_Project/2018_analysis.csv'
SAVE_PATH_17 = '/home/capstone/Documents/AMS_553_Final_Project/2017_analysis.csv'

def translate_index(index):
    return tuple([index[0][::-1]]) + index[1:]

def analyze(simulation, gathered, save_path):
    print("Loading Gathered data...")
    gathered_data = pd.read_csv(gathered, index_col=['vehicle_class', 'entrance_site', 'exit_site', 'week_of_year'], usecols=['vehicle_class', 'entrance_site', 'exit_site', 'week_of_year', 'payment_type', 'profit'])
    gathered_data = gathered_data[gathered_data['payment_type'] == 'E-ZPass']
    print("loading simulation data...")
    simulation_data = pd.read_csv(simulation, index_col=['Vehicle Class', 'Entrance', 'Exit', 'Week']) if type(simulation) == str else simulation
    print(simulation_data)
    errors = {}
    for index in tqdm(gathered_data.index):
        if not (index[1] in ACCESS_POINTS and index[2] in ACCESS_POINTS):
            continue
        try:
            actual_profit = gathered_data.loc[index]['profit']
            simulated_profit = simulation_data.loc[translate_index(index)]
            err = (simulated_profit - actual_profit)/actual_profit
            err['Mean Perc. Err.'] = err.mean()
            errors[index] = err
        except:
            print("ERROR:", index)
    errors = pd.DataFrame(errors).T
    errors.index.names = ['vehicle_type', 'entrance', 'exit', 'week']
    if save_path is not None:
        errors.to_csv(save_path)
    return errors

if __name__ == '__main__':
    print(analyze(DATA_PATH, PATH_2019, None))
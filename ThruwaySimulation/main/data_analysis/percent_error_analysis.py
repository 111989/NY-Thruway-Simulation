import pandas as pd
import main.data_analysis.analyze_original_data as analysis

BASE_PATH = '/home/capstone/Documents/AMS_553_Final_Project/Original_simulation_results/%s_simulation.csv'
ANALYSIS_PATH = '/home/capstone/Documents/AMS_553_Final_Project/Original_simulation_results/%s_analysis_2.csv'
ANALYSIS_SAVE_PATH = '/home/capstone/Documents/AMS_553_Final_Project/Original_simulation_results/%s_analysis_2.csv'
ADJUSTED_SAVE_PATH = '/home/capstone/Documents/AMS_553_Final_Project/Original_simulation_results/%s_adjusted.csv'
YEARS = ['2017', '2018', '2019']
INDEX = ['Vehicle Class', 'Entrance', 'Exit', 'Week']
ANALYSIS_INDEX = ['vehicle_type', 'entrance', 'exit', 'week']
ORIGINAL_DATA = {"2019": analysis.PATH_2019,"2018": analysis.PATH_2018, "2017": analysis.PATH_2017}


def run_prelim_analysis():
    for year in YEARS:
        path = BASE_PATH % year
        data = pd.read_csv(path, index_col=INDEX)
        analysis.analyze(data, ORIGINAL_DATA[year], ANALYSIS_SAVE_PATH % year)

def run_error_analysis():
    min_error = None
    for year in YEARS:
        path = ANALYSIS_PATH % year
        data = pd.read_csv(path, index_col=ANALYSIS_INDEX)
        overall_mean_error = data['Mean Perc. Err.'].mean()
        if min_error is None:
            min_error = (year, overall_mean_error)
        elif overall_mean_error < min_error[1]:
            min_error = (year, overall_mean_error)
    return min_error

def adjust_for_error():
    year, percent_error = run_error_analysis()
    print(year, percent_error)
    path = BASE_PATH % year
    data = pd.read_csv(path, index_col=INDEX)
    for column in data.columns:
        data[column] = data[column] / (1 + percent_error)
    analysis_results = analysis.analyze(data, ORIGINAL_DATA[year], None)
    #analysis_results.to_csv(ADJUSTED_SAVE_PATH % year)


if __name__ == '__main__':
    print(adjust_for_error())
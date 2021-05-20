import main.Graph.GraphCreator as gc
import main.data_analysis.analyze_original_data as analysis

SIMULATION_19 = "/home/capstone/Documents/AMS_553_Final_Project/2019_simulation.csv"
SIMULATION_18 = "/home/capstone/Documents/AMS_553_Final_Project/2018_simulation.csv"
SIMULATION_17 = "/home/capstone/Documents/AMS_553_Final_Project/2017_simulation.csv"

def run_pipeline(pipeline_name, distribution_data_path, original_data_path, simulation_save_path, analysis_save_path):
    print("----- %s -----" % pipeline_name)
    results = gc.run_original_simulation(10, gc.create_poisson_distributions, gc.EXIT_PERCENTAGES_PATH, gc.PATH_PRICE_PATH, distribution_data_path, simulation_save_path)
    analysis_results = analysis.analyze(results, original_data_path, analysis_save_path)
    print(analysis_results)

if __name__ == '__main__':
    run_pipeline("2019", gc.DISTRIBUTION_DATA_PATH_19, analysis.PATH_2019, SIMULATION_19, analysis.SAVE_PATH_19)
    run_pipeline("2018", gc.DISTRIBUTION_DATA_PATH_18, analysis.PATH_2018, SIMULATION_18, analysis.SAVE_PATH_18)
    run_pipeline("2017", gc.DISTRIBUTION_DATA_PATH_17, analysis.PATH_2017, SIMULATION_17, analysis.SAVE_PATH_17)
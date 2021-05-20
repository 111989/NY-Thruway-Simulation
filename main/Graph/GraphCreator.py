from dijkstar import Graph, find_path
from main.data_cleaning.text_to_dataFrame import text_to_data_frame
from tqdm import tqdm
import itertools
import pandas as pd
import scipy.stats as stats
import numpy.random as random
import time


# ITERABLE
ACCESS_POINTS = ["15", "16", "17", "18", "19", "20", "21", "21B", "22", "B1", "B2", "B3", "23", "24"]
TOLLS = {"T1", "T2", "T3", "T4"}
VEHICLE_TYPES = {"H2", "L2", "H3", "L3", "H4", "L4", "H5", "H6", "H7"}

# CONFIGURATION
CONFIGS = set(itertools.product(VEHICLE_TYPES, ACCESS_POINTS))
TYPE_INDEX = 0
ACCESS_POINT_INDEX = 1

# INPUT/OUTPUT
TOLL_COLUMN = "Toll"
PERCENTAGE_KEY = "percentage"
LAMBDA_KEY = "lambda"
BASE_INDEX = ["vehicle_class", "entrance_site", "exit_site"]
TOLL_FEE_PATH = "/home/capstone/Documents/AMS_553_Final_Project/Simulation_tolls_2.xlsx"
EXPORT_PATH = "/home/capstone/Documents/AMS_553_Final_Project/expanded_results_2.csv"
EXIT_PERCENTAGES_PATH = '/home/capstone/Documents/AMS_553_Final_Project/exit_percentages.csv'
PATH_PRICE_PATH = '/home/capstone/Documents/AMS_553_Final_Project/all_prices.csv'
MISSING_PATH = '/home/capstone/Documents/AMS_553_Final_Project/missing_prices_2.csv'
ORIGINAL_RESULTS_PATH = '/home/capstone/Documents/AMS_553_Final_Project/original_results_%.csv'
DISTRIBUTION_DATA_PATH_19 = '/home/capstone/Documents/AMS_553_Final_Project/dataframe19.txt'
DISTRIBUTION_DATA_PATH_18 = '/home/capstone/Documents/AMS_553_Final_Project/dataframe18.txt'
DISTRIBUTION_DATA_PATH_17 = '/home/capstone/Documents/AMS_553_Final_Project/dataframe17.txt'

# Distributions
DISTRIBUTION_ADJUSTMENT = (1 + -0.9056880191412613)

# MAIN
WEEKS_IN_YEAR = 52
RUNS = 10000


def create_project_graph():
    graph = Graph()
    add_undirected_edge(graph, "15", "T1", 1)
    add_undirected_edge(graph, "T1", "16", 1)
    add_undirected_edge(graph, "16", "17", 1)
    add_undirected_edge(graph, "17", "T3", 1)
    add_undirected_edge(graph, "T3", "18", 1)
    add_undirected_edge(graph, "18", "19", 1)
    add_undirected_edge(graph, "19", "20", 1)
    add_undirected_edge(graph, "20", "21", 1)
    add_undirected_edge(graph, "21", "21B", 1)
    add_undirected_edge(graph, "21B", "T2", 1)
    add_undirected_edge(graph, "T2", "22", 1)
    add_undirected_edge(graph, "22", "B1", 1)
    add_undirected_edge(graph, "B1", "B2", 1)
    add_undirected_edge(graph, "B2", "T4", 1)
    add_undirected_edge(graph, "T4", "B3", 1)
    add_undirected_edge(graph, "22", "23", 1)
    add_undirected_edge(graph, "23", "24", 1)
    return graph


def add_undirected_edge(graph: Graph, u, v, edge):
    graph.add_edge(u, v, edge)
    graph.add_edge(v, u, edge)


def calculate_toll_paths():
    all_paths = {}
    graph = create_project_graph()
    entrance_exit_pairs = itertools.product(ACCESS_POINTS, ACCESS_POINTS)
    for entrance_point, exit_point in entrance_exit_pairs:
        if entrance_point != exit_point:
            if entrance_point not in all_paths.keys():
                all_paths[entrance_point] = {}
            if exit_point not in all_paths[entrance_point].keys():
                all_paths[entrance_point][exit_point] = {}
            path = find_path(graph, entrance_point, exit_point).nodes
            path_tolls = set(path).intersection(TOLLS)
            for toll in path_tolls:
                all_paths[entrance_point][exit_point][toll] = True
            for toll in TOLLS.difference(path_tolls):
                all_paths[entrance_point][exit_point][toll] = False
    return all_paths


def calculate_path_percentages():
    all_paths = calculate_toll_paths()
    exit_percentages = load_external_csv(EXIT_PERCENTAGES_PATH)
    all_percentages = {}
    for vehicle_type, entrance_point in CONFIGS:
        if vehicle_type not in all_percentages.keys():
            all_percentages[vehicle_type] = {}
        if entrance_point not in all_percentages[vehicle_type].keys():
            all_percentages[vehicle_type][entrance_point] = {}
        for exit_point in all_paths[entrance_point].keys():
            for toll in TOLLS:
                if toll not in all_percentages[vehicle_type][entrance_point].keys():
                    all_percentages[vehicle_type][entrance_point][toll] = 0
                if all_paths[entrance_point][exit_point][toll]:
                    partial_percentage = calculate_csv_value(exit_percentages, vehicle_type, entrance_point, exit_point)
                    all_percentages[vehicle_type][entrance_point][toll] += partial_percentage
    return all_percentages


def load_external_csv(path):
    return pd.read_csv(path, index_col=BASE_INDEX).T


def calculate_csv_value(exit_percentages, vehicle_type, entrance_point, exit_point, reverse = True, exits=True ,key=PERCENTAGE_KEY):
    return exit_percentages[vehicle_type[::-1] if reverse else vehicle_type][entrance_point][calculate_csv_exit_point(exit_point) if exits else exit_point][key]


def calculate_csv_exit_point(exit_point):
    return "16H" if exit_point == "16" else exit_point


def analyze_percentages():
    percentages = calculate_path_percentages()
    zero_configs = []
    for vehicle_type in percentages.keys():
        print(vehicle_type)
        for entrance_point in percentages[vehicle_type].keys():
            print("\t%s" % entrance_point)
            for toll in percentages[vehicle_type][entrance_point].keys():
                print("\t\t%s: %f" % (toll, percentages[vehicle_type][entrance_point][toll]))
            total_sum = sum(percentages[vehicle_type][entrance_point].values())
            print("\t\tSUM: %f" % total_sum)
            if total_sum <= 0: zero_configs.append((vehicle_type, entrance_point))
    print("ZERO CONFIGS: %s" % zero_configs)


def calculate_fee_proportion_constants(fee_path):
    fees = pd.read_excel(fee_path, index_col=TOLL_COLUMN)
    path_percentages = calculate_path_percentages()
    prop_consts = {}
    for configuration in CONFIGS:
        prop_const = 0
        for toll in TOLLS:
            percentage = path_percentages[configuration[TYPE_INDEX]][configuration[ACCESS_POINT_INDEX]][toll]
            fee = fees[configuration[TYPE_INDEX]][toll]
            prop_const += percentage * fee
        prop_consts[configuration] = prop_const
    return pd.Series(prop_consts)


def create_test_dist():
    # For Testing
    dists = {}
    for configuration in CONFIGS:
        dists[configuration] = (stats.nbinom, {"n": 1000, "p": .5})
    return dists


def create_poisson_distributions(distribution_data_path):
    dists = {}
    dist_data = text_to_data_frame(distribution_data_path)
    for vehicle_type, entrance_point in CONFIGS:
        lambda_param = dist_data[vehicle_type[::-1]][entrance_point][LAMBDA_KEY]
        dists[(vehicle_type, entrance_point)] = (stats.poisson, {"mu": lambda_param})
    return dists

def run_expanded_toll_simulation():
    start_time = time.time()
    conf = list(CONFIGS)
    conf.sort()
    data = {}
    dists = create_poisson_distributions(DISTRIBUTION_DATA_PATH_19)
    proportion_constants = calculate_fee_proportion_constants(TOLL_FEE_PATH)
    for run in tqdm(range(1, RUNS + 1)):
        random.seed(run)
        data[run] = {}
        #print("%s RUN %d %s" % ("-" * 10, run, "-" * 10))
        for week in range(1, WEEKS_IN_YEAR + 1):
            profit = 0
            for configuration in conf:
                arrival_amount = calculate_arrival_amount(dists, configuration)
                fee_proportion_const = proportion_constants[configuration]
                profit += arrival_amount * fee_proportion_const
            data[run][week] = round(profit, 2)
    final_data = pd.DataFrame(data).T
    print(final_data)
    final_data.to_csv(EXPORT_PATH)
    end_time = time.time()
    total_time = end_time - start_time
    print(total_time)


def calculate_arrival_amount(distributions, configuration):
    return distributions[configuration][0].rvs(**distributions[configuration][1]) / DISTRIBUTION_ADJUSTMENT

def run_original_simulation(runs, distribution_creator, exit_percenatges_path, price_path, distribution_data_path,save_path):
    exit_percentages = load_external_csv(exit_percenatges_path)
    prices = load_external_csv(price_path)
    conf = list(CONFIGS)
    conf.sort()
    distributions = distribution_creator(DISTRIBUTION_DATA_PATH_19)
    zero_configs = []
    results = {}
    missing = []
    total = runs * WEEKS_IN_YEAR * len(conf) * len(ACCESS_POINTS)
    with tqdm(total=total) as pbar:
        for run in range(1, runs + 1):
            random.seed(run)
            for week in range(1, WEEKS_IN_YEAR + 1):
                for configuration in conf:
                    for exit_point in ACCESS_POINTS:
                        pbar.update(1)
                        if configuration[ACCESS_POINT_INDEX] == exit_point:
                            continue
                        arrival_amount = calculate_arrival_amount(distributions, configuration)
                        exit_percent = calculate_csv_value(exit_percentages, configuration[TYPE_INDEX], configuration[ACCESS_POINT_INDEX], exit_point)
                        try:
                            price = calculate_csv_value(prices, configuration[TYPE_INDEX], configuration[ACCESS_POINT_INDEX], exit_point, reverse=False, exits=False, key="price")
                            exit_profit = round(arrival_amount * exit_percent * price, 2)
                            key = (configuration[TYPE_INDEX], configuration[ACCESS_POINT_INDEX], exit_point, week)
                            if key not in results.keys():
                                results[key] = {}
                            results[key]["Price %d" % run] = exit_profit
                        except KeyError:
                            missing.append({"vehicle_class": configuration[TYPE_INDEX], "Entrance": configuration[ACCESS_POINT_INDEX], "exit": exit_point})
                            print("NOT FOUND: (%s, %s, %s)" % (configuration[TYPE_INDEX], configuration[ACCESS_POINT_INDEX], exit_point))
    results = pd.DataFrame(results).T
    results.index.names = ["Vehicle Class", "Entrance", "Exit", "Week"]
    print(results)
    if save_path is not None:
        results.to_csv(save_path)
    return results


if __name__ == '__main__':
    ALL_TOLL_CONFIGS = {"T4": {"T1", "T2", "T3"}, "T3": {"T1", "T2", "T4"}, "T2": {"T1", "T3", "T4"}, "T1": {"T2", "T3","T4"}}
    for toll_config in ALL_TOLL_CONFIGS.keys():
        TOLLS = ALL_TOLL_CONFIGS[toll_config]
        EXPORT_PATH = "/home/capstone/Documents/AMS_553_Final_Project/Expanded_Simulation_results/expanded_results_%s.csv" % toll_config
        print(TOLLS)
        print(EXPORT_PATH)
        run_expanded_toll_simulation()

    #print(run_original_simulation(RUNS, create_poisson_distributions, EXIT_PERCENTAGES_PATH, PATH_PRICE_PATH, DISTRIBUTION_DATA_PATH_19, None))

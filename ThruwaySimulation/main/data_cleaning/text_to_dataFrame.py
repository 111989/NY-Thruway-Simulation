import pandas as pd


TEXT_PATH = '/home/capstone/Documents/AMS_553_Final_Project/dataframe19.txt'
CSV_PATH = '/home/capstone/Documents/AMS_553_Final_Project/2019_data.csv'


def text_to_data_frame(path):
    data = {}
    with open(path) as f:
        lines = f.readlines()
        columns = [line.strip() for line in lines[0].split("\t")[1:]]
    for line in lines[1:]:
        index, entrance_site, vehicle_class, lambda_param, intercept_param, alpha_param = [line.strip() for line in line.split("\t")]
        data[vehicle_class, entrance_site] = {"lambda": float(lambda_param), "intercept": float(intercept_param), "alpha": float(alpha_param)}
    data = pd.DataFrame(data)
    return data

if __name__ == '__main__':
    text_to_data_frame(TEXT_PATH)
import pandas as pd
from tqdm import tqdm
from main.Graph.GraphCreator import ACCESS_POINTS

DATA_PATH = '/home/capstone/Documents/AMS_553_Final_Project/final_study_data.csv'
SAVE_PATH = '/home/capstone/Documents/AMS_553_Final_Project/vehicle_counts_5.xlsx'
def analyze(path):
    data = pd.read_csv(path)
    data = data[data['exit_site'].isin(ACCESS_POINTS) & data['entrance_site'].isin(ACCESS_POINTS)]
    data = data[data['payment_type'] == 'E-ZPass']
    data = data.set_index(['vehicle_class', 'entrance_site'])
    grouped_data = data.groupby(data.index)
    writer = pd.ExcelWriter(SAVE_PATH, engine='xlsxwriter')
    for group in tqdm(grouped_data):
        outbound = group[1]['vehicle_count']
        outbound = outbound.rename(str(group[0]))
        outbound.to_excel(writer, sheet_name=str(group[0]), index=False)
    writer.save()

if __name__ == '__main__':
    analyze(DATA_PATH)
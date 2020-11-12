import datetime
import pandas as pd
import os

def main(file_path: str):
    df = pd.read_csv(os.path.abspath(file_path), header=0, engine='python', keep_default_na=False)
    data = df.to_dict('records')

    new_data = []
    for row in data:
        fixed_dates = list(filter(lambda date: len(date) > 0, row['date'].split(",")))
        num_dates_autoassign = int(row['Frequency']) - len(fixed_dates)
        if num_dates_autoassign < 0:
            raise ValueError("Invalid data in row ", row)
        chat_index = 0
        # place fixed dates first
        for date in fixed_dates:
            new_data.append({
                'id': row['senior_executive'] + str(chat_index),
                'senior_executive': row['senior_executive'],
                'type': row['chat_type'],
                'description': row['description'],
                'tags' : row['tags'].split(","),
                #'credits' : row['credits'], ### Hard coded it rn, has to be changed depending on the chat_type
                'end_date': (datetime.strptime(date, '%Y/%m/%d') - datetime(2020, 1, 1)).days, 
                'date': datetime.strptime(date, '%Y/%m/%d') ## For fixed date, date and end_date are same
            })
            chat_index += 1
        # assign dates spaced out 365/num_dates_autoassign
        date_idx = 1 # Assuming launching on start of 2021
        space_interval = 365 // num_dates_autoassign
        while date_idx < num_dates_autoassign + 1:
            new_data.append({
                'id': row['senior_executive'] + str(chat_index),
                'senior_executive': row['senior_executive'],
                'type': row['chat_type'],
                'end_date': date_idx * space_interval,
                'tags' : row['tags'].split(","),
                'description': row['description'],
                #'credits' : row['credits'], ### Hard coded it rn, has to be changed depending on the chat_type
            })
            chat_index += 1
            date_idx += 1


if __name__ == "__main__":
    import pdb

    file_path = '../scheduler/sample/data_clean.csv'
    main(file_path)
    exit(0)

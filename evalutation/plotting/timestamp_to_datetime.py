import datetime
import pandas as pd

data = pd.read_csv('missing_frames.csv')

data['datetime'] = data['s_clock'].apply(lambda x : datetime.datetime.fromtimestamp(int(x)))
data.to_csv('missing_frames_with_datetime.csv', index=False)
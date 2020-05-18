import pandas as pd

command_intensity_times = pd.read_csv('command_intensity_times.csv')
logger_times_intensity = pd.read_csv('logger_times_intensity.csv')

'''
Find difference in time between a command and when it is actuated
'''
to_df = pd.DataFrame(data = {'CommandTime' : [], 'DeviceTime' : [], 'LogTime' : [], 'Value' : []})
last_value = 101
for index, row in command_intensity_times.iterrows():
    command_time = row['After']
    command_value = row['Value']
    if command_value != last_value:
        last_value = command_value
    else:
        continue
    time_filter = logger_times_intensity[logger_times_intensity['LoggerBefore'] >= command_time]
    result = time_filter[time_filter['Intensity'] == command_value]
    if len(result) == 0:
        continue
    # TODO: time when e.g. if intensity = 100, then light > 1
    result_value = result.iloc[0]
    log_time = result_value[0]
    device_time = result_value[1]
    to_df = to_df.append({'CommandTime' : command_time, 'DeviceTime' : device_time, 'LogTime' : log_time, 'Value' : command_value}, ignore_index=True)
    #print(log_time)

to_df.to_csv('intensity_delays.csv', index=False)
import pandas as pd

command_times_setpoint = pd.read_csv('command_times_setpoint.csv')
logger_times_setpoint = pd.read_csv('logger_times_setpoint.csv')

'''
Find difference in time between a setpoint and when the light level is reached 
TODO: include last setpoint, so we can find the time for different lengths (e.g. when changing setpoint from 0 to 4, how long does it take? compared to 1 to 2)
'''
to_df = pd.DataFrame(data = {'CommandTime' : [], 'DeviceTime' : [], 'LogTime' : [], 'Value' : []})
last_value = 101
for index, row in command_times_setpoint.iterrows():
    command_time = row['After']
    command_value = row['Value']
    if command_value != last_value:
        last_value = command_value
    else:
        continue
    time_filter = logger_times_setpoint[logger_times_setpoint['LoggerBefore'] >= command_time]
    result = time_filter[time_filter['Light'] == command_value]
    if len(result) == 0:
        continue
    result_value = result.iloc[0]
    log_time = result_value[0]
    device_time = result_value[1]
    to_df = to_df.append({'CommandTime' : command_time, 'DeviceTime' : device_time, 'LogTime' : log_time, 'Value' : command_value}, ignore_index=True)
    #print(log_time)

to_df.to_csv('setpoint_delays.csv', index=False)
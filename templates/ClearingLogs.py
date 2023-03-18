import datetime
import os
import sys
# calculate the date 11 days ago
eleven_days_ago = datetime.datetime.now() - datetime.timedelta(days=11)
# format the date as a string
date_str = eleven_days_ago.strftime('%d/%m/%Y')
# create the target line to search for in the log file
target_line = f'--- Start Execution Time : {date_str}'

# open the log file
with open(str(sys.argv[1]), 'r') as file:
    # find the target line
    for line in file:
        if target_line in line:
            break
    else:
        print(f"Target line '{target_line}' not found in file")
        exit()

    # create a temporary file with the lines after the target line
    with open('temp.txt', 'w') as temp_file:
        for line in file:
            temp_file.write(line)

# overwrite the original file with the contents of the temporary file
os.replace('temp.txt', str(sys.argv[1]))


# open the file for reading
with open( str(sys.argv[1]), 'r') as f:
    contents = f.read()

# prepend the new line
new_line = f'--- Start Execution Time : {date_str} ---'
new_contents = new_line + contents

# write the updated contents back to the file
with open( str(sys.argv[1]), 'w') as f:
    f.write(new_contents)

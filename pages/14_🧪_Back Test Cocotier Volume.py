from utilities.bdd_communication import *
from utilities.Functionnalities import *
import warnings
warnings.filterwarnings("ignore")
from ProjectSettings import  *

st.set_page_config(
    page_title= page_title,
    page_icon= page_icon,
)

st.title(page_title)


st.title("Back Test Cocotier Volume")

#Entries todo
dateObservation = 24
nbPool = 6
star_time = "2021-08-08"
hour = "00:00:00"
ending_time = "2021-08-11"
ennDate = f"{ending_time} {hour}"
sttDate = f"{star_time} {hour}"
start_date = datetime.strptime(sttDate, "%Y-%m-%d %H:%M:%S")
end_date = datetime.strptime(ennDate, "%Y-%m-%d %H:%M:%S")

current_date = start_date
# Define the maximum number of threads
MAX_THREADS = 10

# Semaphore to control the concurrency
semaphore = threading.Semaphore(MAX_THREADS)
command = 'node database/dl_for_quick_analysis.js'
# command = 'pwd'
path = "database/quick_analysis"

# 1] Data Collection
#variables
data = {'current_date': pd.to_datetime(['2020-01-02']),
        'pool': [['BNB', 'ATD', 'ACC']]}
dff = pd.DataFrame(data)
dff.set_index('current_date', inplace=True)
dff.drop(dff.index, inplace=True)
### Download all the OHLCV
def downloadingDate(current_date):
    # Acquire the semaphore
    semaphore.acquire()

    execute_terminal_command2(command, current_date.strftime("%Y-%m-%d"), hour)
    remove_non_csv_files(path)

    # Release the semaphore
    semaphore.release()

def get_historical_klines(x,deltahour,sttDate,ennDate):
    # Open the CSV file
    file_path = f"./database/quick_analysis/{x}.csv"
    df = pd.read_csv(file_path)

    # Convert sttDate and ennDate to datetime objects
    stt_date = pd.to_datetime(sttDate, format="%Y-%m-%d %H:%M:%S")
    enn_date = pd.to_datetime(ennDate, format="%Y-%m-%d %H:%M:%S")

    # Convert the 'date' column to datetime
    df['date'] = pd.to_datetime(df['date'], unit='ms')

    # Filter the dataframe based on the start and end dates
    mask = (df['date'] >= stt_date) & (df['date'] <= enn_date)
    filtered_df = df.loc[mask]

    # Extract the delta hour value from the string (e.g., '2h', '4h')
    delta_hours = int(re.findall(r'\d+', deltahour)[0])

    # Create a time range at delta hour intervals
    time_range = pd.date_range(stt_date, enn_date, freq=f'{delta_hours}H')

    # Filter the dataframe to keep only the rows at delta hour intervals
    filtered_df = filtered_df[filtered_df['date'].isin(time_range)]

    # Create a new dataframe with the desired columns
    new_df = filtered_df[['date', 'open', 'close']].copy()
    new_df.columns = ['timestamp', f'{x.lower()}_open', f'{x.lower()}_close']

    return new_df

def cocotier(combination,combo):
    semaphore.acquire()
    crypto = {}
    x = ""
    for elm in combination[0][1] :
        try :
            x = elm.replace("'","")
            try :
                crypto[x] = get_historical_klines(x,combination[1],sttDate,ennDate)
            except :
                x = x+'-USDT'
                crypto[x] = get_historical_klines(x,combination[1],sttDate,ennDate)
            crypto[x] = crypto[x].astype({x.lower()+ '_open': 'float64',x.lower()+ '_close': 'float64'})
            crypto[x] = crypto[x].set_index('timestamp')
        except Exception as ll:
            print(f"{ll}\n{x}!")
            traceback.format_exc()
    try :
        array_mauvais_shape = detection_mauvais_shape(crypto)
        # crypto = correction_shape(crypto, array_mauvais_shape)
        # for elm in array_mauvais_shape:
        #     crypto[elm]['timestamp'] = generation_date(crypto[elm], int(delta_hour[:1]))
        #     crypto[elm] = crypto[elm].set_index('timestamp')
        for i in array_mauvais_shape:
            del crypto[i]
        crypto = variationN(crypto, combination[2])
        crypto = coeffMulti(crypto)
        crypto = mergeCryptoTogether(crypto)
        crypto, maxis = botMax(crypto)
        crypto = botMaxVariation2(crypto, maxis)
        crypto = coeffMultiBotMax(crypto)
        coefMulti = coefmultiFinal(crypto)
        combination.append(coefMulti.tail(1).iloc[-1,-1])
    except Exception as ll:
        print(f"{ll}\n")
    semaphore.release()

def getData(progressText):
    progressText.text("Downloading")
    current_date = start_date
    try:
        shutil.rmtree(path)
    except:
        pass
    threads = []
    while current_date <= end_date:
        progressText.text(current_date)
        # thread = threading.Thread(target=downloadingDate, args=(current_date,))
        # thread.start()
        # threads.append(thread)
        downloadingDate(current_date)
        current_date += timedelta(days=1)

    # Wait for all threads to finish
    # for thread in threads:
    #     thread.join()
    progressText.text("Process is done!")

    ### Extraire all the pair names
    pair_names = []

    # Get the list of file names in the directory
    file_names = os.listdir(path)
    progressText.text("Extracting pair names")
    # Process each file name
    for file_name in file_names:
        # Extract the pair name before the '$' character
        pair_name = file_name.split('$')[0]

        # Add the pair name to the list if it's not already present
        if pair_name not in pair_names:
            pair_names.append(pair_name)

    ### Create the csv files for all the dates
    progressText.text("Create the csv files for all the dates")
    pair_data = {}
    # Process each file name
    for file_name in file_names:
        # Extract the pair name before the '$' character
        pair_name = file_name.split('$')[0]

        # Check if the pair name is already in the dictionary
        if pair_name in pair_data:
            pair_data[pair_name].append(file_name)
        else:
            pair_data[pair_name] = [file_name]

    progressText.text("Reformate the csv files")
    # Iterate over the pair names and their corresponding files
    for pair_name, files in pair_data.items():
        # Create a new file for the pair name
        output_file = os.path.join(path, f"{pair_name}.csv")

        # Open the output file in write mode
        with open(output_file, 'w', newline='') as csv_out:
            writer = csv.writer(csv_out)

            # Write the header to the output file
            writer.writerow(['date', 'open', 'high', 'low', 'close', 'volume'])

            # Iterate over the files for the pair name
            for file in files:
                # Open each input file
                with open(os.path.join(path, file), 'r') as csv_in:
                    reader = csv.reader(csv_in)
                    next(reader)  # Skip the header row

                    # Write the data rows to the output file
                    writer.writerows(reader)

    ### Remove rest of csv files
    progressText.text("Remove the rest of the csv files")
    # Iterate over the file names
    for file_name in file_names:
        # Check if the file name contains the '$' character
        if '$' in file_name:
            # Create the file path
            file_path = os.path.join(path, file_name)

            # Remove the file
            os.remove(file_path)

    ### Remove redudancy in the csv files
    progressText.text("Remove redundancy in the newer csv files")
    # Get the list of file names in the directory
    file_names = os.listdir(path)

    # Iterate over the file names
    for file_name in file_names:
        # Create the file path
        file_path = os.path.join(path, file_name)

        # Read the contents of the file
        with open(file_path, 'r') as file:
            lines = file.readlines()

        # Remove repeated rows and keep only the first occurrence
        unique_lines = []
        unique_set = set()
        for line in lines:
            if line not in unique_set:
                unique_lines.append(line)
                unique_set.add(line)

        # Write the unique lines back to the file
        with open(file_path, 'w') as file:
            file.writelines(unique_lines)
    # pools(progressText)

def pools(progressText):
    # 2] Data Preprocessing
    progressText.text("Starting Extracting")
    file_list = [f for f in listdir(path) if isfile(join(path, f))]
    df_list = {}
    for file in file_list:
        progressText.text(path+'/'+file)
        df_list[file[:-9]] = get_historical_from_path(path + "/" + file)
    # Convert the start and end times to datetime objects
    start = star_time
    # start = datetime.strptime(star_time, "%Y-%m-%d")
    end = ending_time
    # end = datetime.strptime(ending_time, "%Y-%m-%d")
    # Define the timedelta for incrementing the date
    delta = timedelta(days=1)
    # Loop through the dates between start and end
    while start <= end:
        current_date = start.strftime("%Y-%m-%d")
        progressText.text(current_date)
        # Filter the dataframes to keep only the specific date
        filtered_dataframes = {}
        for key, df in df_list.items():
            filtered_df = df.loc[df.index.date == pd.to_datetime(start).date()]
            filtered_dataframes[key] = filtered_df
        df_metric = get_analyisis_from_window(filtered_dataframes, dateObservation).sort_values(by="volume_evolution",
                                                                                                ascending=False)
        dfVe = df_metric.iloc[:nbPool]
        market = list(dfVe.index)
        dff.loc[datetime.strptime(current_date, "%Y-%m-%d")] = [list(dfVe['volume_evolution'].index)]
        start += delta

    ### Save the Pools By day dataframe
    dff.to_csv('./database/pools.csv', header=False)
    st.dataframe(dff)
    progressText.text("Pool Saved")
    # finish(progressText)

def finish(progressText):
    # 3] Generate All Combinations
    progressText.text("Generate All combinations")

    crypto = {}
    deltaHours = ["2h","4h","8h","12h"]
    Ni = ["N","N-1","N-2"]
    array1 = []
    with open('database/pools.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            timestamp = row[0]
            elements = row[1].strip('[]').split(', ')
            array1.append((timestamp, elements))
    combinations = list(itertools.product(array1, deltaHours, Ni))
    combinations = [list(item) for item in combinations]

    # 4] Cocotier Process
    progressText.text("Cocotier Process")

    # Launch a thread for each iteration
    threads = []
    combinations = list(combinations)
    for combo,combination in enumerate(combinations):
        progressText.text(f"Cocotier Process Combiation N°{combo}")
        thread = threading.Thread(target=cocotier, args=(combination,combo))
        thread.start()
        threads.append(thread)


    # Wait for all threads to finish
    for thread in threads:
        thread.join()


    # 5] Presenting the First DataFrame
    progressText.text("First DataFrame")
    # Flatten the nested lists
    flat_data = []
    for combination in combinations:
        progressText.text(combination)
        datetime = combination[0][0]
        pool = combination[0][1]
        deltahour = combination[1]
        Ni = combination[2]
        BotMax = combination[3]
        flat_data.append([datetime, deltahour, Ni, BotMax, pool])

    df = pd.DataFrame(flat_data, columns=['datetime', 'deltahour', 'Ni', 'BotMax','pool'])
    st.dataframe(df)
    # 6] Produit Cumulée and final Dataframe
    progressText.text("Produit cumulé")
    # Convert 'datetime' column to datetime format
    df['datetime'] = pd.to_datetime(df['datetime'])

    # Group DataFrame by 'deltahour' and 'Ni', calculate product of 'BotMax'
    df_grouped = df.groupby(['deltahour', 'Ni']).agg({'datetime': ['min', 'max'], 'BotMax': 'prod'}).reset_index()

    # Rename columns
    df_grouped.columns = ['deltahour', 'Ni', 'startDate', 'endingDate', 'BotMax']

    # Convert 'startDate' and 'endingDate' columns to desired format
    df_grouped['startDate'] = df_grouped['startDate'].dt.strftime('%Y-%m-%d %H:%M:%S')
    df_grouped['endingDate'] = df_grouped['endingDate'].dt.strftime('%Y-%m-%d %H:%M:%S')


    st.dataframe(df_grouped)
    progressText.text("")

def main():
    st.text("In this Section, you can store the data in the local database, \nand just run the script on"
            "these data to gain time. \nBut also you can download from the first")
    st.markdown(
        "<span style='color:red'>It's important to know that downloading phase needs <b>time</b> \nand excellent <b>internet connection</b></span>",
        unsafe_allow_html=True)
    st.markdown(
        "<span style='color:yellow'>When you select the current date, it's not sure it will work, because it's not finished yet!</b></span>",
        unsafe_allow_html=True)
    date_init = datetime.now() - timedelta(days=10)
    # Entries
    global dateObservation
    dateObservation = st.number_input("Date D'observation", min_value=0, max_value=24, step=1, value=24)
    global nbPool
    nbPool = st.number_input("Nombre de Pool", step=1, value=6)
    global star_time
    star_time = st.date_input('date de début', date_init)
    global hour
    hour = st.time_input("Time", time(0, 0))
    global ending_time
    ending_time = st.date_input('date de fin', datetime.now() - timedelta(days=1))
    global ennDate
    ennDate = f"{ending_time} {hour}"
    global sttDate
    sttDate = f"{star_time} {hour}"
    global start_date
    start_date = datetime.strptime(sttDate, "%Y-%m-%d %H:%M:%S")
    global end_date
    end_date = datetime.strptime(ennDate, "%Y-%m-%d %H:%M:%S")
    progressText = st.text("")
    try:
        install_package_if_needed("ccxt")
        install_package_if_needed("csv-writer")
    except Exception as e:
        print("Error occurred please contact Administrator Mahdi")
        print(e)

    # Download button
    download_button_placeholder = st.empty()
    if download_button_placeholder.button("Download and Finish processing"):
        # Replace all the buttons with empty placeholders
        download_button_placeholder.empty()
        extract_button_placeholder = st.empty()
        finish_button_placeholder = st.empty()

        getData(progressText)

    # Extract Pools button
    extract_button_placeholder = st.empty()
    if extract_button_placeholder.button("Extract Pools"):
        # Replace all the buttons with empty placeholders
        download_button_placeholder.empty()
        extract_button_placeholder.empty()
        finish_button_placeholder = st.empty()

        pools(progressText)

    # Finish Processing button
    finish_button_placeholder = st.empty()
    if finish_button_placeholder.button("Finish Processing With the latest stored Data"):
        # Replace all the buttons with empty placeholders
        download_button_placeholder.empty()
        extract_button_placeholder.empty()
        finish_button_placeholder.empty()

        finish(progressText)

if __name__ == '__main__':
    main()

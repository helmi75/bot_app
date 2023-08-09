import streamlit

from utilities.bdd_communication import *
from utilities.Functionnalities import *
import plotly.express as px
import warnings

warnings.filterwarnings("ignore")
from ProjectSettings import *

st.set_page_config(
    page_title=page_title,
    page_icon=page_icon,
)

st.title(page_title)

st.title("Back Test Cocotier Volume")

dateObservation = 24
nbPool = 6
star_time = "2021-08-08"
hour = "00:00:00"
ending_time = "2021-08-11"
ennDate = f"{ending_time} {hour}"
sttDate = f"{star_time} {hour}"
date_format = "%Y-%m-%d %H:%M:%S"
start_date = datetime.strptime(sttDate, date_format)
end_date = datetime.strptime(ennDate, date_format)
start_date_prime = start_date-timedelta(days=2) - timedelta(hours=1000)
stttDAte = start_date_prime.strftime(date_format)
current_date = start_date_prime
newerBotMax = 1.000
visualisedData = []
N = "N-1"
delta = "4h"
array1 = []
# Define the maximum number of threads
MAX_THREADS = 10

# Semaphore to control the concurrency
semaphore = threading.Semaphore(MAX_THREADS)
command = 'node database/dl_for_quick_analysis.js'
# command = 'pwd'
path = "database/quick_analysis"

# 1] Data Collection
# variables
data = {'current_date': pd.to_datetime(['2020-01-02']),
        'pool': [['BNB', 'ATD', 'ACC']]}
dff = pd.DataFrame(data)
dff.set_index('current_date', inplace=True)
dff.drop(dff.index, inplace=True)


#todo mahdi rahou el mochekel met download, mana3refech 3lech el date elli 9bal el date elli n7ebou 3liha matetsabech

### Download all the OHLCV
def downloadingDate(current_date):
    # Acquire the semaphore
    semaphore.acquire()

    execute_terminal_command2(command, current_date.strftime("%Y-%m-%d"), hour)
    remove_non_csv_files(path)

    # Release the semaphore
    semaphore.release()


def get_historical_klines(x, deltahour, sttDate, ennDate):
    # Open the CSV file
    file_path = f"./database/quick_analysis/{x}.csv"
    df = pd.read_csv(file_path)

    # Convert sttDate and ennDate to datetime objects
    stt_date = pd.to_datetime(sttDate, format=date_format)
    enn_date = pd.to_datetime(ennDate, format=date_format)

    # Convert the 'date' column to datetime
    df['date'] = pd.to_datetime(df['date'], unit='ms')

    # Use .loc to filter the dataframe based on the start and end dates
    filtered_df = df.loc[(df['date'] >= stt_date) & (df['date'] <= enn_date)]

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



def findPreviousBotMax(combination, combinations):
    target_2h = combination[1]  # Get the '2h' value from the current combination
    target_N = combination[2]  # Get the 'N' value from the current combination
    current_date = combination[0][0]  # Get the date from the current combination
    prev_datee = datetime.strptime(current_date, date_format) - timedelta(days=1)
    for i in range(len(combinations) - 1, -1, -1):
        prev_combination = combinations[i]
        prev_2h = prev_combination[1]  # Get the '2h' value from the previous combination
        prev_N = prev_combination[2]  # Get the 'N' value from the previous combination
        prev_date = datetime.strptime(prev_combination[0][0], date_format)  # Get the date from the previous combination

        if prev_2h == target_2h and prev_N == target_N and prev_date == prev_datee:
            return prev_combination[-1]  # Return the last element of the previous combination

    return 1  # Return None if no previous value is found


def cocotier(combination, combo, previous, stt, enn):
    semaphore.acquire()
    crypto = {}
    x = ""
    for elm in combination[0][1]:
        try:
            x = elm.replace("'", "")
            try:
                crypto[x] = get_historical_klines(x, combination[1], stt, enn)
            except:
                x = x + '-USDT'
                crypto[x] = get_historical_klines(x, combination[1], stt, enn)
            crypto[x] = crypto[x].astype({x.lower() + '_open': 'float64', x.lower() + '_close': 'float64'})
            crypto[x] = crypto[x].set_index('timestamp')
        except Exception as ll:
            st.error("Please ReDownload the Data, it hasn't been all downloaded")
            print(f"cocotierException1\n{ll}\n{x}!")
            traceback.format_exc()
    try:
        array_mauvais_shape = detection_mauvais_shape(crypto)
        for i in array_mauvais_shape:
            del crypto[i]
        for cr in crypto:
            c = cr.lower()
            lastvalue = crypto[cr].iloc[-1, crypto[cr].columns.get_loc(c + "_close")]
            crypto[cr][c + "_close"] = crypto[cr][c + "_open"].shift(-1)
            crypto[cr].iloc[-1, crypto[cr].columns.get_loc(c + "_close")] = lastvalue
            # print(crypto[cr][c+"_close"])
        crypto = variationN(crypto, combination[2])
        crypto = coeffMulti(crypto)
        crypto = mergeCryptoTogether(crypto)
        crypto, maxis = botMax(crypto)
        crypto = botMaxVariation2(crypto, maxis)
        crypto = coeffMultiBotMax(crypto, initialValue=previous)
        coefMulti = coefmultiFinal(crypto)
        combination.append(coefMulti.tail(1).iloc[-1, -1])
    except Exception as ll:
        st.error(f"Please verify the Downloaded Data, redo it if it's necessary! {ll}")
        print(f"cocotierException1\n{ll}\n")
    semaphore.release()


def cocotierSingle(pool, delta, N, sttDate, ennDate):
    global newerBotMax
    global visualisedData
    crypto = {}
    x = ""
    for elm in pool:
        try:
            x = elm.replace("'", "")
            try:
                crypto[x] = get_historical_klines(x, delta, sttDate, ennDate)
            except:
                x = x + '-USDT'
                crypto[x] = get_historical_klines(x, delta, sttDate, ennDate)
            crypto[x] = crypto[x].astype({x.lower() + '_open': 'float64', x.lower() + '_close': 'float64'})
            crypto[x] = crypto[x].set_index('timestamp')
        except Exception as ll:
            print(f"cocotierSingleException1\n{ll}\n{x}!")
            traceback.format_exc()
    try:
        array_mauvais_shape = detection_mauvais_shape(crypto)
        for i in array_mauvais_shape:
            del crypto[i]
        for cr in crypto:
            c = cr.lower()
            lastvalue = crypto[cr].iloc[-1, crypto[cr].columns.get_loc(c + "_close")]
            crypto[cr][c + "_close"] = crypto[cr][c + "_open"].shift(-1)
            crypto[cr].iloc[-1, crypto[cr].columns.get_loc(c + "_close")] = lastvalue
        crypto = variationN(crypto, N)
        crypto = coeffMulti(crypto)
        crypto = mergeCryptoTogether(crypto)
        crypto, maxis = botMax(crypto)
        crrrr = crypto
        crypto = botMaxVariation2(crypto, maxis)
        crypto = coeffMultiBotMax(crypto, initialValue=newerBotMax)
        st.dataframe(crypto)
        coefMulti = coefmultiFinal(crypto)
        for i, j in enumerate(crrrr.index):
            newerBotMax = coefMulti.iloc[i, -1]
            st.text(f"{j}\t{pool[maxis[i]]}\t{newerBotMax}")
            visualisedData.append({"date": j, "crypto": pool[maxis[i]], "BotMax": newerBotMax})

    except Exception as ll:
        st.error(f"cocotierSingleException2\n{ll}\n")


def getData(progressText):
    progressText.text("Downloading")
    current_date = start_date_prime
    try:
        shutil.rmtree(path)
    except:
        pass
    threads = []
    while current_date <= end_date:
        percentage = (current_date - start_date_prime) / (end_date - start_date_prime) * 100
        progressText.text(f"The percentage is: {percentage:.2f}%")
        # thread = threading.Thread(target=downloadingDate, args=(current_date,))
        # thread.start()
        # threads.append(thread)
        downloadingDate(current_date)
        current_date += timedelta(hours=1000)

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
        if '$' in file_name or file_name.endswith(":USDT.csv"):
            # Create the file path
            file_path = os.path.join(path, file_name)
            # Remove the file
            os.remove(file_path)
    file_names = os.listdir(path)
    for file_name in file_names:
        # Check if the file name contains the '$' character
        if file_name.endswith(":USDT.csv"):
            file_path = os.path.join(path, file_name)

            # print(file_path)
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
        progressText.text(path + '/' + file)
        df_list[file[:-9]] = get_historical_from_path(path + "/" + file)
    # Convert the start and end times to datetime objects
    start = start_date
    # start = datetime.strptime(star_time, "%Y-%m-%d")
    # Define the timedelta for incrementing the date
    delta = timedelta(days=1)
    # Loop through the dates between start and end
    while start <= end_date:
        previous_date = start - timedelta(hours=1000)
        current_date = start.strftime(date_format)
        progressText.text(current_date)
        # Filter the dataframes to keep only the specific date
        filtered_dataframes = {}
        for key, df in df_list.items():
            # filtered_df = df.loc[df.index >= previous_date]
            filtered_df = df.loc[(df.index >= previous_date) & (df.index <= start)]
            # filtered_df = df.loc[df.index.date == pd.to_datetime(start).date()]
            filtered_dataframes[key] = filtered_df
        df_metric = get_analyisis_from_window(filtered_dataframes, dateObservation).sort_values(by="volume_evolution",
                                                                                                ascending=False)
        st.text(current_date)
        st.dataframe(df_metric.iloc[:, 0:3])
        dfVe = df_metric.iloc[:nbPool]
        market = list(dfVe.index)
        dff.loc[datetime.strptime(current_date, date_format)] = [list(dfVe['volume_evolution'].index)]
        start += delta

    ### Save the Pools By day dataframe
    dff.to_csv('./database/pools.csv', header=False, date_format=date_format)
    st.dataframe(dff)
    progressText.text("Pool Saved")
    # finish(progressText)


def finish(progressText):
    global array1
    array1 = []
    # 3] Generate All Combinations
    progressText.text("Generate All combinations")

    crypto = {}
    deltaHours = ["2h", "4h", "8h", "12h"]
    Ni = ["N", "N-1", "N-2"]

    with open('database/pools.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            timestamp = row[0]
            elements = row[1].strip('[]').split(', ')
            array1.append((timestamp, elements))
    combinations = list(itertools.product(array1, deltaHours, Ni))
    combinations = [list(item) for item in combinations]
    combinations = [item for item in combinations if item[0][0] != ennDate]

    # 4] Cocotier Process
    progressText.text("Cocotier Process")

    # Launch a thread for each iteration
    # threads = []
    combinations = list(combinations)
    for combo, combination in enumerate(combinations):
        progressText.text(f"Cocotier Process {((combo / len(combinations)) * 100):.2f}%")
        previouslyBot = findPreviousBotMax(combination, combinations)
        # thread = threading.Thread(target=cocotier, args=(combination, combo,previouslyBot))
        from datetime import datetime, timedelta
        if ennDate != combination[0][0]:
            nexDate = ((datetime.strptime(combination[0][0], date_format)) + timedelta(days=1)- timedelta(
                hours=int(delta.replace('h', '')))- timedelta(
                hours=int(delta.replace('h', '')))).strftime(date_format)
            nowDate = (datetime.strptime(combination[0][0], date_format) - timedelta(hours=int(combination[1].replace('h','')))).strftime(date_format)
            # nexDate = ((datetime.strptime(combination[0][0], date_format)) + timedelta(days=1)).strftime(date_format)
            # nowDate = (datetime.strptime(combination[0][0], date_format) + timedelta(hours=int(combination[1].replace('h','')))).strftime(date_format)
            try :
                cocotier(combination, combo, previouslyBot, nowDate , nexDate)
            except:
                st.error(f"{nexDate} is not downloaded yet")
        # thread.start()
        # threads.append(thread)

    # # Wait for all threads to finish
    # for thread in threads:
    #     thread.join()

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

    df = pd.DataFrame(flat_data, columns=['datetime', 'deltahour', 'Ni', 'BotMax', 'pool'])
    st.dataframe(df)
    # 6] Produit Cumulée and final Dataframe
    progressText.text("Produit cumulé")
    # Convert 'datetime' column to datetime format
    df['datetime'] = pd.to_datetime(df['datetime'])

    # Group DataFrame by 'deltahour' and 'Ni', calculate product of 'BotMax'
    df_grouped = df.groupby(['deltahour', 'Ni']).agg({'datetime': ['min', 'max'], 'BotMax': 'last'}).reset_index()

    # Rename columns
    df_grouped.columns = ['deltahour', 'Ni', 'startDate', 'endingDate', 'BotMax']

    # Convert 'startDate' and 'endingDate' columns to desired format
    df_grouped['startDate'] = df_grouped['startDate'].dt.strftime(date_format)
    df_grouped['endingDate'] = df_grouped['endingDate'].dt.strftime(date_format)

    st.dataframe(df_grouped)
    progressText.text("")
    # Assuming your DataFrame is named 'df_grouped'
    df_grouped['deltahour_Ni'] = df_grouped['deltahour'] + ' ' + df_grouped['Ni']

    # Find the maximum BotMax value
    max_botmax = df_grouped['BotMax'].max()
    max_row = df_grouped.loc[df_grouped['BotMax'] == max_botmax, ['deltahour', 'Ni']]
    max_deltahour = max_row['deltahour'].values[0]
    max_Ni = max_row['Ni'].values[0]
    # Create a new column for color
    df_grouped['color'] = ['MaxValue' if x == max_botmax else 'Normal' for x in df_grouped['BotMax']]

    fig = px.histogram(df_grouped, x='deltahour_Ni', y='BotMax', color='color',
                       color_discrete_map={'MaxValue': 'blue', 'Normal': 'lightgray'})

    fig.update_layout(
        yaxis_title="BotMax"
    )

    # Display the plot using Streamlit
    st.plotly_chart(fig)
    return max_deltahour, max_Ni

def verif(delta, Ni):
    global visualisedData
    st.markdown(f"<h2 style='color:red'>-> Cocotier [{delta}/{Ni}]</h2>", unsafe_allow_html=True)
    st.subheader(f"From {start_date} to {end_date}")
    for i, j in enumerate(array1):
        pool = [item.replace("'", "") for item in j[1]]
        st.text("-------------------------------------")
        datea = ((datetime.strptime(j[0], date_format))- timedelta(
                hours=int(delta.replace('h', '')))).strftime(date_format)
        st.text(f"// Date: {datea} \t Pool : {pool}")
        if ennDate != datea:
            # nexDate = ((datetime.strptime(j[0], date_format)) + timedelta(days=1)).strftime(date_format)
            # nowDate = (datetime.strptime(j[0], date_format) + timedelta(
            #     hours=int(delta.replace('h', '')))).strftime(date_format)
            nexDate = ((datetime.strptime(datea, date_format)) + timedelta(days=1)- timedelta(
                hours=int(delta.replace('h', '')))).strftime(date_format)
            nowDate = (datetime.strptime(datea, date_format)).strftime(date_format)
            try :
                cocotierSingle(pool, delta, Ni, nowDate, nexDate)
            except:
                st.error(f"{nexDate} is not downloaded yet")
    # st.text(visualisedData) here to display the chart graphic for helmi
    # Extract x and y values from the data
    # Extract the x and y values
    x = [entry['date'] for entry in visualisedData]
    y = [entry['BotMax'] for entry in visualisedData]

    # Create the scatter plot
    fig = go.Figure(data=go.Scatter(x=x, y=y, mode='lines'))

    # Set the graph title and axis labels
    fig.update_layout(title='BotMax Value Over Time', xaxis_title='Date', yaxis_title='BotMax Value')

    # Add annotations for each crypto symbol
    annotations = [dict(x=x_val, y=y_val, text=crypto, showarrow=True, arrowhead=1) for x_val, y_val, crypto in
                   zip(x, y, [entry['crypto'] for entry in visualisedData])]
    fig.update_layout(annotations=annotations)

    # Display the graph in Streamlit
    st.plotly_chart(fig)
    visualisedData = []


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
    date_fini = datetime.now() - timedelta(days=1)
    hourring = 0
    minuting = 0
    try :
        with open('./database/pools.csv', "r") as csvfile:
            reader = csv.reader(csvfile)
            dates = [datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S") for row in reader]
            date_init = min(dates)
            date_fini = max(dates)
            hourring = date_init.hour
            minuting = date_init.minute
            st.markdown(
                f"<div style = 'border:1px solid red'><span style='color:green; font-size:150%' >The last saved data is from <span style='color:blue; font-size:160%'>{date_init}</span> to <span style='color:blue; font-size:160%'>{date_fini}</span>\nYou can proceed the Cocotier process without Downloading or extracting the pools!\n"
                f"<br><span style='color:yellow'>Please verify the dates you're working on it, and correct the time.</span></span></div><br><br>",
                unsafe_allow_html=True)
    except:
        pass
    # Entries
    global dateObservation
    dateObservation = st.number_input("Date D'observation", min_value=0, max_value=24, step=1, value=24)
    global nbPool
    nbPool = st.number_input("Nombre de Pool", step=1, value=6)
    global star_time
    star_time = st.date_input('date de début', date_init)
    global hour
    hour = st.time_input("Time", time(hourring, minuting))
    global ending_time
    ending_time = st.date_input('date de fin', date_fini)
    global ennDate
    ennDate = f"{ending_time} {hour}"
    global sttDate
    sttDate = f"{star_time} {hour}"
    global start_date
    start_date = datetime.strptime(sttDate, date_format)
    global end_date
    end_date = datetime.strptime(ennDate, date_format)
    global start_date_prime
    start_date_prime = start_date -timedelta(days=2) - timedelta(hours=1000)
    global stttDAte
    stttDAte = start_date_prime.strftime(date_format)
    global delta, N
    global newerBotMax
    newerBotMax = 1.000
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
    verification = False
    # Finish Processing button
    finish_button_placeholder = st.empty()
    if finish_button_placeholder.button("Finish Processing With the latest stored Data"):
        # Replace all the buttons with empty placeholders
        download_button_placeholder.empty()
        extract_button_placeholder.empty()
        finish_button_placeholder.empty()
        delta, N = finish(progressText)
        # if st.button("Verif with the best match"):
        newerBotMax = 1.0
        visualisedData = []
        verif(delta, N)
        # if st.button("8H/N-1"):
        newerBotMax = 1.0
        visualisedData = []
        verif("8h", "n-1")
        # if st.button("4H/N"):
        newerBotMax = 1.0
        visualisedData = []
        verif("4h", "n")


if __name__ == '__main__':
    main()

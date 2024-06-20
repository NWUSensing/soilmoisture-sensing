# Soil Moisture Sensing with UHF RFID tags

This repository explains the workflow and files of our soil moisture sensing system based on UHF RFID tags. Specifically, we design RFID moisture sensing tags that their signal features, such as received signal strength (RSS) and phase, change with the soil moisture levels. Additionally, we assign a reference tag to each moisture-sensing tag to mitigate environmental influences. That is to say, we design our RFID moisture sensor with a sensing tag and a reference tag. Finally, by measuring the differential RSS of the two tags, our sensor can estimates the soil moisture.

## Overview and Hardware Preparation
The below figure shows the hardware connections of our system:

![device](./data/device.png)

- Our RFID moisture sensors are wirelessly connected to a FU-M6-M-4G RFID reader.
- The reader is connected to a Raspberry Pi 4B via USB for controlling the reader and collecting RSS data.
- Based on the collected RSS data, the Raspberry Pi can estimate the moisture levels by using the code shown in this repository.
- To remotely access the Raspberry Pi, we connect a 4G LTE module to it. To use the 4G module, one needs to insert a local SIM card into it. Alternatively,  one can use a local Wi-Fi network for a short distance remote connection or test.


## Directory Structure
(1)	Reader controlling. Except for the `./moisture_estimation` directory, all other directories contain files used by the ThingMagic MercuryAPI to control the reader. Our code for controlling the reader is located in `./TMR_Read`, and by modifying the symbolic link file `ReadAsync.cs`, we can change the reader's behavior, such as the reading time on each channel  and TxPower.

(2)	Data collection, preprocessing and moisture estimation.
Regarding the `./moisture_estimation` directory, it includes all the code for processing reader data, as described below:

**./moisture_estimation/data** : This directory stores all the collected data. Each file contains the metadata collected at a specific tag location. For example, the below figure shows measurement of sensor 16 and 19.

![collect data](./data/collect_data.png)

Contents of `Data_8.txt`:

![collect data info](./data/Data_8.png)

**./process/detect.py**: This python code will show the detected tags. More details are in “step 5 of Quickstart” below.

**./process/predict.py**: This program estimates the soil moisture, and stores estimations in `./moisture_estimation/vwc_estimation.txt`. More details are in "step 6 of Quickstart" below.

**./process/tag.txt**:  The txt file stores the RFID moisture sensor ID information. For Example:

```text
tag1,0010,0011
tag2,0020,0021
tag3,0030,0031
tag4,0040,0041
tag5,0050,0051
tag6,0060,0061
tag7,0070,0071
tag8,0080,0081
tag9,0090,0091
...
```

The first column is the RFID sensor ID, each sensor includes two tags, the second column represents the sensing tag ID, and the third column indicates the reference tag ID. The tag ID consists of 4 digits in total, with the first three digits corresponding to the sensor ID. The last digit, '1', represents a sensing tag, while '0' represents a reference tag.

(3)	Others. 
Our code consists of two main parts: dotnet code for controlling the reader to perform tag reading, and python code with the environment already set up using venv. For dotnet environment configuration, please refer to `ReadMe_Linux_Install_CompileRun_Steps.txt`. To activate our virtual environment named "virtual" for python, simply use the command `source ./moisture_estimation/env/bin/activate`.

Recompile the modifiedx`ReadAsync.cs`:

`dotnet clean Samples/Codelets/ReadAsyncLinux/ReadAsyncLinux.csproj`

`dotnet build Samples/Codelets/ReadAsyncLinux/ReadAsyncLinux.csproj`

## Quickstart

1. **Power on the system.** Deploy the RFID reader and Raspberry Pi on UAV. Then, power on the RFID reader and Raspberry Pi.
2. **Remote Connection.** 
    We use VSCode's Remote SSH to connect remotely to the Raspberry Pi. If Visual Studio Code is not installed on laptop, please refer to [Connect over SSH with vscode](https://code.visualstudio.com/docs/remote/ssh-tutorial) for installation.
    Then, open VS code, connect the Raspberry Pi with a laptop using a 4G LTE remote connection or a local Wi-Fi Conection. Once the connection is on, open the `/home/user/Desktop/soilmoisture-sensing` directory in the Pi via VS Code.

    For 4G LTE: 
    ```bash
    // In China
    HostName 8.tcp.cpolar.cn
    Port 11167
    User user
    password: 12345678
    // In UK
    HostName 1.tcp.eu.cpolar.io
    Port 10054
    User user
    password: 12345678
    ```
    ![ssh connect](./data/remote_connet.gif)
    For local Wi-Fi: Ensure that the Raspberry Pi and laptop are connected to the same Wi-Fi, use `ssh user@GreenTag` to connect, and other operations are the same as using a 4G LTE. 


Check the drone for flight readiness,

3. **Check if the reader is working properly.** Place a test tag in front of the reader. Then, start the reader and redirect the output to nohup.out, keep the reader in a reading state until the end of the experiment, and activate the Python environment simultaneously.

    ```bash
    nohup Linux/ReadAsync tmr:///dev/ttyACM0 --ant 1,2 &
    source ./moisture_estimation/virtual/bin/activate
    ```

    Check the tag information that the reader has currently read, if we see the output in bash similar to the following figure, we know the reader is working properly.

    ```bash
    tail --line 40 nohup.out
    ```

    ![tail output](./data/nohupout.png)

4. **Data collection with UAV.** Pilot the drone to fly to the targeted RFID moisture sensors, which include a reference tag and a sensing tag.

    Make sure the measured tags are in front of the reader’s antenna within <0.5m or even less. Note that the reader’s data collection program runs in the background until the end of the experiment.

5. **Extract the data of our targeted RFID moisture sensors at each location.** 

    Run `detect.py`, and then our program will detect the sensor IDs that can be read. From these IDs, we can Extract and save the data of our targeted sensors at each location. For example, XXX


    Subsequently, the program will save the data read in the `./moisture_estimation/data` directory, specifically in the `Data_ID.txt` file. For example:

    ```bash
    python ./moisture_estimation/detect.py
    ```

    ![detect](./data/detect_and_predict.gif)

    ![detect result](./data/detect.png)

6. **moisture estimation.** By running the code below, one can estimate soil moisture of a targeted sensor. 

    ```bash
    python ./moisture_estimation/predict.py SensorID
    ```
    For example, `python ./moisture_estimation/predict.py 8`. Then, you will obtain the corresponding soil moisture estimation for the tags at the time when our predict.py is running, and the results will be saved in `./moisture_estimation/vwc_estimation.txt`. (As shown in the figure below, the two estimation values are from data received by two different antennas. The `NaN` value in the moisture estimation result is because the antenna did not receive complete data.)

    ![moisture estimation](./data/estimation.png)

7. Continue operating the drone to proceed to the next tag deployment location.

8. Stop reading after finishing measurements at all locations.
    ```bash
    ps aux | grep Read  # find reading process
    ---
    output like:
    user       52987 41.8  0.5 3338164 40336 pts/3   Sl   20:41   2:55 Linux/ReadAsync tmr:///dev/ttyACM0 --ant 1,2
    user       57278  0.0  0.0   6088  1920 pts/3    S+   20:48   0:00 grep --color=auto Read
    ---
    kill 52987  # kill process by process ID
    ```

9. **Offline Estimation.**

**Note**: if you want to change the in/out-put path and so on, please pay attention to lines 205, 206 in the predict.py and lines 8, 31, 56, 57, 69, 132 in the detect.py.

## Troubleshooting

1. `Error, catch2: Access to the port '/dev/ttyACM0' is denied.` in tail command. Possible reasons:
- The reader is not powered on.
- After finishing the reading, without using the kill command to terminate the reading process, the reader and Raspberry Pi were directly shutdown.

Solution: Restart the reader.

import time
import joblib
import sys
import numpy as np
import pandas as pd
from datetime import datetime

import warnings
warnings.filterwarnings("ignore")

def load_data(reader_data, ant_num, hygrometer_data=None, data_num=1, tag_list=None, tag_MRT_dict=None, offset=0, istest=True, readertype='ThingMagic'):
    # load train data
    def is_contains_all_frequencies(group, freq_list):
        return set(group["frequency"].unique()) == set(freq_list)
    raw_data = pd.read_csv(reader_data, header=None)  
    raw_data.columns = ['tagID', 'frequency', 'phase', 'RSSI', 'MRT1', 'MRT2', 'antenna', 'timestamp', 'indexID']
    # convert timestamp format
    if readertype == 'ThingMagic':
        time_format = " %d/%m/%Y %H:%M:%S"
        raw_data["timestamp"] = raw_data["timestamp"].apply(
            lambda x: int(datetime.strptime(x, time_format).timestamp() * 10 ** 6))  
        raw_data["frequency"] /= 1000
    raw_data = raw_data[raw_data["antenna"] == ant_num]
    raw_data["indexID"] = 1
    # grounped data by tagID, ie. ref and sensing
    groupedby_tagID = raw_data.groupby('tagID')
    tagID_grouped_data = {}  
    tagIDs = []
    for group_name, group_df in groupedby_tagID:
        tagID_grouped_data[group_name] = group_df
        tagIDs.append(group_name)
    tagIDs, tag_datas = match_sensing_ref_hygrometer(tagIDs, tagID_grouped_data, hygrometer_data, offset, istest=istest)  
    freq_list = [i * 0.25 + 920.625 for i in range(0, 16) ]  
    # 根据MRTID对数据进行分组，每一个MRTID对应一组数据，
    # 根据freq_num，选择特定数量的频率下的数据，从920.625开始；每个频率下选取data_num条数据
    for key in tagIDs:
        # Filter the data for each indexID, removing data from indexIDs with fewer than x entries. 
        # (Only for Impinj readers, excluding ThingMagic readers, due to the low read rates)
        sorted_grouped_size = tag_datas[key].groupby(["indexID", "frequency"]).size()  # .sort_values(ascending=True).index
        incomplete_data = sorted_grouped_size[sorted_grouped_size < 1].index
        incomplete_data_MRTID = [index for index in set([item[0] for item in incomplete_data])]
        mask_MRTID = tag_datas[key]["indexID"].isin(incomplete_data_MRTID)
        tag_datas[key] = tag_datas[key][~mask_MRTID].reset_index(drop=True)
        # Ensure that data on the desired channel is received.
        MRTID_freq_grouped_data = tag_datas[key].groupby(["indexID"])
        filtered_groups = MRTID_freq_grouped_data.filter(lambda x : is_contains_all_frequencies(x, freq_list))
        tag_datas[key] = filtered_groups.reset_index(drop=True)
        tag_datas[key] = tag_datas[key].groupby(['indexID', 'frequency']).apply(
            lambda x: x.sample(n=data_num)).apply(lambda group: group).reset_index(drop=True)  
        reorganized_MRTID = np.array([[i] * 16 * data_num for i in range(0, len(tag_datas[key])//(data_num * 16))]).flatten()
        tag_datas[key]["indexID"] = reorganized_MRTID

    if len(tagIDs) > 0:
        return tag_datas[tagIDs[0]]
    return pd.DataFrame()


def match_sensing_ref_hygrometer(tags, tagID_grouped_data, hygrometer_name, offset, istest=True):
    # Matching data from sensing tags, reference tags, and hygrometers based on timestamps.
    if not istest:
        hygrometer_data = load_hygrometer_data(hygrometer_name)  
        hygrometer_data["timestamp"] = hygrometer_data["timestamp"] + offset; 
    loaded_datas = {}
    for i in range(len(tags)//2):
        tagID_grouped_data[tags[i]] = tagID_grouped_data[tags[i]].drop(columns=[f"MRT{i}" for i in range(1, len(tags) + 1)] + ["indexID"])
        tagID_grouped_data[tags[i]] = tagID_grouped_data[tags[i]].rename(columns={"timestamp": "timestamp1",
                                                                                  "tagID": "tagID1",
                                                                                  "phase": "phase1",
                                                                                  "RSSI": "RSSI1",
                                                                                  "frequency": "frequency1",
                                                                                  })
        tagID_grouped_data[tags[len(tags)//2 + i]] = tagID_grouped_data[tags[len(tags)//2 + i]].rename(columns={"timestamp": "timestamp2",
                                                                                                                "tagID": "tagID2",
                                                                                                                "phase": "phase2",
                                                                                                                "RSSI": "RSSI2",
                                                                                                                "frequency": "frequency2"})
        sensing_and_ref = pd.merge_asof(tagID_grouped_data[tags[i]].sort_values("frequency1"),
                                       tagID_grouped_data[tags[len(tags)//2 + i]].sort_values("frequency2"),
                                       left_on="frequency1", right_on="frequency2", direction="nearest")  
        if not istest:  
            matched_data = pd.merge_asof(sensing_and_ref.sort_values("timestamp1"),
                                     hygrometer_data.sort_values("timestamp"),
                                     left_on="timestamp1", right_on="timestamp", direction="nearest")
        else:
            matched_data = sensing_and_ref
        freq_mask = matched_data["frequency1"] == matched_data["frequency2"]
        matched_data = matched_data[freq_mask].reset_index(drop=True).drop(columns=["frequency2"]).rename(columns={"frequency1": "frequency"})
        loaded_datas[tags[i]] = matched_data
    return tags[:len(tags)//2], loaded_datas

def load_hygrometer_data(data_path="C:\\Users\\xie_pc\\Desktop\\Green Tag 2.0\\model\\"):
    # load data from soil moisture meter, including timestamp, soil moisture, and conductivity
    hygrometer_data = pd.read_csv(data_path, delimiter="\t", skiprows=8)
    time_format = "%Y/%m/%d %H:%M:%S"
    # hygrometer_data["记录时间"] = pd.to_datetime(hygrometer_data["记录时间"], format=time_format).astype('int64')
    hygrometer_data["记录时间"] = hygrometer_data["记录时间"].apply(
        lambda x: int(datetime.strptime(x, time_format).timestamp() * 10 ** 6))  
    hygrometer_mois_data = hygrometer_data[hygrometer_data["寄存器名称"] == "温度水分电导率-水分"].reset_index(drop=True)
    hygrometer_temp_data = hygrometer_data[hygrometer_data["寄存器名称"] == "温度水分电导率-温度"].reset_index(drop=True)
    hygrometer_conduc_data = hygrometer_data[hygrometer_data["寄存器名称"] == "温度水分电导率-电导率"].reset_index(drop=True)

    hygrometer_data = pd.DataFrame({
        "timestamp": hygrometer_mois_data["记录时间"],
        "moisture": hygrometer_mois_data["存储数值"],
        "temperature": hygrometer_temp_data["存储数值"],
        "conductivity": hygrometer_conduc_data["存储数值"]
    })
    return hygrometer_data

def get_differential_signal_feature(tag_feature, data_num=1, istest=True):
    # get differential signal feature
    tag_feature["DMRT"] = tag_feature["MRT1_f"] - tag_feature["MRT2_f"]
    tag_feature["DRSSI"] = tag_feature["RSSI1_f"] - tag_feature["RSSI2_f"]
    tag_feature["Dphase"] = np.abs((tag_feature["phase1"] - tag_feature["phase2"])) % np.pi  
    return tag_feature

def outlier_removal(tag_feature, freq_num=16, data_num=1, isfilter=True, istest=False):
    # preprocessing dataset collecting by reader

    def lowpass_filter(grouped_data, feature_names, alpha):
        def smooth(window):
            return alpha * float(window.iloc[-1]) + (1 - alpha) * window.iloc[0].astype(float)
        filtered_data = pd.DataFrame()
        for feature_name in feature_names:
            filtered_feature = grouped_data[feature_name].rolling(window=2).apply(smooth)
            filtered_feature.iloc[0] = grouped_data[feature_name].iloc[0]
            filtered_data[feature_name] = filtered_feature
        return filtered_data[feature_names]

    def hampel_filter(tag_feature, feature_names, window_size, threshold):
        filtered_data = pd.DataFrame()
        for feature_name in feature_names:
            filtered_data[feature_name] = tag_feature[feature_name]
            widw_size = window_size * 6 if feature_name == "MRT" else window_size  
            median = tag_feature[feature_name].rolling(window=widw_size, center=True, min_periods=1).median()  
            deviation = np.abs(tag_feature[feature_name] - median)  
            mad = deviation.rolling(window=widw_size, center=True, min_periods=1).median()  

            outlier_mask = deviation > threshold * mad  
            filtered_data.loc[outlier_mask, feature_name] = median[outlier_mask]  
        return filtered_data[feature_names]

    if isfilter:
        processed_data = pd.DataFrame(columns=["MRT1", "MRT2", "RSSI1", "RSSI2"])

        for _, grouped_data in tag_feature.groupby(["frequency"]):
            filtered_data = hampel_filter(grouped_data, feature_names=["MRT1", "MRT2", "RSSI1", "RSSI2"], window_size=48, threshold=1.5)
            filtered_data = lowpass_filter(filtered_data, feature_names=["MRT1", "MRT2", "RSSI1", "RSSI2"], alpha=0.2)
            processed_data = pd.concat([processed_data, filtered_data], ignore_index=True, sort=False)
        processed_data = processed_data.sort_index()
        tag_feature["MRT1_f"] = processed_data["MRT1"]
        tag_feature["MRT2_f"] = processed_data["MRT2"]
        tag_feature["RSSI1_f"] = processed_data["RSSI1"]
        tag_feature["RSSI2_f"] = processed_data["RSSI2"]

    return tag_feature


def preprocess_data(data_path, ant_num):
    data = load_data(data_path, ant_num=ant_num)
    if len(data) == 0:
        return data
    data = outlier_removal(data)
    data = get_differential_signal_feature(data)

    tag_data_grouped = data.groupby("indexID")
    samples, labels = [], []
    for indexID, data in tag_data_grouped:
        samples.append(data["DRSSI"].values)
    samples = np.array(samples)
    samples = np.around(samples, 2)

    ant1_mean = np.array(
        [-4.22601317, -4.08923506, -3.9592874, -3.82385174, -3.72516042, -3.56103512, -3.35357987, -3.2842283,
         -3.15833333, -3.08165316, -2.9525076, -2.83222729, -2.71780648, -2.63915907, -2.49813408, -2.37895137])
    ant1_scale = np.array(
        [3.5052876, 3.58086963, 3.61615863, 3.61557421, 3.67342338, 3.62643173, 3.51907234, 3.45804733, 3.51004574,
         3.5355392, 3.56619148, 3.58853324, 3.65416602, 3.70161134, 3.7717863, 3.86645903])
    ant2_mean = np.array(
        [-4.8311986, -4.82725284, -4.8232021, -4.83478565, -4.8191776, -4.77459318, -4.67459318, -4.69454943,
         -4.61818898, -4.64223097, -4.69742782, -4.70740157, -4.71903762, -4.73684164, -4.76797025, -4.78847769])
    ant2_scale = np.array(
        [3.05444149, 3.03107009, 3.05081156, 3.05333673, 3.06522042, 3.07801765, 3.15458923, 3.099966, 3.00503818,
         3.00833059, 3.02837304, 3.0462767, 3.0894959, 3.13543371, 3.1769217, 3.21024787])
    if ant_num == 1:
        samples = (samples - ant1_mean) / ant1_scale
    if ant_num == 2:
        samples = (samples - ant2_mean) / ant2_scale
    return  samples


if len(sys.argv) < 2:
    print("argv length error")
    exit()

#print(sys.argv)

tag = sys.argv[1]


RF_ant1 = joblib.load("./moisture_estimation/model/ant1_RF.pkl")
RF_ant2 = joblib.load("./moisture_estimation/model/ant2_RF.pkl")

samples1 = preprocess_data(data_path= "./moisture_estimation/data/Data_" + str(tag) + ".txt", ant_num=1)
samples2 = preprocess_data(data_path= "./moisture_estimation/data/Data_" + str(tag) + ".txt", ant_num=2)


RF1_pre = RF_ant1.predict(samples1) if len(samples1) > 0 else "NaN"
RF2_pre = RF_ant2.predict(samples2) if len(samples2) > 0 else "NaN"



print("moisture: " + str(RF1_pre) + ", " + str(RF2_pre))


with open("./moisture_estimation/vwc_estimation.txt", 'a') as file:
    file.writelines(str(datetime.fromtimestamp(time.time()))[:-7] + ", " + tag + ", " + str(RF1_pre) + ", " + str(RF2_pre) + "\n")






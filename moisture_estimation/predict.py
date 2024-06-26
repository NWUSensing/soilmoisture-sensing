import pandas as pd
import numpy as np
import joblib
import sklearn
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeClassifier
import time
from datetime import datetime
import sys

import warnings
warnings.filterwarnings("ignore")

def load_data(reader_data, ant_num, hygrometer_data=None, data_num=1, tag_list=None, tag_MRT_dict=None, offset=0, istest=True, readertype='ThingMagic'):
    # load train data
    def is_contains_all_frequencies(group, freq_list):
        return set(group["frequency"].unique()) == set(freq_list)
    def aver_feature(group):
        aver_data = group.iloc[0].to_frame().T
        aver_data["RSSI1"] = group["RSSI1"].mean()
        aver_data["RSSI2"] = group["RSSI2"].mean()
        return aver_data

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
        tag_datas[key] = tag_datas[key].groupby(['indexID', 'frequency']).apply(aver_feature).reset_index(drop=True)
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

    return  samples

def get_pred(samples, model):
    if len(samples) == 0:
        return "NaN"
    samples = samples[:, [2, 7, 15]]
    labels = np.array([21.95, 24.95, 28.57, 31.96, 35.48, 38.89, 41.78, 45.2, 48.69, 52.01, 55.62, 59.06, 61.63, 66.06, 68.97, 72.34, 75.45, 79.05, 82.25, 85.32])
    pre = model.predict(samples)
    pre_labels = [labels[i] for i in np.argmax(pre, axis=1)][0]
    return pre_labels
    

if len(sys.argv) < 2:
    print("argv length error")
    exit()

#print(sys.argv)

tag = sys.argv[1]


DT_ant1 = joblib.load("./moisture_estimation/model/ant1_dt_freq3.pkl")
DT_ant2 = joblib.load("./moisture_estimation/model/ant2_dt_freq3.pkl")

samples1 = preprocess_data(data_path= "./moisture_estimation/data/Data_" + str(tag) + ".txt", ant_num=1)
samples2 = preprocess_data(data_path= "./moisture_estimation/data/Data_" + str(tag) + ".txt", ant_num=2)

'''
NN_model1 = load_model("./moisture_estimation/ant1_nn_freq3.h5")
NN_model2 = load_model("./moisture_estimation/ant2_nn_freq3.h5")

nn1_pre = NN_model1.predict(samples)
nn2_pre = NN_model2.predict(samples)

nn1_pre = tf.nn.softmax(nn1_pre).numpy()
nn1_pre_labels = [labels[i] for i in np.argmax(nn_pre, axis=1)][0]

nn2_pre = tf.nn.softmax(nn2_pre).numpy()
nn2_pre_labels = [labels[i] for i in np.argmax(nn_pre, axis=1)][0]
'''

DT1_pre_labels = get_pred(samples1, DT_ant1)
DT2_pre_labels = get_pred(samples2, DT_ant2)

print("moisture: " + str(DT1_pre_labels) + ", " + str(DT2_pre_labels))



with open("./moisture_estimation/vwc_estimation.txt", 'a') as file:
    file.writelines(str(datetime.fromtimestamp(time.time()))[:-7] + ", " + tag + ", " + str(DT1_pre_labels) + ", " + str(DT2_pre_labels) + "\n")
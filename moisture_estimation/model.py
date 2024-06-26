"""
Obtain the relationship between DRSSI and humidity by using the dataset (TMR_2+8cm_dataset.csv) stored 
in the "../data" directory and the corresponding humidity sensor data (TMR_hygrometer.txt) through the Random Forest algorithm.
"""
import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from datetime import datetime
import sklearn
import warnings

warnings.filterwarnings("ignore")

def load_data(reader_data, hygrometer_data, tag_list, ant_num, data_num=1, offset=0, istest=False, readertype='ThingMagic'):
    # load train data
    def is_contains_all_frequencies(group, freq_list):
        return set(group["frequency"].unique()) == set(freq_list)

    raw_data = pd.read_csv(reader_data, header=None)
    MRT_list = [f"MRT{i}" for i in range(1, len(tag_list) + 1)]
    raw_data.columns = ['tagID', 'frequency', 'phase', 'RSSI'] + MRT_list + ['antenna', 'timestamp', 'indexID']
    # drop uninterest tag data
    mask_tagID = raw_data["tagID"].isin(tag_list)
    raw_data = raw_data[mask_tagID].reset_index(drop=True)
    # raw_data = raw_data[raw_data["indexID"] < 100]  
    # convert timestamp format
    if readertype == 'ThingMagic':
        time_format = " %d/%m/%Y %H:%M:%S"
        raw_data["timestamp"] = raw_data["timestamp"].apply(
            lambda x: int(datetime.strptime(x, time_format).timestamp() * 10 ** 6))
        raw_data["frequency"] /= 1000
    raw_data = raw_data[raw_data["antenna"] == ant_num]  # only select data from one antenna
    # grounped data by tagID, ie. ref and sensing
    groupedby_tagID = raw_data.groupby('tagID')
    tagID_grouped_data = {}
    tagIDs = []
    for group_name, group_df in groupedby_tagID:
        tagID_grouped_data[group_name] = group_df
        tagIDs.append(group_name)

    tagIDs, tag_datas = match_sensing_ref_hygrometer(tagIDs, tagID_grouped_data, hygrometer_data, offset, istest=istest)
    freq_list = [i * 0.25 + 920.625 for i in range(0, 16)]

    for key in tagIDs:
        '''
        Filter the data for each indexID, removing data from indexIDs with fewer than x entries. 
        (Only for Impinj readers, excluding ThingMagic readers, due to the low read rates)
        '''
        sorted_grouped_size = tag_datas[key].groupby(["indexID", "frequency"]).size()
        incomplete_data = sorted_grouped_size[sorted_grouped_size < 1].index
        incomplete_data_indexID = [index for index in set([item[0] for item in incomplete_data])]
        mask_indexID = tag_datas[key]["indexID"].isin(incomplete_data_indexID)
        tag_datas[key] = tag_datas[key][~mask_indexID].reset_index(drop=True)

        # Ensure that data on the desired channel is received.
        indexID_freq_grouped_data = tag_datas[key].groupby(["indexID"])
        filtered_groups = indexID_freq_grouped_data.filter(lambda x: is_contains_all_frequencies(x, freq_list))
        tag_datas[key] = filtered_groups.reset_index(drop=True)
        tag_datas[key] = tag_datas[key].groupby(['indexID', 'frequency']).apply(
            lambda x: x.sample(n=data_num)).apply(lambda group: group).reset_index(drop=True)  # sampling data
        # reorganized our dataset index
        reorganized_indexID = np.array(
            [[i] * 16 * data_num for i in range(0, len(tag_datas[key]) // (data_num * 16))]).flatten()
        tag_datas[key]["indexID"] = reorganized_indexID

    # tag_datas[tagIDs[0]].to_csv("TMR_train_loaded_data_ant2.csv")

    return [tagIDs, tag_datas]


def match_sensing_ref_hygrometer(tags, tagID_grouped_data, hygrometer_name, offset, istest=False):
    # Matching data from sensing tags, reference tags, and hygrometers based on timestamps.
    if not istest:
        hygrometer_data = load_hygrometer_data(hygrometer_name)
    loaded_datas = {}
    hygrometer_data["timestamp"] = hygrometer_data["timestamp"] + offset;  # compensate timestamp of hygrometer
    for i in range(len(tags) // 2):
        tagID_grouped_data[tags[i]] = tagID_grouped_data[tags[i]].drop(
            columns=[f"MRT{i}" for i in range(1, len(tags) + 1)] + ["indexID"])
        tagID_grouped_data[tags[i]] = tagID_grouped_data[tags[i]].rename(columns={"timestamp": "timestamp1",
                                                                                  "tagID": "tagID1",
                                                                                  "phase": "phase1",
                                                                                  "RSSI": "RSSI1",
                                                                                  "frequency": "frequency1",
                                                                                  })
        tagID_grouped_data[tags[len(tags) // 2 + i]] = tagID_grouped_data[tags[len(tags) // 2 + i]].rename(
            columns={"timestamp": "timestamp2",
                     "tagID": "tagID2",
                     "phase": "phase2",
                     "RSSI": "RSSI2",
                     "frequency": "frequency2"})
        sensing_and_ref = pd.merge_asof(tagID_grouped_data[tags[i]].sort_values("timestamp1"),
                                        tagID_grouped_data[tags[len(tags) // 2 + i]].sort_values("timestamp2"),
                                        left_on="timestamp1", right_on="timestamp2", direction="nearest")
        if not istest:
            matched_data = pd.merge_asof(sensing_and_ref.sort_values("timestamp1"),
                                         hygrometer_data.sort_values("timestamp"),
                                         left_on="timestamp1", right_on="timestamp", direction="nearest")
        else:
            matched_data = sensing_and_ref
        # removed data with mismatched frequencies
        freq_mask = matched_data["frequency1"] == matched_data["frequency2"]
        matched_data = matched_data[freq_mask].reset_index(drop=True).drop(columns=["frequency2"]).rename(
            columns={"frequency1": "frequency"})
        loaded_datas[tags[i]] = matched_data
    return tags[:len(tags) // 2], loaded_datas


def load_hygrometer_data(data_path="C:\\Users\\xie_pc\\Desktop\\Green Tag 2.0\\model\\"):
    # load data from soil moisture meter, including timestamp, soil moisture, and conductivity
    hygrometer_data = pd.read_csv(data_path, delimiter="\t", skiprows=8)
    time_format = "%Y/%m/%d %H:%M:%S"
    # hygrometer_data["记录时间"] = pd.to_datetime(hygrometer_data["记录时间"], format=time_format).astype('int64')
    hygrometer_data["记录时间"] = hygrometer_data["记录时间"].apply(
        lambda x: int(datetime.strptime(x, time_format).timestamp() * 10 ** 6))
    hygrometer_mois_data = hygrometer_data[hygrometer_data["寄存器名称"] == "温度水分电导率-水分"].reset_index(
        drop=True)
    hygrometer_temp_data = hygrometer_data[hygrometer_data["寄存器名称"] == "温度水分电导率-温度"].reset_index(
        drop=True)
    hygrometer_conduc_data = hygrometer_data[hygrometer_data["寄存器名称"] == "温度水分电导率-电导率"].reset_index(
        drop=True)

    hygrometer_data = pd.DataFrame({
        "timestamp": hygrometer_mois_data["记录时间"],
        "moisture": hygrometer_mois_data["存储数值"],
        "temperature": hygrometer_temp_data["存储数值"],
        "conductivity": hygrometer_conduc_data["存储数值"]
    })

    return hygrometer_data


def outlier_removal(tag_feature, isfilter=True, istest=False):
    # preprocessing dataset collecting by reader.

    def lowpass_filter(grouped_data, feature_names, alpha):
        # smoothing the data
        def smooth(window):
            return alpha * float(window.iloc[-1]) + (1 - alpha) * window.iloc[0].astype(float)

        filtered_data = pd.DataFrame()
        for feature_name in feature_names:
            filtered_feature = grouped_data[feature_name].rolling(window=2).apply(smooth)
            filtered_feature.iloc[0] = grouped_data[feature_name].iloc[0]
            filtered_data[feature_name] = filtered_feature
        return filtered_data[feature_names]

    def hampel_filter(tag_feature, feature_names, window_size, threshold):
        # Hampel filter remove outlier replace by mean
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
        processed_data = pd.DataFrame(columns=["RSSI1", "RSSI2"])

        for _, grouped_data in tag_feature.groupby(["frequency"]):
            # Apply the Hampel filter and lowpass filter to RSSI.
            filtered_data = hampel_filter(grouped_data, feature_names=["RSSI1", "RSSI2"], window_size=48, threshold=1.5)
            filtered_data = lowpass_filter(filtered_data, feature_names=["RSSI1", "RSSI2"], alpha=0.2)
            processed_data = processed_data._append(filtered_data)
        processed_data = processed_data.sort_index()
        tag_feature["RSSI1_f"] = processed_data["RSSI1"]
        tag_feature["RSSI2_f"] = processed_data["RSSI2"]

    return tag_feature


def get_differential_signal_feature(tag_feature, istest=False):
    # get differential signal feature
    tag_feature["DMRT"] = tag_feature["MRT1"] - tag_feature["MRT2"]
    tag_feature["DRSSI"] = tag_feature["RSSI1_f"] - tag_feature["RSSI2_f"]
    tag_feature["Dphase"] = np.abs((tag_feature["phase1"] - tag_feature["phase2"])) % np.pi
    return tag_feature


def feature_scaling(preprocessed_data, freq_num):
    # Select data from multiple channels, Apply z-score normalization to DRSSI, return normalized DRSSI
    freqs = np.array([i * 0.25 + 920.625 for i in range(0, 16)])
    allowed_freqs_index = np.linspace(0, len(freqs) - 1, freq_num, dtype=int)  # 均匀的采样不同频率
    allowed_freqs = freqs[allowed_freqs_index]
    mask_data = preprocessed_data["frequency"].isin(allowed_freqs)
    data = preprocessed_data[mask_data].reset_index(drop=True)

    index_grouped_data = preprocessed_data.groupby("indexID")
    samples = []  # np.arrary()
    labels = []
    for indexID, data in index_grouped_data:
        samples.append(data["DRSSI"].values)
        labels.append(data["moisture"].values.mean())
    samples = np.array(samples)
    labels = np.array(labels)

    x_train, x_test, y_train, y_test = sklearn.model_selection.train_test_split(samples, labels, test_size=0.2,
                                                                                random_state=42)
    scaler = sklearn.preprocessing.StandardScaler()
    scaler.fit(x_train)
    x_train = scaler.transform(x_train)
    x_test = scaler.transform(x_test)

    return x_train, x_test, y_train, y_test


def RandomForestRegression(x_train, x_test, y_train, y_test, save=False, filename=None):
    RF = RandomForestRegressor(n_estimators=100, random_state=21, max_depth=10)  # 60,100
    RF.fit(x_train, y_train)
    if save:
        joblib.dump(RF, "./moisture_estimation/model/" + filename + '.pkl')
        # return
    y_pre = RF.predict(x_test)

    RFmse = sklearn.metrics.mean_squared_error(y_test, y_pre)
    plot_CDF(y_test, y_pre)
    # error_analysis(y_test, y_pre)
    # plot_pre(y_test.index, y_test, y_pre)
    # print("d")
    return y_pre


def plot_CDF(predicts, labels, max_moisture=50, min_moisture=10):
    # plot CDF figure
    def cal_acc_enenrror(label, predict, en_error):
        accuracy_in_enerror = []
        sorted_error = np.sort(abs(label - predict))
        percent = 0.05
        for error in en_error:
            CDF_percent = sum(sorted_error < error) / len(sorted_error)
            accuracy_in_enerror.append(CDF_percent)
        return accuracy_in_enerror

    en_error = (max_moisture - min_moisture) / 20  
    en_error_list = np.array([i * en_error for i in range(20)])

    en_error0 = cal_acc_enenrror(np.array(predicts), np.array(labels), en_error_list)
    # calc 90% CDF
    cal0 = cal_CDF(np.array(predicts), np.array(labels), 0.9, 10, 50)

    en_error_percentage = (en_error_list) / 100
    # plot fig
    fig, ax = plt.subplots(figsize=(16, 10))
    plt.xlim(0, 36)
    plt.ylim(0, 1.05)
    plt.xticks([i for i in range(0, 36, 5)], fontsize=18)
    plt.yticks(np.append(np.arange(0, 1.2, 0.2), 0.9), fontsize=18)
    plt.plot(en_error_list, en_error0, c='blue', marker='o', label="Channel 16", linewidth=2)
    plt.axhline(y=0.9, color='black', linestyle='--', xmin=0, xmax=100)
    # plt.axvline(x=12.35, color='black', linestyle='--', ymin=0, ymax=0.9)
    # plt.subplots_adjust(left=0.04, right=0.96, top=0.94, bottom=0.05)
    plt.xlabel("Absolutely Soil Moisture Estimation Error(%)", fontsize=20)
    plt.ylabel("CDF", fontsize=20)
    # plt.title("moisture and time", fontsize=15, fontweight='black', pad=15)
    plt.legend(fontsize=20, markerscale=1)
    # plt.savefig("abs_CDF.png", format='png')
    plt.show(block=True)


def cal_CDF(y_pre, y_truth, percent, max_moisture, min_moisture):
    # Calculate the humidity error corresponding to a specific CDF.
    sorted_error = np.sort(abs(y_pre - y_truth))
    CDF_percent = sorted_error[round(len(sorted_error) * percent)]
    return CDF_percent




reader_file_path = "./data/TMR_2+8cm_dataset.csv"
moisture_file_path = "./data/TMR_hygrometer.txt"
freq_num = 3  # channel num we use in soil moisture estimation,
data_num = 1

sensing_tagID = "0080"
ref_tagID = "0081"

tagIDs, tagID_grouped_data = load_data(reader_file_path, moisture_file_path, tag_list=[sensing_tagID, ref_tagID], ant_num=1)

preprocessed_data = {}  
for i in range(len(tagIDs)):
    preprocessed_data[tagIDs[i]] = outlier_removal(tagID_grouped_data[tagIDs[i]], isfilter=True)

for i in range(len(tagIDs)):
    preprocessed_data[tagIDs[i]] = get_differential_signal_feature(preprocessed_data[tagIDs[i]])

dataset = preprocessed_data[sensing_tagID]
x_train, x_test, y_train, y_test = feature_scaling(dataset, freq_num)

RandomForestRegression(x_train, x_test, y_train, y_test, save=True, filename="test")




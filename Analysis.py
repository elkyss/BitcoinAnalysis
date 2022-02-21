import os
import time
import json
import blocksci
import datetime
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from PATHS import *

# Lets make this one the main feature file!!
# Im commenting out all of the old stuff and moving them down.
# feel free to delete them if you dont use them :)
# most of them are duplicates of stuff in addressBook.py anyway

def chain():
    return blocksci.Blockchain(CONFIG_PATH)

def cc():
    return blocksci.currency.CurrencyConverter(currency='USD',
                                        start=datetime.date(2009,1,3),
                                         end=datetime.date(2021,1,31))

def timeToUnix(datetime):
    return time.mktime(datetime.timetuple())


def BTCtoUSD(btc,time):
    return cc.btc_to_currency(btc, time)


def checkAddress(blockchain,wallet):
    try:
        if blockchain.address_from_string(wallet):
            return True
    except Exception as e:
        print(e)
        return False


################################ analysis_from csv


def calculate_fee(row,time):
    pass


def num_in_a_row(series):
    flag = True


def extract_features_USD(df):
    """

    """
    # Added type Odds to symmetry score. Feel free to use it/work on it
    # type_odds = df.tx_type.value_counts().values[0]/df.tx_type.value_counts().values[1] #values[0] is outputs

    # I changed activity density so it would calculate the avg and std time between txs.
    #life_time = df.time.iloc[-1] - df.time.iloc[1]
    #activity_density = df.time.std()/60  # std in minutes

    # Added all of these guys under value statistics. awesome features love this shit yo
    # dollar_obtain_per_tx = df.loc[df.tx_type == 1].valueUSD.sum()/df.tx_type.value_counts().values[0]
    # dollar_spent_per_tx = df.loc[df.tx_type == -1].valueUSD.sum()/df.tx_type.value_counts().values[1]
    # max_fee = df.feeUSD.max #most values is 0 so need to think if we want to recalculte or take diff from 0
    # total_num_tx = df.shape[0]
    # total_dollar = df.valueUSD.sum()
    return {
        'symmetry_score' : symmetry_score(df),
        'activity_density' : activity_density(df),
        'value_statistics': value_statistics(df)
    }

def activity_density(df):
    """
    Returns a dict with some time related statistics of the wallet
    """
    first_tx = df.time.iloc[0]
    time_vector = np.array(df.time) - first_tx
    time_between_txes = np.array([time_vector[idx] -time_vector[idx-1] for idx in range(len(time_vector)-1)])
    return {
        "lifetime": time_vector[-1],
        "first_tx" : first_tx,
        "tx_freq_mean" : time_between_txes.mean()/60,
        "tx_freq_std": time_between_txes.std()/60
    }


def symmetry_score(df):
    """
    Rrturns a dict with symmetry related attributes.
    in score/ out score tries to capture the notion of symmetry -
    it calculates how often does input txs are seperated by output txs, and vice versa.
    maximum in both is 0.5, minimum is ( (len(df)^2) ** -1 )

        # Reference: https://stackoverflow.com/questions/66441738/pandas-sum-consecutive-rows-satisfying-condition

    """
    tx_type_odds = df.tx_type.value_counts().values[0]/df.tx_type.value_counts().values[1]

    in_condition, out_condition = (df.tx_type - 1).astype(bool), (df.tx_type + 1).astype(bool)
    in_sums, out_sums = (~in_condition).cumsum()[in_condition], (~out_condition).cumsum()[out_condition]

    in_score = (1/df.tx_type.groupby(in_sums).agg(np.sum)).sum()/df.shape[0]
    out_score = (1/df.tx_type.groupby(out_sums).agg(np.sum)).sum()/df.shape[0]

    return {
        'tx_type_odds' : tx_type_odds,
        'consecutive_in_tx_score' : in_score,
        'consecutive_out_tx_score' : out_score
    }

def value_statistics(df):
    dollar_obtain_per_tx = df.loc[df.tx_type == 1].valueUSD.sum()/df.tx_type.value_counts().values[0]
    dollar_spent_per_tx = df.loc[df.tx_type == -1].valueUSD.sum()/df.tx_type.value_counts().values[1]
    return {
        'dollar_obtain_per_tx' : dollar_obtain_per_tx,
        'dollar_spent_per_tx' : dollar_spent_per_tx,
        'obtain_spent_ratio' : dollar_obtain_per_tx/dollar_spent_per_tx,
        'tx_value_std' : df.valueUSD.std(),
        'tx_value_prob_mean' : None, # this uses the probabilty of having the tx value in its' block
        'tx_value_prob_std' : None, # this uses the probabilty of having the tx value in its' block
        'max_fee' : df.feeUSD.max(), #most values is 0 so need to think if we want to recalculte or take diff from 0
        'fee_prob_mean' :  None, # this uses the probabilty of having the tx fee in its' block
        'fee_prob_std' : None, # this uses the probabilty of having the tx fee in its' block
        'total_num_tx' : df.shape[0],
        'total_dollar' : df.valueUSD.sum()
    }

def peers_statistics(df):
    # Feature that counts how many distinct peers a wallet have
    # how many close friends does he have (=peers with more than 2 txs)
    pass


def extract_features_BTC(df):
    odds = df.tx_type.value_counts().values[0]/df.tx_type.value_counts().values[1]
    life_time = df.time.iloc[-1]-df.time.iloc[1]
    activity_density = df.time.std()/60  # std in minutes
    btc_obtain_per_tx = df.loc[df.tx_type == 1].valueBTC.sum()/df.tx_type.value_counts().values[0]
    btc_spent_per_tx = df.loc[df.tx_type == -1].valueBTC.sum()/df.tx_type.value_counts().values[1]
    max_fee = df.feeBTC.max #most values is 0 so need to think if we want to recalculte or take diff from 0
    total_num_tx = df.shape[0]
    total_btc = df.valueBTC.sum()



def heat_cor_view(big_df,wanted_method : str):
    # i referred the input as pandas but this is still raw function
    df_spear_corr = big_df.corr(method=wanted_method)
    im = plt.imshow(df_spear_corr, cmap=plt.get_cmap('coolwarm'))
    plt.xticks(np.arange(big_df.shape[1]), big_df.columns, rotation=90)
    plt.yticks(np.arange(big_df.shape[1]), big_df.columns_)
    plt.colorbar()
    plt.show()
    plt.close()



def some_statistics_on_features(big_df,wanted_plot: str):
    # the same as above
    #here just initial numbers we will know better when will have the size of the big df
    nrow = big_df.shape[1]//3
    ncol = 3
    fig, axes = plt.subplots(nrow, ncol)
    axes = axes.flat
    for i in range(big_df.shape[1]):
        big_df.iloc[:,i].plot(kind=wanted_plot, ax=axes[i])




# ### MUST BE FIXED - we need to
# def AddressVector(wallet):
#     # Returns a time series of wallet balance in USD
#     # Each timestamp is a tx
#     # 1 = wallet receives money (it is an output of the tx)
#     # -1 = wallet sends money (it is an input of the tx)
#     out_list = [[1,
#                  wallet.balance(tx.block_height) * SATOSHI,
#                  tx.block_time] for tx in wallet.output_txes]
#     in_list = [[-1,
#                 wallet.balance(tx.block_height) * SATOSHI,
#                 tx.block_time] for tx in wallet.input_txes]
#     res = sorted(out_list + in_list,key=lambda x: x[2])
#     res = updateTxValue(res)
#     res = pd.DataFrame(res,columns=["type","value","time"])
#     return res
#
#
# def updateTxValue(tx_list):
#     if len(tx_list) == 0:
#         pass
#     elif len(tx_list) == 1:
#         tx_list[0][1] = cc.btc_to_currency(tx_list[0][1],tx_list[0][2])
#         tx_list[0][2] = timeToUnix(tx_list[0][2])
#     elif len(tx_list) > 1:
#         balance_list = list(tx_list[idx][1] - tx_list[idx-1][1] for idx in range(1,len(tx_list)))
#         for idx in range(1,len(tx_list)):
#             tx_list[idx][1] = cc.btc_to_currency(balance_list[idx-1], tx_list[idx][2])
#             tx_list[idx][2] = timeToUnix(tx_list[idx][2])
#         tx_list[0][2] = timeToUnix(tx_list[0][2])
#     return tx_list
#
#
# def VT_VecScore(VTVec):
#     pass
#
#
# def plotValueTimeSeries(address,timeSeries,size,save=False,type=None):
#     plt.close()
#     scatter = plt.scatter(timeSeries["time"],
#                           timeSeries["valueBTC"],
#                           c=timeSeries["type"],
#                           cmap='coolwarm',
#                           s=size)
#     if type:
#         plt.title(f'Tx over time in {type}')
#         plt.gca().add_artist(plt.legend([address],loc=4))
#     else:
#         plt.title(f'Tx over time in {address}')
#     plt.xlabel('Time')
#     plt.ylabel('Tx Value USD')
#     plt.legend(handles=scatter.legend_elements()[0],labels=['Input','Output'])
#     if save:
#         filename = f'{PLOTS_PATH}AV_{address}.png'
#         plt.savefig(filename)
#     else:
#         plt.show()
#
#
# def QuickLoad(ml_data_path):
#     # Qucickly loads a dictionary with addresses a keys,
#     # and Timeseries vectors as values
#     return {file.split('.csv')[0]:pd.read_csv(os.path.join(ml_data_path,file)) for file in os.listdir(ml_data_path)}
#
# def makeVectorBatch(address_list):
#     return {wallet:AddressVector(chain.address_from_string(wallet)) for wallet in address_list if checkAddress(chain,wallet)}

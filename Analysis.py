import os
import time
import json
import blocksci
import datetime
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from PATHS import *

chain = blocksci.Blockchain(CONFIG_PATH)
cc = blocksci.currency.CurrencyConverter(currency='USD',
                                         start=datetime.date(2009,1,3),
                                         end=datetime.date(2021,1,31))
addr = blocksci.address_type.pubkey
wallet = chain.address_from_string(chain.addresses(addr)[2426948].address_string)


def timeToUnix(datetime):
    return time.mktime(datetime.timetuple())


def BTCtoUSD(btc,time):
    return cc.btc_to_currency(btc, time)


### MUST BE FIXED - we need to
def AddressVector(wallet):
    # Returns a time series of wallet balance in USD
    # Each timestamp is a tx
    # 1 = wallet receives money (it is an output of the tx)
    # -1 = wallet sends money (it is an input of the tx)
    out_list = [[1,
                 wallet.balance(tx.block_height) * SATOSHI,
                 tx.block_time] for tx in wallet.output_txes]
    in_list = [[-1,
                wallet.balance(tx.block_height) * SATOSHI,
                tx.block_time] for tx in wallet.input_txes]
    res = sorted(out_list + in_list,key=lambda x: x[2])
    res = updateTxValue(res)
    res = pd.DataFrame(res,columns=["type","value","time"])
    return res


def updateTxValue(tx_list):
    if len(tx_list) == 0:
        pass
    elif len(tx_list) == 1:
        tx_list[0][1] = cc.btc_to_currency(tx_list[0][1],tx_list[0][2])
        tx_list[0][2] = timeToUnix(tx_list[0][2])
    elif len(tx_list) > 1:
        balance_list = list(tx_list[idx][1] - tx_list[idx-1][1] for idx in range(1,len(tx_list)))
        for idx in range(1,len(tx_list)):
            tx_list[idx][1] = cc.btc_to_currency(balance_list[idx-1], tx_list[idx][2])
            tx_list[idx][2] = timeToUnix(tx_list[idx][2])
        tx_list[0][2] = timeToUnix(tx_list[0][2])
    return tx_list


def VT_VecScore(VTVec):
    pass



def plotValueTimeSeries(address,timeSeries,size,save=False,type=None):
    plt.close()
    scatter = plt.scatter(timeSeries["time"],
                          timeSeries["value"],
                          c=timeSeries["type"],
                          cmap='coolwarm',
                          s=size)
    if type:
        plt.title(f'Tx over time in {type}')
        plt.gca().add_artist(plt.legend([address],loc=4))
    else:
        plt.title(f'Tx over time in {address}')
    plt.xlabel('Time')
    plt.ylabel('Tx Value USD')
    plt.legend(handles=scatter.legend_elements()[0],labels=['Input','Output'])
    if save:
        filename = f'{PLOTS_PATH}AV_{address}.png'
        plt.savefig(filename)
    else:
        plt.show()


def QuickLoad(ml_data_path):
    # Qucickly loads a dictionary with addresses a keys,
    # and Timeseries vectors as values
    return {file.split('.csv')[0]:pd.read_csv(os.path.join(ml_data_path,file)) for file in os.listdir(ml_data_path)}


def checkAddress(blockchain,wallet):
    try:
        if blockchain.address_from_string(wallet):
            return True
    except Exception as e:
        print(e)
        return False


def makeVectorBatch(address_list):
    return {wallet:AddressVector(chain.address_from_string(wallet)) for wallet in address_list if checkAddress(chain,wallet)}

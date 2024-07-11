import pandas as pd
import requests
import json
from datetime import datetime, timedelta
import time



def fetch_sse_index_data(index='000001.SS', count=2000):
    url = 'https://push2his.eastmoney.com/api/qt/stock/kline/get'

    end_time = datetime.now().strftime('%Y%m%d')

    params = {
        'fields1': 'f1,f2,f3,f4,f5,f6',
        'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61',
        'ut': 'fa5fd1943c7b386f172d6893dbfba10b',
        'klt': '101',  # 日线数据
        'fqt': '1',  # 前复权
        'secid': f'1.{index[:6]}',  # 上证指数
        'beg': '0',  # 从最新的数据开始
        'end': end_time,
        'lmt': str(count),  # 获取的数据条数
        '_': str(int(time.time() * 1000))
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    response = requests.get(url, params=params, headers=headers)
    data = json.loads(response.text)

    if data['data'] is None:
        raise ValueError("Unable to fetch data. Please check the index code and try again.")

    df = pd.DataFrame(data['data']['klines'], columns=['raw_data'])
    df = df['raw_data'].str.split(',', expand=True)

    rename_dict = {0: 'candle_end_time', 1: 'open', 2: 'close', 3: 'high', 4: 'low', 5: 'amount', 6: 'volume',
                   7: 'amplitude', 8: 'pct_chg', 9: 'chg', 10: 'turnover'}
    df.rename(columns=rename_dict, inplace=True)

    df['candle_end_time'] = pd.to_datetime(df['candle_end_time'])
    df.drop_duplicates('candle_end_time', inplace=True)  # 去重
    df.sort_values('candle_end_time', inplace=True)
    df['candle_end_time'] = df['candle_end_time'].dt.strftime('%Y-%m-%d')

    # 添加 pre_close 列
    df['pre_close'] = df['close'].astype(float).shift(1)

    # 调整数据类型
    for col in ['open', 'close', 'high', 'low', 'amount']:
        df[col] = df[col].astype(float)

    df['info'] = None

    df = df[['candle_end_time', 'open', 'high', 'low', 'close', 'amount', 'pre_close', 'info']]

    return df


# 获取数据
sse_index_data = fetch_sse_index_data()



# 保存数据到 CSV 文件
csv_filename = 'sse_index_data_recent_2000.csv'
sse_index_data.to_csv(csv_filename, index=False)
print(f"\n数据已保存到 {csv_filename}")



# 设置当天的开始和结束时间
start = datetime.now().strftime('%Y-%m-%d') + ' ' + '9:30'
start = datetime.strptime(start, "%Y-%m-%d %H:%M")

end = datetime.now().strftime('%Y-%m-%d') + ' ' + '15:00'
end = datetime.strptime(end, "%Y-%m-%d %H:%M")


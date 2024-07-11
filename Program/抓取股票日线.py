import json
from random import randint
from urllib.request import urlopen
import pandas as pd

pd.set_option('expand_frame_repr', False)
pd.set_option('display.max_rows', 5000)

# =====创建随机数的函数
def _random(n=16):
    start = 10**(n-1)
    end = 10**(n-1)
    return str(randint(start, end))

# ===构建网址
# 参数
stock_code = 'sh600036'
k_type = 'day'
num = 640


# 构建url
url = 'http://web.ifzq.gtimg.cn/appstock/app/fqkline/get?_var=kline_{0}qfq&param={1},{0},,,{2},qfq&r={3}'.format(
    k_type, stock_code, num, _random()
)


# ===获取数据
content = urlopen(url).read().decode('utf-8')

# ===将数据转换成dict格式
content = content.split('=', maxsplit=1)[-1]
content = json.loads(content)


# ===将数据转换成DataFrame格式
# qfq是前复权的缩写
k_data = content['data'][stock_code]
if k_type in k_data:
    k_data = k_data[k_type]
elif 'qfq' + k_type in k_data:  # qfq是前复权的缩写
    k_data = k_data['qfq' + k_type]
else:
    raise ValueError('已知的key在dict中均不存在，请检查数据')
df = pd.DataFrame(k_data)

# ===对数据进行整理
rename_dict = {0: 'candle_end_time', 1: 'open', 2: 'close', 3: 'high', 4: 'low', 5: 'amount', 6: 'info'}
df.rename(columns=rename_dict, inplace=True)
df['candle_end_time'] = pd.to_datetime(df['candle_end_time'])
if 'info' not in df:
    df['info'] = None
df = df[['candle_end_time', 'open', 'high', 'low', 'close', 'amount', 'info']]

print(df)
df.to_csv('sh00036.csv', index=False)


























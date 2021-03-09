# coding:UTF-8
from bs4 import BeautifulSoup
from tqdm import tqdm
import json
import requests
import pandas as pd
import re

def get_HTML(url):
    header = {"User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Mobile Safari/537.36"}
    try:
        r = requests.get(url,timeout = 30,headers=header)
        r.raise_for_status()
        r.encoding = r.apparent_encoding   #指定编码形式
        return r.text
    except:
        return "please inspect your url or setup"

def get_stock_trend():
    print("Getting stock trending...")
    style_dic = {"399372":"大盘成长",
                 "399373":"大盘价值",
                 "399374":"中盘成长",
                 "399375":"中盘价值",
                 "399376":"小盘成长",
                 "399377":"小盘价值"}
    earn_dic = {}
    for idx, name in tqdm(style_dic.items()):
        url = "http://quotes.money.163.com/trade/lsjysj_zhishu_%s.html" % idx
        text = get_HTML(url)
        soup = BeautifulSoup(text,"html.parser")
        table=soup.findAll('table',{"class":"table_bg001 border_box limit_sale"})
        assert len(table) == 1, "Can't find history data from "+url+"!"
        table=table[0]
        trs = table.findAll('tr')
        whole_earn_percent = {}
        for i in range(1, len(trs)):
            tds = trs[i].findAll('td')
            date = tds[0].get_text()
            earn_percent = float(tds[6].get_text())
            whole_earn_percent.update({date:earn_percent})
        earn_dic.update({idx:whole_earn_percent})
    return earn_dic, style_dic

def get_fund_earning(fund_list):
    url = 'http://api.fund.eastmoney.com/f10/lsjz'
    earn_dic_f = {}
    fund_name = {}
    for idx in fund_list:
        html_url = "http://fundf10.eastmoney.com/jjjz_%s.html" % idx
        text = get_HTML(html_url)
        soup = BeautifulSoup(text,"html.parser")
        title = soup.findAll("head")[0].findAll("title")[0].get_text()
        title = re.findall('.*\)', title)[0]
        print("Getting data of", title)
        fund_name.update({idx:title})
        params = {
            "callback": "jQuery183007155143324859292_1615288467737",
            "fundCode": idx,
            "pageIndex": 1,
            "pageSize": 20,
        }
        cookie="xxxx"
        headers = {
            # 'Cookie': cookie,
            'Host': 'api.fund.eastmoney.com',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            'Referer': "http://fundf10.eastmoney.com/"
        }
        r = requests.get(url=url, headers=headers, params=params)
        text = re.findall('\((.*?)\)', r.text)[0]
        LSJZList = json.loads(text)['Data']['LSJZList']
        whole_earn_percent = {}
        for day_data in LSJZList:
            whole_earn_percent.update({day_data['FSRQ'].replace("-",""):float(day_data["JZZZL"])})
        earn_dic_f.update({idx:whole_earn_percent})
    return earn_dic_f, fund_name

if __name__=="__main__":
    with open("fund_list.json","r") as f:
        js_data = json.load(f)
    earn_dic_f, fund_name = get_fund_earning(js_data["fund_list"])
    earn_dic, style_dic = get_stock_trend()
    earn = pd.DataFrame(earn_dic)
    earn_f = pd.DataFrame(earn_dic_f)
    pda = earn.join(earn_f)
    pda.dropna(axis=0, how='any')
    corr = pda.corr()
    corr = corr.iloc[6:,:6]
    new_index = [fund_name[i] for i in corr.index]
    new_columns = [style_dic[i] for i in corr.columns]
    corr.index = new_index
    corr.columns = new_columns
    writer = pd.ExcelWriter("./corr.xlsx")
    corr.to_excel(writer, 'page_1', float_format = '%.4f')
    writer.save()
    print("The correlation saved to corr.xlsx")
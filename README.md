# CalcFundStyle
Calculate the correlation coefficient of some funds to different kinds of stock styles.

Usage:

Install python, then install required packages:

```shell
pip install bs4 tqdm requests pandas
```

Then modify the content of "fund_list.json". Write the code of the fund you want to compute correlation into the json.

Run the following code:

```python
python main.py
```

The result will be saved to corr.xlsx.

If your code is interrupted by network fluctuations, try a few more times (Since the code grabs fund information from fundf10.eastmoney.com and gets stock information from quotes.money.163.com). The code uses the data of recent 20 days to compute the correlation coefficient.
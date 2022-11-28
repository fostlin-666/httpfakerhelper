from helpers import lookup, usd
import time 

print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) )
# a = "AAPL"
# a = requests.get("https://cloud-sse.iexapis.com/stable/stock/123/quote?token=pk_afa1f1515d5f412ea4fda28716ab16f7")

# b = a.text

# c = b.replace('null',' ')
# print(c)

# d = json.loads(b)
# print(type(eval(b.replace('null',' '))))
# print(type(d))

# latestPrice = d["latestPrice"]
# companyName = d["companyName"]

# s = str(latestPrice) + companyName
a = lookup("33")

print(a is None)
# print(type(a))
# print(usd(a['price']))
# print(type(usd(a['price])))
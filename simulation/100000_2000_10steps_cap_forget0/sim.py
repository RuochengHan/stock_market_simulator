import numpy as np
from scipy.stats import chi2
import sys
from operator import add

def make_trade(trade_price, trade_num, ai_stock, ai_money, i, j):
    money = trade_num * trade_price
    ai_stock[j] = ai_stock[j] + trade_num
    ai_money[j] = ai_money[j] - money
    ai_stock[i] = ai_stock[i] - trade_num
    ai_money[i] = ai_money[i] + money


fstock = open('ai_stock.txt', 'w+')
fmoney = open('ai_money.txt', 'w+')
fwealth = open('ai_wealth.txt', 'w+')
fprice = open(sys.argv[1], 'w+')

# initiate
price = 1
price_df = 20
num_stock = 2000
all_money = 2000
num_ai = 100
time = 100000
forget_ratio = 0
large = 99999
small = 0
#norm = 2.718281828459045 ** (1/32)
norm = 1

ai_stock = np.random.multinomial(num_stock, np.ones(num_ai)/num_ai, size=1)[0]
ai_money = np.random.dirichlet(np.ones(num_ai), size=1)[0] * all_money
#ai_money[0] = 200
ai_wealth = ai_stock * price + ai_money
ai_pred = np.random.lognormal(0, 0.1, size=num_ai) / norm * price  #lognormal

#print(ai_pred)
#print(sum(ai_pred))

ai_sell_price = [large] * num_ai
ai_sell_num = [0] * num_ai
ai_buy_price = [small] * num_ai
ai_buy_num = [0] * num_ai
ai_trade = [0] * num_ai # sell is 1, buy is 2
ai_rich = [False] * num_ai

volume = 0
exchange = 0
t = 0
while (t < time):

    #print(ai_pred)
    price_last = price
    sell_list = []
    buy_list = []
    for i in range(num_ai): # trade list
        if (ai_stock[i] > 0) and (ai_pred[i] < price): # sell_list
            ai_sell_price[i] = (1 + np.random.normal(0, 0.001, 1)[0]) * price # this will be a variable in the future
            ai_sell_num[i] = np.random.randint(ai_stock[i] + 1, size=1)[0]
            sell_list.append(i)
            ai_trade[i] = 1
        elif (ai_money[i]/price >= 1) and (ai_pred[i] > price): # buy_list
            ai_buy_price[i] = (1 + np.random.normal(0, 0.001, 1)[0]) * price # this will be a variable in the future
            ai_buy_num[i] = np.random.randint(int(ai_money[i]/price) + 1, size=1)[0]
            buy_list.append(i)
            ai_trade[i] = 2
        i = i + 1

    trade_list = sell_list + buy_list
    #print(trade_list)
    #print(len(trade_list))
    if buy_list != []:
        max_buy_price = np.max([ai_buy_price[l] for l in buy_list])
    if sell_list != []:
        min_sell_price = np.min([ai_sell_price[l] for l in sell_list])

    np.random.shuffle(trade_list)
    volume = 0
    trade_times = 0
    for i in trade_list: # trade
        if (min_sell_price > max_buy_price):
            break

        if (ai_trade[i] == 1): # sell from buy_list
            j = buy_list[np.argmax([ai_buy_price[l] for l in buy_list])]
            max_buy_price = ai_buy_price[j]
            if (ai_sell_price[i] <= max_buy_price):
                trade_num = min(ai_sell_num[i], ai_buy_num[j])
                make_trade(max_buy_price, trade_num, ai_stock, ai_money, i, j) # i->j +: sell
                ai_sell_num[i] = ai_sell_num[i] - trade_num
                ai_buy_num[j] = ai_buy_num[j] - trade_num
                if ai_sell_num[i] == 0:
                    ai_sell_price[i] = large
                if ai_buy_num[j] == 0:
                    ai_buy_price[j] = small
                price = max_buy_price
                volume = volume + trade_num * 2
                trade_times = trade_times + 1
        else: # buy from sell_list
            j = sell_list[np.argmin([ai_sell_price[l] for l in sell_list])]
            min_sell_price = ai_sell_price[j]
            #print(str(ai_trade[j]) + ' ' + str(j))
            #print([l for l in sell_list])
            if (ai_buy_price[i] >= min_sell_price):
                trade_num = min(ai_buy_num[i], ai_sell_num[j])
                make_trade(min_sell_price, trade_num, ai_stock, ai_money, j, i) # j->i : sell
                ai_sell_num[j] = ai_sell_num[j] - trade_num
                ai_buy_num[i] = ai_buy_num[i] - trade_num
                if ai_sell_num[j] == 0:
                    ai_sell_price[j] = large
                if ai_buy_num[i] == 0:
                    ai_buy_price[i] = small
                price = min_sell_price
                volume = volume + trade_num * 2
                trade_times = trade_times + 1

        if (trade_times == 10):
            break

    ai_wealth = ai_stock * price + ai_money


    # total capital control
    mean_pred = np.mean(ai_pred)
    if (mean_pred > price):
        ai_money = np.array(list(map(add, ai_money, chi2.rvs(0.1, size=num_ai))))
    else:
        ai_money = np.array(list(map(add, ai_money, -chi2.rvs(0.1, size=num_ai))))
        ai_money[ai_money < 0] = 0

    for l in range(num_ai):
        # ai pred renew
        r = np.random.uniform(0, 1, size=1)[0]
        if (r < forget_ratio):
            # forget about previous guess
            ai_pred[l] = np.random.lognormal(0, 0.1, size=1)[0] / norm * price
            #ai_pred[l] = chi2.rvs(price_df, size=1)[0] / price_df * price
        else:
            # change according to previous guess
            guess = ((ai_pred[l] - price_last) * (price - price_last) >= 0)
            if not guess:
                ai_pred[l] = ai_pred[l] * (1 + (price / price_last - 1) * np.random.normal(1, 1, 1)[0])
                #ai_pred[l] = ai_pred[l] + (price - price_last) * np.random.normal(1, 1, 1)[0]

        # ai control
        if (ai_rich[l] is True) and (ai_stock[l] == 0):
            # ai renew if rich ai sell all stock
            ai_pred[l] = np.random.lognormal(0, 0.1, size=num_ai)[0] / norm * price
            ai_money[l] = chi2.rvs(price_df, size=1)[0] / price_df * 20
            exchange = exchange + 1
            ai_rich[l] = False

        elif (ai_money[l] < price and ai_stock[l] == 0):
            # ai renew if poor ai do not have enough wealth
            ai_pred[l] = np.random.lognormal(0, 0.1, size=num_ai)[0] / norm * price
            ai_money[l] = chi2.rvs(price_df, size=1)[0] / price_df * 20
            exchange = exchange + 1

        elif (ai_wealth[l] > 0.1 * sum(ai_wealth)):
            # ai marked rich if owns 10% of total wealth
            ai_pred[l] = 0
            ai_rich[l] = True

        # add banker superiority
        #ai_pred_all = np.mean(ai_pred)
        #ai_wealth_ratio = ai_wealth / sum(ai_wealth) # random?
        #ai_pred = ai_wealth_ratio * ai_pred_all + (1 - ai_wealth_ratio) * ai_pred
    # output
    print(str(price) + '\t' + str(sum(ai_money)) + '\t'
            + str(trade_times) + '\t'
            + str(volume) + '\t' + str(t))

    fprice.write(str(price) + ' ' +  str(volume) + '\n')
    for i in range(num_ai):
        fstock.write(str(ai_stock[i]) + ' ')
        fmoney.write(str(ai_money[i]) + ' ')
        fwealth.write(str(ai_wealth[i]) + ' ')
    fstock.write(str(ai_stock[i]) + '\n')
    fmoney.write(str(ai_money[i]) + '\n')
    fwealth.write(str(ai_wealth[i]) + '\n')

    t = t + 1

print(str(exchange))

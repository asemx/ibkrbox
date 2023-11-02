from datetime import datetime
import sys
import argparse
import pickle
import pandas as pd
from ib_insync import *
import platform
import numpy as np
import math
import tempfile
from pathlib import Path

def get_ib(ip, port, acc=""):
    ib = IB()
    ib.connect(ip, port, clientId=19, timeout=20, account=acc)
    return ib

def get_last(ib, con, dur="3600 S", bar="1 min", rth = False):
    ib.reqMarketDataType(3)
    try:
        bars = ib.reqHistoricalData(
            con,
            endDateTime="",
            durationStr=dur,
            barSizeSetting=bar,
            whatToShow="TRADES",
            useRTH=rth,
        )
    except:
        bars = []
    if len(bars) == 0:
        last = math.nan
        if "D" not in dur:
            last = get_last(ib, con, dur="4 D", bar="1 day")
        return last
    return bars[-1].close

def box_trade(
    ib,
    expiry,
    strike1,
    strike2,
    limit,
    quantity=1,
    short=False,
    is_future=False,
    show=True,
    acc = "",
    timeout = 10,
    max=None
):
    assert strike1 < strike2, "incorrect strikes"
    sym = "ES" if is_future else "SPX"
    exchange = "CME" if is_future else "SMART"
    mul = 50 if is_future else 100

    if not short:
        boxorder = ["BUY", "SELL", "SELL", "BUY"]
        assert limit > 0.0
        assert max >= limit
    else:
        boxorder = ["SELL", "BUY", "BUY", "SELL"]
        assert limit < 0.0
        assert max >= limit

    boxspread = [
        FuturesOption(sym, expiry, S, T, exchange=exchange, tradingClass="EW")
        if is_future
        else Option(sym, expiry, S, T, exchange=exchange, tradingClass="SPX")
        for S in (strike1, strike2)
        for T in ("C", "P")
    ]
    boxspread = ib.qualifyContracts(*boxspread)

    legs = [
        ComboLeg(conId=x[0].conId, ratio=1, action=x[1], exchange=exchange)
        for x in zip(boxspread, boxorder)
    ]
    bag = Contract(
        symbol=sym, secType="BAG", exchange=exchange, currency="USD", comboLegs=legs
    )
    _df = util.df(boxspread)[
        ["symbol", "strike", "right", "lastTradeDateOrContractMonth"]
    ]
    _df.loc[:, "action"] = util.df(bag.comboLegs)["action"]
    print(f"\nBox Legs:\n{_df}")
    if not short:
        print(
            f"Lend {quantity*int(limit*mul)} today, receive {quantity*(strike2-strike1)*mul} on {expiry}"
        )
    else:
        print(
            f"Borrow {abs(quantity*int(limit*mul))} today, repay {quantity*(strike2-strike1)*mul} on {expiry}"
        )
    if show:
        return None

    trade = None
    mintick = .05
    for limit in np.arange(limit, max+mintick, mintick):
        if quantity == 0: break
        print(f'placing limit order for {quantity} at {limit:.2f}. Waiting for {timeout}s...')
        trade = ib.placeOrder(bag, LimitOrder("BUY", quantity, limit, account=acc))
        try:
            ib.sleep(timeout)
        except:
            ib.cancelOrder(trade.order)
            return None
        if trade.filled() != 0:
            print(f'order filled for {trade.filled()} at {trade.orderStatus.avgFillPrice:.2f}')
        if trade.filled() != quantity:
            print(f'cancelling unfilled order, remaining quantity {quantity}')
            ib.cancelOrder(trade.order)
            ib.sleep(3)
        else:
            break
        quantity -= trade.filled()
    return trade


def get_rate(expiry, show=True):
    days = (datetime.strptime(expiry, "%Y%m%d") - datetime.now()).days
    # pull rates from treasury
    assert days < 7 * 365
    dt = datetime.now().strftime("%Y%m%d")
    tmpf = (
        Path("/tmp" if platform.system() == "Darwin" else tempfile.gettempdir())
        / f"{dt}.rates"
    )
    try:
        rates_ = pd.read_pickle(tmpf)
        rates = list(rates_.iloc[0])[1:11]
    except:
        rates = None
    if not rates:
        url_ = f'https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/all/{datetime.now().strftime("%Y%m")}?type=daily_treasury_yield_curve&field_tdr_date_value_month={datetime.now().strftime("%Y%m")}&page&_format=csv'
        # print(url_)
        rates_ = pd.read_csv(url_)
        assert list(rates_.columns)[1:11] == [
            "1 Mo",
            "2 Mo",
            "3 Mo",
            "4 Mo",
            "6 Mo",
            "1 Yr",
            "2 Yr",
            "3 Yr",
            "5 Yr",
            "7 Yr",
        ], "problem with treasury rates site, pass rate or limit price manually"
        rates = list(rates_.iloc[0])[1:11]
        rates_.to_pickle(tmpf)
    assert rates != None, "problem with rate calculation, pass rate or limit manually"
    rate = rates[
        [
            n
            for n, i in enumerate(
                [30, 60, 90, 120, 180, 365 * 1, 365 * 2, 365 * 3, 365 * 5, 365 * 7]
            )
            if i > days
        ][0]
    ]
    if show:
        print(f"selected treasury rate: {rate}\n{rates_}")
    return rate


def get_expiry_es(ib, months):
    exp = [
        x.realExpirationDate
        for x in ib.reqContractDetails(Future("ES", exchange="CME"))
    ]
    exp.sort()
    exp = exp[: int(months / 3) + 2]
    for i in exp:
        spx = Future("ES", i, "CME")
        spx = ib.qualifyContracts(spx)[0]
        chains = ib.reqSecDefOptParams(spx.symbol, "CME", spx.secType, spx.conId)
        chain = next(c for c in chains if c.exchange == "CME")
        exps = [x.expirations for x in chains if x.tradingClass == "EW"][0]
        if months < 1:
            return exps[0]
        for j in exps:
            if (datetime.strptime(j, "%Y%m%d") - datetime.now()).days >= months * 30:
                return j
    assert False, "expiry not found"


def get_expiry(ib, months):
    spx = ib.qualifyContracts(Index("SPX", "CBOE"))[0]
    chain = next(
        c
        for c in ib.reqSecDefOptParams(spx.symbol, "", spx.secType, spx.conId)
        if c.tradingClass == "SPX" and c.exchange == "SMART"
    )
    expdays = [
        abs(months * 30 - (datetime.strptime(exp, "%Y%m%d") - datetime.now()).days)
        for exp in chain.expirations
    ]
    _, idx = min((v, i) for i, v in enumerate(expdays))
    return chain.expirations[idx]


def get_strikes(ib, amount, is_futures):
    spx = ib.qualifyContracts(Index("SPX", "CBOE"))[0]
    price = get_last(ib, spx)
    print(f"SPX last close: {price}")
    assert not util.isNan(price) and price > 100, "invalid SPX market price"
    spread = int(amount / (50.0 if is_futures else 100.0))
    assert spread % 10 == 0, "use amount in 1000s"
    strike = int(price / 100) * 100
    if spread <= 200:
        return strike, strike + spread
    else:
        rem = spread % 200
        remhalf = (spread - rem) / 2
        return strike - remhalf, strike + remhalf + rem


def get_limit(expiry, rate, s1, s2, is_future=False):
    days = (datetime.strptime(expiry, "%Y%m%d") - datetime.now()).days
    if not rate:
        rate = get_rate(expiry) + 0.30
    limit = (s2 - s1) / (1 + rate / 100.0) ** (days / 365)
    mintick = 0.05
    limit = mintick * round(limit / mintick)
    return limit

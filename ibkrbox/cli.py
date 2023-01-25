import logging

import click
import click_log

from ib_insync import *
from .ibkrbox import *

logger = logging.getLogger(__name__)
click_log.basic_config(logger)

CONTEXT_SETTINGS = dict(
    help_option_names=["-h", "--help"], auto_envvar_prefix="IBKRBOX"
)


@click.command(context_settings=CONTEXT_SETTINGS)
@click_log.simple_verbosity_option(logger)
@click.option(
    "-i",
    "--ip",
    default="localhost",
    help="ip address or hostname of IBKR tws or gateway",
    type=str,
)
@click.option(
    "-p", "--port", default=7496, help="port of IBKR tws or gateway", type=int
)
@click.option("--s1", help="first strike", type=float)
@click.option("--s2", help="second strike", type=float)
@click.option("-r", "--rate", help="rate to use", type=float)
@click.option("-a", "--amount", help="amount per contract", type=float)
@click.option("-m", "--months", help="duration in months", type=int)
@click.option("-e", "--expiry", help="contract expiry to use", type=str)
@click.option("-l", "--limit", help="limit price", type=float)
@click.option("-q", "--quantity", default=1, help="num contracts", type=int)
@click.option("--short", help="sell the box to loan", is_flag=True)
@click.option("--es", help="use ES options", is_flag=True)
@click.option("--show", help="show only, do not send order", is_flag=True)
def cli(
    ip, port, s1, s2, rate, amount, months, expiry, limit, quantity, short, es, show
):
    """Construct a Box Spread using SPX or ES options.
    Use "show" option to display the order only, without executing.
    """
    assert months != None or limit != None, "pass limit price, or months to calc limit"
    assert months != None or expiry != None, "pass expiry, or months to calc expiry"
    assert amount != None or (
        s1 != None and s2 != None
    ), "pass strikes or amount per contract"
    ib = get_ib(ip, port)
    assert ib.isConnected(), "IB connection error, please retry"
    if not expiry:
        expiry = get_expiry_es(ib, months) if es else get_expiry(ib, months)
    if s1 and not s2:
        s2 = s1 + int(amount / (50.0 if es else 100.0))
    if s2 and not s1:
        s1 = s2 - int(amount / (50.0 if es else 100.0))
    if not s1:
        s1, s2 = get_strikes(ib, amount, es)
    if not limit:
        if not rate:
            rate = get_rate(expiry) + 0.30
        limit = get_limit(expiry, rate, s1, s2, es)
    limit = -abs(limit) if short else abs(limit)
    print(f"\nUsing expiry, s1, s2, limit, quantity, short, es: {expiry}, {s1}, {s2}, {limit}, {quantity}, {short}, {es}"
        )
    trade = box_trade(ib, expiry, s1, s2, limit, quantity, short, es, show)
    if rate: print(f'rate: {rate}')
    if trade != None:
        ib.sleep(5)
        print(util.df(trade.log))

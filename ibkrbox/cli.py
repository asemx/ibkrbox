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
@click.option("--acc", default="", help="account id to use", type=str)
@click.option("-l", "--limit", help="limit price", type=float)
@click.option("-t", "--timeout", default=20, help="seconds to wait for order fill", type=int)
@click.option("-l", "--limit", help="limit price", type=float)
@click.option("--offset", help="will try until price limit+-offset", default=None, type=float)
@click.option("-q", "--quantity", default=1, help="num contracts", type=int)
@click.option("--short", help="sell the box to loan", is_flag=True)
@click.option("--es", help="use ES options", is_flag=True)
@click.option("--execute", help="send order for execution", is_flag=True)
def cli(
    ip, port, s1, s2, rate, amount, months, expiry, limit, quantity, short, es, execute, acc,timeout,offset
):
    """Construct a Box Spread using SPX or ES options.
    Use "execute" option to send order for execution.
    """
    assert months != None or limit != None, "pass limit price, or months to calc limit"
    assert months != None or expiry != None, "pass expiry, or months to calc expiry"
    assert amount != None or (
        s1 != None and s2 != None
    ), "pass strikes or amount per contract"
    ib = get_ib(ip, port, acc)
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
    if not offset:
        max = limit
    else:
        assert offset/limit < .05, "offset should be with in spread, or less than 5%"
        max = limit + offset
    mintick = 0.05
    limit, max = mintick * round(limit / mintick), mintick * round(max / mintick)
    print(f"\nUsing expiry, s1, s2, price limit/max, quantity, short, es: {expiry}, {s1}, {s2}, {limit:.2f}/{max:.2f}, {quantity}, {short}, {es}"
        )
    if rate: print(f'using interest rate: {rate:.2f}')
    trade = box_trade(ib, expiry, s1, s2, limit, quantity, short, es, not execute, acc, timeout, max)
    if trade != None:
        ib.sleep(5)

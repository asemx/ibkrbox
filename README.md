# ibkrbox
Constructs a Box Spread combo order for SPX or ES futures option, only required arguments are amount you want to lend or borrow , and for how many months.

This utility will automatically look up current treasury rates, and add .30 to get the yield rate. This will be used to calculate limit price. rate or limit price can be overridden as needed.

It can also automatically calculate the right strikes and spread, with approximate expiry for given duration. All of these can be overridden as needed.

This utility is easy to install and use with existing IBKR TWS or gateway session. Just make sure to enable API access in the GUI of IBKR TWS or gateway.

Please file a issue if you notice any problem(s).

## Installation
```code
pip install ibkrbox
```

## Usage

```code
ibkrbox -h
```
<img width="630" alt="image" src="https://github.com/asemx/ibkrbox/assets/998264/0e6bf269-8bb5-4387-8d50-b29105095ef3">

### 1. construct a combo SPX Box Spread lending for 50K, duration 4 months (use "--execute" option to send the order to IBKR)
This will not execute the order, so you can safely run this. When executing, it will retry orders until "offset" limit.
```code
ibkrbox -a 50000 -m 4 --offset .50
```
<img width="929" alt="image" src="https://github.com/asemx/ibkrbox/assets/998264/b73d35d3-a3c0-4a7f-aaa6-3ffa40afab43">


### 2. same as above but using Options on ES Futures (use "--execute" option to send the order to IBKR)
This will not execute the order, so you can safely run this.
```code
ibkrbox -a 50000 -m 4 --es
```
<img width="469" alt="image" src="https://user-images.githubusercontent.com/998264/215017485-1fb9cd8c-bf0c-44e8-8775-7844831a8f85.png">



### 3. construct a combo SPX Box Spread borrowing for 50K, duration 4 months (use "--execute" option to send the order to IBKR) 
This will not execute the order, so you can safely run this.
```code
ibkrbox -a 50000 -m 4 --short
```

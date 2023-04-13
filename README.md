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
<img width="630" alt="image" src="https://user-images.githubusercontent.com/998264/215016906-f72926c9-bada-4430-a2bb-c07db5ea69c6.png">


### 1. construct a combo SPX Box Spread lending for 50K, duration 4 months (use "--execute" option to send the order to IBKR)
This will not execute the order, so you can safely run this.
```code
ibkrbox -a 50000 -m 4
```
<img width="474" alt="image" src="https://user-images.githubusercontent.com/998264/215017182-3577e49f-7787-41c9-b500-303b6afded19.png">


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

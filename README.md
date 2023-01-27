# ibkrbox
Constructs a Box Spread combo order for SPX or ES futures option, only required arguments are amount you want to lend or borrow , and for how many months.

This utility will automatically look up current treasury rates, and add .30 to get the yield rate. This will be used to calculate limit price. rate or limit price can be overridden as needed.

It can also automatically calculate the right strikes and spread, with approximate expiry for given duration. All of these can be overridden as needed.

This utility is easy to install and use with existing IBKR TWS or gateway session. Just make sure to enable API access in the GUI of IBKR TWS or gateway.

## Installation
```code
pip install ibkrbox
```

## Usage

```code
ibkrbox -h
```
<img width="629" alt="image" src="https://user-images.githubusercontent.com/998264/200383898-c9433221-0107-4366-9b06-60179233f5c1.png">


### 1. construct a combo SPX Box Spread lending for 50K, duration 4 months (use "--execute" option to send the order)
```code
ibkrbox -a 50000 -m 4
```
<img width="795" alt="image" src="https://user-images.githubusercontent.com/998264/200384213-06b1e995-6cfb-4c68-a022-53385b3e494f.png">


### 2. construct a combo SPX Box Spread borrowing for 50K, duration 4 months, and display.
```code
ibkrbox -a 50000 -m 4 --short
```

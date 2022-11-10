# Python 3.X Bitcoin blockchain converter 

The purpose of this Python 3.X pipeline is to retrieve, compress and store the transactions from the Bitcoin blockchain into a big flat int array. This makes output data compatible with all languages, allowing researchers to analyze the data regardless of their tech stack of choice. 

The motivation behind this project is my MSc thesis, where the goal is to extract and analyze Bitcoin's user graph based on the output of this pipeline.

## Features ##

The pipeline provides the three following functionalities:
  
- Normalize and store transaction data into an uint32 array

- Normalize, cluster transaction inputs and outputs using the [common-input-ownership](https://en.bitcoin.it/wiki/Common-input-ownership_heuristic) heuristic, and store transaction data into an in uint32 array

- Normalize/cluster, create Bitcoin user graph out of the clustered transaction data, and store it into an uint32 array

- Each transaction consists of its txid, input/output addresses, output values, timestamp and fee (the sum value of the inputs is stored, hence transaction fee can be calculated as follows: _sum_(inputsTotalValue) - _sum_(outputsTotalValue))


## Hardware requirements ##
To get the the transaction data you'll need:
- 16GB RAM
- 600GB of storage (Bitcoin blockchain weighs approximately 440GB as of November 2022, our compressed version trims it down to about 45GB)

To get the clustered transaction data you'll need:
- 128GB RAM (output dictionary of Union-Find algorithm used to cluster the addresses weights approximately 92GB and requires 9.2GB of storage in _.pickle_ format)
- 600GB of storage

## Installing ##

The project has very limited dependencies by design in order to make it easy to install and use for researchers from all backgrounds. We also assume that researchers already have the Bitcoin blockchain data available. If not, you can get it using [Bitcoin Core](https://bitcoin.org/en/download).

To parse the Bitcoin blockchain, we used a [Python blockchain parser](https://github.com/alecalve/python-bitcoin-blockchain-parser) developed by [@alecalve](https://github.com/alecalve). 

To download all of the dependencies, open up a terminal, cd into the repository local directory (in your computer) and type in the following command:

    python -m pip install -r requirements.txt

## Data Format ##

Each transaction is represented by a sequence of 8-byte integeres. The pattern used is the following:

    txid, input addresses count (n), input_0, ..., inputAddr_n-1, output addresses count (m), outputAddr_0, ..., output_m-1, outputValue_0_flag, outputValue_0, ..., outputValue_m-1_flag, outputValue_m-1, timestamp, sumOfInputValues_flag, sumOfInputValues
    
    Element count per transaction: n + 3*m + 6

The purpose of the _flag_ values preceding each ouput value and the sum of inputs is to indicate whether the following value is denominated in Bitcoin or Satoshi. 

In the Bitcoin blockchain, output values are denominated in Satoshi; 100M Satoshi = 1 Bitcoin. Satoshis are non-negative integers. A uint32 can store any integer in the range (0,2^32-1).

Hence, to store values greater than or equal to 42.94967296 Bitcoin in uint32, a we convert the Satoshi value to Bitcoin and round it to the second decimal point, hence the value is now stored in integer format. 

The following example better illustrates this:

    Value flags:
    0: following value is Satoshi
    1: following value is Bitcoin
    

    Raw transaction:
    Input 0: 4312340000 Satoshi
    Input 1: 100000000 Satoshi
    
    Output 0: 4312340000 Satoshi
    Output 1: 4000000 Satoshi
    Output 2: 5000000 Satoshi
    
    Output_0 value: 4,312,340,000 Satoshi
    Convert to Bitcoin: 43.1234
    Round to second decimal: 43.12
    Cast to integer: 4312
    Value flag: 1
    
    Output_1 value: 4,000,000 Satoshi
    Value flag: 0
    
    Output_2 value: 5,000,000 Satoshi
    Value flag: 0
    
    sumOfInputValues: 4412340000
    Convert to Bitcoin: 44.12
    Round to second decimal: 44.12
    Cast to integer: 4412
    Value flag: 1
    
    
    Normalized transaction = [txid, 2, inpAddr_0, inpArr_1, 3, outAddr_0, outAddr_1, outAddr_2, 1, 4312, 0, 4000000, 0, 5000000, timestamp, 1, 4412]
    
    Transaction fee = 44.12 - (43.12 + 0.4 +0.5) = 0.1 Bitcoin
    
    
    
    
    




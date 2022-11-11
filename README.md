# Python 3 Bitcoin Blockchain Converter 

The purpose of this Python 3 pipeline is to retrieve, compress and store the transactions from the Bitcoin blockchain into a big flat int array. This makes output data compatible with all languages, allowing researchers to analyze the data regardless of their tech stack of choice. 

The motivation behind this project is my MSc thesis, where the goal is to extract and analyze Bitcoin's user graph based on the output of this pipeline. The pipeline's execution time is about three days long; the sub-tasks dominating execution time are _downloadBlockchain.py_ and _getInputs.py_. 

## Table of Contents ##
- [**Features**](#features)
- [**Hardware Requirements**](#hardware-requirements)
- [**Installing**](#installing)
- [**Data Compression And Normalization**](#data-compression-and-normalization)


## Features ##

The pipeline provides the three following functionalities:
  
- Compress, normalize and store transaction data into an uint32 array

- Compress, normalize, cluster transaction inputs and outputs using the [common-input-ownership](https://en.bitcoin.it/wiki/Common-input-ownership_heuristic) heuristic, and store transaction data into an in uint32 array

- Compress/normalize/cluster, create Bitcoin user graph out of the clustered transaction data, and store it into an uint32 array

Each transaction consists of the following attributes:
- Txid
- Input addresses
- Output addresses
- Output values
- Timestamp 
- Fee

Additional transaction attributes can be added by manipulating the code accordingly. For instance, categorical string data, such as output script type, could be stored by casting each value to an integer.

## Hardware requirements ##
To store the the unclustered blockchain you'll need:
- 16GB RAM
- 600GB of storage (Bitcoin blockchain weighs approximately 440GB as of November 2022, our compressed version trims it down to about 45GB)

To store either the clustered blockchain or the graph you'll need:
- 128GB RAM (output dictionary of Union-Find algorithm used to cluster the addresses weights approximately 92GB and requires 9.2GB of storage in _.pickle_ format)
- 600GB of storage

To store both the clustered blockchain and the graph you'll need:
- 128GB RAM
- 650GB of storage 

## Installing ##

By design, the project has very limited dependencies in order to make it easy to install and use for researchers from all backgrounds. We also assume that researchers already have the Bitcoin blockchain data available. If not, you can get it using [Bitcoin Core](https://bitcoin.org/en/download).

To parse the Bitcoin blockchain, we used a [Python blockchain parser](https://github.com/alecalve/python-bitcoin-blockchain-parser) developed by [@alecalve](https://github.com/alecalve). 

To download all of the dependencies, open up a terminal, cd into the repository's local directory (in your computer) and type in the following command:

    python -m pip install -r requirements.txt

## Data Compression And Normalization ##

Each transaction is represented by a sequence of 8-byte integeres. The pattern used is the following:

    txid, input addresses count (n), input_0, ..., inputAddr_n-1, output addresses count (m), outputAddr_0, ..., output_m-1, outputValue_0_flag, outputValue_0, ..., outputValue_m-1_flag, outputValue_m-1, timestamp, sumOfInputValues_flag, sumOfInputValues
    
    Element count per transaction: n + 3*m + 6

While we don't store the transaction fee explicitly, it can be trivially calculated as follows: _sumOfInputValues_ - _sum_(outputValue_0 : outputValue_m-1).

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
    Convert to Bitcoin: 44.1234
    Round to second decimal: 44.12
    Cast to integer: 4412
    Value flag: 1
    
    
    Normalized transaction = [txid, 2, inpAddr_0, inpArr_1, 3, outAddr_0, outAddr_1, outAddr_2, 1, 4312, 0, 4000000, 0, 5000000, timestamp, 1, 4412]
    
    Transaction fee = 44.12 - (43.12 + 0.4 +0.5) = 0.1 Bitcoin


To convert input/output addresses and txid values from HEX to uint32 we used the [MurmurHash](https://en.wikipedia.org/wiki/MurmurHash) non-cryptographic hash function. It is a computationally efficient algorithm and features a relatively low collision rate.

Approximately 3.5% of total txids resulted in a collision. As of November 2022, there are about 770M transactions on the Bitcoin blockchain, hence approximately 2.7M txids will be hashed into an uint32 that an older txid had already been hashed to during the conversion process.

In order to be able to traverse the blockchain in this flat array format efficiently, we store each transaction's offset in a separate array. Therefore, given the transaction order in the blockchain, transaction _i_ can be trivially retrieved from the array as follows:

    Transaction i's slice in the array:
    transactionArray [ offsets[i] : offsets[i+1] ]
    
    Transaction i length = offsets[i+1] - offsets[i]

## Pipeline: Step-by-step ##

The pipeline consists of five stages, each represented by an individual script in the  _src_ directory:

1. Get blockchain
2. Get input addresses
3. Get cluster
4. Get flat blockchain
5. Get graph

According to a researcher's needs, s/he can opt for the following outputs:

1. Unclustered blockchain
2. Clustered blockchain
3. Blockchain user graph
4. Combo (i.e. graph + clustered blockchain)

Stages 3 and 5 are skipped when the desired output is the compressed Bitcoin blockchain with no address clustering. If clustering and/or the user graph are desired, stages 3 and 5 will be part of the execution pipeline. 

### getBlockchain.py ###
In the first stage, the corresponding script parses the raw blockchain data using the aforementioned library, casting transaction data to integers and storing it in a series of Python dictionaries. Each dictionary key corresponds to a hashed transaction id, and the corresponding value is a Python list containing the transaction data. In then event of a hash collision, a key points to a list of lists (a list of transactions whose txids share the same hash). 

During our research, we didn't encounter any keys pointing to more than two transactions, hence the cost of hash collisions is limited.

        Dictionary entry with no hash collision:
        {txid_0: [txid_0_data]}

        Dictionary entry with hash collision:
        {txid_0: [ [txid_0_data],  [txid_1_data] ..., [txid_n_data]]}

As aforementioned, we store transaction data in Python lists. While it is customary to store numeric data in Numpy arrays, we avoided using the particular data structure throught the pipeline (except for the output data) for the following reasons:

1. Traversing numpy arrays is considerbly slower than traversing Python lists due to [on-the-fly object unpacking](https://stackoverflow.com/questions/63870418/why-numpy-arrays-are-slower-than-lists-with-for-loops)
2. Numpy is an optimal choice for vector operations. No vector operations are performed throught the pipeline, traversing the array/list data is the dominant cost.
3. Storage footprint is approximately the same in pickle format. Pickle files weigh approximately 10% of an object's memory footprint. 
4. While a larger memory footprint is a tradeoff when using lists over Numpy arrays, list traversal provides an 5-fold (minimum) performance boost. Most researchers can get their hands on 16GB/128GB machines to get the blockchain and/or the graph respectively.

The script's output is an arbitrary number of dictionaries stored in pickle files. Given that the pipeline was designed so that anyone with a 16GB machine can get the unclustered blockchain, for every 5M transactions scanned, the script dumps the data in a .pickle file to avoid usign up all the available memory. Once main memory is full and virtual memory is employed, the result is a severe performance hit. Hence, storing the data in many smaller files prevents this from happening.

### getInputAddr.py ###
In the second stage, the script parses the dictionarys created in the first stage to retrieve the input addresses. 





# Python 3.X Bitcoin blockchain converter 

The purpose of this Python 3.X pipeline is to retrieve the transactions from the Bitcoin blockchain and store them into a big flat array rendering output data compatible with all languages.

The motivation behind this project is my MSc thesis, where the goal is to extract and analyze Bitcoin's user graph based on the output of this pipeline.

## Features ##

The pipeline provides the three following functionalities:
  
- Normalize and store transaction data into an int32 array

- Normalize, cluster transaction inputs and outputs using the [common-input-ownership]([url](https://en.bitcoin.it/wiki/Common-input-ownership_heuristic)) heuristic, and store transaction data into an in int32 array

- Normalize/cluster, create Bitcoin user graph out of the clustered transaction data, and store it into an int32 array


## Hardware requirements ##
To get the the transaction data you'll need:
- 16GB RAM
- 600GB of storage (Bitcoin blockchain weighs approximately 440GB as of November 2022, our compressed version trims it down to about 45GB)

To get the clustered transaction data you'll need:
- 128GB RAM (output dictionary of Union-Find algorithm used to cluster the addresses weights approximately 92GB and requires 9.2GB of storage in _.pickle_ format)
- 600GB of storage

## Installing ##

The project has very limited dependencies by design in order to make it easy to install and use for researchers from all backgrounds. We also assume that researchers already have the Bitcoin blockchain data available. If not, you can get it using [Bitcoin Core]([url](https://bitcoin.org/en/download)).

To parse the Bitcoin blockchain, we used a [Python blockchain]([url](https://github.com/alecalve/python-bitcoin-blockchain-parser)) parser developed by @alecalve. 

To download the module, type in the following command:

    python -m pip install blockchain-parser


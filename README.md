# Python 3 Bitcoin Blockchain Converter 

The purpose of this Python 3 pipeline is to retrieve, compress and store the transactions from the Bitcoin blockchain into a big flat int array. This makes output data compatible with all languages, allowing researchers to analyze the data regardless of their tech stack of choice. 

The motivation behind this project is my MSc thesis, where the goal is to extract and analyze Bitcoin's user graph based on the output of this pipeline. The pipeline's execution time is about three days long; the sub-tasks dominating execution time are __getBlockchain.py__ and __getInputAddr.py__. 

## Table of Contents ##
- [**Features**](#features)
- [**Hardware Requirements**](#hardware-requirements)
- [**Installing**](#installing)
- [**Data Compression And Normalization**](#data-compression-and-normalization)
- [**Pipeline: Step-by-step**](#pipeline-step-by-step)
- [**Execution**](#execution)


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

    txid, input addresses count (n), input_0, ..., inputAddr_n-1, output addresses count (m), outputAddr_0, ..., outputAddr_m-1, outputValue_0_flag, outputValue_0, ..., outputValue_m-1_flag, outputValue_m-1, timestamp, sumOfInputValues_flag, sumOfInputValues
    
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


To convert input/output addresses (scriptPubKey of output) and txid values from HEX to uint32 we used the [MurmurHash](https://en.wikipedia.org/wiki/MurmurHash) non-cryptographic hash function. It is a computationally efficient algorithm and features a relatively low collision rate.

Approximately 3.5% of total txids resulted in a collision. As of November 2022, there are about 770M transactions on the Bitcoin blockchain, hence approximately 2.7M txids will be hashed into an uint32 that an older txid had already been hashed to during the conversion process.

In order to be able to traverse the blockchain in this flat array format efficiently, we store each transaction's offset in a separate array. Therefore, given the transaction order in the blockchain, transaction _i_ can be trivially retrieved from the array as follows:

    Transaction i's slice in the array:
    transactionArray [ offsets[i] : offsets[i+1] ]
    
    Transaction i length = offsets[i+1] - offsets[i]

## Pipeline: Step-by-step ##

The pipeline consists of five stages, each represented by an individual script in the  _src_ directory:

1. [**Get blockchain**](#getblockchainpy)
2. [**Get input addresses**](#getinputaddrpy)
3. [**Get cluster**](#getclusterpy)
4. [**Get flat blockchain**](#getflatblockchainpy)
5. [**Get graph**](#getgraphpy)

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

As aforementioned, we store transaction data in Python lists. While it is customary to store numeric data in Numpy arrays, we avoided using the particular data structure throughout the pipeline (except for the output data) for the following reasons:

1. Traversing numpy arrays is considerbly slower than traversing Python lists due to [on-the-fly object unpacking](https://stackoverflow.com/a/63873120/9042791).
2. Numpy is an optimal choice for vector operations. No vector operations are performed throughout the pipeline, traversing the array/list data is the dominant cost.
3. Storage footprint is approximately the same in pickle format. Pickle files weigh approximately 10% of an object's memory footprint. 
4. While a larger memory footprint is a tradeoff when using lists over Numpy arrays, list traversal provides an 5-fold (minimum) performance boost. Most researchers can get their hands on 16GB/128GB machines to get the blockchain and/or the graph respectively.

The script's output is an arbitrary number of dictionaries stored in pickle files. Given that the pipeline was designed so that anyone with a 16GB machine can get the unclustered blockchain, for every 5M transactions scanned, the script dumps the data in a .pickle file to avoid usign up all the available memory. Once main memory is full and virtual memory is employed, the result is a severe performance hit. Hence, storing the data in many smaller files prevents this from happening.

### getInputAddr.py ###
In the second stage, the script parses the dictionarys created in the first stage to retrieve each tx's input addresses and their total value.

Each transaction input spends a transaction output that is part of the UTXO set at the time. So, each input in the blockchain is represented by a txid and the corresponding output slot/index. The _"receiver's address"_ is stored in that transaction output's address field. 

Given that a txid referenced by an input is in the same dictionary/file as the input, the cost of retrieving the address is O(1), since dictionary keys are the hashed txids. If the referenced txid is part of the dictionary's key set, the following outcomes are possible:

1. Txid points to a single transaction - no hash collisions. The referenced output index is __smaller__ than the tx's number of outputs. Hit.
2. -//-. The referenced output index is __greater__ than the tx's number of outputs. Correct transaction is in some previous dict. Miss.
3. Txid point to multiple transactions - hash collision. First transaction whose output count is greater than the output index is a match (at least one tx satisfies this). Hit.
4. -//-. Output index is greater than every transaction's output count. Correct transaction is in some previous dict. Miss.

Due to hash collisions, extra checks need to take place to ensure that the transaction matching the txid referenced by the input is the right transaction, or at least a feasible candidate. The computationally cheapest way of achieving this is by checking whether a transaction's total output count is greater than the referenced output slot. 

For instance, if an input is spending transaction X's 4th output, and txid X exists in the same dictionary, but it points to a transaction with 2 outputs, then we can conclude that the right transaction is located in some other dictionary (hash collision across different dictionaries).

In the event that X points to many transactions (hash collision within the same dictionary), then the script arbitrarily picks any transaction matching the criteria laid out above. So far we haven't identified any other computationally inexpensive methods to resolve hash collisions. Because of the relatively low collision rate, the particular heuristic should output an accurate copy of the raw blockchain.

For every dictionary, the script keeps all of the transaction inputs whose addresses were not in the same dict. Once a dict's parsing is complete, if there are inputs with missing addresses, the script starts scanning all of the previous dictionaries untill all input addresses are found. Given that the current dict is dict_N, the lookup starts from dict_N-1 and (worst case) goes all the way to dict_0.

The lookup process in pseudocode:

  ```python3
  begin lookUp
    
    dict_index=N-1
    while i<=0:
      temp=load_dict(dict_index)
      dict_N, missing_input_addresses = lookup(dict_N,temp,missing_input_addresses)
      if len(missing_input_addresses)>0:
        dict_index-=1
      else:
        break
    if len(missing_input_addresses)>0:
        print("Error")
        return 0
    else:
        return 1
  end lookup
  ```
If there are missing addresses after the lookup is completed there is definitely something wrong with either the output from stage 1, or the code in stage 2. Every address referenced by an input is in the blockchain, specifically either in a previous transaction recorded in the same block or some older block.

During our research, we retrieved all the blocks starting from height 0, all the way up to (approx.) height 750K and encountered no such error. The output of stage 2 is our fully normalized version of the Bitcoin blockchain, stored in a number of Python dictionaries. In the fourth stage, these dicts are converted to flat integer arrays and stored in h5 format.

### getCluster.py ###
In the third stage (optional), input addresses are clustered using the common-input-ownership heuristic. This heuristic explicitly assumes that all input addresses belong to the same entity. CIO is probably the most widely adopted clustering method for the Bitcoin blockchain and computationally inexpensive (the latter being a factor of its popularity).

We implement this heuristic using the [weighted union find](https://aquarchitect.github.io/swift-algorithm-club/Union-Find/) algorithm. The script uses a Python dictionary to store the data. Both keys and values are addresses; each key points to an address, that address is the key's parent node. If a key value pair is equal, the key/address is a root node. Root nodes basically correspond to cluster ids.


        union_find_dict= { address_0: address_5, address_5:address_8, address_8:address_10, address_10: address_10 }

        Tree: 0 -> 5 -> 8 -> 10

        union_find_dict[0]=5, address_5 is the father of address_0

        findRoot(0)=10, address_10 is the root node of address_0. Root nodes/addresses correspond to clusters. address_0 belongs to cluster address_10.

        findRoot(10)=10, address_10's root is itself; address_10 is a root node, therefore it corresponds to a cluster id.

Stage 3's output is the aforementioned dictionary. Given an address X that is encountered in at least one transaction's input space, _findRoot(X)_ returns the appropriate cluster/root node.

### getFlatBlockchain.py ###
In the fourth stage, the dictionaries are converted to flat integer arrays. Each dictionary is stored in an _.h5_ file that consists of two arrays; _offsets_ and _transactions_. As aforementioned, the offsets array allows O(1) access of any arbitrary transaction i, where i corresponds to the transaction's position in the blockchain. This is possible because we store transactions in the exact same sequence found in the blockchain. The transactions array consists of all transaction data stored in the the corresponding dictionary.

If the clustered blockchain is part of the pipeline's output, the process is a bit more involved because each transaction input space needs to be replaced with its corresponding cluster, which is derived from stage three's output. 

So, the following transformation is applied to each transaction's input space:

    Input: tx

    tx=[input addresses count (n), input_0, ..., inputAddr_n-1, output addresses count (m), outputAddr_0, ..., output_m-1, outputValue_0_flag, outputValue_0, ..., outputValue_m-1_flag, outputValue_m-1, timestamp, sumOfInputValues_flag, sumOfInputValues]

    T=get_clusters, for a list of addresses as input, it returns a list of the corresponding cluster ids

    tx_input_space = tx[1:n]

    cluster_set=set( T(tx_input_space) )

    assert len(cluster_set)==1

    tx_input_space = cluster_set[0]

Given _tx_'s input space of size _n_, each address should point to the same root node. Applying the set function to the return value of _T_ should return a set of size one, else there's been a mistake in the implementation of stage three. Since we have validated our stage three implementation's correctness, this extra check is for illustrative purposes only. Hence, to reduce complexity, T is only applied to the first address of _tx_'s input space, and the returned value corresponds to the new input space, which is reduced from size _n_ (n>=1) to size 1.

The same process is applied to _tx_'s output space, the difference being that T needs to be applied to all of the addresses, since it is possible for each output address to belong to a different cluster.

    tx_output_space = tx[output_space_start_index : output_space_end_index ]

    clusters = T(tx_output_space)

    cluster_set= set(clusters)

    assert len(cluster_set)<=len(tx_output_space)

Further compression can be achieved in the event that _cluster_set_'s size is smaller than _tx_output_space_, given that _tx_output_space_ size is greater than one. If that's the case, we can store each cluster id once instead of multiple times, followed by the number of outputs associated with this cluster and the corresponding output values. 

The following example illustrates this:

    tx =[ ... output addresses count (100), outputAddr_0, ..., outputAddr_99, outputValue_0_flag, outputValue_0, ..., outputValue_99_flag, outputValue_99, ... ]

    clusters = {cluster_X: [outputAddr_0, ..., outputAddr_99] - [outputAddr_1, outputAddr_30], clusterY: [outputAddr_1, outputAddr_30]}

    tx= [ ... cluster count (2), cluster_X, cluster_Y, 98, cluster_X_output_values, 2, outputValue_1_flag, outputValue_1, outputValue_30_flag, outputValue_30, ...]

    tx original output and output value space size = 1 + 100 + 2*100 = 301

    compressed output and output value space size = 1 + 2 + 1 +2*98 + 1 + 2*2 = 205

    32% compression 

Thus, compression is achieved by rearranging the transaction's original output value space, such that all output values corresponding to a single cluster id can be trivially accesed while storing each individual cluster id only once. 

The example does depict an ideal setting; the set of cluster ids is significantlly smaller than a transaction's set of output addresses. If the size of the two sets is about the same, zero compression is achieved. Empirically speaking though, such instances are frequent enough that the resulting format is more storage efficient than the original one.

Given these transformations, each transaction in the clustered blockhain is now represented by the following sequence:

    txid, cluster_id, cluster count (m), cluster_0, ..., cluster_m-1, cluster_0_tx_count, cluster_0_output_values (flag,value pairs), ..., cluster_m-1_tx_count, cluster_m-1_output_values, timestamp, sumOfInputValues_flag, sumOfInputValues

If the blockchain's user graph is part of the pipeline's output, the same data is stored in lists. This is because the last stage (getGraph) uses the lists as input (traversing lists is much faster than traversing numpy arrays). If the user graph is not needed, the clustered blockchain is stored the exact same way the unclustered blockchain is.

### getGraph.py ###
The fifth and final stage of the pipeline converts the lists from stage four to a series of _.h5_ files. Each file consists of three arrays; _offsets_, _nodes_ and _edges_. The _nodes_ array contains all of the cluster_ids located in the dictionary, _edges_ contains each node's outgoing edges, and _offsets_ provides each node's edges' location in the _edges_ array. 

Each transaction is decomposed into _m_ edges, where _m_ equals the number of output values. The starting node is the transaction sender's cluster id and the terminal node is the corresponding output address/cluster id. 

To access some arbitrary node's edges, we need the node's index in the _nodes_ array to retrieve the node's edges' slice in the _edges_ array from the _offsets_ array. 

The following example illustrates the process:

    clusterID = nodes[k], cluster ID stored in position k of nodes array
    
    edges_start_index = offsets[k]
    edges_end_index = offsets[k+1]
    
    nodeEdges = edges[edges_start_index:edges_end_index]

An edge is stored in the following format:

    receiver_cluster_id, outputValue_flag, outputValue, timestamp
 
Each edge is of fixed length. The number of edges in the graph can be trivially calculated as follows: 

    number_of_edges = len(edges)/edge_length, where edge_length equals 4
    If the code is modified such that a transaction consists of more attributes, edge_length will be greater than 4.

Moreover, the script calculates each transaction's fees by summing the output values and subtracting the sum from sumOfInputValues. This is done to create the corresponding _change_ edge, which starts from the associated sender/cluster node and points to the _coinbase_ node (whose id is 4294967295). 

Because the value of each coinbase transaction equals the number of newly minted Bitcoins plus the sum of transaction fees of a given block, the _coinbase_ node is the only node where the sum of its incoming edges value is less than the sum of its outgoing edges value.

For all the other nodes, the following property holds:

    sum(incoming_edges_value) >= sum(outgoing_edges_value)

The effect of this property is that a node can not spend more than it makes. The _coinbase_ node can satisfy this property by creating a self-loop for each block, where the monetary value of each edge is equal to the number of Bitcoins created in the corresponding block.

## Execution ##

Executing the pipeline is trivial. In case you have Bitcoin Core running in the background, make sure to stop the server before launching the pipeline. This is necessary because Bitcoin Core has a lock on the blockchain database, so as long as it's running the Python blockchain parser won't be able to parse the blocks.

To execute the pipeline do the following:
- Clone the repository to your machine
- Open up a terminal, cd into the repository and then cd into the /src directory
- Execute inputs.py to selct the desired outputs (i.e. clustered blockchain and graph) and provide the path to the blocks directory ("~/.bitcoin/blocks") 
- inputs.py will terminate and launch the pipeline as a deamon process (it will run in the background)
- main.py will create a src/blockchain directory to store the desired outputs

As mentioned in the beginning, the pipeline takes about three days to complete execution. During execution main.py keeps a log of the pipeline's progress at src/log.json.

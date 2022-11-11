from fileManager import saveJSON,loadJSON,savePickle
import time, os, mmh3
from blockchain_parser.blockchain import Blockchain


def getReceivers(tx):
    receivers, satoshis = [], []
    appendRec=receivers.append
    appendSatoshis=satoshis.append
    
    for out in tx.outputs:
        
        if out.addresses:
            appendRec(out.addresses[0].address)
        else:
            appendRec("unknown")
        
        if out.value>4294967295:
            appendSatoshis(1) #indicates next value is bitcoin
            appendSatoshis(int(round(out.value*0.00000001,2)*100)) #satoshis to btc to be int32, round to 2nd decimal
        else:
            appendSatoshis(0) #indicates next value is satoshi 
            appendSatoshis(out.value)
            
    return receivers,satoshis

def getData(txs):
    t=[]
    tAppend=t.append
    for aTX in txs:
        
        #getSenders_start
        if aTX.is_coinbase():
            senders=[["cb",4294967295]] #dummy unspent txid and output slot for coinbase transactions
        else:
                    #Each input spends an output from a previous transaction part of the UTXO set.
                    #Input = (unspent_txid, output_slot)
            senders=[[i.transaction_hash,i.transaction_index] for i in aTX.inputs]
        #getSenders_end
        
        receivers,satoshis=getReceivers(aTX)
        
        tAppend([senders,receivers,satoshis,aTX.txid])
        
    return t


def foo():
    t1=time.time()
    
    try:
        dictIndex, tcount, startBlock=loadJSON("currentBlock.json")[2], loadJSON("currentBlock.json")[1], loadJSON("currentBlock.json")[0]+1
    except:
        dictIndex, tcount, startBlock = 0,0,-1

    hashMap={}
    hashMapGet, hashf, listl, tcounttemp=hashMap.get, mmh3.hash, len, 0
    endBlock, blockchain = 744117, Blockchain(os.path.expanduser('~/.bitcoin/blocks'))
    
    print("Total blocks in the blockchain:",endBlock,"Starting from:",startBlock)
  
    t2=time.time()
    
    for block in blockchain.get_ordered_blocks(os.path.expanduser('~/.bitcoin/blocks/index'),start=startBlock, end=endBlock):
        transactions = getData(block.transactions)
        date=int(block.header.timestamp.timestamp())
        
        for t in transactions:
            
            txid=hashf(t[3],signed=False)
            
            inp=[hashf(x,signed=False) if i==0 else x for aTuple in t[0] for i,x in enumerate(aTuple)]
            out=[hashf(outAddr,signed=False) for outAddr in t[1]]
            tL=[len(inp),*inp,len(out),*out,*t[2],date]
            
            result=hashMapGet(txid)
            
            if result:
                #txid hash collision, hashed(txid): [tx0List, tx1List, ..., txNList]
                if type(result[0])==list:
                    result.append(tL)
                else:
                    hashMap[txid]=[result,tL]
            else:
                #no txid hash collision: hashed(txid): tx0List
                hashMap[txid]=tL

        tcounttemp+=listl(transactions)
           
        
        #Every 5M txs parsed, dump data in pickle file 
        if tcounttemp>5000000:
            print("5M. Dumping data ...",time.time()-t2)
            tcount+=tcounttemp
            tcounttemp=0
            
            t2=time.time()
            savePickle(hashMap,f"blockchain/hashMap_{dictIndex}.pickle")
            print("Stored pickle ...",time.time()-t2)
            
            hashMap={}
            hashMapGet=hashMap.get
            dictIndex+=1
            saveJSON([block.height,tcount,dictIndex],"currentBlock.json")
            
    
    if hashMap:
        t2=time.time()
        savePickle(hashMap,f"blockchain/hashMap_{dictIndex}.pickle")
        print("Stored last pickle ...",time.time()-t2)

    saveJSON([block.height,tcount+tcounttemp,dictIndex],"currentBlock.json")
        
    print("Elapsed time",time.time()-t1,"Total transactions scanned",tcount)




if __name__=="__main__":
    print("getBlockchain.py")
    
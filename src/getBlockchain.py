from fileManager import saveJSON,loadJSON,savePickle
import time
import os
from blockchain_parser.blockchain import Blockchain
import mmh3


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
            senders=[["cb",4294967295]]
        else:
            senders=[[i.transaction_hash,i.transaction_index] for i in aTX.inputs]
        #getSenders_end
        
        receivers,satoshis=getReceivers(aTX)
        
        tAppend([senders,receivers,satoshis,aTX.txid])
        
    return t


def foo():
    t1=time.time()
    dictIndex=loadJSON("currentBlock.json")[2]
    hashMap={}
    k1, hashMapGet, hashf, listl, tcounttemp, tcount=loadJSON("currentBlock.json")[1], hashMap.get, mmh3.hash, len, 0,0
    startBlock, endBlock, blockchain = loadJSON("currentBlock.json")[0]+1, 744117, Blockchain(os.path.expanduser('~/.bitcoin/blocks'))
    
    print("Total blocks in the blockchain:",endBlock,"Starting from:",startBlock)
  
    t2=time.time()
    
    for block in blockchain.get_ordered_blocks(os.path.expanduser('~/.bitcoin/blocks/index'),start=startBlock, end=endBlock):
        transactions = getData(block.transactions)
        date=int(block.header.timestamp.timestamp())
        
        for t in transactions:
            
            txid=hashf(t[3],signed=False)
            
            inp=[hashf(x,signed=False) if i==0 else x for aTuple in t[0] for i,x in enumerate(aTuple)]
            out=[hashf(outAddr,signed=False) for outAddr in t[1]]
            tL=[len(inp),*inp,len(out),*out,*t[2],date]#npArray([len(inp),*inp,len(out),*out,*t[2],date],dtype="uint32")
            
            result=hashMapGet(txid)
            
            if result:
                if type(result[0])==list:
                    result.append(tL)
                else:
                    hashMap[txid]=[result,tL]
            else:
                hashMap[txid]=tL

        tcounttemp+=listl(transactions)
           
        
        if tcounttemp>5000000:
            print("5M. Dumping data ...",time.time()-t2)
            k1+=tcounttemp
            saveJSON([block.height,k1],"currentBlock.json")
            tcount+=tcounttemp
            tcounttemp=0
            t2=time.time()
            savePickle(hashMap,f"bitcoinMaps/hashMap_{dictIndex}.pickle")
            print("Stored pickle ...",time.time()-t2)
            hashMap={}
            hashMapGet=hashMap.get
            dictIndex+=1
            t2=time.time()
            
    
    if hashMap:
        t2=time.time()
        savePickle(hashMap,f"bitcoinMaps/hashMap_{dictIndex}.pickle")
        print("Stored last pickle ...",time.time()-t2)

    saveJSON([block.height,k1+tcounttemp,dictIndex],"currentBlock.json")
        
    print("Elapsed time",time.time()-t1,"Total transactions scanned",tcount)




if __name__=="__main__":
    print("downloadBlockchain.py")
    
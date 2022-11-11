from fileManager import saveJSON,loadJSON, loadPickle, savePickle
import time

def findRoot(child,parents):
    parent=parents[child]
    while child!=parent:
        child=parent
        parent=parents[child]

    return child
        

def cluster(txs,parents,treeSize):
    
    
    
    for k,aTX in txs.items():

        if type(aTX[0])!=list: 
            aTX=[aTX]
            
        inputs=[]
        for aSubTX in aTX:
            isCoinbase=1 if aSubTX[2]==4294967295 else 0
            inpCount=aSubTX[0]
            outStart=inpCount+1
            outCount=aSubTX[outStart]
            inputs.append(list(set(aSubTX[(1+1*isCoinbase):outStart])))
        
       
        for subInputs in inputs:
            
            try:
                k=next(anInput for anInput in subInputs if parents.get(anInput))
                #index of first non-orphan input/node in input space
            except:
                k=-1 #all nodes are orphans

            if k==-1:
                
                for anInput in subInputs:
                    parents[anInput]=subInputs[0]#all nodes are children of input_0
               	treeSize[subInputs[0]]=len(subInputs)
                
            else:
            
                kRoot=findRoot(k,parents)
               
                
                for anInput in subInputs:
                    
                    if not parents.get(anInput):
                        parents[anInput]=kRoot #orphan node
                        treeSize[kRoot]+=1
                       
                    else:
                        #all root nodes are now children of input k's root
                        #except for inputs whose root == root[input_k]
                        if anInput!=k:
                            
                            inpRoot=findRoot(anInput,parents)
                            
                            
                            if inpRoot!=kRoot:
                                kSize=treeSize[kRoot]
                                inpSize=treeSize[inpRoot]
                                if kSize>inpSize:
                                    parents[inpRoot]=kRoot
                                    parents[anInput]=kRoot
                                    treeSize[kRoot]=kSize+inpSize
                                else:
                                    parents[kRoot]=inpRoot
                                    parents[anInput]=inpRoot
                                    treeSize[inpRoot]=kSize+inpSize
                                    k=anInput
                                    kRoot=inpRoot

def foo():
    parents, treeSize = {}, {}

	#times=[]
	for i in range(0,150):
		hashMap=loadPickle(f"bitcoinMaps/{i}.pickle")
		#t1=time.time()
		cluster(hashMap,parents,treeSize)
		#times.append({"N":len(parents.keys()),"t":time.time()-t1})
		#if (i+1)%10==0:
			#saveJSON(times,"times.json")

	savePickle(parents,"ps.pickle")
	#savePickle(treeSize,"t.pickle")
	#saveJSON(times,"times.json")

if __name__=="__main__":
    print("getCluster.py")
	
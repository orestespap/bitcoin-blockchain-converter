from fileManager import loadPickle, savePickle
import time, gc
from getCluster import findRoot
import os
#import numpy as np
#import h5py



def clusterf(hashMap,parents):
    getParents=parents.get
    data, offsets, flag, z= [],[], 0, 0
    
    for k,aTX in hashMap.items():
        if type(aTX[0])!=list:
            aTX=[aTX]

        for aSubTX in aTX:
            isCoinbase=1 if aSubTX[2]==4294967295 else 0
            inpCount=aSubTX[0]
            outStart=inpCount+1
            outCount=aSubTX[outStart]


            inpRoots=set(parents[x] if getParents(x) else x for x in set(aSubTX[(1+1*isCoinbase):outStart]))
            if len(inpRoots)!=1:
                #All input addresses must point to the same root address, therefore inpRoots should be a set of size 1.
                print(k,aSubTX)
                flag=1
                break


            outCount=aSubTX[outStart]
            outRoots=[parents[x] if getParents(x) else x for x in aSubTX[outStart+1:outStart+1+outCount]]
            setOutRoots=set(outRoots)
            lenSetOutRoots=len(setOutRoots)
            const1=outStart+outCount+1


            d={x:[] for x in outRoots}
            if lenSetOutRoots==outCount or lenSetOutRoots==1:
                values=[outCount,*aSubTX[const1:const1+2*outCount]]
                
            else:

                for i,y in enumerate(outRoots):
                    d[y].append(i)

                values=[]
                for key in d:
                    temp=[]
                    for i in d[key]:
                        temp.extend([*aSubTX[const1+2*i:const1+2*i+2]])

                    values.append(len(d[key]))
                    values.extend(temp)
            
            suffix=[aSubTX[-1]] if isCoinbase else [*aSubTX[-3::]]
                
            temp=[k,tuple(inpRoots)[0],lenSetOutRoots,*d.keys(),*values,*suffix]
            z+=len(temp)
            offsets.append(z)
            data.extend(temp)

        if flag:
            break
    if flag:
        return -1,-1

    return data,offsets

def rootify(parents):
    for k in parents:
        parents[k]=findRoot(k,parents)
    return 1


def foo(unclustered=False,clustered=False, graphh=False):
    lastFileIndex=sorted([int(x.split(".")[0]) for x in os.listdir("blockchain/unclustered")])[-1]
    if clustered or graphh:
        parents=loadPickle("ps.pickle")
        rootify(parents)

        for i in range(0,lastFileIndex+1):

            hashMap=loadPickle(f"blockchain/unclustered/{i}.pickle")
            print(i,len(hashMap))
            #t1=time.time()
            tdata, toffsets=clusterf(hashMap,parents)
            if tdata==-1:
                print("error",i)
                break
            #print(time.time()-t1)

            print("Storing files")

            savePickle(tdata,f'blockchain/clustered/d{i}.pickle')
            savePickle(toffsets,f'blockchain/clustered/o{i}.pickle')

            if not unclustered:
                os.system(f'rm -r blockchain/unclustered/{i}.pickle')
            
            del tdata
            del toffsets
            del hashMap
            gc.collect()
            if clustered:
                #STORE BLOCKCHAIN h5
                pass
    if unclustered:
        #STORE BLOCKCHAIN h5
        pass
    else:
        os.system(f'rm -r blockchain/unclustered')
    os.system("rm -r ps.pickle")


if __name__=="__main__":
    print("getFlatBlockchain.py")
    
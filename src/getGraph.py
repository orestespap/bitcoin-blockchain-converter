from fileManager import loadPickle, savePickle, saveJSON
import time,gc,h5py
import numpy as np
import os

def foo():
    errors=0
    times=[]
    t1=time.time()
    graph={}

    for j in range(0,150):
        txs=loadPickle(f'blockchain/clustered/d{j}.pickle')
        offsets=loadPickle(f'blockchain/clustered/o{j}.pickle')
        startt=0
        endd=offsets[0]
        t2=time.time()
        for jj,currentOffset in enumerate(offsets):

            d=txs[startt:endd]      

            try:
                startt=currentOffset
                endd=offsets[jj+1]
            except:
                pass

            key=d[1]        
            outputClusters=d[2]
            outputs=d[3+outputClusters]



            outputClusterAddr=[oC for oC in d[3:3+outputClusters]]
            if outputs==outputClusters or outputClusters==1:
                values=[v for v in d[3+outputClusters+1:3+outputClusters+1+2*outputs]]

            else:

                indexes=[]
                values=[]
                const=3+outputClusters
                for i in range(0,outputClusters):
                    values.extend(d[const+1:const+1+2*d[const]])
                    indexes.append(d[const])
                    const=const+2*d[const]+1


            if d[1]!=4294967295:
                sumValues=sum(x if values[2*i]==0 else x/0.000001 for i,x in enumerate(values[1::2]))
                sumInp=d[-1] if d[-2]==0 else d[-1]/0.000001
                change=sumInp-sumValues
                changeFlag=0
                if change<0:
                    errors+=1
                    change=0
                else:
                    if change>4294967295:
                        changeFlag=1
                        change=int(round(change*0.00000001,2)*100)
                    else:
                        change=int(change)


                if change:
                    outputClusterAddr.append(4294967295)
                    values.append(changeFlag)
                    values.append(change)


            timestamp=d[-3]
            if d[1]==4294967295:
                timestamp=d[-1]
            if outputClusters==outputs:
                temp=[]

                for i,x in enumerate(outputClusterAddr):
                    temp.append(x)
                    temp.extend([*values[2*i:2*i+2],timestamp])

            elif outputClusters==1:
                temp=[]
                tempValues=values[:-2]
                for i,x in enumerate(tempValues[::2]):
                    temp.extend([outputClusterAddr[0],x,tempValues[2*i+1],timestamp])

                if d[1]!=4294967295 and change:
                    temp.extend([4294967295,changeFlag,change,d[-3]])

            else:
                temp=[]
                start=0

                for oi,ind in enumerate(indexes):
                    tempValues=values[start:start+ind*2]
                    for i,x in enumerate(tempValues[::2]):
                        temp.extend([outputClusterAddr[oi],x,tempValues[2*i+1],timestamp])
                    start+=ind*2
                if d[1]!=4294967295 and change:
                    temp.extend([4294967295,changeFlag,change,d[-3]])


            res=graph.get(key)
            if res:
                res.extend(temp)
            else:
                graph[key]=temp
        if (j+1)%10==0:
            savePickle(graph,f"blockchain/graphs/graphDict{j}.pickle")
            graph={}
            saveJSON({"dictLength":len(graph.keys()),"iter":j,"time":time.time()-t2},"out.json")

    print("errors",errors)
    if graph:
        savePickle(graph,f"blockchain/graphs/graphDict{j}.pickle")
        del graph
    print("total exec time",time.time()-t1)


    maps=os.listdir("graphs/")
    for i,mapString in enumerate(maps):
        map_=loadPickle(f"graphs/{mapString}")
        offsets,nodes,s=[],[],0

        for k in map_:
                s+=len(map_[k])
                offsets.append(s)
                nodes.append(k)

        f = h5py.File(f'blockchain/graphs/graph{i}.h5', 'w')
        f.create_dataset('nodes', data=np.array(nodes,dtype=np.uint32))
        f.create_dataset('offsets', data=np.array(offsets,dtype=np.uint32))
        del offsets
        del nodes
        gc.collect()
        f.create_dataset('edges', data=np.array([v for k in map_ for v in map_[k]],dtype=np.uint32))
        f.close()
        os.system(f'rm -r blockchain/graphs/{mapString}')

if __name__=="__main__":
    print("getGraph.py")
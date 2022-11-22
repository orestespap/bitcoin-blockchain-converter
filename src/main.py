import time
from getBlockchain import foo as f1
from getInputAddr import foo as f2
from getCluster import foo as f3
from getFlatBlockchain import foo as f4
from getGraph import foo as f5
import os
from fileManager import saveJSON, loadJSON

if __name__=="__main__":
    
    #TODO:
    
    #blockchain path for parser

    #getFlatBlockchain, store unclustered and clustered blockchain in h5

    #getBlockhain -> get last block

    inputs=loadJSON("inputs.json")
    graphh=inputs["graph"]
    clustered=inputs["clustered"]
    unclustered=inputs["unclustered"]
    blocksPath=inputs["blocks"]

    os.system('mkdir blockchain')
    
    os.system('mkdir blockchain/unclustered')

    saveJSON({"stage":1,"status":"inProgress"},"log.json")
    t1=time.time()

    f1(blocksPath)
    saveJSON({"stage":1,"status":"completed","executionTimeInSeconds":time.time()-t1},"log.json")
   
    saveJSON({"stage":2,"status":"inProgress"},"log.json")
    t2=time.time()
    f2()
    saveJSON({"stage":2,"status":"completed","executionTimeInSeconds":time.time()-t2},"log.json")
    
    if graphh or clustered:
        saveJSON({"stage":3,"status":"inProgress"},"log.json")
        os.system('mkdir blockchain/clustered')
        t2=time.time()
        f3()
        saveJSON({"stage":3,"status":"completed","executionTimeInSeconds":time.time()-t2},"log.json")


    saveJSON({"stage":4,"status":"inProgress"},"log.json")
    t2=time.time()
    f4(unclustered,clustered)
    saveJSON({"stage":4,"status":"completed","executionTimeInSeconds":time.time()-t2},"log.json")

    if graphh:
        saveJSON({"stage":5,"status":"inProgress"},"log.json")
        os.system('mkdir blockchain/graphs')
        t2=time.time()
        f5()
        saveJSON({"stage":5,"status":"completed","executionTimeInSeconds":time.time()-t2},"log.json")
        if not clustered:
            os.system("rm -r blockchain/clustered")
        else:
            os.system("rm -r blockchain/clustered/*.pickle")        

    
    print(f"Blockchain conversion successfully completed. Elapsed time(seconds): {time.time()-t1}")
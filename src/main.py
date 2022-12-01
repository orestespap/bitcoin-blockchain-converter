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

    log={"stage_1":{"status":"inProgress","executionTimeInSeconds":-1}}
    saveJSON(log,"log.json")
    t1=time.time()

    f1(blocksPath)
    log["stage_1"]["status"], log["stage_1"]["executionTimeInSeconds"]="completed", time.time()-t2
    log["stage_2"]={"status":"inProgress","executionTimeInSeconds":-1}
    
    saveJSON(log,"log.json")
    t2=time.time()
    f2()
    log["stage_2"]["status"], log["stage_2"]["executionTimeInSeconds"]="completed", time.time()-t2
    saveJSON(log,"log.json")
    
    if graphh or clustered:
        log["stage_3"]={"status":"inProgress","executionTimeInSeconds":-1}
        saveJSON(log,"log.json")
        os.system('mkdir blockchain/clustered')
        t2=time.time()
        f3()
        log["stage_3"]["status"], log["stage_3"]["executionTimeInSeconds"]="completed", time.time()-t2
        saveJSON(log,"log.json")


    
    log["stage_4"]={"status":"inProgress","executionTimeInSeconds":-1}
    saveJSON(log,"log.json")
    t2=time.time()
    f4(unclustered,clustered)
    log["stage_4"]["status"], log["stage_4"]["executionTimeInSeconds"]="completed", time.time()-t2
    saveJSON(log,"log.json")

    if graphh:
        log["stage_5"]={"status":"inProgress","executionTimeInSeconds":-1}
        saveJSON(log,"log.json")
        os.system('mkdir blockchain/graphs')
        t2=time.time()
        f5()
        log["stage_5"]["status"], log["stage_5"]["executionTimeInSeconds"]="completed", time.time()-t2
        saveJSON(log,"log.json")
        if not clustered:
            os.system("rm -r blockchain/clustered")
        else:
            os.system("rm -r blockchain/clustered/*.pickle")        

    os.system("rm -r inputs.json")
    
    
    print(f"Blockchain conversion successfully completed. Elapsed time(seconds): {time.time()-t1}")
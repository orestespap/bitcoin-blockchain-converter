import time
from gertBlockchain import foo as f1
from getInputAddr import foo as f2
from getCluster import foo as f3
from getFlatBlockchain import foo as f4
from getGraph import foo as f5

if __name__=="__main__":
    
    #TODO:user input to opt for clustered/un-clustered blockchain
    #and graph/no graph
    
    
    #mkdir where all output data is stored in an organized manner
    
    t1=time.time()
    
    f1()
    
    f2()
    
    if createCluster:
        f3()
    
    f4(createCluster)
    
    if createGraph:
        f5()
    
    t2=time.time()-t1
    print(f"Blockchain conversion successfully completed. Elapsed time(seconds): {t2}")
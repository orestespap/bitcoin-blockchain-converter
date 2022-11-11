import time
from getBlockchain import foo as f1
from getInputAddr import foo as f2
from getCluster import foo as f3
from getFlatBlockchain import foo as f4
from getGraph import foo as f5

if __name__=="__main__":
    
    #TODO:user input to opt for clustered/un-clustered blockchain
    #and graph/no graph, blockchain path for parser

    #user input to get clustered blockchain, given that flat blockchain exists
    #user input to get the graph ...
    
    
    #mkdir where all output data is stored in an organized manner
    
    t1=time.time()
    
    f1()
    print("getBlockchain completed ... ",time.time()-t1,"seconds")
    
    t2=time.time()
    f2()
    print("getInputAddr completed ... ",time.time()-t2,"seconds")
    
    if createCluster:
        t2=time.time()
        f3()
        print("getCluster completed ... ",time.time()-t2,"seconds")

    t2=time.time()
    f4(createCluster)
    print("getFlatBlockchain completed ... ",time.time()-t2,"seconds")
    

    if createGraph:
        t2=time.time()
        f5()
        print("getGraph completed ... ",time.time()-t2,"seconds")
        

    print(f"Blockchain conversion successfully completed. Elapsed time(seconds): {time.time()-t1}")
import time
from getBlockchain import foo as f1
from getInputAddr import foo as f2
from getCluster import foo as f3
from getFlatBlockchain import foo as f4
from getGraph import foo as f5
import os

if __name__=="__main__":
    
    #TODO:
    
    #blockchain path for parser

    #getFlatBlockchain, store unclustered and clustered blockchain in h5


    os.system('mkdir blockchain')

    while True:
        try:
            unclustered=int(input("Store unclustered Blockchain?\nYES(1), NO(0): "))
            clustered=int(input("Store clustered Blockchain?\nYES(1), NO(0): "))
            if clustered:
                graphh=int(input("Store Blockchain user graph?\nYES(1), NO(0): "))
        except:
            print("Invalid input.")
        else:
            if unclustered+clustered+graphh:
                break
            else:
                print("Select at least one output.")
    
    os.system('mkdir blockchain/unclustered')


    t1=time.time()

    f1()
    print("getBlockchain completed ... ",time.time()-t1,"seconds")
    
    t2=time.time()
    f2()
    print("getInputAddr completed ... ",time.time()-t2,"seconds")
    
    if graphh or clustered:
        os.system('mkdir blockchain/clustered')
        t2=time.time()
        f3()
        print("getCluster completed ... ",time.time()-t2,"seconds")

    t2=time.time()
    f4(unclustered,clustered)
    print("getFlatBlockchain completed ... ",time.time()-t2,"seconds")
    

    if graphh:
        os.system('mkdir blockchain/graphs')
        t2=time.time()
        f5()
        print("getGraph completed ... ",time.time()-t2,"seconds")
        if not clustered:
            os.system("rm -r blockchain/clustered")
        else:
            os.system("rm -r blockchain/clustered/*.pickle")        


    print(f"Blockchain conversion successfully completed. Elapsed time(seconds): {time.time()-t1}")
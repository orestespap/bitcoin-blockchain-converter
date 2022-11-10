import time
from downloadBlockchain import downloadBlockchainFoo as f1
from getInputs import getInputsFoo as f2
from flatBlockchain import flatBlockchainFoo as f3
from createGraph import graphFoo as f4

if __name__=="__main__":
    t1=time.time()
    f1()
    f2()
    f3()
    f4()
    t2=time.time()-t1
    print(f"Blockchain conversion successfully completed. Elapsed time(seconds): {t2}")
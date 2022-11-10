from fileManager import loadPickle, savePickle, saveJSON, loadJSON
import time

def getInputsFoo():
    lookupDepth=loadJSON("lookupDepth.json")
    t1=time.time()
    for i in range(0,150):
        print("Loading pickle file")
        orIndexx=i
        hashMap=loadPickle(f"bitcoinMaps/hashMap_{orIndexx}.pickle")
        print(time.time()-t1)
        hashMapGet=hashMap.get
        tlookups=0
        transCount=0
        t1=time.time()
        missingInp={}
        f=0
        print("Start")

        for k,txL in hashMap.items():
            if type(txL[0])!=list:
                txL=[txL]

            temp=[]

            for txPos,aTX in enumerate(txL):
                inpSize=int(aTX[0])

                if aTX[2]==4294967295:
                    continue

                t_inpIDs, t_addrS=[], []

                curr_inp=-1
                inpSum=0
                for i in range(1,inpSize+1,2):
                    curr_inp+=1

                    try:
                        outTX=hashMap[aTX[i]]
                    except:
                        t_inpIDs.append(curr_inp)
                        tlookups+=1
                        continue

                    outputSlot=int(aTX[i+1])

                    miss=1
                    skip=outTX[0]
                    if type(skip)!=list:
                        if outputSlot<outTX[skip+1]:
                            t_addrS.append(outTX[skip+2+outputSlot])
                            index=outTX[skip+1]+2+skip+2*outputSlot
                            isBTC,inpValue=outTX[index:index+2]
                            if isBTC:
                                inpValue/=0.000001
                            inpSum+=inpValue
                            miss=0

                    else:

                        for foldedTX in outTX:
                            skip=foldedTX[0]
                            if outputSlot>=foldedTX[skip+1]:
                                continue
                            t_addrS.append(foldedTX[skip+2+outputSlot])
                            index=foldedTX[skip+1]+2+skip+2*outputSlot
                            isBTC,inpValue=foldedTX[index:index+2]
                            if isBTC:
                                inpValue/=0.000001
                            inpSum+=inpValue
                            miss=0
                            break

                    if miss:
                        tlookups+=1
                        t_inpIDs.append(curr_inp)


                if t_inpIDs:
                    temp.append([txPos,inpSize/2,len(t_inpIDs),len(t_inpIDs),*t_inpIDs,t_addrS,inpSum])
                else:
                    isBTC=0
                    if inpSum>4294967295:
                        isBTC=1
                        inpSum=int(round(inpSum*0.00000001,2)*100)
                    else:
                        inpSum=int(inpSum)

                    txL[txPos]=[len(t_addrS),*t_addrS,*aTX[inpSize+1::],isBTC,inpSum]

            if temp:
                missingInp[k]=temp


            if len(txL)==1:
                hashMap[k]=txL[0]
            else:
                hashMap[k]=txL


            transCount+=1
            if transCount%500000==0:
                print(transCount)

        savePickle(hashMap,f"testMaps/{orIndexx}.pickle")
        t2=time.time()
        print(t2-t1)

        print("Current map:",orIndexx)
        indexx=orIndexx

        transCount=0
        indexx-=1
        flag=0
        depth=0
        if not any(1 for v in missingInp.values() if type(v)==list and 0 not in v):
            indexx=-1

        while indexx>=0:
            depth+=1
            print("Map index:",indexx)
            oldMap=loadPickle(f"testMaps/{indexx}.pickle")

            for k,item in missingInp.items():
                if type(item)!=list:
                    continue

                tx=hashMap[k]


                if type(tx[0])==list:
                    for j, enfoldedItem in enumerate(item):
                        if enfoldedItem==0:
                            continue

                        inpSum=0

                        for jj, k2 in enumerate(enfoldedItem[4:4+enfoldedItem[2]]):
                            if k2==-1:
                                continue
                            outTXID=tx[enfoldedItem[0]][2*k2+1]
                            outTXIDSlot=tx[enfoldedItem[0]][2*k2+2]
                            try:
                                outTX=oldMap[outTXID]
                            except:
                                pass

                            if type(outTX[0])==list:
                                for t in outTX:
                                    skip=t[0]
                                    if outTXIDSlot>=t[skip+1]:
                                        continue
                                    z=t[skip+2+outTXIDSlot]
                                    index=t[skip+1]+2+skip+2*outTXIDSlot
                                    isBTC,inpValue=t[index:index+2]
                                    if isBTC:
                                        inpValue/=0.000001
                                    inpSum+=inpValue
                                    enfoldedItem[-2].insert(k2,z)
                                    enfoldedItem[3]-=1
                                    enfoldedItem[jj+4]=-1
                                    break
                            else:
                                skip=outTX[0]
                                if outTXIDSlot>=outTX[skip+1]:
                                    continue
                                z=outTX[skip+2+outTXIDSlot]
                                index=outTX[skip+1]+2+skip+2*outTXIDSlot
                                isBTC,inpValue=outTX[index:index+2]
                                if isBTC:
                                    inpValue/=0.000001
                                inpSum+=inpValue
                                enfoldedItem[-2].insert(k2,z)
                                enfoldedItem[3]-=1
                                enfoldedItem[jj+4]=-1



                        enfoldedItem[-1]+=inpSum

                        if enfoldedItem[3]==0:
                            temp=[len(enfoldedItem[-2])]
                            temp.extend(enfoldedItem[-2][:])
                            v=tx[enfoldedItem[0]]
                            temp.extend(v[v[0]+1::])
                            isBTC=0
                            inpSum=enfoldedItem[-1]
                            if inpSum>4294967295:
                                isBTC=1
                                inpSum=int(round(inpSum*0.00000001,2)*100)
                            else:
                                inpSum=int(inpSum)
                            temp.extend([isBTC,inpSum])
                            tx[enfoldedItem[0]]=temp
                            missingInp[k][j]=0

                else:

                    item=item[0]
                    inpSum=0
                    for jj, k2 in enumerate(item[4:4+item[2]]):                

                        if k2==-1:
                            continue

                        outTXID=tx[2*k2+1]    
                        outTXIDSlot=tx[2*k2+2]
                        try:
                            outTX=oldMap[outTXID]
                        except:
                            pass
                        if type(outTX[0])==list:
                            for t in outTX:
                                skip=t[0]
                                if outTXIDSlot>=t[skip+1]:
                                    continue

                                z=t[skip+2+outTXIDSlot]
                                index=t[skip+1]+2+skip+2*outTXIDSlot
                                isBTC,inpValue=t[index:index+2]
                                if isBTC:
                                    inpValue/=0.000001
                                inpSum+=inpValue
                                item[-2].insert(k2,z)
                                item[3]-=1
                                item[jj+4]=-1
                                break
                        else:
                            skip=outTX[0]
                            if outTXIDSlot>=outTX[skip+1]:
                                continue
                            z=outTX[skip+2+outTXIDSlot]
                            index=outTX[skip+1]+2+skip+2*outTXIDSlot
                            isBTC,inpValue=outTX[index:index+2]
                            if isBTC:
                                inpValue/=0.000001
                            inpSum+=inpValue
                            item[-2].insert(k2,z)
                            item[3]-=1
                            item[jj+4]=-1


                    item[-1]+=inpSum
                    if item[3]==0:
                        temp=[len(item[-2])]
                        temp.extend(item[-2][:])
                        temp.extend(tx[tx[0]+1::])
                        isBTC=0
                        inpSum=item[-1]
                        if inpSum>4294967295:
                            isBTC=1
                            inpSum=int(round(inpSum*0.00000001,2)*100)
                        else:
                            inpSum=int(inpSum)

                        temp.extend([isBTC,inpSum])
                        hashMap[k]=temp
                        missingInp[k]=0

            if not any(1 for v in missingInp.values() if type(v)==list and 0 not in v):
                flag=1
                break
            indexx-=1


        lookupDepth.append(depth)
        if flag:
            print("Success.")
            savePickle(hashMap,f"testMaps/{orIndexx}.pickle")
        else:
            error=any(1 for v in missingInp.values() if type(v)==list and 0 not in v)
            if error:
                print("Missing inps. @", orIndexx)
                break
            else:
                print("Success.")
                savePickle(hashMap,f"testMaps/{orIndexx}.pickle")
    saveJSON(lookupDepth,f"lookupDepth.json")


if __name__=="__main__:
    print("getInputs.py")

import pickle, json

def loadPickle(filePath):
	with open(filePath,'rb') as aFile:
		data=pickle.load(aFile)
	return data

def savePickle(data,filePath):
	with open(filePath,'wb') as aFile:
		pickle.dump(data,aFile)

def loadJSON(filePath):
	with open(filePath,encoding='utf8') as aFile:
		data=json.load(aFile)
	return data

def saveJSON(data,filePath):
	with open(filePath, 'w',encoding='utf8') as aFile:
		json.dump(data,aFile,indent=4)

if __name__=="__main__":
    print("fileManager.py")
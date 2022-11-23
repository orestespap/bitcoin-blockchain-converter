from fileManager import saveJSON
import subprocess

if __name__ == '__main__':
    while True:
        try:
            unclustered=int(input("Store unclustered Blockchain?\nYES(1), NO(0): "))
            clustered=int(input("Store clustered Blockchain?\nYES(1), NO(0): "))
            if clustered:
                graphh=int(input("Store Blockchain user graph?\nYES(1), NO(0): "))
            blocks=input("Type in your path to blockchain blocks directory: ")
        except:
            print("Invalid input.")
        else:
            if unclustered+clustered+graphh:
                break
            else:
                print("Select at least one output.")
    saveJSON({"unclustered":unclustered,"clustered":clustered,"graph":graph,"blocks":blocks},"inputs.json")
    subprocess.call("nohup python3 main.py > log.txt 2>&1 </dev/null 
&",shell=True)

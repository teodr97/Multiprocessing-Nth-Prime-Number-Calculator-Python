import multiprocessing as mp
import multiprocessing.sharedctypes as sct
import math as m
import time as t
import sys as s
import queue as q
import os

"""

    Made by Dragon Octavian-Teodor - 10th of October, 2020.
    
    This is my first complete attmept at making a program that calculates
the first 'n' prime numbers using more than one process. Please tell me if
you find anything wrong in here or if you encounter any problems and I'll
try to find a solution.

    The instructions commented out with are JUST for debugging purposes
as they are greatly slowing down the speed of the calculation process when
using more than one core.

"""

counter = mp.Value("d", 1)

s.setrecursionlimit(10 ** 5)

def primeCalc(number):
    if number == 2:
        return True
    elif number > 2 and number % 2 == 0:
        return False
    __maxDiv = m.floor(m.sqrt(number))
    for i in range(3, 1 + __maxDiv, 2):
        if number % i == 0:
            return False
    return True

def primeCalcProcTask(que, procAmount, procNumber, primeTargetRank, counter, solArray, procStatArr, solOrdArr):
    localCounterValue = 0
    #print("[THREAD", procNumber, "]", (primeTargetRank - localCounterValue) // procAmount)
    while counter.value < primeTargetRank:
        with procStatArr.get_lock(): procStatArr[procNumber - 1] = 0
        n = que.get(True)
        
        if primeCalc(n):
            with counter.get_lock():
                counter.value += 1
                localCounterValue = counter.value
            #print(n, localCounterValue) #debug
            with solArray.get_lock():
                solArray[procNumber - 1] = n
            with solOrdArr.get_lock():
                solOrdArr[procNumber - 1] = localCounterValue
            if counter.value >= primeTargetRank:
                with solArray.get_lock():
                    solArray[procNumber - 1] = n
                    #print(solArray[:])
                with solOrdArr.get_lock():
                    solOrdArr[procNumber - 1] = localCounterValue
                with procStatArr.get_lock(): procStatArr[procNumber - 1] = 1
                return
        with procStatArr.get_lock():
            procStatArr[procNumber - 1] = 1
        while 0 in procStatArr[:]: pass
        que.put(n + procAmount)
        if (primeTargetRank - localCounterValue) // procAmount == 0:
            return

def parallelCalc(procNo):
    toBeChecked = mp.Queue()
    counter = mp.Value("i", 1)
    procStatusArr = sct.Array("i", procNo)
    solutionsArray = sct.Array("i", procNo)
    solutionsOrderArray = sct.Array("i", procNo)
    processList = [mp.Process(target = primeCalcProcTask,
                              args = (toBeChecked, procNo, i + 1, number, counter,
                                      solutionsArray, procStatusArr, solutionsOrderArray)) \
                   for i in range(procNo)]
    
    print("══════════PROCESS LIST══════════")
    for proc in processList:
        print(proc)
    print("════════════════════════════════")
    print("══════════INITIALISING══════════")
    t0 = t.time()
    for i in range(procNo):
        toBeChecked.put(i + 3)
    for proc in processList: proc.start()
    for proc in processList: proc.join()
    t1 = t.time()
    print("═════════FINISHED CALC══════════")
    print("[TOTAL CALCULATION TIME][", procNo, " PROCS]: ", t1 - t0, "s.", sep = "")
    for proc in processList: proc.close()
    #print(solutionsArray[:])
    #print(solutionsOrderArray[:])
    solutionsOrderArray = sorted(solutionsOrderArray)
    solutionsArray = sorted(solutionsArray)
    #print(solutionsArray[:])
    #print(solutionsOrderArray[:])
    for i in range(len(solutionsOrderArray)):
        if solutionsOrderArray[i] == number:
            print("[CALC SUCCESS][MSG]: The final result is: ", solutionsArray[i],".", sep = "")
    exit(0)

"""

    The program will only accept a number of prime numbers
to be calculated that is divisible by the amount of
processes used. If the number is not divisible, the biggest
number smaller than the one specified yet divisible by the
amount of used processes will be used because otherwise the
program will not output the correct answer every time (I
guess this is because of sync issues between processes,
dunno. If you find the issue don't hesitate to tell me XD).
    
"""

if __name__ == "__main__":
    inputValid = False

    while inputValid != True:
        try:
            print("══════════════════════════════════════")
            procNo = int(input("Enter the number of the processes you want to use (max. 16): "))
            print("══════════════════════════════════════")
            number = int(input("Enter the rank of the prime number to be calculated (min. is 2 for 1 process or amount of processes used for more)\n\n" \
                               + "\n(!!!) If the rank of the prime number is not divisible \nby the amount of processes used, then the biggest number \nthat is " \
                               + "smaller than the target rank and divisible by the \namount of processes will be used instead. (!!!) \nInput: "))
            print("══════════════════════════════════════")
            if procNo > 16 or procNo < 1 or number < procNo: raise Exception
            inputValid = True
        except:
            print("The rank is not valid (not int)! Try again...")
        while number % procNo != 0:
            print("Reducing target prime number rank to:", number - 1, "(not divisible by procNo)...")
            number -= 1
    parallelCalc(procNo)

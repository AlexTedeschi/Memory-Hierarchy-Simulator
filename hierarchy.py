#!usr/bin/env/python3
#Created by Alex Tedeschi
#Assignment 2 CDA5155 1/24/2022
#Run by using the command: python3 hierarchy.py < trace.dat (Tested on linprog)
import sys
import math

numHitsITLB = 0
numMissesITLB = 0
numHitsDTLB = 0
numMissesDTLB = 0
ptHits = 0
ptFaults = 0
numHitsIC = 0
numMissesIC = 0
numHitsDC = 0
numMissesDC = 0
totalReads = 0
totalWrites = 0
totalInstr = 0
totalData = 0
memoryRefs = 0
diskRefs = 0
LRUCounterIC = 0
LRUCounterDC = 0
LRUCounterITLB = 0
LRUCounterDTLB = 0
LRUPageTable = 0
traceIndex = 0 #index of trace table
pageRA = 0 #page most recently accessed
currentWayIT = 0
currentWayDT = 0
indexIT = 0
indexDT = 0
indexPT = 0

def findInt(tempStr): #finds the integer within a string
    for word in tempStr.split():
        if word.isdigit(): return int(word)

def divideByZero(n, d): #any divide by 0 operations default to 0
    return str(format(float(n/d), '.6f')) if d else "N/A"
        
with open('trace.config', 'r') as file: #opening config file and sets variables from data in the config file
    next(file)
    numSetsIT = findInt(file.readline())
    setSizeIT = findInt(file.readline())
    next(file)
    next(file)
    numSetsDT = findInt(file.readline())
    setSizeDT = findInt(file.readline())
    next(file)
    next(file)
    virtualPages = findInt(file.readline())
    physicalPages = findInt(file.readline())
    pageSize = findInt(file.readline())
    next(file)
    next(file)
    numSetsIC = findInt(file.readline())
    setSizeIC = findInt(file.readline())
    lineSizeIC = findInt(file.readline())
    next(file)
    next(file)
    numSetsDC = findInt(file.readline())
    setSizeDC = findInt(file.readline())
    lineSizeDC = findInt(file.readline())
    wtnwa = "n" if file.readline().find('y') == -1 else "y"
    next(file)
    virtualAddresses = "n" if file.readline().find('y') == -1 else "y"
    TLBs = "n" if file.readline().find('y') == -1 else "y"
    file.close()
    indexBitsIT = int(math.log(numSetsIT,2))
    indexBitsDT = int(math.log(numSetsDT,2))
    pageTableIndex = int(math.log(virtualPages,2))
    pageOffset = int(math.log(pageSize,2))
    indexBitsIC = int(math.log(numSetsIC,2))
    offsetBitsIC = int(math.log(lineSizeIC,2))
    indexBitsDC = int(math.log(numSetsDC,2))
    offsetBitsDC = int(math.log(lineSizeDC,2))

class cache: #class for both caches
    def __init__(self):
        self.LRU = 0
        self.valid = 0
        self.tag = 0
        self.dirty = 0 #only used in DCache
        
class TLB: #class for both TLBs
    def __init__(self):
        self.LRU = 0
        self.valid = 0
        self.tag = 0
        self.pageNum = 0
        self.dirty = 0 #only sued in DTLB

class PageT: #class for page table
    def __init__(self):
        self.LRU = 0
        self.valid = 0
        self.dirty = 0
        self.index = 0
        
class printData: #class for trace printout
    def __init__(self):
        self.virtualAddress = ""
        self.virtualPageNum = ""
        self.pageOffset = ""
        self.refType = ""
        self.TLBTag = ""
        self.TLBIndex = ""
        self.TLBRef = ""
        self.ptRef = ""
        self.physPageNum = ""
        self.cacheTag = ""
        self.cacheIndex = ""
        self.cacheRef = ""

def findLRUCache(cache, numWays, index): #finds the LRU of the cache being entered
    indexOfLRU = 0
    tempLRU = cache[0][index].LRU
    for i in range(numWays):
        if(cache[i][index].LRU < tempLRU):
            tempLRU = cache[i][index].LRU
            indexOfLRU = i
    return indexOfLRU

def findLRUPage(page, numPages): #finds the LRU of the page table
    indexOfLRU = 0
    tempLRU = page[0].LRU
    for i in range(numPages):
        if(page[i].LRU < tempLRU):
            tempLRU = page[i].LRU
            indexOfLRU = i
    return indexOfLRU

def printConfig(): #prints out configuration
    print("Instruction TLB contains " + str(numSetsIT) + " sets.")
    print("Each set contains " + str(setSizeIT) + " entries.")
    print("Number of bits used for the index is " + str(indexBitsIT) + ".\n")

    print("Data TLB contains " + str(numSetsDT) + " sets.")
    print("Each set contains " + str(setSizeDT) + " entries.")
    print("Number of bits used for the index is " + str(indexBitsDT) + ".\n")

    print("Number of virtual pages is " + str(virtualPages) + ".")
    print("Number of physical pages is " + str(physicalPages) + ".")
    print("Each page contains " + str(pageSize) + " bytes.")
    print("Number of bits used for the page table index is " + str(pageTableIndex) + ".")
    print("Number of bits used for the page offset is " + str(pageOffset) + ".\n")

    print("I-cache contains " + str(numSetsIC) + " sets.")
    print("Each set contains " + str(setSizeIC) + " entries.")
    print("Each line is " + str(lineSizeIC) + " bytes.")
    print("Number of bits used for the index is " + str(indexBitsIC) +  ".")
    print("Number of bits used for the offset is " + str(offsetBitsIC) + ".\n")

    print("D-cache contains " + str(numSetsDC) + " sets.")
    print("Each set contains " + str(setSizeDC) + " entries.")
    print("Each line is " + str(lineSizeDC) + " bytes.")
    print("The cache uses a no write-allocate and write-through policy.") if wtnwa == "y" else print("The cache uses write-allocate and write-back policy.")
    print("Number of bits used for the index is " + str(indexBitsDC) + ".")
    print("Number of bits used for the offset is " + str(offsetBitsDC) + ".\n")

    print("The addresses read in are virtual addresses.") if virtualAddresses == "y" else print("The addresses read in are physical addresses.")
    print("TLBs are disabled in this configuration.") if TLBs == "n" else print(end = '')

def printStats(): #prints out simulation stats
    print("\nSimulation statistics\n")
    print("itlb hits        : " + str(numHitsITLB))
    print("itlb misses      : " + str(numMissesITLB))
    print("itlb hit ratio   : " + divideByZero(numHitsITLB, numHitsITLB+numMissesITLB))
    print("\ndtlb hits        : " + str(numHitsDTLB))
    print("dtlb misses      : " + str(numMissesDTLB))
    print("dtlb hit ratio   : " + divideByZero(numHitsDTLB, numHitsDTLB+numMissesDTLB))
    print("\npt hits          : " + str(ptHits))
    print("pt faults        : " + str(ptFaults))
    print("pt hit ratio     : " + divideByZero(ptHits, ptHits+ptFaults))
    print("\nic hits          : " + str(numHitsIC))
    print("ic misses        : " + str(numMissesIC))
    print("ic hit ratio     : " + divideByZero(numHitsIC, numHitsIC+numMissesIC))
    print("\ndc hits          : " + str(numHitsDC))
    print("dc misses        : " + str(numMissesDC))
    print("dc hit ratio     : " + divideByZero(numHitsDC, numHitsDC+numMissesDC))
    print("\nTotal reads      : " + str(totalReads))
    print("Total writes     : " + str(totalWrites))
    print("Ratio of reads   : " + divideByZero(totalReads, totalReads+totalWrites))
    print("\nTotal inst refs  : " + str(totalInstr))
    print("Total data refs  : " + str(totalData))
    print("Ratio of insts   : " + divideByZero(totalInstr, totalInstr+totalData))
    print("\nmain memory refs : " + str(memoryRefs))
    print("disk refs        : " + str(diskRefs))
    
ICache = [[cache() for y in range(numSetsIC)] for x in range(setSizeIC)] #numSetsIC are rows. setSizeIC are columns (ways)
DCache = [[cache() for y in range(numSetsDC)] for x in range(setSizeDC)] #numSetsDC are rows. setSizeDC are columns (ways)
ITLB = [[TLB() for y in range(numSetsIT)] for x in range(setSizeIT)] #numSetsIT are rows. setSizeIT are columns (ways)
DTLB = [[TLB() for y in range(numSetsDT)] for x in range(setSizeDT)] #numSetsDT are rows. setSizeDT are columns (ways)
pageTable = [PageT() for y in range(physicalPages)] #no ways in page table. rows only
traceData = [] #array for trace output

for trace in sys.stdin.readlines(): #one line from trace.dat at a time
    traceIndex += 1
    traceData.append(printData())
    nextStep = False #used to break out of loop when finding a hit in the cache, tlb, or page
    typeIns = trace[0]
    operation = trace[2]
    binary = str(bin(int(trace[4:], 16)).replace("0b", "").zfill(32))
    
    if virtualAddresses == "y" and trace[0] == "I":
        offset = int(binary[32-pageOffset:], 2)
        indexIT = int(binary[32-pageOffset-indexBitsIT:32-pageOffset], 2)
        indexPT = int(binary[32-pageOffset-pageTableIndex:32-pageOffset], 2)
        tag = int(binary[0:32-pageOffset-indexBitsIT], 2)
        virtualPageNum = int(binary[0:32-pageOffset], 2)
        
        traceData[traceIndex-1].virtualAddress = trace[4:].replace("\n", "").zfill(8)
        traceData[traceIndex-1].virtualPageNum = str(hex(virtualPageNum).replace("0x", ""))
        traceData[traceIndex-1].pageOffset = str(hex(offset).replace("0x", ""))
        traceData[traceIndex-1].refType = "inst"
        traceData[traceIndex-1].TLBTag = str(hex(tag)).replace("0x","")
        traceData[traceIndex-1].TLBIndex = str(indexIT)

        for a in range(setSizeIT):
            if ITLB[a][indexIT].tag == tag and ITLB[a][indexIT].valid == 1: #TLB hit
                numHitsITLB += 1
                ITLB[a][indexIT].LRU = LRUCounterITLB
                LRUCounterITLB += 1
                traceData[traceIndex-1].TLBRef = str("hit")
                traceData[traceIndex-1].ptRef = str("none")
                traceData[traceIndex-1].physPageNum = ITLB[a][indexIT].pageNum
                currentWayIT = a
                nextStep = True
                break
            
        if nextStep == True:
            nextStep = False
        else:
            traceData[traceIndex-1].TLBRef = str("miss") #TLB miss
            for b in range(setSizeIT):
                LRUPageTable += 1
                LRUCounterITLB += 1
                numMissesITLB += 1
                memoryRefs += 1
                currentLRUITLB = findLRUCache(ITLB, setSizeIT, indexIT)
                currentLRUPage = findLRUPage(pageTable, physicalPages)
                
                for c in range(physicalPages):
                    if pageTable[c].valid == 1 and pageTable[c].index == int(binary[0:32-pageOffset], 2): #Page Table hit
                        ptHits += 1
                        pageTable[c].LRU = LRUPageTable
                        pageRA = c
                        traceData[traceIndex-1].ptRef = str("hit")
                        traceData[traceIndex-1].physPageNum = c
                        if pageTable[c].dirty == 1:
                            pageTable[c].dirty = 0
                            diskRefs += 1
                        if trace[2] == "W":
                            pageTable[c].dirty = 1
                        nextStep = True
                        break
                    
                if nextStep == True:
                    nextStep = False
                else:
                    for d in range(physicalPages): #Page Table miss
                        if pageTable[d].valid == 0:
                            diskRefs += 1
                            pageTable[d].valid = 1
                            pageTable[d].LRU = LRUPageTable
                            traceData[traceIndex-1].ptRef = str("miss")
                            traceData[traceIndex-1].physPageNum = d
                            ptFaults += 1
                            pageRA = d
                            pageTable[d].index = virtualPageNum
                            break
                        elif d == physicalPages - 1 and pageTable[d].valid == 1: #invalidate bits that stored a page number that has been replaced
                            for i in range(setSizeIT):
                                for j in range(numSetsIT):
                                    if ITLB[i][j].pageNum == pageRA:
                                        ITLB[i][j].valid = 0
                            for k in range(setSizeDT):
                                for l in range(numSetsDT):
                                    if DTLB[k][l].pageNum == pageRA:
                                        DTLB[k][l].valid = 0
                            for m in range(setSizeIC):
                                for n in range(numSetsIC):
                                    tempStr1 = str(bin(ICache[m][n].tag).replace("0b", "")) + str(bin(n).replace("0b", "")).ljust(offsetBitsIC, '0')
                                    if str(bin(currentLRUPage).replace("0b", "")).ljust(pageOffset, '0') == tempStr1:
                                        ICache[m][n].valid = 0
                            for o in range(setSizeDC):
                                for p in range(numSetsDC):
                                    tempStr2 = str(bin(DCache[o][p].tag).replace("0b", "")) + str(bin(p).replace("0b", "")).ljust(offsetBitsDC, '0')
                                    if str(bin(currentLRUPage).replace("0b", "")).ljust(pageOffset, '0') == tempStr2:
                                        DCache[o][p].valid = 0
                            diskRefs += 1
                            pageTable[currentLRUPage].LRU = LRUPageTable
                            traceData[traceIndex-1].ptRef = str("miss")
                            traceData[traceIndex-1].physPageNum = currentLRUPage
                            ptFaults += 1
                            pageRA = currentLRUPage
                            pageTable[currentLRUPage].index = str(hex(virtualPageNum).replace("0x", ""))
                            if pageTable[currentLRUPage].dirty == 1:
                                pageTable[currentLRUPage].dirty = 0
                                diskRefs += 1
                            if trace[2] == "W":
                                pageTable[currentLRUPage].dirty = 1
                                
                if ITLB[b][indexIT].valid == 0: #TLB miss situations
                    ITLB[b][indexIT].valid = 1
                    ITLB[b][indexIT].pageNum = pageRA
                    ITLB[b][indexIT].tag = tag
                    ITLB[b][indexIT].LRU = LRUCounterITLB
                    traceData[traceIndex-1].virtualPageNum = str(hex(virtualPageNum).replace("0x", ""))
                    currentWayIT = b
                    break
                elif ITLB[currentLRUITLB][indexIT].valid == 1 and b == setSizeIT - 1:
                    ITLB[currentLRUITLB][indexIT].pageNum = pageRA
                    ITLB[currentLRUITLB][indexIT].tag = tag
                    ITLB[currentLRUITLB][indexIT].LRU = LRUCounterITLB
                    traceData[traceIndex-1].virtualPageNum = str(hex(virtualPageNum).replace("0x", ""))
                    currentWayIT = currentLRUITLB
    
    if virtualAddresses == "y" and trace[0] == "D":
        offset = int(binary[32-pageOffset:], 2)
        indexDT = int(binary[32-pageOffset-indexBitsDT:32-pageOffset], 2)
        indexPT = int(binary[32-pageOffset-pageTableIndex:32-pageOffset], 2)
        tag = int(binary[0:32-pageOffset-indexBitsDT], 2)
        virtualPageNum = int(binary[0:32-pageOffset], 2)
        
        traceData[traceIndex-1].virtualAddress = trace[4:].replace("\n", "").zfill(8)
        traceData[traceIndex-1].virtualPageNum = str(hex(virtualPageNum).replace("0x", ""))
        traceData[traceIndex-1].pageOffset = str(hex(offset).replace("0x", ""))
        traceData[traceIndex-1].refType = "inst"
        traceData[traceIndex-1].TLBTag = str(hex(tag)).replace("0x","")
        traceData[traceIndex-1].TLBIndex = str(indexDT)

        for e in range(setSizeDT):
            if DTLB[e][indexDT].tag == tag and DTLB[e][indexDT].valid == 1: #TLB hit
                numHitsDTLB += 1
                DTLB[e][indexDT].LRU = LRUCounterDTLB
                LRUCounterDTLB += 1
                traceData[traceIndex-1].TLBRef = str("hit")
                traceData[traceIndex-1].ptRef = str("none")
                traceData[traceIndex-1].physPageNum = DTLB[e][indexDT].pageNum
                currentWayDT = e
                nextStep = True
                if DTLB[e][indexDT].dirty == 1:
                    DTLB[e][indexDT].dirty = 0
                    diskRefs += 1
                if trace[2] == "W":
                    DTLB[e][indexDT].dirty = 1
                break

        if nextStep == True:
            nextStep = False
        else:
            traceData[traceIndex-1].TLBRef = str("miss") #TLB Miss
            for f in range(setSizeDT):
                LRUPageTable += 1
                LRUCounterDTLB += 1
                numMissesDTLB += 1
                memoryRefs += 1
                currentLRUDTLB = findLRUCache(DTLB, setSizeDT, indexDT)
                currentLRUPage = findLRUPage(pageTable, physicalPages)
                
                for g in range(physicalPages):
                    if pageTable[g].valid == 1 and pageTable[g].index == int(binary[0:32-pageOffset], 2): #Page Table hit
                        ptHits += 1
                        pageTable[g].LRU = LRUPageTable
                        pageRA = g
                        traceData[traceIndex-1].ptRef = str("hit")
                        traceData[traceIndex-1].physPageNum = g
                        if pageTable[g].dirty == 1:
                            pageTable[g].dirty = 0
                            diskRefs += 1
                        if trace[2] == "W":
                            pageTable[g].dirty = 1
                        nextStep = True
                        break
                    
                if nextStep == True:
                    nextStep = False
                else:
                    for h in range(physicalPages): #Page Table miss
                        if pageTable[h].valid == 0:
                            diskRefs += 1
                            pageTable[h].valid = 1
                            pageTable[h].LRU = LRUPageTable
                            traceData[traceIndex-1].ptRef = str("miss")
                            traceData[traceIndex-1].physPageNum = h
                            ptFaults += 1
                            pageRA = h
                            pageTable[h].index = virtualPageNum
                            break
                        elif h == physicalPages - 1 and pageTable[h].valid == 1: #invalidate bits that stored a page number that has been replaced
                            for q in range(setSizeIT):
                                for r in range(numSetsIT):
                                    if ITLB[q][r].pageNum == pageRA:
                                        ITLB[q][r].valid = 0
                            for s in range(setSizeDT):
                                for t in range(numSetsDT):
                                    if DTLB[s][t].pageNum == pageRA:
                                        DTLB[s][t].valid = 0
                            for u in range(setSizeIC):
                                for v in range(numSetsIC):
                                    tempStr3 = str(bin(ICache[u][v].tag).replace("0b", "")) + str(bin(v).replace("0b", "")).ljust(offsetBitsIC, '0')
                                    if str(bin(currentLRUPage).replace("0b", "")).ljust(pageOffset, '0') == tempStr3:
                                        ICache[u][v].valid = 0
                            for x in range(setSizeDC):
                                for y in range(numSetsDC):
                                    tempStr4 = str(bin(DCache[x][y].tag).replace("0b", "")) + str(bin(y).replace("0b", "")).ljust(offsetBitsDC, '0')
                                    if str(bin(currentLRUPage).replace("0b", "")).ljust(pageOffset, '0') == tempStr4:
                                        DCache[x][y].valid = 0
                            diskRefs += 1
                            pageTable[currentLRUPage].LRU = LRUPageTable
                            traceData[traceIndex-1].ptRef = str("miss")
                            traceData[traceIndex-1].physPageNum = currentLRUPage
                            ptFaults += 1
                            pageRA = currentLRUPage
                            pageTable[currentLRUPage].index = str(hex(virtualPageNum).replace("0x", ""))
                            if pageTable[currentLRUPage].dirty == 1:
                                pageTable[currentLRUPage].dirty = 0
                                diskRefs += 1
                            if trace[2] == "W":
                                pageTable[currentLRUPage].dirty = 1
                                
                if DTLB[f][indexDT].valid == 0: #TLB miss situations
                    DTLB[f][indexDT].valid = 1
                    DTLB[f][indexDT].pageNum = pageRA
                    DTLB[f][indexDT].tag = tag
                    DTLB[f][indexDT].LRU = LRUCounterDTLB
                    traceData[traceIndex-1].virtualPageNum = str(hex(virtualPageNum).replace("0x", ""))
                    currentWayDT = f
                    break
                elif DTLB[f][indexDT].valid == 1 and f == setSizeDT - 1:
                    DTLB[currentLRUDTLB][indexDT].pageNum = pageRA
                    DTLB[currentLRUDTLB][indexDT].tag = tag
                    DTLB[currentLRUDTLB][indexDT].LRU = LRUCounterDTLB
                    traceData[traceIndex-1].virtualPageNum = str(hex(virtualPageNum).replace("0x", ""))
                    if DTLB[currentLRUDTLB][indexDT].dirty == 1:
                        DTLB[currentLRUDTLB][indexDT].dirty = 0
                        diskRefs += 1
                    if trace[2] == "W":
                        DTLB[currentLRUDTLB][indexDT].dirty = 1
                    currentWayDT = currentLRUDTLB
                        
    if trace[0] == "I":
        if virtualAddresses == "y": #virtual to physical address
            binary = str(binary[0:32-pageOffset-pageTableIndex]+ str(bin(int(ITLB[currentWayIT][indexIT].pageNum)).replace("0b", "").zfill(pageTableIndex)) + binary[32-pageOffset:])
        totalReads += 1
        totalInstr += 1
        LRUCounterIC += 1
        offset = int(binary[32-offsetBitsIC:], 2)
        index = int(binary[32-offsetBitsIC-indexBitsIC:32-offsetBitsIC], 2)
        tag = int(binary[0:32-offsetBitsIC-indexBitsIC], 2)
        traceData[traceIndex-1].cacheTag = str(hex(tag)).replace("0x","")
        traceData[traceIndex-1].cacheIndex = index
        currentLRU = findLRUCache(ICache, setSizeIC, index)
        
        for aa in range(setSizeIC):
            if ICache[aa][index].tag == tag and ICache[aa][index].valid == 1: #tag of the current instruction is already in cache. Is a hit.
                numHitsIC += 1
                ICache[aa][index].LRU = LRUCounterIC
                traceData[traceIndex-1].cacheRef = "hit"
                nextStep = True
                break
        if nextStep == True: #if instruction was a hit, go to next instruction
            nextStep = False
        else:
            for bb in range(setSizeIC):
                if ICache[bb][index].valid == 0: #cache is not full and tag is not present already. Is a miss.
                    memoryRefs += 1
                    numMissesIC += 1
                    ICache[bb][index].valid = 1
                    ICache[bb][index].tag = tag
                    ICache[bb][index].LRU = LRUCounterIC
                    traceData[traceIndex-1].cacheRef = "miss"
                    break
                elif bb == setSizeIC - 1 and ICache[bb][index].valid == 1: #cache is full but is a miss.
                    memoryRefs += 1
                    numMissesIC += 1
                    ICache[currentLRU][index].tag = tag
                    ICache[currentLRU][index].LRU = LRUCounterIC
                    traceData[traceIndex-1].cacheRef = "miss"
    if trace[0] == "D":
        if trace[2] == "R":
            totalReads += 1
        else:
            totalWrites += 1
        if virtualAddresses == "y": #virtual to physical address
            binary = str(binary[0:32-pageOffset-pageTableIndex]+ str(bin(int(DTLB[currentWayDT][indexDT].pageNum)).replace("0b", "").zfill(pageTableIndex)) + binary[32-pageOffset:])
        traceData[traceIndex-1].refType = "data"
        totalData += 1
        LRUCounterDC += 1
        offset = int(binary[32-offsetBitsDC:], 2)
        index = int(binary[32-offsetBitsDC-indexBitsDC:32-offsetBitsDC], 2)
        tag = int(binary[0:32-offsetBitsDC-indexBitsDC], 2)
        traceData[traceIndex-1].cacheTag = str(hex(tag)).replace("0x","")
        traceData[traceIndex-1].cacheIndex = index
        currentLRU = findLRUCache(DCache, setSizeDC, index)
        
        for cc in range(setSizeDC):
            if DCache[cc][index].tag == tag and DCache[cc][index].valid == 1: #tag of the current instruction is already in cache. Is a hit.
                numHitsDC += 1
                DCache[cc][index].LRU = LRUCounterDC
                if DCache[cc][index].dirty == 1:
                    DCache[cc][index].dirty = 0
                    diskRefs += 1
                if wtnwa == "y":
                    memoryRefs += 1
                nextStep = True
                traceData[traceIndex-1].cacheRef = "hit"
                break
        if nextStep == True: #if instruction was a hit, go to next instruction
            nextStep = False
        else:
            for dd in range(setSizeDC):
                if DCache[dd][index].valid == 0 and (wtnwa == "n" or trace[2] == "R"): #cache is not full and tag is not present already. Is a miss.
                    memoryRefs += 1
                    numMissesDC += 1
                    DCache[dd][index].valid = 1
                    DCache[dd][index].tag = tag
                    DCache[dd][index].LRU = LRUCounterDC
                    traceData[traceIndex-1].cacheRef = "miss"
                    break
                elif dd == setSizeDC - 1 and DCache[dd][index].valid == 1 and (wtnwa == "n" or trace[2] == "R"): #cache is full but is a miss.
                    memoryRefs += 1
                    numMissesDC += 1
                    DCache[currentLRU][index].tag = tag
                    DCache[currentLRU][index].LRU = LRUCounterDC
                    traceData[traceIndex-1].cacheRef = "miss"
                    if DCache[dd][index].dirty == 1:
                        DCache[dd][index].dirty = 0
        
def printInfo():
    print("\nVirtual  Virtual Page   Ref  TLB     TLB   TLB  PT   Phys   Cache   Cache Cache")
    print("Address  Page #  Offset Type Tag     Index Ref  Ref  Page # Tag     Index Ref ")
    print("-------- ------- ------ ---- ------- ----- ---- ---- ------ ------- ----- -----")
    for a in traceData: #"%08x %7x %6x %4s %7x %5x %4s %4s %6x %7x %5x %4s"
        print("%8s %7s %6s %-4s %7s %5s %-4s %-4s %6s %7s %5s %-4s" % (a.virtualAddress, a.virtualPageNum, a.pageOffset, a.refType, 
        a.TLBTag, a.TLBIndex, a.TLBRef, a.ptRef, a.physPageNum, a.cacheTag, a.cacheIndex, a.cacheRef))
    
printConfig()           
printInfo()
printStats()
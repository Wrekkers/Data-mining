# -*- coding: utf-8 -*-
"""
Created on Fri Mar 31 10:12:35 2017

@author: BHANU & Abhilash
"""

import timeit

class FP_Node:
    def __init__(self, item, numocc, parentNode):
        self.name = item
        self.count = numocc
        self.children = {}
        self.nodeLink = None
        self.parent = parentNode
        
    def inc(self, val):
        self.count += val
        
    def disp(self, ind=1):
        if(ind == 1):
            print(self.name, ' : ', self.count)
        else:
            print ('    |'*(ind-1),'--', self.name, ':', self.count)
        for child in self.children.values():
            child.disp(ind+1)


def FPtree_gen(sort_items, dataset, header):
    
    Fp_tree = FP_Node('Null Set', 1, None)
    
    for trans in dataset:
        orderedItems = list()
        for item in sort_items:
            if (item in set(trans)):
                orderedItems.append(item)
        #call update
        if (len(orderedItems)>0):
            updateTree(orderedItems, Fp_tree, header, 1)

    return Fp_tree

def updateTree(items, inTree, headerTable, count):
    if (items[0]) in inTree.children:#check if orderedItems[0] in retTree.children
        inTree.children[items[0]].inc(count) #incrament count
    else:   #add items[0] to inTree.children
        inTree.children[items[0]] = FP_Node(items[0], count, inTree)
        if headerTable[items[0]][1] == None: #update header table 
            headerTable[items[0]][1] = inTree.children[items[0]]
        else:
            updateHeader(headerTable[items[0]][1], inTree.children[items[0]])
    if len(items) > 1:#call updateTree() with remaining ordered items
        updateTree(items[1::], inTree.children[items[0]], headerTable, count)


def updateHeader(nodeToTest, targetNode):   #this version does not use recursion
    while (nodeToTest.nodeLink != None):    
        nodeToTest = nodeToTest.nodeLink
    nodeToTest.nodeLink = targetNode
    

raw = open('sam.dat')

data = []
f_set = []
max_no = 0

i=-1
for line in raw:
    i+=1
    data.append([int(y) for y in line.split()])
    for x in data[i]:
        if (x>max_no):
            max_no = x
            

struc = [[0 for col in range(max_no)] for row in range(len(data)+1)]

row=0
for trans in data:
    col=0
    for item in trans:
        struc[row+1][item-1] = 1
        struc[0][item-1] += 1
        col+=1
    row +=1
    

#min_S = input('Enter the value of minimum Suppourt :')
#min_C = input('Enter the valur of minimum Confidence :')

min_S = 0.5
min_C = 0.7

support = min_S * len(data)

item_sort = []
headerTable = {}
item_skip = [0]*(max_no)


curr_ind = 0
for i in range(max_no):
    curr_max = 0
    flag = 0
    for j in range(max_no):
        if(item_skip[j] == 0):
            if(curr_max < struc[0][j] and support <= struc[0][j]):
                curr_ind = j
                curr_max = struc[0][j]
                flag = 1
    
    if(item_skip[curr_ind] == 0 and flag == 1):
        item_sort.extend([curr_ind+1])
        headerTable[curr_ind+1] = [struc[0][curr_ind], None]
        item_skip[curr_ind] = 1


#print(headerTable)


FP_tree = FPtree_gen(item_sort, data, headerTable)


FP_tree.disp()


#######MINING########



def ascendTree(leafNode, prefixPath): #ascends from leaf node to root
    if leafNode.parent != None:
        prefixPath.append(leafNode.name)
        ascendTree(leafNode.parent, prefixPath)

#def findPrefixPath(basePat, treeNode): #treeNode comes from header table
def findPrefixPath(treeNode):
    condPats = {}
    while treeNode != None:
        prefixPath = []
        ascendTree(treeNode, prefixPath)
        if len(prefixPath) > 1: 
            condPats[frozenset(prefixPath[1:])] = treeNode.count
        treeNode = treeNode.nodeLink
    return condPats

def createTree2(condPats,flist):
    freqItemSet = set(flist.keys())
    for k in flist:
        flist[k] = [flist[k], None]
    retTree = FP_Node('Null Set', 1, None) #create tree
    for patSet, count in condPats.items():  #go through dataset 2nd time
        localD = {}
        for item in patSet:  #put transaction items in order
            if item in freqItemSet:
                localD[item] = flist[item][0]
        if len(localD) > 0:
            orderedItems = [v[0] for v in sorted(localD.items(), key=lambda p: p[1], reverse=True)]
            updateTree(orderedItems, retTree, flist, count)#populate tree with ordered freq itemset
    return retTree, flist #return tree and header table


def findFPforItem(fptree, headerTable,minSup,item,freq_pat,bas_pat,bas_freq):
    condPats = findPrefixPath(headerTable[item][1])
    bas_pat.append(item)
    #print('patt',bas_pat)
    flist = {}
    if len(condPats) > 0:
        for pat in condPats:
            for pat_item in pat:
                if pat_item in flist:
                    flist[pat_item] = flist[pat_item] + condPats[pat]
                else:
                    flist[pat_item] = condPats[pat]
                #flist[pat_item] = flist.get(pat_item,0) + condPats[pat]
    else:
        freq_pat[item] = bas_freq 
    
    if len(flist) > 0:
        for k in list(flist):  #remove items not meeting minSup
            if flist[k] < minSup: 
                del(flist[k])
        if len(flist)==1 :
            for l in flist:
                freq_pat[item] = bas_freq
                fp = []
                fp.extend(bas_pat)
                fp.append(l)
                freq_pat[frozenset(fp)] = flist[l]
                del bas_pat[:]
        else:
            #print("Tree",item)
            #print('patt',bas_pat)
            condTree, condFlist = createTree2(condPats,flist)
            findFP(condTree, condFlist, minSup,freq_pat,bas_pat,bas_freq)
    #print(item)            
    #print(freq_pat)
        
        
def findFP(fptree, headerTable, minSup,freq_pat,bas_pat,bas_freq):
    orderedHeaderList = [v[0] for v in sorted(headerTable.items(), key=lambda p: p[1][0], reverse=False)]
    #freq_pat = {}
    if len(bas_pat)>0:
            freq_pat[frozenset(bas_pat)] = bas_freq
    for item in orderedHeaderList:  
        findFPforItem(fptree,headerTable,minSup,item,freq_pat,bas_pat,headerTable[item][0])

freq_pat= {}

bas_pat = []
bas_freq = 0

findFP(FP_tree,headerTable,support,freq_pat,bas_pat,bas_freq)

print(freq_pat)
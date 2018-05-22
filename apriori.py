# -*- coding: utf-8 -*-
"""
Created on Wed Mar 22 21:34:13 2017

@author: BHANU & Abhilash
"""

import timeit


def apriori_fset(d_str,sup,tot_trans,max_it):
    f_itemset = []
    one_set = []
    curr_it = 0
    total_set = 0
    for i in range(max_it):
        if((d_str[0][i]/tot_trans)>= sup):
            f_itemset.append([(i+1),d_str[0][i]])
            one_set.extend([i+1])
            total_set += 1
    
    #increasing the list of frequent item set by 1
    for j in range(max_it):
        f_itemset.extend(add_elem(f_itemset,sup,curr_it,total_set,d_str,one_set,tot_trans))
        curr_it = total_set
        total_set = len(f_itemset)
        if (total_set - curr_it < 2):
            #finished adding all
            break
    
    return f_itemset

def add_elem(old_l, sup,curr,tot_i,data_str,k_one,tot_trans):
    i=0
    new_l = []
    for l in old_l:
        if (i>=curr and i<=tot_i):
            m = l[len(l)-2]
            for n in k_one:
                if(n<=m):
                    continue
                temp = []
                temp.extend(l[:(len(l)-1)])
                temp.extend([n])
                a_flg = 1
                j=0
                for chk in l[:(len(l)-1)]:
                    temp2 = []
                    temp2.extend(l[:(len(l)-1)])
                    temp2.pop(j)
                    temp2.extend([n])
                    ctr = 0
                    for l2 in old_l:
                        if(set(temp2)==set(l2[:(len(l2)-1)])):
                            ctr = -1
                            break
                        ctr += 1
                    if (ctr == len(old_l)):
                        a_flg = 0
                    del temp2[:]
                    if(a_flg==0):
                        break
                    j+=1
                if(a_flg == 0):
                    continue
                count_f = 0
                for t in data_str:
                    for x in temp:
                        flag = 1
                        if (t[x-1]==0 or t[x-1]>1):
                            flag = 0
                            break
                    if(flag == 1):
                        count_f +=1
                if((count_f/tot_trans)>= sup):
                    temp.extend([count_f])
                    new_l.append(temp)
                
        i += 1
    return new_l

def apriori_rulegen(fre_set, struct, conf):
    rules = []
    for sets in fre_set:
        if (len(sets)<2):
            continue
        #rest of the algorithm
        rules.extend(rules_set(sets,struct,conf,fre_set))        
    return rules                


def rules_set (giv_set,data_s,conf,f_set):
    new_rules = []
    len_set = len(giv_set)-1
    skip_list = [0]*(len_set)
    
    curr_rule = "0"*(len_set)
    curr_rule = curr_rule[:(len_set-1)] + '1'
    count_all = giv_set[len_set]
    
    for pos in range((2 ** (len_set))-2):
        # will partion the set using binary
        new_r = []
        left = []
        right = []
        skip_now = 0
        for i in range(len_set):
            
            if(curr_rule[i]=='0'):
                left.extend([giv_set[i]])
            else:
                if(skip_list[i]==1):
                    skip_now=1
                    break
                right.extend([giv_set[i]])
        if(skip_now == 0):
            count_left = 0
            curr_conf = 0.0
            
            #check skip list (if in skip list )
            
            for c_set in f_set:
                if(set(c_set[:(len(c_set)-1)]) == set(left)):
                    count_left = c_set[(len(c_set)-1)]
                    break
            curr_conf = count_all/count_left
            flag = 0
            if(curr_conf>=conf):
                new_r.append(left)
                new_r.append(right)
                new_rules.append(new_r)
                flag = 1
                if(flag == 0):
                    for r in range(len_set):
                        if(curr_rule[r]=='1'):
                            skip_list[r]=1
        curr_rule = bin(int(curr_rule,2) + int('1',2))
        curr_rule = curr_rule[2:]
        curr_rule = curr_rule.zfill(len_set)
        
    return new_rules


raw = open('chess.dat')

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

start = timeit.timeit()

f_set = apriori_fset(struc,min_S,len(data),max_no)

check = timeit.timeit()

F_rule = apriori_rulegen(f_set, struc, min_C)

end = timeit.timeit()

X = f_set
print('Frequent Item Sets: ')
for freq in X:
    print(freq[:(len(freq)-1)])

print('Rules: ')
for rule in F_rule:
    print(rule[0],'->',rule[1])
    
print ("Time taken for frequent set generation: ", (check-start))

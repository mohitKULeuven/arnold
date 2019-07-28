#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 31 06:39:42 2019

@author: mohit
"""
import numpy as np
import itertools as it
import Tensor
from collections import Counter
import random


def allUnique(x):
    seen = set()
    return not any(i in seen or seen.add(i) for i in x) 

def counterSubset(list1, list2,removed,listBadTensor):
    tmp=list2.copy()
    tmp=[i for i in tmp if i not in removed]
    for t in listBadTensor:
        if t in tmp:
            return False
    c1, c2 = Counter(list1), Counter(list2)
    for k, n in c1.items():
        if n > c2[k]:
            return False
    return True

def isSubset(list1, list2,removed,listBadTensor):
    output=[]
    m=len(list1)
    n=len(list2)
    indMat=np.zeros([m, n])
    tmpList=[]
    for i in range(m):
        for j in range(n):
            if counterSubset(list1[i], list2[j],removed[i],listBadTensor):
                indMat[i][j]=1
        tmpList.append([k for k,e in enumerate(indMat[i]) if e==1])
    
    for indices in it.product(*tmpList):
        if allUnique(indices):
            output.append(list(indices))
    if output:
        return output,True
    return output,False
 
def tensorSum(T):
    for i in range(len(T)):
        T[i].bubbleSort()
    output=T[0].data
    for i in range(1,len(T)):
        if T[i].data.shape==T[i-1].data.shape and T[i-1].dimensions==T[i].dimensions:
            output+=T[i].data
    return Tensor.Tensor(output,T[i].type,T[i].dimensions,0,1,T[i].name)

def tensorDotProduct(T,dimension_length): 
    newDim=T[0].dimensions.copy()
    lengthNewDim=len(newDim)
    
    dimPos=[0]*len(T) #identifies the position of dimension in the newDim
    dimPos[0]=list(range(len(T[0].dimensions)))
    
    for i in range(1,len(T)):
        dimPos[i]=[]
        for elem in T[i].dimensions.copy():
            if elem in newDim:
                dimPos[i].append(newDim.index(elem))
            else:
                newDim.append(elem)
                dimPos[i].append(lengthNewDim)
                lengthNewDim+=1
    
    outputMatSize=[]
    outputMatLoop = ()
    for i in range(len(newDim)):
        outputMatSize.append(dimension_length[newDim[i]])
        outputMatLoop+=(range(dimension_length[newDim[i]]),)
    outputTensor = np.ones(outputMatSize)
    
    for multiIndex in it.product(*outputMatLoop):
        for i in range(len(T)):
            outputTensor[multiIndex]=outputTensor[multiIndex]*T[i].data[tuple([multiIndex[j] for j in dimPos[i]])]
    return Tensor.Tensor(outputTensor,T[i].type,newDim,0,1,T[i].name)

def powerset(seq):
    """
    Returns all the subsets of this set. This is a generator.
    """
    if len(seq) <= 1:
        yield seq
        yield []
    else:
        for item in powerset(seq[1:]):
            yield [seq[0]]+item
            yield item
            
def compareTensorsLE(T1, T2,dimension_length):
    
    indices2=[T2.dimensions.index(i) for i in T1.dimensions if i in T2.dimensions]
    outputMatLoop1 = ()
    
    for i in range(len(T1.dimensions)):
        outputMatLoop1+=(range(dimension_length[T1.dimensions[i]]),)
    for multiIndex1 in it.product(*outputMatLoop1):
        outputMatLoop2 = ()
        for i in range(len(T2.dimensions)):
            if i in indices2:
                tmp=T1.dimensions.index(T2.dimensions[i])
                outputMatLoop2+=(range(multiIndex1[tmp],multiIndex1[tmp]+1),)
            else:
                outputMatLoop2+=(range(dimension_length[T2.dimensions[i]]),)
        for multiIndex2 in it.product(*outputMatLoop2):
            if T1.data[multiIndex1] > T2.data[multiIndex2]:
                return False
    return True

def compareTensorsGE(T1, T2,dimension_length):
    indices=[T1.dimensions.index(i) for i in T2.dimensions]
    outputMatLoop1 = ()
    outputMatLoop2 = ()
    for i in range(len(T2.dimensions)):
        outputMatLoop1+=(range(dimension_length[T1.dimensions[i]]),)
    for multiIndex1 in it.product(*outputMatLoop1):
        for i in range(len(T1.dimensions)):
            if i in indices:
                outputMatLoop2+=(range(multiIndex1[indices.index(i)],multiIndex1[indices.index(i)]+1),)
            else:
                outputMatLoop2+=(range(dimension_length[T2.dimensions[i]]),)
        for multiIndex2 in it.product(*outputMatLoop2):
            if T1[multiIndex1] < T2[multiIndex2]:
                return False
    return True

def tensorSlice(X,dim,dimension_length):
    if X.dimensions==dim:
        return X
    outputMatSize=[]
    outputMatLoop = ()
    for i in range(len(dim)):
        outputMatSize.append(dimension_length[dim[i]])
        outputMatLoop+=(range(dimension_length[dim[i]]),)
    outputTensor = np.zeros(outputMatSize)
    for multiIndex in it.product(*outputMatLoop):
        a=[]
        dimension = len(X.data.shape)
        for i in range(dimension):
            a.append(slice(0,X.data.shape[i]))
        for i in range(len(dim)):
            a[dim[i]]=multiIndex[i]
        if np.count_nonzero(X.data[tuple(a)])!=0:
            outputTensor[multiIndex]=1
    return Tensor.Tensor(outputTensor,X.type,dim,-1,1,X.name)


def dimSum(X,dim,dimension_length):
    dim=list(set(X.dimensions)-set(dim))
    outputMatSize=[]
    outputMatLoop = ()
    for i in range(len(dim)):
        outputMatSize.append(dimension_length[dim[i]])
        outputMatLoop+=(range(dimension_length[dim[i]]),)
    outputTensor = np.zeros(outputMatSize)
    for multiIndex in it.product(*outputMatLoop):
        a=[]
        dimension = len(X.data.shape)
        for i in range(dimension):
            a.append(slice(0,X.data.shape[i]))
        for i in range(len(dim)):
            a[X.dimensions.index(dim[i])]=multiIndex[i]
        outputTensor[multiIndex]=np.sum(X.data[tuple(a)])
    return Tensor.Tensor(outputTensor,X.type,dim,-1,1,X.name)  


def bubbleSort(X,dim):
    X=copy.deepcopy(X)
    for passnum in range(len(dim)-1,0,-1):
        for i in range(passnum):
            if dim[i]>dim[i+1]:
                tmp=dim[i]
                dim[i]=dim[i+1]
                dim[i+1]=tmp
                X=np.swapaxes(X,i,i+1)
    return (X,dim)
    
def reservoir_sampling(items, k):
    """ 
    Reservoir sampling algorithm for large sample space or unknow end list
    See <http://en.wikipedia.org/wiki/Reservoir_sampling> for detail>
    Type: ([a] * Int) -> [a]
    Prev constrain: k is positive and items at least of k items
    Post constrain: the length of return array is k
    """
    sample = items[0:k]

    for i in range(k, len(items)):
        j = random.randrange(1, i + 1)
        if j <= k:
            sample[j] = items[i]

    return sample

def list_sample(items, k):
    random.seed(1)
    if k>len(items):
        k=len(items)
    return [items[i] for i in random.sample(range(len(items)), k)]


def compare(data,n,operator):
    if not isinstance(data,list):
        if operator=="ge":
            return data >= n
        elif operator=="le":
            return data <= n
        elif operator=="l":
            return data < n
        elif operator=="g":
            return data > n
        
    for d in data:
#        print(d)
        if not compare(d,n,operator):
            return False
    return True


def tensorType(data):
    if compare(data,1,"ge"): 
        return data,1
    elif compare(data,-1,"le"):
        return -1*data,-1
    
    elif compare(data,0,"ge") and compare(data,1,"le"):
        return data,2
    elif compare(data,0,"le") and compare(data,-1,"ge"):
        return -1*data,-2
    
    elif compare(data,0,"ge"):
        return data,3
    elif compare(data,0,"le"):
        return -1*data,-3
    
    else:
        return data,4



def tensor_properties(data,inputVars,dimensions):            
    tensors=[]
    for i,example in enumerate(data):
        if i==0:
            j=0
            for k,tensor in example.items():
                if isinstance(tensor,int) or isinstance(tensor,float):
                    a,b=tensorType(tensor)
                elif not isinstance(tensor,list):
                    a,b=tensorType(tensor.tolist())
                else:
                    a,b=tensorType(tensor)
                
                if k in inputVars:
                    tensors.append(Tensor.Tensor(None,b,dimensions[j],j,1,k))
                else:
                    tensors.append(Tensor.Tensor(None,b,dimensions[j],j,0,k))
                j+=1
        else:
            j=0
            for k,tensor in example.items():
                if isinstance(tensor,int) or isinstance(tensor,float):
                    a,b=tensorType(tensor)
                elif not isinstance(tensor,list):
                    a,b=tensorType(tensor.tolist())
                else:
                    a,b=tensorType(tensor)
                if tensors[j].type != b :
                    if abs(tensors[j].type) == abs(b):
                        raise Exception("examples not compatible, Tensor",j,"appeared as positive as well as negative tensor. Error occured in example",i)
                    if tensors[j].type < b:
                        tensors[j].type = b
                j+=1

    return tensors



def exampleToTensor(data,inputVars,dimensions,tensor_properties):            
    tensors=[]
    j=0
    for k,tensor in data.items():
        if isinstance(tensor,int) or isinstance(tensor,float):
            a,b=tensorType(tensor)
        elif not isinstance(tensor,list):
            a,b=tensorType(tensor.tolist())
        else:
            a,b=tensorType(tensor)
        
        if k in inputVars:
            tensors.append(Tensor.Tensor(a,tensor_properties[j].type,dimensions[j],j,1,k))
        else:
            tensors.append(Tensor.Tensor(a,tensor_properties[j].type,dimensions[j],j,0,k))
#            else:
#            tensors.append(Tensor.Tensor([a,listOfTensors[j],dimensions[j],j]))
        j+=1
#    
    return tensors
def createMzn(constraints,folder,file_name,list_constants,list_example,dimensions,dimension_length):
#    prec=0
    print(dimensions)
    file = open(folder+file_name+'.mzn', 'w')
    i=0
    for k,tensor in list_example.items():
        if len(dimensions[i])==0:
            if k in list_constants:
                file.write("int: "+k+";\n")
            else:
                file.write("var int: "+k+";\n")
        else:
            line="array["
            for j in range(len(dimensions[i])):
                line+="1.."+str(dimension_length[dimensions[i][j]])
                if j < len(dimensions[i])-1:
                    line+=","
                else:
                    if k in list_constants:
                        line+="] of int:"+k+";\n"
                    else:
                        line+="] of var int:"+k+";\n"
            file.write(line)
        i+=1
        
    names=list(list_example.keys())
    for m,constraint in enumerate(constraints):
#        constraint.printNode()
        file.write("constraint ")
        line=""
        
        if len(constraint.E)+len(constraint.F)==0:
            if len(constraint.ZM)>0:
                line+="forall("
                for j,s in enumerate(constraint.ZM):
                    line+=chr(97+s)+" in 1.."+str(dimension_length[s])
                    if j<len(constraint.ZM)-1:
                        line+=","
                    else:
                        line+=")"
                    
        if len(constraint.E)>0:
            tmp=set()
            for j in range(len(constraint.E[0])):
                tmp=tmp | set(constraint.EM[0][j])
            sumSet=set(tmp)-set(constraint.ES[0])
            sumSet=sumSet | set(constraint.ZM)
#            print(sumSet)
            if len(sumSet)>0:
                line+="forall("
            for j,s in enumerate(sumSet):
                line+=chr(97+s)+" in 1.."+str(dimension_length[s])
                if j<len(sumSet)-1:
                    line+=","
                else:
                    line+=")"
            line+='('
        elif len(constraint.F)>0:
            tmp=set()
            for j in range(len(constraint.F[0])):
                tmp=tmp | set(constraint.FM[0][j])
            sumSet=set(tmp)-set(constraint.FS[0])
            sumSet=sumSet | set(constraint.ZM)
            
#            print(sumSet)
            if len(sumSet)>0:
                line+="forall("
            for j,s in enumerate(sumSet):
                line+=chr(97+s)+" in 1.."+str(dimension_length[s])
                if j<len(sumSet)-1:
                    line+=","
                else:
                    line+=")"
            line+='('
        
        for i in range(len(constraint.E)):            
            if len(constraint.ES[i])>0:
                line+="sum("
            for j,s in enumerate(constraint.ES[i]):
                line+=chr(97+s)+" in 1.."+str(dimension_length[s])
                if j<len(constraint.ES[i])-1:
                    line+=","
                else:
                    line+=") ("
            
            for j,elem in enumerate(constraint.E[i]):
                line+=names[constraint.E[i][j]]
                if len(dimensions[constraint.E[i][j]])>0:
                    line+='['
                for l,k in enumerate(dimensions[constraint.E[i][j]]):
                    line+=chr(97+k)
                    if l==len(dimensions[constraint.E[i][j]])-1:
                        line+="]"
                    else:
                        line+=","
                if j<len(constraint.E[i])-1:
                    line+="*"
            if len(constraint.ES[i])>0:
                line+=")"
            if i<len(constraint.E)-1:
                line+='+'
        for i in range(len(constraint.F)): 
            if len(constraint.E)>0 or i>0:
                line+=" + "
            if len(constraint.FS[i])>0:
                line+="sum("
            for j,s in enumerate(constraint.FS[i]):
                line+=chr(97+s)+" in 1.."+str(dimension_length[s])
                if j<len(constraint.FS[i])-1:
                    line+=","
                else:
                    line+=") ("
            
            for j,elem in enumerate(constraint.F[i]):
                if j==0:
                    line+="-"
                line+=names[constraint.F[i][j]]
                if len(dimensions[constraint.F[i][j]])>0:
                    line+='['
                for l,k in enumerate(dimensions[constraint.F[i][j]]):
                    line+=chr(97+k)
                    if l==len(dimensions[constraint.F[i][j]])-1:
                        line+="]"
                    else:
                        line+=","
                if j<len(constraint.F[i])-1:
                    line+="*"
            if len(constraint.FS[i])>0:
                line+=")"
        
        if len(constraint.E)+len(constraint.F)==0:
            line+=" ( 0"
        line+=" <= "
        if constraint.negZ==1:
            line+="-"
        line+=names[constraint.Z]
        if len(dimensions[constraint.Z])>0:
            line+='['
        for l,k in enumerate(dimensions[constraint.Z]):
            line+=chr(97+k)
            if l==len(dimensions[constraint.Z])-1:
                line+="]"
            else:
                line+=","
                
#        if len(constraint.E)>0 or len(constraint.F)>0:
        line+=')'
         
        file.write(line+';\n')
#    for i in names:
#    file.write("constraint forall(a in  1..5, b in 1..5) (x[a,b] >= 0); \n")
#    file.write("constraint z >= 0; \n")
    file.write('solve satisfy;')
#    return prec

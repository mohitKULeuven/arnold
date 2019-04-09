import numpy as np
import itertools as it
import Tensor
from collections import Counter
#from random import randrange
import random
import copy

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
    return Tensor.Tensor([output,T[i].type,T[i].dimensions,0,1])

def tensorDotProduct(T,var): 
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
        outputMatSize.append(len(var[newDim[i]]))
        outputMatLoop+=(range(len(var[newDim[i]])),)
    outputTensor = np.ones(outputMatSize)
    
    for multiIndex in it.product(*outputMatLoop):
        for i in range(len(T)):
            outputTensor[multiIndex]=outputTensor[multiIndex]*T[i].data[tuple([multiIndex[j] for j in dimPos[i]])]
    return Tensor.Tensor([outputTensor,T[i].type,newDim,0,1])

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
            
def compareTensorsLE(T1, T2,var):
    
    indices2=[T2.dimensions.index(i) for i in T1.dimensions if i in T2.dimensions]
    outputMatLoop1 = ()
    
    for i in range(len(T1.dimensions)):
        outputMatLoop1+=(range(len(var[T1.dimensions[i]])),)
    for multiIndex1 in it.product(*outputMatLoop1):
        outputMatLoop2 = ()
        for i in range(len(T2.dimensions)):
            if i in indices2:
                tmp=T1.dimensions.index(T2.dimensions[i])
                outputMatLoop2+=(range(multiIndex1[tmp],multiIndex1[tmp]+1),)
            else:
                outputMatLoop2+=(range(len(var[T2.dimensions[i]])),)
        for multiIndex2 in it.product(*outputMatLoop2):
#            print(T1.data[multiIndex1],T2.data[multiIndex2])
            if T1.data[multiIndex1] > T2.data[multiIndex2]:
#                print("False")
                return False
#    print(T1.data, T1.dimensions)
#    print(T2.data, T2.dimensions)
#    print("True")
    return True

def compareTensorsGE(T1, T2,var):
#    [i for i,e in enumerate(T1.dimensions) if e in T2.dimensions]
    indices=[T1.dimensions.index(i) for i in T2.dimensions]
    outputMatLoop1 = ()
    outputMatLoop2 = ()
    for i in range(len(T2.dimensions)):
        outputMatLoop1+=(range(len(var[T1.dimensions[i]])),)
    for multiIndex1 in it.product(*outputMatLoop1):
        for i in range(len(T1.dimensions)):
            if i in indices:
                outputMatLoop2+=(range(multiIndex1[indices.index(i)],multiIndex1[indices.index(i)]+1),)
            else:
                outputMatLoop2+=(range(len(var[T2.dimensions[i]])),)
        for multiIndex2 in it.product(*outputMatLoop2):
            if T1[multiIndex1] < T2[multiIndex2]:
                return False
    return True

def tensorSlice(X,dim,var):
#    print(X.index)
#    print(dim)
#    print(X.data)
    if X.dimensions==dim:
        return X
#    print(X.index)
#    print(X.dimensions)
#    print(dim)
#    print(X.data)
    outputMatSize=[]
    outputMatLoop = ()
    for i in range(len(dim)):
        outputMatSize.append(len(var[dim[i]]))
        outputMatLoop+=(range(len(var[dim[i]])),)
    outputTensor = np.zeros(outputMatSize)
    for multiIndex in it.product(*outputMatLoop):
        a=[]
        dimension = len(X.data.shape)
        for i in range(dimension):
            a.append(slice(0,X.data.shape[i]))
        for i in range(len(dim)):
#            print(a)
#            print(dim[i])
#            print(multiIndex[i])
            a[dim[i]]=multiIndex[i]
        if np.count_nonzero(X.data[tuple(a)])!=0:
            outputTensor[multiIndex]=1
#    print("dim",dim)
#    print(outputTensor)
#    print(X.data)
    return Tensor.Tensor([outputTensor,X.type,dim,-1,1])

#printing
#[[ 30. 100.]
# [ 30. 100.]] [1, 0]
#[1]
#dimSum
#[130. 130.]
#[0]

def dimSum(X,dim,var):
#    print("printing")
#    print(X.data,X.dimensions,dim)
#    print(dim)
#    newdim = range(len(X.dimensions))
#    print("nedim",newdim)
#    print("dim",dim)
    dim=list(set(X.dimensions)-set(dim))
#    print(dim)
#    dim=newdim
    outputMatSize=[]
    outputMatLoop = ()
    for i in range(len(dim)):
        outputMatSize.append(len(var[dim[i]]))
        outputMatLoop+=(range(len(var[dim[i]])),)
    outputTensor = np.zeros(outputMatSize)
    for multiIndex in it.product(*outputMatLoop):
        a=[]
        dimension = len(X.data.shape)
        for i in range(dimension):
            a.append(slice(0,X.data.shape[i]))
        for i in range(len(dim)):
#            print(dim[i],multiIndex[i])
            a[X.dimensions.index(dim[i])]=multiIndex[i]
        outputTensor[multiIndex]=np.sum(X.data[tuple(a)])
#    print("dim ",dim)
#    print("dimSum")
#    print(outputTensor,dim)
#    print(dim)
    return Tensor.Tensor([outputTensor,X.type,dim,-1,1])  
#
#
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
#    print("Here")
#    print(type(data),len(data))
#    print(compare(data,1,"ge"))
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


def exampleToTensor(data,inputVars,dimensions,listOfTensors):            
    if not listOfTensors:
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
                        tensors.append(Tensor.Tensor([a,b,dimensions[j],j,1]))
                    else:
                        tensors.append(Tensor.Tensor([a,b,dimensions[j],j,0]))
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
#                listOfTensors.append(Tensor.Tensor([a,b,dimensions[j],j]))
    
    else:
        tensors=[]
#        for i,example in enumerate(examples):
        j=0
        for k,tensor in data.items():
            if isinstance(tensor,int) or isinstance(tensor,float):
                a,b=tensorType(tensor)
            elif not isinstance(tensor,list):
                a,b=tensorType(tensor.tolist())
            else:
                a,b=tensorType(tensor)
            
            if k in inputVars:
                tensors.append(Tensor.Tensor([a,listOfTensors[j],dimensions[j],j,1]))
            else:
                tensors.append(Tensor.Tensor([a,listOfTensors[j],dimensions[j],j,0]))
#            else:
#            tensors.append(Tensor.Tensor([a,listOfTensors[j],dimensions[j],j]))
            j+=1
#    
    return tensors
#def tensorSum(X,dim):
#    for i in range(len(X)):
#        X[i],dim[i]=bubbleSort(X[i],dim[i])
#    output=X[0]
#    for i in range(1,len(X)):
#        if X[i].shape==X[i-1].shape and dim[i-1]==dim[i]:
#            output+=X[i]
#    return (output,dim)


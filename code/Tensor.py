# Python program to print level order traversal using Queue 
#from numpy.distutils.fcompiler import none
import numpy as np
import itertools as it
import copy


# A node structure 
class Tensor: 
    # A utility function to create a new tensor
    def __init__(self ,data,tensor_type,dimensions,index,is_input,name): 
        self.data = np.array(copy.deepcopy(data))
        self.type=tensor_type
        self.dimensions = copy.deepcopy(dimensions)
        self.index=index #tells the index of this tensor in listTensors
        self.input=is_input
        self.name=name
         #type 1 is good, type 2 is bad (for products), type 3 is ugly (products)
    
    # generated children must satisfy signatures
    def multiply(self, n):
        tmp=Tensor(n*self.data,self.type,self.dimensions,self.index,1,self.name)
        return tmp
        
    def tensorSlice(self,var):
        outputMatSize=[]
        outputMatLoop = ()
        for i in range(len(self.dimensions)):
            outputMatSize.append(len(var[self.dimensions[i]]))
            outputMatLoop+=(range(len(var[self.dimensions[i]])),)
        outputTensor = np.zeros(outputMatSize)
        for multiIndex in it.product(*outputMatLoop):
            a=[]
            dimension = len(self.data.shape)
            for i in range(dimension):
                a.append(slice(0,self.data.shape[i]))
            for i in range(len(self.dimensions)):
                a[self.dimensions[i]]=multiIndex[i]
            if np.count_nonzero(self.data[tuple(a)])!=0:
                outputTensor[multiIndex]=1
                
        return outputTensor
    
    # check if the node satisfies signatures
    def dimSum(self,var):
        newdim = range(len(self.data.shape))
        newdim=list(set(newdim)-set(self.dimensions))
        dim=newdim
        outputMatSize=[]
        outputMatLoop = ()
        for i in range(len(dim)):
            outputMatSize.append(len(var[dim[i]]))
            outputMatLoop+=(range(len(var[dim[i]])),)
        outputTensor = np.zeros(outputMatSize)
        for multiIndex in it.product(*outputMatLoop):
            a=[]
            dimension = len(self.data.shape)
            for i in range(dimension):
                a.append(slice(0,self.data.shape[i]))
            for i in range(len(dim)):
                a[dim[i]]=multiIndex[i]
            outputTensor[multiIndex]=np.sum(self.data[tuple(a)])
        return np.amax(outputTensor).astype(np.int64), np.amin(outputTensor).astype(np.int64)    

    
    def bubbleSort(self):
        for passnum in range(len(self.dimensions)-1,0,-1):
            for i in range(passnum):
                if self.dimensions[i]>self.dimensions[i+1]:
                    tmp=self.dimensions[i]
                    self.dimensions[i]=self.dimensions[i+1]
                    self.dimensions[i+1]=tmp
                    self.data=np.swapaxes(self.data,i,i+1)
        return self
    
    def powerset(self):
        """
        Returns all the subsets of this set. This is a generator.
        """
        seq=self.dimensions
        if len(seq) <= 1:
            yield seq
            yield []
        else:
            for item in Tensor.powerset(seq[1:]):
                yield [seq[0]]+item
                yield item

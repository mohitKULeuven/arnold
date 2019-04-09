# Python program to print level order traversal using Queue 
#from numpy.distutils.fcompiler import none
import helper
import copy
import Tensor
import itertools as it

#Mod of each number is >= 1
#don't forget to upgrade operations in each child
# if we incease E, we have to make sure the new term has only one element wiht sum over only one dimension, similarly while removing only term with size 1 can be removed
# A node structure 
class Constraint: 
    # A utility function to create a new node 
    def __init__(self ,left,right): 
        self.left=left
        self.right=right
        self.tensorList = data[8]
        self.highest = copy.deepcopy(data[9])
        self.operation=copy.deepcopy(data[10])
        self.negZ=data[11]
        
#        self.highestOperation=self.highest[0]
#        
#        self.highestDimRemovedTerm = self.highest[1]
#        self.highestDimRemovedPerTerm = self.highest[2]
#        self.highestTensorDividedTerm = self.highest[3]
#        self.highestTensorDividedPerTerm = self.highest[4]
#        self.highestBadTensorMultiplyTerm = self.highest[5]
#        self.highestBadTensorMultiplyPerTerm = self.highest[6]
#        self.highestTensorRemoved = self.highest[7]
#        
#        self.highestTensorAdded = self.highest[8]
#        self.highestBadTensorDivideTerm = self.highest[9]
#        self.highestBadTensorDividePerTerm = self.highest[10]
#        self.highestTensorMultiplyTerm = self.highest[11]
#        self.highestTensorMultiplyPerTerm = self.highest[12]
#        self.highestDimAddedTerm = self.highest[13]
#        self.highestDimAddedPerTerm = self.highest[14]
        
     
    def isTrivial(self,tensorList):
        if self.LHSequalsRHS():
            return True
        if self.negZ==0 and (len(self.E))==0:
            return True
        
        ind=0
        for i in range(len(self.E)):
            for j in range(len(self.E[i])):
                if tensorList[self.E[i][j]].input==0:
                    ind=1
        if ind==0:
            for i in range(len(self.F)):
                for j in range(len(self.F[i])):
                    if tensorList[self.F[i][j]].input==0:
                        ind=1
        if ind==0:
            if tensorList[self.Z].input==0:
                ind=1
        if ind==0:
            return True
        
        return False
    
    def EequalsF(self):#not complete
        if len(self.E) != len(self.F):
            return False
        for i in len(self.E):
            if len(self.E[i]) != len(self.F[i]) or len(self.ES[i]) != len(self.FS[i]):
                return False
            
        return True
    
    def LHSequalsRHS(self):
#        print(self.E[0][0],self.Z)
#        print(len(self.E)==1,len(self.E[0])==1,len(self.ES[0])==0,self.E[0][0]==self.Z, set(self.EM[0][0])==set(self.ZM))
        if len(self.E)==1 and len(self.E[0])==1 and len(self.ES[0])==0 and self.E[0][0]==self.Z and set(self.EM[0][0])==set(self.ZM):
            return True
        if self.negZ==1 and len(self.F)==1 and len(self.F[0])==1 and len(self.FS[0])==0 and self.F[0][0]==self.Z and set(self.FM[0][0])==set(self.ZM):
            return True
        return False
        
    def isFempty(self):
        for f in self.F:
            if f:
                return False
        return True
                
    #removing dimension
    def removeDimension(self):
        children=[]
        if self.highest[0]<=0 and len(self.F)>0:
            for i in range(self.highest[1],len(self.FS)):
                sumOptions=self.FS[i]
#                sumOptions = [item for item in sumOptions if item >= self.highest[2]]
                for j in range(len(sumOptions)):
                    if sumOptions[j]>=self.highest[2][i]:
                        key=[self.E,self.EM,self.ES,self.F,self.FM,self.FS,self.Z,self.ZM,self.tensorList,self.highest,self.operation,self.negZ]
                        child=Node(key)
                        child.FS[i].remove(sumOptions[j])
                        child.highest[0]=0
                        child.highest[1]=i
                        child.highest[2][i]=sumOptions[j]
#                        child.operation.append(["removeDimension",[i,sumOptions[j]]])
                        child.operation.append([self,"removeDimension",self.FS[i],sumOptions[j]])
                        children.append(child)
        return children
    
    #doesn't satisfy the signatures; size of F[i] must be 1
    def divideTensor(self):
        children=[]
        if self.highest[0]<=1 and len(self.F)>0:
            
            for i in range(self.highest[3],len(self.F)):
                if len(self.F[i])>1:
                    for j in range(len(self.F[i])-1,-1,-1):
                        if self.F[i][j] in self.tensorList[0]:
                            tmp=set()
                            for k in range(len(self.FM[i])):
                                if k!=j:
                                    tmp=tmp | set(self.FM[i][k])
#                            toBeRemoved=list(set(self.FM[i][j])-set(tmp))
                            toBeRemoved=list(set(self.FS[i])-set(tmp))
                            if self.F[i][j] >= self.highest[4][i] and len(toBeRemoved)==0:
                                key=[self.E,self.EM,self.ES,self.F,self.FM,self.FS,self.Z,self.ZM,self.tensorList,self.highest,self.operation,self.negZ]
                                child=Node(key)
                                del child.F[i][j]
                                del child.FM[i][j]
#                                child.F[i].remove(self.F[i][j])
#                                child.FM[i].remove(self.FM[i][j])
                                child.highest[0]=1
                                child.highest[3]=i
                                child.highest[4][i]=self.F[i][j]
                                child.operation.append([self,"divideTensor",self.F[i],self.F[i][j],child.F[i]])
                                children.append(child)
        return children
    
    #doesn't satisfy the signatures
    def multiplyBadTensor(self,listOfTensors,n,slicing):
        children=[]
        if self.highest[0]<=2 and len(self.F)>0:
            for i in range(self.highest[5],len(self.E)):
                if len(self.F[i])<n:
                    for j in range(self.highest[6][i],len(listOfTensors)):
                        if j in self.tensorList[1]:
                            if slicing==0:
                                ps=[listOfTensors[j].dimensions]
                            else:
                                ps=listOfTensors[j].powerset()
                            for e in ps:
                                key=[self.E,self.EM,self.ES,self.F,self.FM,self.FS,self.Z,self.ZM,self.tensorList,self.highest,self.operation,self.negZ]
                                child=Node(key)
                                child.E[i].append(j)
                                child.EM[i].append(e)
                                child.highest[0]=2
                                child.highest[5]=i
                                child.highest[6][i]=j
                                child.operation.append([self,"multiplyBadTerm",self.E[i],j])
                                children.append(child)
        return children
    
    
    #doesn't satisfy the signatures; size of F[i] must be 1
    def removeTerm(self):
        children=[]
        if self.highest[0]<=3 and len(self.F)>0:
            for i in range(len(self.F)-1,-1,-1):
#                self.prettyPrint()
                if len(self.F[i])==1 and self.F[i][0]>=self.highest[7] and len(self.FS[i])==0:
                    key=[self.E,self.EM,self.ES,self.F,self.FM,self.FS,self.Z,self.ZM,self.tensorList,self.highest,self.operation,self.negZ]
                    child=Node(key)
                    del child.F[i]
                    del child.FM[i]
                    del child.FS[i]
#                    child.F.remove(self.F[i])
#                    child.FM.remove(self.FM[i])
#                    child.FS.remove(self.FS[i])
                    child.highest[0]=3
                    child.highest[7]=self.F[i][0]
                    child.operation.append([self,"removeTerm",self.F[i]])
                    children.append(child)
        return children
    
    #doesn't satisfy the signatures
    def addTerm(self,listOfTensors,m,n,slicing):
        children=[]
        if self.highest[0]<=4 and len(self.E)+len(self.F)<m:
            for i in range(self.highest[8],len(listOfTensors)):
#                if i in self.tensorList[0]:
                if slicing==0:
                    ps=[listOfTensors[i].dimensions]
#                else:
#                    ps=[self.tensorList[0][i].powerset()]
                prod=len(self.tensorList[1])
                if prod>=n-1:
                    prod=n-1
#                    print("prod:",prod,self.tensorList[1])
                for comb in it.combinations_with_replacement(self.tensorList[1],prod):
                    key=[self.E,self.EM,self.ES,self.F,self.FM,self.FS,self.Z,self.ZM,self.tensorList,self.highest,self.operation,self.negZ]
                    child=Node(key)
                    e=[i]
                    for c in comb:
                        e.append(c)
                        if slicing==0:
                            ps.append(listOfTensors[c].dimensions)
#                        else:
#                            ps.append(self.tensorList[i].powerset()) # returns powerset of dimensions
                    child.E.append(e)
                    
#                    for elements in enumerate(ps):
#                        for elem in elements:
#                            key=[self.E,self.EM,self.ES,self.F,self.FM,self.FS,self.Z,self.ZM,self.tensorList,self.highest,self.operation,self.negZ]
#                            child=Node(key)
#                            child.E.append(e)
                    child.EM.append(ps)
                    child.ES.append([])
                    child.highest[0]=4
                    child.highest[8]=i
                    child.operation.append([self,"addTerm",e])
                    children.append(child)
        return children
    
    def divideBadTensor(self):
        children=[]
        if self.highest[0]<=5 and len(self.E)>0:
            for i in range(self.highest[9],len(self.E)):
                if len(self.E[i])>1 and len(self.ES[i])==0:
                    for j in range(len(self.E[i])-1,-1,-1):
                        if self.E[i][j] in self.tensorList[1]:
                            if self.E[i][j] >= self.highest[10][i]:
                                key=[self.E,self.EM,self.ES,self.F,self.FM,self.FS,self.Z,self.ZM,self.tensorList,self.highest,self.operation,self.negZ]
                                child=Node(key)
#                                child.printNode()
                                del child.E[i][j]
                                del child.EM[i][j]
#                                child.E[i].remove(self.E[i][j])
#                                child.EM[i].remove(self.EM[i][j])
                                child.highest[0]=5
                                child.highest[9]=i
                                child.highest[10][i]=self.E[i][j]
#                                child.operation.append(["divideBadTensor",[i,self.E[i][j]]])
                                child.operation.append([self,"divideBadTensor",self.E[i],self.E[i][j]])
                                children.append(child)
        return children
    
    
    #doesn't satisfy the signatures
    def multiplyTensor(self,listOfTensors,n,slicing):
        children=[]
        if self.highest[0]<=6 and len(self.E)>0:
            for i in range(self.highest[11],len(self.E)):
                if len(self.E[i])<n:
                    for j in range(self.highest[12][i],len(listOfTensors)):
                        if j in self.tensorList[0]:
                            if slicing==0:
                                ps=[listOfTensors[j].dimensions]
                            else:
                                ps=listOfTensors[j].powerset()
                            for e in ps:
                                key=[self.E,self.EM,self.ES,self.F,self.FM,self.FS,self.Z,self.ZM,self.tensorList,self.highest,self.operation,self.negZ]
                                child=Node(key)
                                child.E[i].append(j)
                                child.EM[i].append(e)
                                child.highest[0]=6
                                child.highest[11]=i
                                child.highest[12][i]=j
#                                child.operation.append(["multiplyTensor",[i,j]])
                                child.operation.append([self,"multiplyTensor",self.E[i],j])
                                children.append(child)
        return children
    
    #would satisfy the signatures except LHS Dim intersection RHS Dim not equal to 0
    def sumDimension(self):
        children=[]
#        if self.Z==6 and self.negZ==0 and len(self.F)==0 and len(self.E)==1 and len(self.E[0])==1 and self.E[0][0]==2:
#            print(self.highest[0],len(self.E))
            
        if self.highest[0]<=7 and len(self.E)>0:
            sumOptions=[]
            for i in range(self.highest[13],len(self.EM)):
                tmp=set()
                for j in range(len(self.EM[i])):
                    tmp=tmp | set(self.EM[i][j])
                sumOptions=list(tmp-set(self.ES[i]))
                
#                sumOptions = [item for item in sumOptions if item >= self.highest[14]]
                for j in range(len(sumOptions)):
                    if sumOptions[j]>=self.highest[14][i]:
                        key=[self.E,self.EM,self.ES,self.F,self.FM,self.FS,self.Z,self.ZM,self.tensorList,self.highest,self.operation,self.negZ]
                        child=Node(key)
                        child.ES[i].append(sumOptions[j])
                        child.highest[0]=7
                        child.highest[13]=i
                        child.highest[14][i]=sumOptions[j]
                        child.operation.append([self,"sumDimension",self.ES[i],sumOptions[j]])
    #                    child.printNode()
    #                    child.prettyPrint()
                        children.append(child)
#        if self.Z==6 and self.negZ==0 and len(self.F)==0 and len(self.E)==1 and len(self.E[0])==1 and self.E[0][0]==2:
#            print(self.highest[0],len(self.E))
#            for child in children:
#                child.prettyPrint()
        return children
    
        
    # generated children must satisfy signatures -- maybe not
    # operations' first term has highest order tensor, second term has highest order 
    # dimension and 3rd term has highest order operations
    # add +ve term < multiply < add dim < remove dim < divide < remove -ve term
    def generateChildren(self,listOfTensors,m,n,slicing,negation):
        children=[]
        
        if self.negZ==1 and negation==0:
            children.extend(self.removeDimension())
            children.extend(self.divideTensor())
            children.extend(self.multiplyBadTensor(listOfTensors,n,slicing))
            children.extend(self.removeTerm())
        elif self.negZ==0 and negation==0:
            children.extend(self.addTerm(listOfTensors,m,n,slicing))
            children.extend(self.divideBadTensor())
            children.extend(self.multiplyTensor(listOfTensors,n,slicing))
            children.extend(self.sumDimension())
        else:
            children.extend(self.removeDimension())
            children.extend(self.divideTensor())
            children.extend(self.multiplyBadTensor(listOfTensors,n,slicing))
            children.extend(self.removeTerm())
            children.extend(self.addTerm(listOfTensors,m,n,slicing))
            children.extend(self.divideBadTensor())
            children.extend(self.multiplyTensor(listOfTensors,n,slicing))
            children.extend(self.sumDimension())
        
#        elif negZ==0:
#            children.extend(self.removeDimension())
#            children.extend(self.divideTerm())
#            children.extend(self.removeTerm())
#            children.extend(self.multiplyBadTerm(listOfTensors,n,slicing))
#            children.extend(self.addTerm(listOfTensors,m,n,slicing))
#            children.extend(self.divideBadTerm())
#            children.extend(self.multiplyTerm(listOfTensors,n,slicing))
#            children.extend(self.sumDimension())
            
        return children
    
    # check if the node satisfies signatures
    def satisfiesSignatures(self,m,n):
        if len(self.E)+len(self.F)>m:
            return False
        
        remainingDim=set()
        ind=0
        for i in range(len(self.EM)):
            M=set()
            ind=1
            for j in range(len(self.EM[i])):
                M=M.union(self.EM[i][j])
            
            if not set(self.ES[i]) <= M:
                return False
            
            if i==0:
                remainingDim=M-set(self.ES[i])
            else:
                if remainingDim!=M-set(self.ES[i]):
                    return False
            
            if len(self.E[i])>n:
                return False
            
#        remainingDim=set()
        for i in range(len(self.FM)):
            M=set()
            for j in range(len(self.FM[i])):
                M=M.union(self.FM[i][j])
            if not set(self.FS[i]) <= M:
                return False
            
            if ind==0 and i==0:
#                print(remainingDim)
#                print(M-set(self.FS[i]))
                remainingDim=M-set(self.FS[i])
            else:
#                print(remainingDim)
#                print(M-set(self.FS[i]))
                if remainingDim!=M-set(self.FS[i]):
                    return False
            
            if len(self.F[i])>n:
                return False
        
        return True
    
    def validStructure(self):
        isEmpty=1
        for f in self.F:
            if f:
                isEmpty=0
        for e in self.E:
            if e:
                isEmpty=0
        if isEmpty:
            return True
        if len(self.E)==len(self.EM) and len(self.F)==len(self.FM) and len(self.E)==len(self.ES) and len(self.F)==len(self.FS):
            for i in range(len(self.E)):
                if len(self.E[i])!=len(self.EM[i]):
                    return False
            for i in range(len(self.F)):
                if len(self.F[i])!=len(self.FM[i]):
                    return False
            return True
        return False
    
    # check if the node satisfies the constraint represented by the node
    def satisfiesConstraint(self,listOfTensors,var):
#        if self.checkStructure():
        sumTerms=[]
#        self.prettyPrint()
        for i in range(len(self.E)):
            slices=[]
            for j in range(len(self.E[i])):
                slices.append(helper.tensorSlice(listOfTensors[self.E[i][j]],self.EM[i][j],var))
            tmp=helper.dimSum(helper.tensorDotProduct(slices,var),self.ES[i],var)
#            print(tmp)
            sumTerms.append(tmp)
            
#        subtractTerms=[]
        for i in range(len(self.F)):
            slices=[]
            for j in range(len(self.F[i])):
#                print("######", i,j ,"######")
#                self.prettyPrint()
#                print(self.operation)
                slices.append(helper.tensorSlice(listOfTensors[self.F[i][j]],self.FM[i][j],var))
            tmp=helper.dimSum(helper.tensorDotProduct(slices,var),self.FS[i],var)
#            print(tmp.multiply(-1))
            sumTerms.append(tmp.multiply(-1))
#        print("printing")
#        for tmp in sumTerms:
#            print(tmp.data,tmp.dimensions)
#        print("len:",len(sumTerms))
        if self.negZ==0:
            if len(self.E)+len(self.F)==0:
                return helper.compareTensorsLE(Tensor.Tensor([0,1,[],-1,1]),helper.tensorSlice(listOfTensors[self.Z],self.ZM,var),var)
            return helper.compareTensorsLE(helper.tensorSum(sumTerms),helper.tensorSlice(listOfTensors[self.Z],self.ZM,var),var)
        else:
            if len(self.E)+len(self.F)==0:
                return helper.compareTensorsLE(Tensor.Tensor([0,1,[],-1,1]),helper.tensorSlice(listOfTensors[self.Z].multiply(-1),self.ZM,var),var)
#            print(sumTerms)
            return helper.compareTensorsLE(helper.tensorSum(sumTerms),helper.tensorSlice(listOfTensors[self.Z].multiply(-1),self.ZM,var),var)
        
        return False

    def printNode(self):
        print("####################### printing node ######################")
        print("E: ",self.E)
        print("EM: ",self.EM)
        print("ES: ",self.ES)
        print("F: ",self.F)
        print("FM: ",self.FM)
        print("FS: ",self.FS)
        print("Z: ",self.Z)
        print("ZM: ",self.ZM)
        print("############################ done ##########################")
              
    
    def prettyPrint(self):
#        print("####################### printing node ######################")
        ind=0
        for i in range(len(self.E)):
            ind=1
            if i!=0:
                print("+",end="",sep="")
            if self.ES[i]:
                print("SUM",self.ES[i],end="",sep="")
            for j in range(len(self.E[i])):
                if j>0:
                    print("*",end="",sep="")
                print(chr(65+self.E[i][j]),self.EM[i][j],end="",sep="")
        
        for i in range(len(self.F)):
            if self.FS[i]:
                if ind==1:
                    print("+",end="",sep="")
                print("SUM",self.FS[i],end="",sep="")
            print("-",end="",sep="")
            for j in range(len(self.F[i])):
                if j>0:
                    print("*",end="",sep="")
                print(chr(65+self.F[i][j]),self.FM[i][j],end="",sep="")
        if self.negZ==0:
            print(" <= ",chr(65+self.Z),self.ZM,sep="")
        else:
            print(" <= -",chr(65+self.Z),self.ZM,sep="")
#        print("############################ done ##########################")
    
    def printPath(self):
        print("##########################")
        for item in self.operation:
            item[0].prettyPrint()
            print("=>")
            print(item[1:])
        self.prettyPrint()
        print("##########################")
        
    def isUgly(self):
        for f in self.F:
            if set(f).intersection(set(self.tensorList[2])):
                return True
            
        for e in self.F:
            if set(e).intersection(set(self.tensorList[2])):
                return True
        return False    
            
    def isEqual(self,root):
        if self.Z != root.Z or self.ZM != root.ZM or len(self.E) != len(root.E) or len(self.F) != len(root.F)  or len(self.ES) != len(root.ES) or len(self.FS) != len(root.FS) or self.negZ != root.negZ:
            return False
        
        tmp1=[]
        for i in range(len(self.E)):
            tmp1.append(sorted(self.E[i]))
        tmp2=[]
        for i in range(len(self.E)):
            tmp2.append(sorted(root.E[i]))
        
        if len(self.ES)>0:
            list11, list12 = zip(*sorted(zip(tmp1, self.ES.copy())))
            list21, list22 = zip(*sorted(zip(tmp2, root.ES.copy())))
            if list11 != list21 or list12 != list22:
                return False
        else:
            list11 = sorted(tmp1)
            list21 = sorted(tmp2)
            if list11 != list21:
                return False
        
        tmp1=[]
        for i in range(len(self.F)):
            tmp1.append(sorted(self.F[i]))
        tmp2=[]
        for i in range(len(self.F)):
            tmp2.append(sorted(root.F[i]))
            
        if len(self.FS)>0:
            list11, list12 = zip(*sorted(zip(tmp1, self.FS.copy())))
            list21, list22 = zip(*sorted(zip(tmp2, root.FS.copy())))
            if list11 != list21 or list12 != list22:
                return False
        else:
            list11 = sorted(tmp1)
            list21 = sorted(tmp2)
            if list11 != list21:
                return False
            
        return True
        
    def isAncestor(self, root):
        if self.isEqual(root):
            return True
        if self.Z != root.Z or self.ZM != root.ZM or self.isUgly() or root.isUgly() or self.negZ != root.negZ:
            return False
        
        tmp=[]
        for f in self.F:
            tmp.append([t for t in f if t not in self.tensorList[1]])
        
        removed=[]
        for f in self.F:
            removed.append([t for t in f if t in self.tensorList[1]])
        
        ind=0
        subsetIndex, tag = helper.isSubset(tmp,root.F,removed,self.tensorList[1])
        if not tag:
            return False
        for indexlist in subsetIndex:
            tmpInd=1
            for i,j in enumerate(indexlist):
                if len(set(self.FS[i])-set(root.FS[j]))>0:
                    tmpInd=0
            if tmpInd==1:
                ind=1
                break
        if ind==0:
            return False

        tmp=[]
        for e in root.E:
            tmp.append([t for t in e if t not in root.tensorList[1]])
        removed=[]
        for e in root.E:
            removed.append([t for t in e if t in root.tensorList[1]])
#        print('tmp',tmp,'E',self.E,'removed',removed)
        
        subsetIndex, tag = helper.isSubset(tmp,self.E,removed,root.tensorList[1])
#        if root.negZ==0 and root.Z==2 and len(root.E)==1 and len(root.E[0])==1 and root.E[0][0]==3 and len(root.F)==0 and len(root.ES[0])==1 and root.ES[0][0]==1:
#            if self.negZ==0 and self.Z==2 and len(self.E)==1 and len(self.E[0])==1 and self.E[0][0]==3 and len(self.F)==0 and len(self.ES[0])==1 and self.ES[0][0]==0:
#                print(subsetIndex,tag)
        if not tag:
            return False
        
        for indexlist in subsetIndex:
            tmpInd=1
            for i,j in enumerate(indexlist):
                if len(set(root.ES[i])-set(self.ES[j]))>0:
                    tmpInd=0
            if tmpInd==1:
                return True
                
        return False

    def uglyNodes(self,listOfTensors,m,n,slicing,var,examples):
        nodes=[]
#        print(self.E)
        for i,e in enumerate(self.E):
#            print(n,len(e))
            for k in range(1,1+n-len(e)):
#                print(self.tensorList[2],i)
                for comb in it.combinations_with_replacement(self.tensorList[2],k):
#                    print("ugly comb",comb)
                    for j in comb:
#                        print("ugly",j)
                        if slicing==0:
                            ps=[listOfTensors[j].dimensions]
                        else:
                            ps=listOfTensors[j].powerset()
                        for p in ps:
                            key=[self.E,self.EM,self.ES,self.F,self.FM,self.FS,self.Z,self.ZM,self.tensorList,self.highest,self.operation,self.negZ]
                            node=Node(key)
                            node.E[i].extend(comb)
                            node.EM[i].append(p)
                            node.operation.append([self,"uglyNode",self.E[i],comb])
                            if node.validStructure() and node.satisfiesSignatures(m,n) and all(node.satisfiesConstraint(exp,var) for exp in examples):
#                                print(ps)
                                nodes.append(node)
        for i,e in enumerate(self.F):
#            print(n,e)
            for k in range(1+n-len(e)):
                for comb in it.combinations_with_replacement(self.tensorList[2],k):
                    
                    for j in comb:
                        if slicing==0:
                            ps=[listOfTensors[j].dimensions]
                        else:
                            ps=listOfTensors[j].powerset()
                        for p in ps:
                            key=[self.E,self.EM,self.ES,self.F,self.FM,self.FS,self.Z,self.ZM,self.tensorList,self.highest,self.operation,self.negZ]
                            node=Node(key)
                            node.F[i].extend(comb)
                            node.FM[i].append(p)
                            node.operation.append([self,"uglyNode",self.F[i],comb])
                            if node.validStructure() and node.satisfiesSignatures(m,n) and all(node.satisfiesConstraint(exp,var) for exp in examples):
                                nodes.append(node)
        return nodes
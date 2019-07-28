from itertools import combinations_with_replacement
from itertools import combinations
import itertools
import Node
import helper

def intelligentEnumeration(listOfTensors,root,var,m,n,slicing,negation,prevRoots,examples,constraintList):     
    tmpConstraintList=[]
    
#    for nodes in prevRoots:
#        if root.isAncestor(nodes):
#            if root.negZ==1 and root.Z==4 and len(root.E)==0 and len(root.F)==1 and len(root.F[0])==2 and root.F[0][0]==0 and root.F[0][1]==7:
#                print("######################")
#                root.prettyPrint()
#                nodes.prettyPrint()
#                print("######################")
#            if root.satisfiesSignatures(m,n) and all(root.satisfiesConstraint(exp,var) for exp in examples):
#                tmpConstraintList.append(root)
#            return tmpConstraintList
    
    if root is None or (root.satisfiesSignatures(m,n) and not all(root.satisfiesConstraint(exp,var) for exp in examples)): 
        return tmpConstraintList
#    if root.Z==6 and root.negZ==0 and len(root.F)==0 and len(root.E)==1 and len(root.E[0])==1 and root.E[0][0]==2:
#        root.printPath()
            
#    if root.negZ==0 and root.Z==2 and len(root.E)==1 and len(root.E[0])==1 and root.E[0][0]==3 and len(root.F)==0 and len(root.ES[0])==1 and root.ES[0][0]==1:
#        root.prettyPrint()
    children=root.generateChildren(listOfTensors,m,n,slicing,negation)
#    if root.Z==6 and root.negZ==0 and len(root.F)==0 and len(root.E)==1 and len(root.E[0])==1 and root.E[0][0]==2:
#        for child in children:
#            child.prettyPrint()
    childSatisfaction=0
    for child in children:
        if child.validStructure() and (not child.satisfiesSignatures(m,n) or all(child.satisfiesConstraint(exp,var) for exp in examples)):
            if child.operation[len(child.operation)-1][1]=="multiplyBadTerm":
                tmp=set()
                for j in range(len(child.EM[child.highest[5]])):
                    tmp=tmp or set(child.EM[child.highest[5]][j])
                sumOptions=list(tmp-set(child.ES[child.highest[5]]))
                for j in range(len(sumOptions)):
                    key=[child.E,child.EM,child.ES,child.F,child.FM,child.FS,child.Z,child.ZM,child.tensorList,child.highest,child.operation]
                    tmp=Node(key)
                    tmp.ES[child.highest[5]].append(sumOptions[j])
                    tmp.operation.append([child,"BadTermSum",child.ES[child.highest[5]],sumOptions[j]])
                    if tmp.validStructure() and tmp.satisfiesSignatures(m,n) and all(tmp.satisfiesConstraint(exp,var) for exp in examples):
                        constraintList.append(tmp)
                        tmpConstraintList.append(tmp)
            
            uglyNodes = child.uglyNodes(listOfTensors,m,n,slicing,var,examples)
            for node1 in constraintList:
                for node2 in uglyNodes:
                    if node2.isAncestor(node1):
                        
                        constraintList.remove(node1)
                        break
            for node2 in uglyNodes:
                foundDescendent=0
                for node1 in constraintList:
                    if node1.isAncestor(node2):
                        foundDescendent=1
                        break
                if foundDescendent!=1:
                    constraintList.append(node2) 
#                    if node2.Z==3 and node2.negZ==1 and len(node2.E)==0 and len(node2.F)==1 and len(node2.F[0])==2 and node2.F[0][0]==1 and node2.F[0][1]==2:
#                        print("ugly adding")
#                        node2.prettyPrint()
                    tmpConstraintList.append(node2)
            constraints=intelligentEnumeration(listOfTensors,child,var,m,n,slicing,negation,prevRoots,examples,constraintList)
            if constraints:
                childSatisfaction=1
                for node1 in constraintList:
                    for node2 in constraints:
                        if node2.isAncestor(node1):
                            constraintList.remove(node1)
#                                node1.prettyPrint()
#                                node2.prettyPrint()
                            break
                
                for node2 in constraints:
                    foundDescendent=0
                    for node1 in constraintList:
                        if node1.isAncestor(node2):
                            foundDescendent=1
                            break
                    
                    if foundDescendent!=1:
                        constraintList.append(node2)
                        tmpConstraintList.append(node2)
        else:
            uglyNodes = child.uglyNodes(listOfTensors,m,n,slicing,var,examples)
            for nodes in uglyNodes:
                if nodes.validStructure() and nodes.satisfiesSignatures(m,n) and all(nodes.satisfiesConstraint(exp,var) for exp in examples):
                    tmpConstraintList.extend(intelligentEnumeration(listOfTensors,nodes,var,m,n,slicing,negation,prevRoots,examples,constraintList))

    if childSatisfaction==0 and root.satisfiesSignatures(m,n) and all(root.satisfiesConstraint(exp,var) for exp in examples):
        for nodes in constraintList:
            if root.isAncestor(nodes):
                constraintList.remove(nodes)
        foundDescendent=0
        for nodes in constraintList:
            if nodes.isAncestor(root):
                foundDescendent=1
                break
        if foundDescendent!=1:
            constraintList.append(root)
            tmpConstraintList.append(root)
    return tmpConstraintList

def dumbEnumeration(listOfTensors,root,var,m,n,slicing,negation,prevRoots,examples,constraintList):     
    constraintList.append(root)
    
    if root is None: 
        return constraintList
            
    children=root.generateChildren(listOfTensors,m,n,slicing,negation)
    for child in children:
        if child.validStructure():
            if child.operation[len(child.operation)-1][1]=="multiplyBadTerm":
                tmp=set()
                for j in range(len(child.EM[child.highest[5]])):
                    tmp=tmp or set(child.EM[child.highest[5]][j])
                sumOptions=list(tmp-set(child.ES[child.highest[5]]))
                for j in range(len(sumOptions)):
                    key=[child.E,child.EM,child.ES,child.F,child.FM,child.FS,child.Z,child.ZM,child.tensorList,child.highest,child.operation]
                    tmp=Node(key)
                    tmp.ES[child.highest[5]].append(sumOptions[j])
                    tmp.operation.append([child,"BadTermSum",child.ES[child.highest[5]],sumOptions[j]])
                    if tmp.validStructure():
                        constraintList.append(tmp)
            
            uglyNodes = child.uglyNodes(listOfTensors,m,n,slicing,var,examples)
            for node2 in uglyNodes:
                if node2.validStructure():
                    intelligentEnumeration(listOfTensors,node2,var,m,n,slicing,negation,prevRoots,examples,constraintList)
                 
                
            intelligentEnumeration(listOfTensors,child,var,m,n,slicing,negation,prevRoots,examples,constraintList)
            
    return constraintList


#n tells the limit on number of products in a term and m tells number of terms
# for n=m=2 and k tensors with l dimensions each
#k^2 * (k-1) * (k-2) * (k+1) * 2^(5l-3)
    
def naiveNodes(listOfTensors,listTensorsType,m,n,slicing,negation,negZ):
    key=[0]*12       
    nodes=[]
    nSizeCombinations=[]
    for i in range(1,n+1):
        nSizeCombinations.extend(list(combinations_with_replacement(range(len(listOfTensors)),i)))
#        if len(nSizeCombinations)<m:
#            m=len(nSizeCombinations)
    print(nSizeCombinations)
    for j in range(m+1):
        perterm=[0]*j
#        print("list: ",list(combinations_with_replacement(nSizeCombinations,j)))
        for F in list(combinations_with_replacement(nSizeCombinations,j)):
#            print("powerSet",list(helper.powerset(F)))
#            print("F",F)
            if not F:
                ps=[[]]
            else:
                ps=helper.powerset(list(F))
            for tmpF in ps:
                key[0]=[list(f) for f in tmpF]
                key[3]=[list(f) for f in F if f not in tmpF]
                
                
                sumOptions=[]
                key[1]=[]
                for t,terms1 in enumerate(key[0]):
                    tensorSlice1=[]
                    for index1 in terms1:
                        tensor1=listOfTensors[index1]
                        tensorSlice1.append(tensor1.dimensions)
                    key[1].append(tensorSlice1)
                    
                    tmp=[]
                    for t in tensorSlice1:
                        tmp=list(set(tmp).union(t))
#                    print("tmp:",tmp)
                    if tmp:
                        sumOptions.append(list(helper.powerset(tmp)))
                    else:
                        sumOptions.append([[]])
#                print(key[0],sumOptions)
                for slices1 in itertools.product(*sumOptions):
                    key[2]=list(slices1)
                    
                    sumOptions1=[]
                    key[4]=[]
                    for t,terms1 in enumerate(key[3]):
                        tensorSlice1=[]
                        for index1 in terms1:
                            tensor1=listOfTensors[index1]
                            tensorSlice1.append(tensor1.dimensions)
                        key[4].append(tensorSlice1)
                        
                        tmp=[]
                        for t in tensorSlice1:
                            tmp=list(set(tmp).union(t))
                        if tmp:
                            sumOptions1.append(helper.powerset(tmp))
                        else:
                            sumOptions1.append([[]])
                        
                    for slices2 in itertools.product(*sumOptions1):
                        key[5]=list(slices2)
                        for i,tensor in enumerate(listOfTensors):
                            key[6]=i
                            key[7]=tensor.dimensions
                            key[8]=listTensorsType
                            key[9]=[0,0,perterm.copy(),0,perterm.copy(),0,perterm.copy(),0,0,0,perterm.copy(),0,perterm.copy(),0,perterm.copy()]
                            key[10]=[]
                            key[11]=negZ
                            nodes.append(Node.Node(key))
                            if negation==1:
                                key[11]=0
                                nodes.append(Node.Node(key))
    return nodes


def generateRoots(listOfTensors,listTensorsType,m,n,slicing,negation,negZ):
    roots=[]
    key=[0]*12
    key[0]=[]
    key[1]=[]
    key[2]=[]
    perterm=[0]*m
    if negation==0 or negZ==0:
        key[3]=[]
        key[4]=[]
        key[5]=[]
        for i,tensor in enumerate(listOfTensors):
            key[6]=i
            if slicing==0:
                key[7]=tensor.dimensions
                key[8]=listTensorsType
                key[9]=[0,0,perterm.copy(),0,perterm.copy(),0,perterm.copy(),0,0,0,perterm.copy(),0,perterm.copy(),0,perterm.copy()]
                key[10]=[]
                key[11]=0
                roots.append(Node.Node(key))
            else:
                for dim in tensor.powerset(tensor.dimensions):
                    key[7]=dim
                    key[8]=listTensorsType
                    key[9]=[0,0,perterm.copy(),0,perterm.copy(),0,perterm.copy(),0,0,0,perterm.copy(),0,perterm.copy(),0,perterm.copy()]
                    key[10]=[]
                    key[11]=0
                    roots.append(Node.Node(key))
    
    if negZ==1:
        nSizeCombinations=list(combinations_with_replacement(range(len(listOfTensors)),n))
        if len(nSizeCombinations)<m:
            m=len(nSizeCombinations)
        for F in list(combinations_with_replacement(nSizeCombinations,m)):
            key[3]=[list(f) for f in F]
            termSlice=[]
            for terms in F:
                tensorSlice=[]
                for index in terms:
                    tensor=listOfTensors[index]
                    if slicing==0:
                        tensorSlice.append([tensor.dimensions])
                    else:
                        tensorSlice.append(tensor.powerset(tensor.dimensions))
                termSlice.append(list(itertools.product(*tensorSlice)))
            for slices in itertools.product(*termSlice):
                key[4]=[list(s) for s in slices]
                key[5]=[]
                for i in range(len(slices)):
                    tmp=[]
                    for j in range(len(slices[i])):
                        tmp=list(set(tmp).union(set(slices[i][j])))
                    key[5].append(tmp)
                for i,tensor in enumerate(listOfTensors):
                    key[6]=i
                    if slicing==0:
                        key[7]=tensor.dimensions
                        key[8]=listTensorsType
                        key[9]=[0,0,perterm.copy(),0,perterm.copy(),0,perterm.copy(),0,0,0,perterm.copy(),0,perterm.copy(),0,perterm.copy()]
                        key[10]=[]
                        key[11]=negZ
                        roots.append(Node.Node(key))
                        if negation==1:
                            key[11]=0
                            roots.append(Node.Node(key))
                    else:
                        for dim in tensor.powerset(tensor.dimensions):
                            key[7]=dim
                            key[8]=listTensorsType
                            key[9]=[0,0,perterm.copy(),0,perterm.copy(),0,perterm.copy(),0,0,0,perterm.copy(),0,perterm.copy(),0,perterm.copy()]
                            key[10]=[]
                            key[11]=negZ
                            roots.append(Node.Node(key))
    return roots


#termSlice=[]
#                        for terms in key[3]:
#                            tensorSlice=[]
#                            for index in terms:
#                                tensor=listOfTensors[index]
#                                if slicing==0:
#                                    tensorSlice.append([tensor.dimensions])
#                                else:
#                                    tensorSlice.append(tensor.powerset(tensor.dimensions))
#                            termSlice.append(list(itertools.product(*tensorSlice)))
#                        for slices in itertools.product(*termSlice):
#                            key[4]=[list(s) for s in slices]
#                            sumOver=[]
#                            for i in range(len(slices)):
#                                tmp=[]
#                                for j in range(len(slices[i])):
#                                    tmp=list(set(tmp).union(set(slices[i][j])))
#                                sumOver.append(list(helper.powerset(tmp)))
#                                
#                            r=[[]]
#                            for x in sumOver:
#                                t = []
#                                for y in x:
#                                    for i in r:
#                                        t.append(i+[y])
#                                r = t
##                            print("r:",r)
#                            for elem in r:
#                                key[5]=elem
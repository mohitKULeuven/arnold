from itertools import combinations_with_replacement
import itertools
import Node

def intelligentEnumeration(tensor_properties,root,var,m,n,slicing,negation,prevRoots,examples,constraintList):     
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
    children=root.generateChildren(tensor_properties,m,n,slicing,negation)
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
            
            uglyNodes = child.uglyNodes(tensor_properties,m,n,slicing,var,examples)
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
                    tmpConstraintList.append(node2)
            constraints=intelligentEnumeration(tensor_properties,child,var,m,n,slicing,negation,prevRoots,examples,constraintList)
            if constraints:
                childSatisfaction=1
                for node1 in constraintList:
                    for node2 in constraints:
                        if node2.isAncestor(node1):
                            constraintList.remove(node1)
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
            uglyNodes = child.uglyNodes(tensor_properties,m,n,slicing,var,examples)
            for nodes in uglyNodes:
                if nodes.validStructure() and nodes.satisfiesSignatures(m,n) and all(nodes.satisfiesConstraint(exp,var) for exp in examples):
                    tmpConstraintList.extend(intelligentEnumeration(tensor_properties,nodes,var,m,n,slicing,negation,prevRoots,examples,constraintList))

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


def generateRoots(tensor_properties,listTensorsType,m,n,slicing,negation,negZ):
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
        for i,tensor in enumerate(tensor_properties):
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
        nSizeCombinations=list(combinations_with_replacement(range(len(tensor_properties)),n))
        if len(nSizeCombinations)<m:
            m=len(nSizeCombinations)
        for F in list(combinations_with_replacement(nSizeCombinations,m)):
            key[3]=[list(f) for f in F]
            termSlice=[]
            for terms in F:
                tensorSlice=[]
                for index in terms:
                    tensor=tensor_properties[index]
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
                for i,tensor in enumerate(tensor_properties):
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
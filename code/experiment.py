#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan  4 11:20:27 2019
@author: mohit
"""
import solver
import helper
import Tensor
import Node

def naiveLearn(examples,inputVariables,listOfTensors,dimensions,var,m,n,slicing,negation,negZ):
#    listOfTensors=helper.exampleToTensor(examples,dimensions)
    exampleTensors=[]
    for example in examples:
        exampleTensors.append(helper.exampleToTensor(example,inputVariables,dimensions,listOfTensors))
#    print(examples)
    listGoodTensor=[]
    listBadTensor=[]
    listUglyTensor=[]
    for i,tensor in enumerate(listOfTensors):
        if abs(tensor.type)==1:
            listGoodTensor.append(i)
        elif abs(tensor.type)==2:
            listBadTensor.append(i)
        else:
            listUglyTensor.append(i)            
#    print("...Generating Roots...")
    roots=solver.naiveNodes(listOfTensors,[listGoodTensor,listBadTensor,listUglyTensor],m,n,slicing,negation,negZ)
    print("Nodes generated:",len(roots))
    constraints=[]
#    roots[0].printNode()
#    print("...Enumerating Roots...")
    l=0
    for i,root in enumerate(roots):
        if root.Z==0 and root.negZ==0 and (len(root.E) + len(root.F)==0):
            l+=1
            root.prettyPrint()
    
        if root.validStructure() and root.satisfiesSignatures(m,n) and all(root.satisfiesConstraint(exp,var) for exp in exampleTensors):
            constraints.append(root)
    print("l",l)
    return constraints,len(listGoodTensor),len(listBadTensor),len(listUglyTensor),len(roots)


def learn(examples,inputVariables,listOfTensors,dimensions,var,m,n,slicing,negation,negZ):
#    listOfTensors=helper.exampleToTensor(examples,dimensions)
    exampleTensors=[]
    for example in examples:
        exampleTensors.append(helper.exampleToTensor(example,inputVariables,dimensions,listOfTensors))
#    print(examples)
    listGoodTensor=[]
    listBadTensor=[]
    listUglyTensor=[]
    for i,tensor in enumerate(listOfTensors):
        if abs(tensor.type)==1:
            listGoodTensor.append(i)
        elif abs(tensor.type)==2:
            listBadTensor.append(i)
        else:
            listUglyTensor.append(i)            
#    print("...Generating Roots...")
    roots=solver.generateRoots(listOfTensors,[listGoodTensor,listBadTensor,listUglyTensor],m,n,slicing,negation,negZ)
#    print("...",len(roots),"Roots Generated...")
#    for root in roots:
#        root.prettyPrint()
    constraints=[]
    
#    print("...Enumerating Roots...")
    for i,root in enumerate(roots):
        if root.validStructure() and (not root.satisfiesSignatures(m,n) or all(root.satisfiesConstraint(exp,var) for exp in exampleTensors)):
            
            solver.intelligentEnumeration(listOfTensors,root,var,m,n,slicing,negation,roots[0:i],exampleTensors,constraints)

#    print(len(constraints))
#    for node in constraints:
#        node.prettyPrint()
#        node.printPath()
#    if len(listGoodTensor)+len(listBadTensor)>0:
#        print('good:',listGoodTensor)
#        listOfTensors.append(Tensor.Tensor([1,1,[],len(listOfTensors),1]))
#        OneIndex=len(listOfTensors)-1
#        one=listOfTensors[OneIndex]
#        for i in listGoodTensor:
#            key=[0]*12
#            key[0]=[[OneIndex]]
#            key[1]=[[one.dimensions]]
#            key[2]=[[]]
#            perterm=[0]*m
#            key[3]=[]
#            key[4]=[]
#            key[5]=[]
#            key[6]=i
#            key[7]=listOfTensors[i].dimensions
#            key[8]=[listGoodTensor,listBadTensor,listUglyTensor]
#            key[9]=[0,0,perterm,0,perterm,0,perterm,0,0,0,perterm,0,perterm,0,perterm]
#            key[10]=[]
#            key[11]=0
#            constraints.append(Node.Node(key))
#            constraints[len(constraints)-1].prettyPrint()
#        for i in listBadTensor:
#            key=[0]*12
#            key[0]=[]
#            key[1]=[]
#            key[2]=[]
#            perterm=[0]*m
#            key[3]=[]
#            key[4]=[]
#            key[5]=[]
#            key[6]=i
#            key[7]=listOfTensors[i].dimensions
#            key[8]=[listGoodTensor,listBadTensor,listUglyTensor]
#            key[9]=[0,0,perterm,0,perterm,0,perterm,0,0,0,perterm,0,perterm,0,perterm]
#            key[10]=[]
#            key[11]=0
#            constraints.append(Node.Node(key))
#            
#            key=[0]*12
#            key[0]=[[OneIndex]]
#            key[1]=[[one.dimensions]]
#            key[2]=[[]]
#            perterm=[0]*m
#            key[3]=[]
#            key[4]=[]
#            key[5]=[]
#            key[6]=i
#            key[7]=listOfTensors[i].dimensions
#            key[8]=[listGoodTensor,listBadTensor,listUglyTensor]
#            key[9]=[0,0,perterm,0,perterm,0,perterm,0,0,0,perterm,0,perterm,0,perterm]
#            key[10]=[]
#            key[11]=1
#            constraints.append(Node.Node(key))
        
    return constraints,len(listGoodTensor),len(listBadTensor),len(listUglyTensor),len(roots)

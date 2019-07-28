#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 31 06:27:16 2019

@author: mohit
"""

import helper
import solver
import Node

def learn(list_example,list_constants,tensor_properties,dimensions,var,m,n,slicing,negation,negZ):
#    print(list_example,list_constants,tensor_properties,dimensions,var,m,n,slicing,negation,negZ)
    exampleTensors=[]
    for example in list_example:
        exampleTensors.append(helper.exampleToTensor(example,list_constants,dimensions,tensor_properties))
    listGoodTensor=[]
    listBadTensor=[]
    listUglyTensor=[]
    for i,tensor in enumerate(tensor_properties):
        if abs(tensor.type)==1:
            listGoodTensor.append(i)
        elif abs(tensor.type)==2:
            listBadTensor.append(i)
        else:
            listUglyTensor.append(i)            
    roots=solver.generateRoots(tensor_properties,[listGoodTensor,listBadTensor,listUglyTensor],m,n,slicing,negation,negZ)
    constraints=[]
    
    for i,root in enumerate(roots):
        if root.validStructure() and (not root.satisfiesSignatures(m,n) or all(root.satisfiesConstraint(exp,var) for exp in exampleTensors)):
            
            solver.intelligentEnumeration(tensor_properties,root,var,m,n,slicing,negation,roots[0:i],exampleTensors,constraints)

    #Adding Non-negative constraitns for all decision variable
    tmp=[]
    for constraint in constraints:
        if  not constraint.isTrivial(tensor_properties):
            tmp.append(constraint)
#            constraint.printNode()
    constraints=tmp
#    print(exampleTensors)
    for tensor in exampleTensors[0]:
#        print("################################")
#        print(tensor.name)
        if tensor.name not in list_constants:
            key=[[] for j in range(12)]
            key[6]=tensor.index
            key[7]=tensor.dimensions
#            key[2]=[[]]
            if tensor.type<0:
                key[11]=1
            elif tensor.type>0:
                key[11]=0
            constraints.append(Node.Node(key))
#        if tensor.name not in list_constants and tensor.type>0:
#            key=[[] for j in range(12)]
#            key[3]=[[tensor.index]]
#            key[4]=[[tensor.dimensions]]
#            key[5]=[[]]
#            key[11]=0
#            constraints.append(Node.Node(key))
#            constraints[len(constraints)-1].printNode()
    
    return constraints

def learn_constraints(list_example,list_constants,num_sum,num_prod,slicing,negation,negZ,folder,file_name):
    var,dimensions=helper.findVarDim(list_example[0])
    listOfTensors=helper.exampleToTensor(list_example,list_constants,dimensions,[])
    
    constraints=learn(list_example,list_constants,listOfTensors,dimensions,var,num_sum,num_prod,slicing,negation,negZ)
    
    helper.createMzn(constraints,folder,file_name,list_constants,list_example,dimensions,var)
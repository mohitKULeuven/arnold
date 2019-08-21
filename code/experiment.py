#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 22 08:30:20 2019

@author: mohit
"""

import pymzn
import arnold
import time
import numpy as np
import helper
import math
import csv
import itertools
import os
import argparse
import pickle
import copy


def precision_cal(constraints,testExamples,inputVariables,variables,listOfTensors,dimensions,dimension_length,folder,file_name):
    helper.createMzn(constraints,folder,file_name,inputVariables,testExamples[0],dimensions,dimension_length)
#    precision=[]
#    for i in range(5):
    mznFile,dznFile=folder+file_name+'.mzn',folder+file_name+'.dzn'
    
    if 'shipping' in dznFile:
        dataDic={'W':4, 'F':3,'demand':[30,20,35,20],'production':[40,40,25]}
    elif 'scheduling_bratko' in dznFile:
        dataDic={'a':12, 'b':2,'c':3, 'd':4, 'e':5,'f':12}
    elif 'number_of_days' in dznFile:
        dataDic={'num_days':7,'const':15,'data':[[1,1000],[2,1200],[3,2500],[4,3100],[5,1100],[6,2100],[7,4000]]}
    elif 'rostering' in dznFile:
        dataDic={'mon':1,'sun':7,'num_shifts':3,'num_workers':4,'workload':[4,2,1]}
#        elif 'curriculum' in dznFile:
#            dataDic={}
    elif 'stuckey_assignment' in dznFile:
        dataDic={'num_workers':5, 'num_products':5,'const':1, 'lb':10, 'profit' :  [[7,1,3,4,5],[8,2,5,1,4],[4,3,7,2,5],[3,1,6,3,5],[3,1,6,3,5]]}
    elif 'golfers' in dznFile:
        dataDic={'weeks':4, 'groups':3,'groupSize':3,'golfers':9,'const':1}
    elif 'assignment' in dznFile:
        dataDic={'rows':4, 'cols':5,'const':1, 'cost' :  [[14,  5, 8,  7, 15],[2, 12, 6,  5,  3],[7,  8, 3,  9,  7],[2,  4, 6, 10,  1]]}
    elif 'capital_budget' in dznFile:
        dataDic={'const':38, 'const2':5, 'npv':[16,22,12,8],'cash_flow':[5,7,4,3],'budget':250}
    elif 'curriculum' in dznFile:
        dataDic={'n_courses':46, 'n_periods':8, 'load_per_period_lb':10, 'load_per_period_ub':24, 'courses_per_period_lb':2, 'courses_per_period_ub':10, 'course_load':[1,  3,  1,  2,  4, 4,  1,  5,  3,  4, 4,  5,  1,  3,  3, 4,  1,  1,  3,  3, 3,  3,  3,  3,  1, 4,  4,  3,  3,  3, 2,  4,  3,  3,  3, 3,  3,  3,  3,  3, 3,  3,  2,  3,  3, 3]}
    elif 'knapsack' in dznFile:
        dataDic={'n':5, 'capacity':200000, 'size':[90,72,43,40,33], 'profit':[1300,1000,520,480,325]}
    elif 'schedule' in dznFile:
        dataDic={'const':30, 'const2':50, 'const3':1, 'Ds':[16, 6,13, 7, 5,18, 4], 'Rs' :  [ 2, 9, 3, 7,10, 1,11]}
    
    prec=0
    
    tmp_var=variables.copy()
    for val in inputVariables:
        tmp_var.remove(val)
    tmp=pymzn.minizinc(mznFile,data=dataDic,timeout=10,all_solutions=True,output_vars=tmp_var)
#    print(len(tmp))
#    print(tmp[0])
    numExample=1000
    if len(tmp)<1000:
        numExample=len(tmp)
    output=helper.list_sample(tmp,numExample)
    for sol in output:
        
        if sol is None:
            continue
        
        if 'shipping' in dznFile:
            sol['ship']=to_matrix(sol['ship'],dataDic['W'])
#            elif 'number_of_days' in dznFile:
#                sol['data']=to_matrix(sol['data'],2)
        elif 'rostering' in dznFile:
            sol['on_duty']=to_matrix(sol['on_duty'],dataDic['num_shifts'])
        elif 'stuckey_assignment' in dznFile:
#                sol['profit']=to_matrix(sol['profit'],sol['num_products'])
            sol['x']=to_matrix(sol['x'],dataDic['num_products'])
        elif 'golfers' in dznFile:
            sol['assign']=to_matrix(sol['assign'],dataDic['weeks'])
        elif 'assignment' in dznFile:
            sol['x']=to_matrix(sol['x'],dataDic['cols'])
        elif 'curriculum' in dznFile:
            sol['x']=to_matrix(sol['x'],dataDic['n_courses'])
        
        try:
#            print(sol)
            o=pymzn.minizinc(folder+args.mznfile+'.mzn',data=sol)
#            print(o)
        except:
            continue
        prec+=1
#    print("prec:",prec)
    return float(prec*100)/numExample
        
#    return np.mean(precision), np.std(precision)



def recall_cal(constraints,testExamples,inputVariables,listOfTensors,dimensions,dimension_length):
    n=0
    for data in testExamples:
        tensors=helper.exampleToTensor(data,inputVariables,dimensions,listOfTensors)
        for constraint in constraints:
#            constraint.printNode()
            if not constraint.satisfiesConstraint(tensors,dimension_length):
                n+=1
                break
    return 100.0-(float(n*100)/float(len(testExamples)))

def to_matrix(l, n):
    return [l[i:i+n] for i in range(0, len(l), n)]

def runMinizinc(dznFile,mznFile,variables,numExample):
    outputDic=[]
    for sol in pymzn.minizinc(mznFile,all_solutions=True,output_vars=variables,timeout=5):
        if sol is None:
            continue
        if 'shipping' in dznFile:
            tmp=copy.deepcopy(sol)
            tmp['ship']=to_matrix(sol['ship'],sol['W'])
            outputDic.append(tmp)
        elif 'number_of_days' in dznFile:
            tmp=copy.deepcopy(sol)
            tmp['data']=to_matrix(sol['data'],2)
            outputDic.append(tmp)
        elif 'rostering' in dznFile:
            tmp=copy.deepcopy(sol)
            tmp['on_duty']=to_matrix(sol['on_duty'],sol['num_shifts'])
            outputDic.append(tmp)
        elif 'curriculum' in dznFile:
            tmp=copy.deepcopy(sol)
            tmp['x']=to_matrix(sol['x'],sol['n_courses'])
            outputDic.append(tmp)
        elif 'stuckey_assignment' in dznFile:
            tmp=copy.deepcopy(sol)
            tmp['profit']=to_matrix(sol['profit'],sol['num_products'])
            tmp['x']=to_matrix(sol['x'],sol['num_products'])
            outputDic.append(tmp)
        elif 'golfers' in dznFile:
            tmp=copy.deepcopy(sol)
            tmp['assign']=to_matrix(sol['assign'],sol['weeks'])
            outputDic.append(tmp)
        elif 'assignment' in dznFile:
            tmp=copy.deepcopy(sol)
            tmp['cost']=to_matrix(sol['cost'],sol['cols'])
            tmp['x']=to_matrix(sol['x'],sol['cols'])
            outputDic.append(tmp)
        else:
            outputDic.append(sol)
            

#    num=10000
#    if len(outputDic)<10000:
#        num=len(outputDic)
    data=helper.list_sample(outputDic,numExample)
#    print("...Randomly Selected",len(data),"examples...")
#    print(data[0])
    return data

def crossValidate(folder,numTrain,data,inputVariables,variables,dimensions,dimension_length,sums,products,slicing,negation,negZ,ind):
    numElemBucket=math.floor(len(data)/5)
    timeTaken=[]
    recall=[]
    precision=[]
    numConstraints=[]
    tensor_properties=helper.tensor_properties(data,inputVariables,dimensions)
    for i in range(5):
        trainExamples=data[i*numElemBucket:(i+1)*numElemBucket][:numTrain]
        testExamples=[d for j,d in enumerate(data) if j not in range(i*numElemBucket,(i+1)*numElemBucket)]
        start = time.clock()
#        print(trainExamples)
        constraints=arnold.learn(trainExamples,inputVariables,tensor_properties,dimensions,dimension_length,sums,products,slicing,negation,negZ)
#        constraints=[]
#        for constraint in tmp:
#            if  not constraint.isTrivial(listOfTensors):
#                constraints.append(constraint)
                  
        timeTaken.append(time.clock() - start)  
        file_name='constraints_'+ind+'_'+str(sums)+str(products)+str(negation)+str(negZ)+str(numTrain)+str(i)
        pickle.dump( constraints, open( folder+'pickles/'+file_name+'.pickle', "wb" ) )
        recall.append(recall_cal(constraints,testExamples,inputVariables,tensor_properties,dimensions,dimension_length))
        precision.append(precision_cal(constraints,testExamples,inputVariables,variables,tensor_properties,dimensions,dimension_length,folder,file_name))
        numConstraints.append(len(constraints))
    
    print("######################################")
    print("Sum:",sums,"Prod:",products,"negation:",negation,"negZ:",negZ)
    print("Training Data Size:",len(trainExamples),"Number of Tensors:",len(trainExamples[0]))
    print("Number of Constraints:",np.mean(numConstraints),"Recall:",np.mean(recall),"Time Taken:",np.mean(timeTaken))
    print("######################################")
    return numConstraints,recall,precision,timeTaken

def findVarDim(data):
    lengthSet=set()
    dim=[]
    for elem in list(data.values()):
        dim.append(list(np.array(elem).shape))
        lengthSet.update(list(np.array(elem).shape))
        
    dimensions=[]
    lengthList=list(lengthSet)
    for elem in dim:
        dimensions.append([lengthList.index(e) for e in elem])
    
    var=[]
    for elem in lengthList:
        var.append(elem)
    return var,dimensions
      
def runExperiment(folder,dznFile,mznFile,variables,inputVariables,numExample,trainSize,sumList,prodList,negation):
    data=runMinizinc(folder+dznFile,folder+mznFile,variables,numExample) #data is a list of dictionary with keys being the name of the variables
#    print(data)
    if len(data)<max(trainSize)*5:
        print("Generated only",len(data),"examples. Please reduce training size to <=",len(data)/5)
        return
    
    dimension_length,dimensions=findVarDim(data[0])
#    if 'stuckey_assignment' in args.file:
#        dimensions[2][1]=1
#        dimensions[5][1]=1
#        var.append(var[0])
    slicing=0   
    ind='s'+''.join(str(e) for e in sumList)+'p'+''.join(str(e) for e in prodList)+'n'+str(negation)
    csvfile = open(folder+'results/extended_results'+ind+'.csv', 'w')
    filewriter = csv.writer(csvfile, delimiter=',')
    filewriter.writerow(['# of Tensors','Training Size', 'Avg # of Constraints', 'Std # of Constraints','Avg Recall','Std Recall','Avg Precision','Std Precision','Avg Time','Std Time','Sum','Product','NegTerms','NegZ'])
    csvfile.close()
    results=[]
    for sums,products,negZ in itertools.product(sumList,prodList,[1]):
        for numTrain in trainSize:
            if numTrain<len(data):
                numConstraints,recall,precision,timeTaken=crossValidate(folder,numTrain,data,inputVariables,variables,dimensions,dimension_length,sums,products,slicing,negation,negZ,ind)
                row=[len(data[0]),numTrain,np.mean(numConstraints),np.std(numConstraints),np.mean(recall),np.std(recall),np.mean(precision),np.std(precision),np.mean(timeTaken),np.std(timeTaken),sums,products,negation,negZ]
                results.append(row)
                
                csvfile = open(folder+'results/extended_results'+ind+'.csv', 'a')
                filewriter = csv.writer(csvfile, delimiter=',')
                filewriter.writerow(row)
                csvfile.close()
     

CLI=argparse.ArgumentParser()
CLI.add_argument(
  "--file",  
  type=str,
  default="",  
)
CLI.add_argument(
  "--dznfile",  
  type=str,
  default="",  
)
CLI.add_argument(
  "--mznfile",  
  type=str,
  default="",  
)
CLI.add_argument(
  "--sum",  
  nargs="*",  
  type=int,
  default=[1],  
)
CLI.add_argument(
  "--prod",
  nargs="*",
  type=int,  
  default=[1,2,3],
)
CLI.add_argument(
  "--num_example",
  type=int,  
  default=125,
)
CLI.add_argument(
  "--trainSize",
  nargs="*",
  type=int,  
  default=[1,25],
)
CLI.add_argument(
  "--negation",
  type=int,  
  default=1,
)
CLI.add_argument(
  "--sampleSize",  
  type=int,
  default="100",
)


args = CLI.parse_args()

cwd = os.getcwd()
folder=cwd+'/experiments/'  


with open(folder+args.file+'/'+args.file+'.mzn.inputvars') as f:
    inputVariables = f.readlines()
inputVariables = [x.strip() for x in inputVariables] 
with open(folder+args.file+'/'+args.file+'.mzn.vars') as f:
    variables = f.readlines()
variables = [x.strip() for x in variables] 


if not args.dznfile:
    args.dznfile=args.file
if not args.mznfile:
    args.mznfile=args.file

if not os.path.exists(folder+args.file+'/results'):
    os.makedirs(folder+args.file+'/results')
if not os.path.exists(folder+args.file+'/pickles'):
    os.makedirs(folder+args.file+'/pickles')
    

s = time.clock()
runExperiment(folder+args.file+'/', args.dznfile+'.dzn', args.mznfile+'.mzn', variables, inputVariables, args.num_example, args.trainSize, args.sum, args.prod, args.negation)
print("Total time taken:",time.clock() - s)









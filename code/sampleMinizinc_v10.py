#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 22 08:30:20 2019

@author: mohit
"""

import pymzn
import experiment
import time
import numpy as np
import helper
import math
import csv
import itertools
import os, shutil
import argparse
import pickle
import copy



def recall(constraints,testExamples,inputVariables,listOfTensors,dimensions,var):
    n=0
    for data in testExamples:
        tensors=helper.exampleToTensor(data,inputVariables,dimensions,listOfTensors)
        for constraint in constraints:
            if not constraint.satisfiesConstraint(tensors,var):
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
#            tmp['profit']=to_matrix(sol['profit'],sol['num_products'])
            tmp['data']=to_matrix(sol['data'],2)
            outputDic.append(tmp)
        elif 'rostering' in dznFile:
            tmp=copy.deepcopy(sol)
#            tmp['profit']=to_matrix(sol['profit'],sol['num_products'])
            tmp['on_duty']=to_matrix(sol['on_duty'],sol['num_shifts'])
            outputDic.append(tmp)
        elif 'curriculum' in dznFile:
            tmp=copy.deepcopy(sol)
#            tmp['profit']=to_matrix(sol['profit'],sol['num_products'])
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
            

    print("...Generated",len(outputDic),"examples...")
    data=helper.list_sample(outputDic,numExample)
    print("...Randomly Selected",len(data),"examples...")
#    print(data[0])
    return data

def createExamples(data):
    examples=[]
    for dic in data:
        outputList=list(dic.values())
#        if inputList:
#            tmp=inputList.copy()
#            tmp.extend(outputList)
#        else: 
        tmp=outputList.copy()
        examples.append(tmp)
    return examples

def crossValidate(folder,numTrain,data,inputVariables,dimensions,var,sums,products,slicing,negation,negZ,ind):
    numElemBucket=math.floor(len(data)/5)
    timeTaken=[]
    acctimeTaken=[]
    accuracy=[]
    numConstraints=[]
    good=[]
    bad=[]
    ugly=[]
    listOfTensors=helper.exampleToTensor(data,inputVariables,dimensions,[])
#    for t in listOfTensors:
#        print(t.input)
    for i in range(1):
        trainExamples=data[i*numElemBucket:(i+1)*numElemBucket][:numTrain]
        print(trainExamples)
        testExamples=[d for j,d in enumerate(data) if j not in range(i*numElemBucket,(i+1)*numElemBucket)]
        start = time.clock()
#        constraints,lg,lb,lu,lenRoots=experiment.naiveLearn(trainExamples,inputVariables,listOfTensors,dimensions,var,sums,products,slicing,negation,negZ)
#        print(trainExamples)
        tmp,lg,lb,lu,lenRoots=experiment.learn(trainExamples,inputVariables,listOfTensors,dimensions,var,sums,products,slicing,negation,negZ)
        if i==1:
            print("...",lenRoots,"Roots Generated...")
        constraints=[]
        for constraint in tmp:
#            constraint.prettyPrint()
            if  not constraint.isTrivial(listOfTensors):
                constraints.append(constraint)
#                if constraint.Z==6:
#                    constraint.prettyPrint()
                  
        timeTaken.append(time.clock() - start)  
        pickle.dump( constraints, open( folder+'pickles/constraints_'+ind+'_'+str(sums)+str(products)+str(negation)+str(negZ)+str(numTrain)+str(i)+'_v10.pickle', "wb" ) )
        good.append(lg)
        bad.append(lb)
        ugly.append(lu)
        start = time.clock()
        accuracy.append(recall(constraints,testExamples,inputVariables,listOfTensors,dimensions,var))
        acctimeTaken.append(time.clock() - start)
        numConstraints.append(len(constraints))
#        print("..Completed",i,"iterations...")
    
    print("######################################")
    print("Sum:",sums,"Prod:",products,"negation:",negation,"negZ:",negZ)
    print("Training Data Size:",len(trainExamples),"Number of Tensors:",len(trainExamples[0]))
    print("Number of Constraints:",np.mean(numConstraints),"Recall:",np.mean(accuracy),"Time Taken:",np.mean(timeTaken))
    print("Acc Time Taken:",np.mean(acctimeTaken))
    print("######################################")
    return numConstraints,accuracy,timeTaken,good,bad,ugly

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
        var.append(list(range(elem)))
    return var,dimensions
      
def runExperiment(folder,dznFile,mznFile,variables,inputVariables,numExample,trainSize,sumList,prodList,negation):
    data=runMinizinc(folder+dznFile,folder+mznFile,variables,numExample)
#    print(data[0])
    if len(data)<max(trainSize)*5:
        print("Generated only",len(data),"examples. Please reduce training size to <=",len(data)/5)
        return
    
    var,dimensions=findVarDim(data[0])
    if 'stuckey_assignment' in args.file:
        dimensions[2][1]=1
        dimensions[5][1]=1
        var.append(var[0])
    slicing=0   
    ind='s'+''.join(str(e) for e in sumList)+'p'+''.join(str(e) for e in prodList)+'n'+str(negation)
    csvfile = open(folder+'results/extended_results'+ind+'_v10.csv', 'w')
    filewriter = csv.writer(csvfile, delimiter=',')
    filewriter.writerow(['# of Tensors','GoodTensors','GoodTensors_std','BadTensors','BadTensors_std','UglyTensors','UglyTensors_std','Training Size', 'Avg # of Constraints', 'Std # of Constraints','Avg Recall','Std Recall','Avg Time','Std Time','Sum','Product','NegTerms','NegZ'])
    csvfile.close()
    results=[]
    for sums,products,negZ in itertools.product(sumList,prodList,[1]):
        for numTrain in trainSize:
            if numTrain<len(data):
                csvfile = open(folder+'results/extended_results'+ind+'_v10.csv', 'a')
                filewriter = csv.writer(csvfile, delimiter=',')
                numConstraints,accuracy,timeTaken,good,bad,ugly=crossValidate(folder,numTrain,data,inputVariables,dimensions,var,sums,products,slicing,negation,negZ,ind)
                row=[len(data[0]),np.mean(good),np.std(good),np.mean(bad),np.std(bad),np.mean(ugly),np.std(ugly),numTrain,np.mean(numConstraints),np.std(numConstraints),np.mean(accuracy),np.std(accuracy),np.mean(timeTaken),np.std(timeTaken),sums,products,negation,negZ]
                results.append(row)
                filewriter.writerow(row)
                csvfile.close()


def getmznFiles(numvar,folder):
    d={}
    with open(folder+'mzns-with-counts/counts') as f:
        for line in f:
            (key,val) = line.split()
#            print(key,val)
            thefilepath=folder+'mzns-with-counts/'+key+".vars"
            variables=open(thefilepath).readlines(  )
            count = len(variables)
            if count==numvar:
                for i,var in enumerate(variables):
                    variables[i]=var.strip()
                d[key]=variables
    return d
     

CLI=argparse.ArgumentParser()
CLI.add_argument(
  "--file",  # name on the CLI - drop the `--` for positional/required parameters
#  nargs=1,  # 0 or more values expected => creates a list
  type=str,
  default="",  # default if nothing is provided
)
CLI.add_argument(
  "--dznfile",  # name on the CLI - drop the `--` for positional/required parameters
#  nargs=1,  # 0 or more values expected => creates a list
  type=str,
  default="",  # default if nothing is provided
)
CLI.add_argument(
  "--mznfile",  # name on the CLI - drop the `--` for positional/required parameters
#  nargs=1,  # 0 or more values expected => creates a list
  type=str,
  default="",  # default if nothing is provided
)
CLI.add_argument(
  "--sum",  # name on the CLI - drop the `--` for positional/required parameters
  nargs="*",  # 0 or more values expected => creates a list
  type=int,
  default=[1,2],  # default if nothing is provided
)
CLI.add_argument(
  "--prod",
  nargs="*",
  type=int,  # any type/callable can be used here
  default=[1,2],
)
CLI.add_argument(
  "--example",
  type=int,  # any type/callable can be used here
  default=125,
)
CLI.add_argument(
  "--trainSize",
  nargs="*",
  type=int,  # any type/callable can be used here
  default=[1,5,10,25],
)
CLI.add_argument(
  "--negation",
  type=int,  # any type/callable can be used here
  default=1,
)
CLI.add_argument(
  "--sampleSize",  # name on the CLI - drop the `--` for positional/required parameters
#  nargs=1,  # 0 or more values expected => creates a list
  type=int,
  default=100,  # default if nothing is provided
)


args = CLI.parse_args()

cwd = os.getcwd()
folder=cwd+'/experiments/done/'  

if not os.path.isfile(folder+args.file+'/'+args.file+'.mzn.inputvars'):
    source=os.listdir(folder+"../mzns-with-counts/")
    for file in source:
        if file == args.file+'.mzn.inputvars':
            shutil.copy(folder+"../mzns-with-counts/"+file,folder+args.file)

with open(folder+args.file+'/'+args.file+'.mzn.inputvars') as f:
    inputVariables = f.readlines()
inputVariables = [x.strip() for x in inputVariables] 

if not os.path.isfile(folder+args.file+'/'+args.file+'.mzn.vars'):
    source=os.listdir(folder+"../mzns-with-counts/")
    for file in source:
        if file == args.file+'.mzn.vars':
            shutil.copy(folder+"../mzns-with-counts/"+file,folder+args.file)

with open(folder+args.file+'/'+args.file+'.mzn.vars') as f:
    variables = f.readlines()
variables = [x.strip() for x in variables] 


if not args.dznfile:
    args.dznfile=args.file
    
if not args.mznfile:
    args.mznfile=args.file

print(variables, inputVariables)

if not os.path.exists(folder+args.file):
    os.makedirs(folder+args.file)
    os.makedirs(folder+args.file+'/results')
    os.makedirs(folder+args.file+'/pickles')
    
print(args.mznfile)
if not os.path.isfile(folder+args.file+'/'+args.mznfile+'.mzn'):
    source=os.listdir(folder+"../mzns-with-counts/")
    for file in source:
        if file == args.mznfile+".mzn":
            shutil.copy(folder+"../mzns-with-counts/"+file,folder+args.file)

s = time.clock()
runExperiment(folder+args.file+'/',args.dznfile+'.dzn',args.mznfile+'.mzn',variables,inputVariables,args.example,args.trainSize,args.sum,args.prod,args.negation)
print("total time taken:",time.clock() - s)









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
import os
import argparse
import pickle

#from mpl_toolkits import mplot3d
#import matplotlib.pyplot as plt
#import glob
#import os
#import sys
#import signal



def recall(constraints,testExamples,inputLen,listOfTensors,dimensions,var):
    n=0
    for data in testExamples:
        tensors=helper.exampleToTensor(data,inputLen,dimensions,listOfTensors)
        for constraint in constraints:
            if not constraint.satisfiesConstraint(tensors,var):
                n+=1
                break
    return 100.0-(float(n*100)/float(len(testExamples)))

def runMinizinc(dznFile,mznFile,variables,numExample):
    if numExample>0:
        outputDic=[]
        for sol in pymzn.minizinc(mznFile,wait=False,all_solutions=True,output_vars=variables):
            if sol is None:
                continue
            outputDic.append(sol)
            if len(outputDic)==numExample*10:
                print("Generated",len(outputDic),"Solutions")
                break
    else:
        outputDic=pymzn.minizinc(mznFile,dznFile,all_solutions=True) 
        numExample=500
    print("...Generated",len(outputDic),"examples...")
    data=helper.list_sample(outputDic,numExample)
    print("...Randomly Selected",len(data),"examples...")
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

def crossValidate(folder,k,inputLen,data,dimensions,var,sums,products,slicing,negation,negZ):
    numElemBucket=math.floor(len(data)/5)
    timeTaken=[]
    acctimeTaken=[]
    accuracy=[]
    numConstraints=[]
    good=[]
    bad=[]
    ugly=[]
    listOfTensors=helper.exampleToTensor(data,inputLen,dimensions,[])
    for i in range(1):
#        print("..Starting",i,"iterations...")
        trainExamples=data[i*numElemBucket:(i+1)*numElemBucket][:k]
        testExamples=[d for j,d in enumerate(data) if j not in range(i*numElemBucket,(i+1)*numElemBucket)]
        start = time.clock()
        tmp,lg,lb,lu,lenRoots=experiment.learn(trainExamples,inputLen,listOfTensors,dimensions,var,sums,products,slicing,negation,negZ)
        if i==1:
            print("...",lenRoots,"Roots Generated...")
        constraints=[]
        for constraint in tmp:
            if  not constraint.isTrivial(listOfTensors):
                constraints.append(constraint)
                constraint.prettyPrint()
#                if constraint.negZ==1 and constraint.Z==3 and len(constraint.E)==0 and len(constraint.F)==1 and len(constraint.F[0])==1 and constraint.F[0][0]==3:
#                    constraint.prettyPrint()
#                if constraint.negZ==1 and constraint.Z==3 and len(constraint.E)==0 and len(constraint.F)==2 and len(constraint.F[0])==1 and len(constraint.F[1])==1 and constraint.F[0][0]==3 and constraint.F[1][0]==3: 
#                    constraint.prettyPrint()
#                    constraint.printPath()
                  
        timeTaken.append(time.clock() - start)  
        pickle.dump( constraints, open( folder+'pickles/constraints'+str(sums)+str(products)+str(negation)+str(negZ)+str(k)+str(i)+'_v7.pickle', "wb" ) )
        good.append(lg)
        bad.append(lb)
        ugly.append(lu)
        start = time.clock()
        accuracy.append(recall(constraints,testExamples,inputLen,listOfTensors,dimensions,var))
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

      
def runExperiment(folder,dznFile,mznFile,variables,numExample,trainSize,sumList,prodList,negation):
    data=runMinizinc(folder+dznFile,folder+mznFile,variables,numExample)
    if len(data)<max(trainSize)*5:
        print("Generated only",len(data),"examples. Please reduce training size to <=",len(data)/5)
        return
#    inputList=[]
#    if dznFile:
    inputDic = pymzn.dzn2dict(folder+dznFile)
    inputVars=list(inputDic.keys())
    inputList=list(inputDic.values())
    lengthSet=set()
    dim=[]
    
#    for i,elem in enumerate(inputList):
#        if isinstance(elem,list):
#            dim.append(list(np.array(elem).shape))
#            lengthSet.update(list(np.array(elem).shape))
#        else:
#            dim.append([])
     
    examples=createExamples(data,inputList)
    for elem in list(data[0].values()):
        dim.append(list(np.array(elem).shape))
        lengthSet.update(list(np.array(elem).shape))
        
    dimensions=[]
    lengthList=list(lengthSet)
    for elem in dim:
        dimensions.append([lengthList.index(e) for e in elem])
    
    var=[]
    for elem in lengthList:
        var.append(list(range(elem)))
        
#    products,sums,negation,negZ=2,1,1,1
    print(examples[0])
#    print("var:",var)
#    print("dimensions:",dimensions)
    slicing=0   
    ind='s'+''.join(str(e) for e in sumList)+'p'+''.join(str(e) for e in prodList)+'n'+str(negation)
    csvfile = open(folder+'results/extended_results'+ind+'_v7.csv', 'w')
    filewriter = csv.writer(csvfile, delimiter=',')
    filewriter.writerow(['# of Tensors','GoodTensors','GoodTensors_std','BadTensors','BadTensors_std','UglyTensors','UglyTensors_std','Training Size', 'Avg # of Constraints', 'Std # of Constraints','Avg Recall','Std Recall','Avg Time','Std Time','Sum','Product','NegTerms','NegZ'])
    csvfile.close()
    results=[]
    for sums,products,negZ in itertools.product(sumList,prodList,[1]):
        for numTrain in trainSize:
            if numTrain<len(examples):
                csvfile = open(folder+'results/extended_results'+ind+'_v7.csv', 'a')
                filewriter = csv.writer(csvfile, delimiter=',')
                numConstraints,accuracy,timeTaken,good,bad,ugly=crossValidate(folder,numTrain,len(inputList),examples,dimensions,var,sums,products,slicing,negation,negZ)
                row=[len(examples[0]),np.mean(good),np.std(good),np.mean(bad),np.std(bad),np.mean(ugly),np.std(ugly),numTrain,np.mean(numConstraints),np.std(numConstraints),np.mean(accuracy),np.std(accuracy),np.mean(timeTaken),np.std(timeTaken),sums,products,negation,negZ]
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
    
    


cwd = os.getcwd()
folder=cwd+'/experiments/done/'   

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
  default=0,
)
CLI.add_argument(
  "--trainSize",
  nargs="*",
  type=int,  # any type/callable can be used here
  default=[1,5,25,100],
)
CLI.add_argument(
  "--negation",
  type=int,  # any type/callable can be used here
  default=1,
)
CLI.add_argument(
  "--numVar",
  type=int,  # any type/callable can be used here
  default=4,
)
CLI.add_argument(
  "--numFile",
  type=int,  # any type/callable can be used here
  default=0,
)


args = CLI.parse_args()

mznfiles = pickle.load( open( folder+'mzn_with_var_'+str(args.numVar)+'.pickle', "rb" ) )
if args.numFile>0:
    args.file=list(mznfiles.keys())[args.numFile-1]
    variables=mznfiles[args.mznfile]

if not args.dznfile:
    args.dznfile=args.file
    
if not args.mznfile:
    args.mznfile=args.file

print(args)

#mznfiles=getmznFiles(args.numVar,folder)
#print(mznfiles)
#pickle.dump( mznfiles, open( folder+'mzn_with_var_'+str(args.numVar)+'.pickle', "wb" ) )


#print(args.mznfile,variables)
s = time.clock()
runExperiment(folder+args.file+'/',args.dznfile+'.dzn',args.mznfile+'.mzn',variables,args.example,args.trainSize,args.sum,args.prod,args.negation)
#runExperiment(folder,args.dznFile,args.mznfile,variables,args.example,args.trainSize,args.sum,args.prod,args.negation)
print("total time taken:",time.clock() - s)




#path='/home/mohit/Documents/PhD/IJCAI19/experiments/minizinc/hakhank_edited/mzn/*.mzn'
#files = glob.glob(path)
#print(len(files))
#count=0
#for fileName in files:
#    myfile = open(fileName)
#    if 'predicate' in myfile.read() or 'float' in myfile.read():
#        myfile.close()
##        print(fileName)
#        if os.path.exists(fileName):
#            os.remove(fileName)
#            count+=1
#        else:
#            print("The file does not exist")
#print("deleted",count,"files")



#def crossValidate(k,data,dimensions,var,sums,products,slicing,negation,negZ):
#    timeTaken=[]
#    accuracy=[]
#    numConstraints=[]
#    tmp=math.floor(len(data)/k)
#    for i in range(tmp):
#        trainExamples=data[i*k:(i+1)*k]
#        testExamples=[d for j,d in enumerate(data) if j not in range(i*k,(i+1)*k)]
##        print(len(data),len(testExamples),range(i*k,(i+1)*k))
#        start = time.clock()
#        constraints=experiment.learn(trainExamples,dimensions,var,sums,products,slicing,negation,negZ)
#        timeTaken.append(time.clock() - start)
#        accuracy.append(recall(constraints,testExamples,dimensions,var))
#        numConstraints.append(len(constraints))
#    
#    print("######################################")
#    print("Training Data Size:",k)
#    print("Number of Constraints:",np.mean(numConstraints))
##    print("Test Data Size:",len(testExamples))
#    print("Recall:",np.mean(accuracy))
#    print("Time Taken:",np.mean(timeTaken))
#    print("######################################")
#    return numConstraints,accuracy,timeTaken

#def crossValidate(k,data,dimensions,var,sums,products,slicing,negation,negZ):
#    numExp=len(data)
#    testExamples=data[int(numExp/2):]
#    trainExamples=data[:int(numExp/2)]
#    timeTaken=[]
#    accuracy=[]
#    numConstraints=[]
#    tmp=math.floor(len(trainExamples)/k)
#    for i in range(tmp):
#        train=trainExamples[i*k:(i+1)*k]
##        testExamples=[d for j,d in enumerate(data) if j not in range(i*k,(i+1)*k)]
##        print(len(data),len(testExamples),range(i*k,(i+1)*k))
#        start = time.clock()
#        constraints=experiment.learn(train,dimensions,var,sums,products,slicing,negation,negZ)
#        timeTaken.append(time.clock() - start)
#        accuracy.append(recall(constraints,testExamples,dimensions,var))
#        numConstraints.append(len(constraints))
#    
#    print("######################################")
#    print("Training Data Size:",k)
#    print("Number of Enumeration:",tmp)
#    print("Number of Constraints:",np.mean(numConstraints))
##    print("Test Data Size:",len(testExamples))
#    print("Recall:",np.mean(accuracy))
#    print("Time Taken:",np.mean(timeTaken))
#    print("######################################")
#    return numConstraints,accuracy,timeTaken










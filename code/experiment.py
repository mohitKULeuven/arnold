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
    mznFile,dznFile=folder+file_name+'.mzn',folder+file_name+'.dzn'
    
    if 'shipping' in dznFile:
        dataDic={'W':4, 'F':3,'demand':[30,20,35,20],'production':[40,40,25]}
    
    elif 'assignment' in dznFile:
        dataDic={'rows':4, 'cols':5,'const':1, 'cost' :  [[14,  5, 8,  7, 15],[2, 12, 6,  5,  3],[7,  8, 3,  9,  7],[2,  4, 6, 10,  1]]}
    
    prec=0
    
    tmp_var=variables.copy()
    for val in inputVariables:
        tmp_var.remove(val)
    tmp=pymzn.minizinc(mznFile,data=dataDic,timeout=10,all_solutions=True,output_vars=tmp_var)
    numExample=1000
    if len(tmp)<1000:
        numExample=len(tmp)
    output=helper.list_sample(tmp,numExample)
    for sol in output:
        
        if sol is None:
            continue
        
        if 'shipping' in dznFile:
            sol['ship']=to_matrix(sol['ship'],dataDic['W'])
        elif 'assignment' in dznFile:
            sol['x']=to_matrix(sol['x'],dataDic['cols'])
        
        try:
            o=pymzn.minizinc(folder+args.mznfile+'.mzn',data=sol)
        except:
            continue
        prec+=1
    return float(prec*100)/numExample
        



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
    return data

def crossValidate(folder,numTrain,data,inputVariables,variables,dimensions,dimension_length,sums,products,slicing,negation,negZ,ind):
    global loopnum,numLoop
    numElemBucket=math.floor(len(data)/5)
    timeTaken=[]
    recall=[]
    precision=[]
    numConstraints=[]
    tensor_properties=helper.tensor_properties(data,inputVariables,dimensions)
    printProgressBar(0, 5, prefix = 'Progress:', suffix = 'Complete', length = 50)
    for i in range(5):
        trainExamples=data[i*numElemBucket:(i+1)*numElemBucket][:numTrain]
        testExamples=[d for j,d in enumerate(data) if j not in range(i*numElemBucket,(i+1)*numElemBucket)]
        start = time.clock()
        constraints=arnold.learn(trainExamples,inputVariables,tensor_properties,dimensions,dimension_length,sums,products,slicing,negation,negZ)
                  
        timeTaken.append(time.clock() - start)  
        file_name='constraints_'+ind+'_'+str(sums)+str(products)+str(negation)+str(negZ)+str(numTrain)+str(i)
        pickle.dump( constraints, open( folder+'pickles/'+file_name+'.pickle', "wb" ) )
        recall.append(recall_cal(constraints,testExamples,inputVariables,tensor_properties,dimensions,dimension_length))
        precision.append(precision_cal(constraints,testExamples,inputVariables,variables,tensor_properties,dimensions,dimension_length,folder,file_name))
        numConstraints.append(len(constraints))
        
        time.sleep(0.1)
        loopnum+=1
        printProgressBar(loopnum, numLoop, prefix = 'Progress:', suffix = 'Complete', length = 50)
    
    print("######################################")
    print("Sum:",sums,
          "Prod:",products,
          "Training Data Size:",len(trainExamples),
          "Number of variables:",len(trainExamples[0]))
    print("Recall:",np.mean(recall),
          "Precision:",np.mean(precision),
          "Time Taken:",np.mean(timeTaken))
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
     
        
def learn_constraints(folder,file_name,data,variables,inputVariables,sums,
                      products,negZ,negation):

    dimension_length,dimensions=findVarDim(data[0])
    slicing=0   
    tensor_properties=helper.tensor_properties(data,inputVariables,dimensions)
    
    constraints=arnold.learn(data,inputVariables,tensor_properties,
                             dimensions,dimension_length,sums,products,
                             slicing,negation,negZ)
    
    helper.createMzn(constraints,folder,file_name,inputVariables,
                     data[0],dimensions,dimension_length)

def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    # Print New Line on Complete
    if iteration == total: 
        print()


if __name__ == "__main__":
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
      default=[1,2],
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
        
        
    numLoop=5*len(args.sum)*len(args.prod)*len(args.trainSize)
    loopnum=0
    printProgressBar(loopnum, numLoop, prefix = 'Progress:', suffix = 'Complete', length = 50)
    s = time.clock()
    runExperiment(folder+args.file+'/', args.dznfile+'.dzn', args.mznfile+'.mzn', variables, inputVariables, args.num_example, args.trainSize, args.sum, args.prod, args.negation)









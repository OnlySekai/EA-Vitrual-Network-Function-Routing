from processData.getResource import PreProcessInput
from constant import constant
from processData.routing import Routing
from functools import reduce
import numpy as np
import pandas as pd

class MOEAD(object):
  def __init__(self, inputData: PreProcessInput):
    self.inputData: PreProcessInput = inputData
    self.reference = np.zeros((3,)) + np.inf
    self.F = []
    for index, individual in enumerate(inputData.individuals):
      f = self.calObjective(index)
      self.F.append(f)
      self.updateReferences(f)

  def evlateFnc(self):
    minValue = np.inf
    for index, f in enumerate(self.F):
      value = f[0]+f[1]+f[2]
      if value < minValue:
        minValue = value
        minIndex = index
        objective = f.copy()
    return minValue, minIndex, objective
  def dl(self, indexIndividual):
    routing = Routing(constant.REQUEST_10, self.inputData, indexIndividual)
    # rs = routing.aStart()
    rs = routing.dijkstart()
    assert rs != None, "Can't routing"
    # costDl = rs.g
    sumDl = (self.inputData.input.sumCostEdges + self.inputData.input.sumDelayServerNode)*routing.numberRequest
    # return costDl/sumDl
    return rs/sumDl

    
  def cs(self, indexIndividual):
    individual = self.inputData.individuals[indexIndividual]
    costCs = 0
    sumCs = 0
    for nodeId in self.inputData.serverNodeIds:
      serverStatus = self.inputData.getStatusServerNode(individual, nodeId)
      node = self.inputData.input.nodes[nodeId]
      sumCs += node.costServer
      if serverStatus.get('isActive'):
        costCs += node.costServer
    return costCs/sumCs

  def cv(self, indexIndividual):
    individual = self.inputData.individuals[indexIndividual]
    costCv = 0
    sumCv = 0
    for nodeId in self.inputData.serverNodeIds:
      serverStatus = self.inputData.getStatusServerNode(individual, nodeId)
      node = self.inputData.input.nodes[nodeId]
      for costVnf in node.costVnfs:
        sumCv += costVnf
      if serverStatus.get('isActive'):
        vnfs = [vnf for vnf in serverStatus.get('vnfs') if vnf >-1]
        for vnf in vnfs:
          cost = node.costVnfs[vnf]
          costCv += cost
    return costCv/sumCv


  def calObjective(self, indexIndividual):
    dl = self.dl(indexIndividual)
    cs = self.cs(indexIndividual)
    cv = self.cv(indexIndividual)
    return np.array([dl,cs,cv])

  def crossover(self, dad, mom):
    mid = int(len(dad)/2)
    child = list(dad[:mid])+ list(mom[mid:])
    return child

  def mutation(self, individual):
    for allenIdx, allen in enumerate(individual):
      isMutate = np.random.random() <= constant.RATE_MUTATION
      if not isMutate:
        continue
      while True:
        newValue = np.random.randint(-1, self.inputData.input.numberVnfs)
        if newValue != allen:
          break
      individual[allenIdx] = newValue
    return individual

  def updateReferences(self, objective):
    for i in range(len(self.reference)):
      self.reference[i] = min(self.reference[i], objective[i])

  def updateNeighboringSolution(self, indexIndividual):
    individual = self.inputData.individuals[indexIndividual]
    try:
      costsChild = self.calObjective(indexIndividual)
    except:
      return
    weightVectors = self.inputData.weightVectors
    neighbors = self.inputData.matrixNeighbor[indexIndividual]
    def calOptimizeFunction(costs, weightVector):
      # print(costs, self.reference, individual)
      vector = abs(costs - self.reference)
      return max([weight*cost for weight, cost in zip(weightVector, vector)])
    updatedNeighbor = []
    for index in neighbors:
        costs = self.calObjective(index)
        self.updateReferences(costs)
        fitness = calOptimizeFunction(costs, weightVectors[index])
        fitnessChild = calOptimizeFunction(costsChild, weightVectors[indexIndividual])
        if (fitnessChild < fitness):
          self.inputData.individuals[index] = self.inputData.individuals[indexIndividual]
          self.F[index] = costs
          updatedNeighbor.append(index)
    return neighbors, updatedNeighbor
  
  def execute(self, maxIter: int):
    iter = 0
    print(self.evlateFnc())
    while iter < maxIter:
      iter +=1
      numberSolutions = self.inputData.numberSolutions
      childIndex = np.random.randint(numberSolutions)
      parentIndex = np.random.choice(self.inputData.matrixNeighbor[childIndex], 2)
      mom = self.inputData.individuals[0]
      dad = self.inputData.individuals[1]
      tempChild = self.crossover(dad, mom)
      child = self.mutation(tempChild)
      oldChild = self.inputData.individuals[childIndex].copy()
      self.inputData.individuals[childIndex] = child
      self.updateNeighboringSolution(childIndex)
      self.inputData.individuals[childIndex] = oldChild
      if not iter % 50:
        print(self.evlateFnc())
    pd.DataFrame(self.inputData.individuals).to_csv('tuanRs2.csv', index=False)



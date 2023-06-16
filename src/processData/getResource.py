from constant import constant
import numpy as np
from processData.prepareInput import PrepareInput

class PreProcessInput(object):
   def __init__(self, numberSolutions, numberNeighbor):
      self.input = PrepareInput()
      self.serverNodeIds = []
      self.numberServerNode = 0
      self.individuals = []
      self.weightVectors = []
      self.matrixNeighbor = []
      self.numberSolutions =numberSolutions
      self.numberNeighbor = numberNeighbor
      self.offsetServerNode = self.input.maxVnfOnServer+1

   def initIndividuals(self):
      for id, node in self.input.nodes.items():
         if len(node.costVnfs) == 0:
            continue
         self.serverNodeIds.append(id)
         self.numberServerNode+=1
      self.individuals = np.random.randint(-1, self.input.numberVnfs, (self.numberSolutions, self.numberServerNode*self.offsetServerNode))
      print('initNeighborhoods done')

   def getStatusServerNode(self, individual, severId):
      try:
         orderServerNode = self.serverNodeIds.index(severId)
      except:
         return None
      startConfig = orderServerNode*self.offsetServerNode
      status = individual[startConfig]
      isActive = status > (self.input.numberVnfs+1)/2
      rs = {
         'isActive': isActive,
         'status': status,
         'orderServerNode': orderServerNode,
         'vnfs': individual[startConfig+1: startConfig+self.input.maxVnfOnServer+1]
      }
      return rs
      
   def getNodeHaveVnf(self, individual, typeVnf):
      orderServerNodes = []
      for serverid in self.serverNodeIds:
         serverStatus = self.getStatusServerNode(individual, serverid)
         if serverStatus and serverStatus.get('status') and typeVnf in serverStatus.get('vnfs'):
            orderServerNodes.append(serverid)
      return orderServerNodes
   
   def initWeightVectors(self):
      randomVectors = np.random.rand(self.numberSolutions, constant.NUNBER_OBJECTIVE)
      self.weightVectors=np.array([weightVector/weightVector.sum() for weightVector in randomVectors])
      print('initWeightVectors done')

   def initNeighborhoods(self):
      lenWeightVectors = len(self.weightVectors)
      def eachElement(index):
         neighborhood = []
         neighborDistance = []
         for i in range(lenWeightVectors):
            if i == index:
                continue
            distance = np.linalg.norm(self.weightVectors[index]-self.weightVectors[i])
            if len(neighborhood) < self.numberNeighbor:
                neighborDistance.append(distance)
                neighborhood.append(i)
            else:
                longestNeighbor = np.argmax(neighborDistance)
                if (distance<neighborDistance[longestNeighbor]):
                    del neighborDistance[longestNeighbor]
                    del neighborhood[longestNeighbor]
                    neighborDistance.append(distance)
                    neighborhood.append(i)
         return neighborhood
      for i in range(lenWeightVectors):
         self.matrixNeighbor.append(eachElement(i))
      print('initNeighborhoods done')

   

# a = PreProcessInput(10, 5)

# a.initWeightVectors()
# print(a.weightVectors)
# a.initNeighborhoods()
# print(a.matrixNeighbor)
# a.initIndividuals()
# # print(a.individuals)
# print(a.getStatusServerNode(a.individuals[0], 17))
      

      
         


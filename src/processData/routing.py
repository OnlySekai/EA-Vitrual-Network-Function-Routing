from constant import constant
from processData.getResource import PreProcessInput
from collections import Counter
from typing import Dict
from dijkstar import Graph
import copy
import os
      

class RouteState(object):
   def __init__(self, path: list, requreidVnfs: list, graph:Graph,  g=0, h=0):
      self.path: list = path
      self.requiredVnfs: list =requreidVnfs
      self.g =g
      self.h = h
      self.limitBandwidth: Dict(tuple, int) = {}
      self.limitMem: Dict(int, int) = {}
      self.limitCpu: Dict(int, int) = {}
      self.graph: Graph = graph

class Routing(object):
    def __init__(self, fileName, input: PreProcessInput, indexSolution):
      inputFile = open(os.getcwd() + '/../dataset/' + constant.NAME_DATA_SET + '/' + fileName, 'r')
      lines =inputFile.readlines()
      self.numberRequest = int(lines[0].split(' ')[0])
      self.input = input
      self.indexSolution = indexSolution
      self.individual = input.individuals[indexSolution]
      self.requests = []
      self.minEdge = input.input.minEdgeCost
      garph = copy.deepcopy(self.input.input.graph)
      self.initState = RouteState([], [], garph)
      self.CAP_MAX = 0
      self.MEM_MAX = 0
      self.CPU_MAX = 0
      self.minCpu = constant.INFINITY
      self.minMem = constant.INFINITY

      limitMem: Dict(int, int) = self.initState.limitMem
      limitCpu: Dict(int, int) = self.initState.limitCpu
      for raw in lines[1:self.numberRequest+1]:
        line =raw.split(' ')
        request = {
           'bandwidth': int(line[constant.BANDWIDTH_INDEX]),
           'memory': int(line[constant.MEMORY_INDEX]),
           'cpu': int(line[constant.CPU_INDEX]),
           'startRequest': int(line[constant.START_REQUEST]),
           'endRequest': int(line[constant.END_REQUEST]),
           'numberVnfs': int(line[constant.NUMBER_VNF]),
           'vnfs': [int(vnf) for vnf in line[constant.NUMBER_VNF+1:]]
          }
        self.CAP_MAX += request.get('bandwidth') * (request.get('numberVnfs')+1)
        self.MEM_MAX += request.get('memory') * (request.get('numberVnfs')+1)
        self.minMem = min(self.minMem,request.get('memory'))
        self.CPU_MAX += request.get('cpu') * (request.get('numberVnfs')+1)
        self.minCpu = min(self.minCpu,request.get('cpu'))
        requiredVnfs: list = copy.deepcopy(request.get('vnfs'))

        # if start node have required VNF, process it
        limitMem[request.get('startRequest')] = 0
        startNode = self.input.getStatusServerNode(self.individual, request.get('startRequest'))
        if startNode:
          limitCpu[request.get('startRequest')] = 0
          while len(requiredVnfs):
            nextVnf = requiredVnfs[0]
            if nextVnf in startNode.get('vnfs'):
              limitCpu[request.get('startRequest')] += request.get('cpu')
              requiredVnfs.pop(0)
            else:
              break
        else:
          limitMem[request.get('startRequest')]+=request.get('memory')
        h = self.calEstimate(self.initState.graph, request['startRequest'], request['endRequest'], requiredVnfs, {}, request['cpu'])
        if h==-1:
          self.initState.h = -1
          break
        self.initState.h+= h
        self.initState.requiredVnfs.append(requiredVnfs)
        self.initState.path.append([request.get('startRequest')])
        self.requests.append(request)

    def isCompleteRequest(self, path, requiredVnfs, request):
       endNode = request.get('endRequest')
       lastNode = path[-1]
       return len(requiredVnfs) ==0 and  endNode == lastNode
    
    def isEndState(self, state: RouteState):
      status = True
      for index, request in enumerate(self.requests):
          if not status:
             break
          status = status and self.isCompleteRequest(state.path[index], state.requiredVnfs[index], request)
      return status
    
    def calEstimate(self, garph: Graph, startNode, endNode, requiredVnfs, limitCpu, cpu):
      if not len(requiredVnfs):
        pathToEnd = self.input.input.shortestPath(garph, startNode, endNode)
        if pathToEnd == None:
          return -1
        costToEnd = pathToEnd.total_cost
        return costToEnd
      
      cloneRequiredVnfs = copy.deepcopy(requiredVnfs)
      typeVnf = cloneRequiredVnfs.pop(0)
      nodesHaveVnf = self.input.getNodeHaveVnf(self.individual, typeVnf)
      minPath = constant.INFINITY
      for node in nodesHaveVnf:
        usageCpu = 0
        if limitCpu.get(node):
          usageCpu=limitCpu.get(node)
        if usageCpu+cpu > self.CPU_MAX:
          continue

        pathToNextVnf = self.input.input.shortestPath(garph, startNode, node)
        if pathToNextVnf == None:
          continue

        leftCost = self.calEstimate(garph, node, endNode, cloneRequiredVnfs, limitCpu, cpu)
        if leftCost == -1:
          continue

        costToNextVnf = pathToNextVnf.total_cost
        minPath = min(minPath, costToNextVnf+leftCost)
      if minPath == constant.INFINITY:
        return -1
      return minPath
      

    
    def calHeuCost(self, state:RouteState):
       return state.g +state.h

    def generateNextStage(self, parentStage: RouteState, requestOrder: int, stageStore: list):
      if requestOrder >= len(self.requests):
        indexNumber = self.insertState(stageStore, self.calHeuCost(parentStage), 0, len(stageStore)-1)
        stageStore.insert(indexNumber, parentStage)
        return

      if self.isCompleteRequest(parentStage.path[requestOrder], parentStage.requiredVnfs[requestOrder], self.requests[requestOrder]):
        self.generateNextStage(parentStage, requestOrder+1, stageStore)
        return
      
      currentNodeId = parentStage.path[requestOrder][-1]
      currentGraph: Graph = copy.deepcopy(parentStage.graph)
      edges = copy.deepcopy(self.input.input.getNodeDijit(currentGraph, currentNodeId)).items()
      if not edges: return
      for target, cost in edges:
        currentStage: RouteState = copy.deepcopy(parentStage)
        currentStage.graph = currentGraph

        path = currentStage.path[requestOrder]
        if len(path) > 2 and path[-2] == target:
          continue
        path.append(target)
        mostCommon = Counter([node for path in currentStage.path for node in path]).most_common(1)[0][1] 
        if mostCommon> len(self.requests)+1:
          continue
        request = self.requests[requestOrder]

        
        #update bandwidth
        limitBandwidth= currentStage.limitBandwidth
        edge = path[-2:]
        edge.sort()
        edgeTuple = tuple(edge)
        if limitBandwidth.get(edgeTuple):
          limitBandwidth[edgeTuple] += request.get('bandwidth')
        else:
          limitBandwidth[edgeTuple] = request.get('bandwidth') 
        if limitBandwidth[edgeTuple] > self.CAP_MAX:
          continue
        if limitBandwidth[edgeTuple] + self.minEdge > self.CAP_MAX:
          if self.input.input.getEdge(currentStage.graph, edge[0], edge[1]): currentStage.graph.remove_edge(edge[0], edge[1])
          if self.input.input.getEdge(currentStage.graph, edge[1], edge[0]): currentStage.graph.remove_edge(edge[1], edge[0])
        
        serverStatus  = self.input.getStatusServerNode(self.individual, target)
        requiredVnfs = currentStage.requiredVnfs[requestOrder]
        limitCpu = currentStage.limitCpu
        limitMem = currentStage.limitMem

        if serverStatus:
          if not serverStatus.get('status'):
            if self.input.input.getNodeDijit(currentStage.graph, target): currentStage.graph.remove_node(target)
            continue
          if len(requiredVnfs):
            nextVnf = requiredVnfs[0]
            serverVnf = serverStatus.get('vnfs')
            while nextVnf in serverVnf:
              if not limitCpu.get(target):
                limitCpu[target] = request.get('cpu')
              else:
                if limitCpu[target]+request.get('cpu') < self.CPU_MAX:
                  break
                limitCpu[target] +=request.get('cpu')
              requiredVnfs.pop(0)
              if not len(requiredVnfs):
                break
              nextVnf = requiredVnfs[0]
        else:
          memory = request.get('memory')
          if not limitMem.get(target):
            limitMem[target] =0
          limitMem[target] += memory
          if limitMem[target] > self.MEM_MAX:
            continue
          if limitMem[target] +self.minMem > self.MEM_MAX:
            self.input.input.removeNodeDijit(currentStage.graph, target)
    
        currentStage.g += cost
        estimateCost = self.calEstimate(currentStage.graph,target, request.get('endRequest'), requiredVnfs, limitCpu, request.get('cpu'))
        if estimateCost == -1:
          continue
        currentStage.h += estimateCost
        self.generateNextStage(currentStage, requestOrder+1, stageStore)   

    def insertState(self, arr: list=[], heuCost =0, start=0, end=-1):
      if len(arr) == 0:
        return 0
      mid = int((start + end)/2)
      f = self.calHeuCost(arr[mid])
      if (start == mid):
        if f<heuCost:
          return mid+1
        else:
          if mid == 0:
            return 0
          return mid -1
      if f>heuCost:
         return self.insertState(arr, heuCost, start, mid)
      return self.insertState(arr, heuCost, mid, end)

    def aStart(self):
      if self.initState.h == -1:
        return
      stateStore = [self.initState]
      while (len(stateStore)):
        state = stateStore.pop(0)
        if self.isEndState(state):
          return state
        print('space state ',len(stateStore), ' leftVnfs ',len(state.requiredVnfs))
        state.h = 0
        self.generateNextStage(state, 0, stateStore)
        
        
        

        


# a = Routing('request10.txt')
# print(a.requests)
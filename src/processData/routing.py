from constant import constant
from processData.getResource import PreProcessInput
from collections import Counter
from typing import Dict
import numpy as np
from dijkstar import Graph
from processData.dfs import DFS
import copy
import os
import threading
      

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
      inputFile = open(os.getcwd() + '/dataset/' + constant.NAME_DATA_SET + '/' + fileName, 'r')
      lines =inputFile.readlines()
      self.numberRequest = int(lines[0].split(' ')[0])
      self.input = input
      self.indexSolution = indexSolution
      self.individual = input.individuals[indexSolution]
      self.requests = []
      self.minEdge = input.input.minEdgeCost
      graph = copy.deepcopy(self.input.input.graph)
      self.initState = RouteState([], [], graph)
      self.CAP_MAX = 0
      self.MEM_MAX = 0
      self.CPU_MAX = 0
      self.minCpu = constant.INFINITY
      self.minMem = constant.INFINITY
      self.dfs = DFS(input, indexSolution)


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
          assert startNode.get('isActive'), 'node start {} must active'.format(request.get('startRequest'))
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
        assert h != -1, 'not have route {}'.format(request.get('startRequest'))
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
          isCompleteRequest = self.isCompleteRequest(state.path[index], state.requiredVnfs[index], request)
          status = status and isCompleteRequest
      return status
    
    def calEstimate(self, graph: Graph, startNode, endNode, requiredVnfs, limitCpu, cpu, usageIn = ''):
      if not len(requiredVnfs):
        pathToEnd = self.input.input.shortestPath(graph, startNode, endNode)
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

        pathToNextVnf = self.input.input.shortestPath(graph, startNode, node)
        if pathToNextVnf == None:
          continue

        leftCost = self.calEstimate(graph, node, endNode, cloneRequiredVnfs, limitCpu, cpu)
        if leftCost == -1:
          continue

        costToNextVnf = pathToNextVnf.total_cost
        delayProcessInNode = self.input.input.nodes[node].nodeDelay
        minPath = min(minPath, costToNextVnf+leftCost+delayProcessInNode)
      if minPath == constant.INFINITY:
        return -1
      return minPath
    
    def calHeuCost(self, state:RouteState):
       return state.g +state.h

    def generateNextStage(self, parentStage: RouteState, requestOrder: int, stageStore: list):
      if requestOrder >= len(self.requests):
        # indexNumber = self.insertState(stageStore, self.calHeuCost(parentStage), 0, len(stageStore)-1)
        # stageStore.insert(indexNumber, parentStage)
        stageStore.append(parentStage)
        return
      if self.isCompleteRequest(parentStage.path[requestOrder], parentStage.requiredVnfs[requestOrder], self.requests[requestOrder]):
        self.generateNextStage(parentStage, requestOrder+1, stageStore)
        return
      
      currentNodeId = parentStage.path[requestOrder][-1]
      request = self.requests[requestOrder]
      nextNodes = [request.get('endRequest')]
      requiredVnfs = parentStage.requiredVnfs[requestOrder]
      nextVnf = None
      if len(requiredVnfs):
        nextVnf = requiredVnfs.pop(0)
        nextNodes = self.input.getNodeHaveVnf(self.individual, nextVnf)
      if not len(nextNodes):
        return
      
      # currentGraph: Graph = copy.deepcopy(parentStage.graph)
      arrThread = []

      for target in nextNodes:
        # currentStage: RouteState = copy.deepcopy(parentStage)
        # currentStage.graph = currentGraph
        pathsByDfs =[]
        self.dfs.visited = {}
        self.dfs.state = []
        self.dfs.dfs(self.initState.graph, currentNodeId, target,request.get('memory'), request.get('bandwidth'), parentStage.limitMem, parentStage.limitBandwidth, self.MEM_MAX, self.CAP_MAX, pathsByDfs)
        if not len(pathsByDfs):
          continue
        for pathByDfs in pathsByDfs:
          cost = 0
          if not len(pathByDfs):
            continue
          currentStage: RouteState = copy.deepcopy(parentStage)
          limitCpu = currentStage.limitCpu
          usageCpu = limitCpu.get(target)
          if usageCpu:
            limitCpu[target] += request.get('cpu')
          else:
            limitCpu[target] = request.get('cpu')
          if limitCpu[target] > self.CPU_MAX:
            limitCpu[target] -= request.get('cpu')
            continue
          isLimit = False

          for index, nextNode in enumerate(pathByDfs):
            if nextNode == target:
              continue
            edge = [nextNode, pathByDfs[index+1]]
            edge.sort()
            edgeTuple = tuple(edge)
            
            limitBandwidth = currentStage.limitBandwidth
            if limitBandwidth.get(edgeTuple):
              limitBandwidth[edgeTuple] += request.get('bandwidth')
            else:
              limitBandwidth[edgeTuple] = request.get('bandwidth')
            if limitBandwidth[edgeTuple] > self.CAP_MAX:
              isLimit = True
              limitBandwidth[edgeTuple] -= request.get('bandwidth')
              break
            cost += self.initState.graph.get_edge(nextNode, pathByDfs[index+1])
    
            if index ==0:
              continue
            serverStatus = self.input.getStatusServerNode(self.individual, nextNode)
            if not serverStatus:
              limitMem = currentStage.limitMem
              if limitMem.get(nextNode):
                limitMem[nextNode] += request.get('memory')
              else:
                limitMem[nextNode] = request.get('memory')
              if limitMem[nextNode] > self.MEM_MAX:
                isLimit = True
                limitMem[nextNode] -=request.get('memory')
                break
          if isLimit:
            continue
          h = self.calEstimate(self.initState.graph, target, request.get('endRequest'), requiredVnfs, currentStage.limitCpu,request.get('cpu'), usageIn='genState')
          if h == -1:
            continue
          currentStage.g+= cost
          if nextVnf != None:
            target = pathByDfs[-1]
            costDelay = self.input.input.nodes[target].nodeDelay
            currentStage.g += costDelay
          currentStage.h = h
          currentStage.path[requestOrder].pop()
          currentStage.path[requestOrder].extend(pathByDfs)
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

    def dijkstart(self):
      g =0
      for request in self.requests:
        cost = self.calEstimate(self.initState.graph, request.get('startRequest'), request.get('endRequest'), request.get('vnfs'), {}, 0)
        if cost == -1:
          return None
        g += cost
      return g

    def aStart(self):
      assert self.initState.h != -1, 'init state estimate can\'t be -1'
      iter = 0
      stateStore = [self.initState]
      while (len(stateStore)):
        queue = []
        state = stateStore.pop(0)
        if self.isEndState(state):
          return state
        # print('space state ',len(stateStore), ' leftVnfs ',len(state.requiredVnfs))
        state.h = 0
        self.generateNextStage(state, 0, queue)
        iter +=1
        for state in queue:
          indexNumber = self.insertState(stateStore, self.calHeuCost(state), 0, len(stateStore)-1)
          stateStore.insert(indexNumber, state)
        # if not iter%50:
        #   print(iter, ': currentStage: \n', state.__dict__, '\n space size: ', len(stateStore), '\n --------------------------------')
          # if iter in [1,2]:
          #   input("Press Enter to continue...")
        
        
        

        


# a = Routing('request10.txt')
# print(a.requests)
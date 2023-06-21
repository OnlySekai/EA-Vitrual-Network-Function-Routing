from processData.getResource import PreProcessInput
import copy
class DFS(object):
    def __init__(self, input: PreProcessInput, indexInvidual):
      self.preProcessInput: PreProcessInput = input
      self.input = input.input
      self.state = []
      self.visited = {}
      self.invidual = input.individuals[indexInvidual]
    def dfs(self, graph, start, end, mem, bandwidth, limitMem, limitBandwidth, maxMem, maxBandwidth, store):
      self.state.append(start)
      self.visited[start] = True
      shortestpath = self.input.shortestPath(graph, start, end)
      if not shortestpath:
        return
          
      if start == end:
        store.append(copy.deepcopy(self.state))
        return
      
      for nextNode in self.input.nodes[start].edges.keys():
        if self.visited.get(nextNode):
          continue
        nodeStatus = self.preProcessInput.getStatusServerNode(self.invidual, nextNode)
        usageMem = limitMem.get(nextNode)
        if nodeStatus:
          if not nodeStatus.get('isActive'):
            continue
        else:
          if usageMem and usageMem+ mem > maxMem:
            continue


        edge = [start, nextNode]
        edge.sort()
        edgeTuple = tuple(edge)

        usageBandwidth = limitBandwidth.get(edgeTuple)
        if usageBandwidth and usageBandwidth + bandwidth > maxBandwidth:
          continue

        if usageBandwidth:
          limitBandwidth[edgeTuple] += bandwidth
        else:
          limitBandwidth[edgeTuple] = bandwidth
        if not nodeStatus:
          if usageMem:
            limitMem[nextNode] +=mem
          else:
            limitMem[nextNode] =mem
        self.dfs(graph, nextNode, end, mem, bandwidth, limitMem, limitBandwidth, maxMem, maxBandwidth,store)
        limitBandwidth[edgeTuple]-= bandwidth
        if not nodeStatus:
          limitMem[nextNode] -=mem
        self.visited[nextNode] =False
        self.state.pop() 
      

      
      
from constant import constant
from processData.node import Node
from typing import Dict
from functools import reduce
from dijkstar import Graph, find_path
import os

class PrepareInput(object):
   def __init__(self):
      inputFile = open(os.getcwd() + '/dataset/'+ constant.NAME_DATA_SET +'/' + constant.INPUT, 'r')
      lines =inputFile.readlines()
   
      vnfInfo = lines[constant.LINE_VNF].split(' ')
      self.numberVnfs = int(vnfInfo[constant.VNF_NUMBER_INDEX])
      self.maxVnfOnServer = int(vnfInfo[constant.MAX_VNF_INDEX])
      self.nodeNumber = int(lines[constant.LINE_NODE_NUMBER])
      self.minEdgeCost = constant.INFINITY
      self.nodes: Dict[int, Node] = {}
      self.graph = Graph()
      self.sumDelayServerNode = 0
      self.sumCostServerNode = 0
      self.sumCostVnfs = 0
      self.sumCostEdges = 0
      INDEX_EDGE_NUMBER = constant.LINE_NODE_NUMBER +self.nodeNumber +1
      def initNode():
         for i in range(constant.LINE_NODE_NUMBER+1, INDEX_EDGE_NUMBER):
            nodeConfig = lines[i].split(' ')
            nodeId = int(nodeConfig[constant.INDEX_ID])
            nodeDelay = int(nodeConfig[constant.INDEX_DELAY])
            costServer = int(nodeConfig[constant.INDEX_COST_SERVER])
            costVnfs = []
            if costServer >0:
               costVnfs = [int(i) for i in nodeConfig[-self.numberVnfs:]]
               sumCostVnfs = reduce(lambda a,b: a+b, costVnfs, 0)
               self.sumCostVnfs += sumCostVnfs
               self.sumDelayServerNode += nodeDelay
               self.sumCostServerNode += costServer
               
            self.nodes[nodeId] = Node(nodeDelay, costServer, costVnfs)
      initNode()
         
      def initEdge():
         for i in range(INDEX_EDGE_NUMBER+1, len(lines)):
            edgeConfig = lines[i].split(' ')
            u = int(edgeConfig[0])
            v= int(edgeConfig[1])
            cost = int(edgeConfig[2])
            self.sumCostEdges += cost
            self.minEdgeCost = min(cost, self.minEdgeCost)
            edgesU = self.nodes.get(u).edges
            edgesU[v] = cost
            self.graph.add_edge(v, u, cost)
            edgesV = self.nodes.get(v).edges
            edgesV[u] =cost
            self.graph.add_edge(u, v, cost)
      initEdge()

   def getNodeDijit(self, graph: Graph, node):
      try:
         return graph.get_node(node)
      except:
         return None
      
   def removeNodeDijit(self, graph: Graph, node):
      try:
         return graph.remove_node(node)
      except:
         return None
      
   def getEdge(self, graph: Graph, nodeA, nodeB):
      try:
         return graph.get_edge(nodeA, nodeB)
      except:
         return None
      
   def shortestPath(self, graph: Graph, nodeA, nodeB):
      try:
         return find_path(graph, nodeA, nodeB)
      except:
         return None
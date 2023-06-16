from typing import Dict

class Node(object):
   def __init__(self, nodeDelay, costServer, costVnfs = []):
      self.nodeDelay =nodeDelay
      self.costServer =costServer
      self.costVnfs: list =costVnfs
      self.edges: Dict[int, int] = {}
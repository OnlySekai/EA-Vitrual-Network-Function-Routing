from processData.getResource import PreProcessInput
from processData.routing import Routing
from constant import constant
inputData = PreProcessInput(constant.NUMBER_SOLUTION, 4)


inputData.initIndividuals()
# print(inputData.individuals)

# inputData.initWeightVectors()
# # print(inputData.weightVectors)

# inputData.initNeighborhoods()
# print(inputData.matrixNeighbor)

routing = Routing(constant.REQUEST_10, inputData, 0)
a = routing.aStart()
print('----------------------------')
if not a:
    print(routing.individual)
else: print(a.__dict__)

# from dijkstar import Graph, find_path

# g = Graph()

# # g.add_edge('A', 'B', 2)
# # g.add_edge('B', 'A', 2)
# # g.add_edge('A', 'C', 4)
# # g.add_edge('B', 'C', 1)
# # g.add_edge('B', 'D', 7)
# # g.add_edge('C', 'D', 3)
# # g.add_edge('E', 'A', 10)

# g.add_edge('A', 'B', 3)
# g.add_edge('E', 'G', 3)
# g.add_edge('E', 'B', 10)
# a = find_path(g, 'E', 'B')
# print(a)

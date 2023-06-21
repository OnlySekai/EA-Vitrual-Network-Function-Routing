from processData.getResource import PreProcessInput
from processData.routing import Routing
from constant import constant
from processData.dfs import DFS

done = False
while (not done):
    try:
        inputData = PreProcessInput(1, 4)
        inputData.initIndividuals()
        routing = Routing(constant.REQUEST_10, inputData, 0)
        a = routing.aStart()
    except Exception as e:
        print(e)
    else:
        if a != None: done = True
print(a)
# store = []
# dfs = DFS(inputData.input)

# dfs.dfs(25,94, store)
# print(len(store))

# inputData.initIndividuals()
# inputData.individuals = [
#    [ 1,  9,  7,  4,  4,  9,  1,  9,  3,  9,  6,  8,  6,  3,  6,  4,  1,
#         5,  3,  1,  2,  1,  0,  9,  5,  9,  8,  1,  6,  9,  7,  8,  0,  4,
#         3,  6,  8,  3, -1,  4,  1,  2,  1,  2,  4,  3,  0,  2,  5,  0,  4,
#         2,  2,  2,  8,  6,  5,  8,  3,  0]
# ]
# print(inputData.individuals)

# # inputData.initWeightVectors()
# # # print(inputData.weightVectors)

# # inputData.initNeighborhoods()
# # print(inputData.matrixNeighbor)

# routing = Routing(constant.REQUEST_10, inputData, 0)
# a = routing.aStart()
# # routing.resetInds()
# print('----------------------------')
# if not a:
#     print(routing.individual)
# else: print(a.__dict__)

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

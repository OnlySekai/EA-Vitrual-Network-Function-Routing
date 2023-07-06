from processData.getResource import PreProcessInput
from processData.routing import Routing
from constant import constant
from processData.dfs import DFS
from moead.MOEAD import MOEAD
import pandas as pd
import os

def initIndividuals():
    print(constant.SELECT_REQUEST,constant.NAME_DATA_SET)
    done = False
    individuals = []
    while (not done):
        try:
            inputData = PreProcessInput(1, 4)
            inputData.initIndividuals()
            routing = Routing(constant.SELECT_REQUEST, inputData, 0)
            a = routing.dijkstart()
            if a:
                a= list(inputData.individuals[0])
                if not a in individuals:
                    individuals.append(a)
                    if not len(individuals)% 10:
                        print('numberIndividual: ', len(individuals))
        except Exception as e:
            print(e)
            continue
        else:
            if len(individuals) == constant.NUMBER_SOLUTION:
                done =True
    pathDataset = "/root/vnf-routing/init/{}".format(constant.NAME_DATA_SET)
    if not os.path.exists(pathDataset):
        os.makedirs(pathDataset)
    pd.DataFrame(individuals).to_csv('/root/vnf-routing/init/{}/{}.csv'.format(constant.NAME_DATA_SET, constant.SELECT_REQUEST), index=False)

def run():
    inputData = PreProcessInput(constant.NUMBER_SOLUTION, constant.NUMBER_NEIGHBOR)
    inputData.initIndividuals()
    inputData.initWeightVectors()
    inputData.initNeighborhoods()
    df = pd.read_csv('/root/vnf-routing/init/{}/{}.csv'.format(constant.NAME_DATA_SET, constant.SELECT_REQUEST))
    lst = df.to_numpy()
    inputData.individuals = lst
    # routing = Routing(constant.REQUEST_10, inputData, 5)
    # a = routing.aStart()
    # print('CAP: {}, CPU: {}, MEM: {}'.format(routing.CAP_MAX, routing.CPU_MAX, routing.MEM_MAX))
    # print(a.__dict__)
    modad = MOEAD(inputData)
    modad.execute(5000)
# initIndividuals()
# run()

def main():
    pathDataset = "/root/vnf-routing/dataset"
    pathRs = "/root/vnf-routing/rs"
    directories = [d for d in os.listdir(pathDataset)]
    requests = [constant.REQUEST_10]
    # blackList = [ 'nsf_rural_2',  'cogent_center_4', 'cogent_center_3']
    for directory in directories:
        # if directory in blackList:
        #     continue
        constant.NAME_DATA_SET = directory
        for request in requests:
            constant.SELECT_REQUEST = request
            if os.path.exists('{}/{}/{}.csv'.format(pathRs, constant.NAME_DATA_SET, constant.SELECT_REQUEST)):
                continue
            initIndividuals()
            run()
main()
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

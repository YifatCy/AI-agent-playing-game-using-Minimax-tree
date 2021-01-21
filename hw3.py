import random
import time
from copy import deepcopy
from itertools import product
import main

ids = ['Me']


def combinations(array, tuple_length, prev_array=None):
    if prev_array is None:
        prev_array = []
    if len(prev_array) == tuple_length:
        return [prev_array]
    combs = []
    for i, val in enumerate(array):
        prev_array_extended = prev_array.copy()
        prev_array_extended.append(val)
        combs += combinations(array[i + 1:], tuple_length, prev_array_extended)
    return combs


def all_actions(state, zoc):
    vaccinateList = []
    quarantineList = []
    vaccinateListFull = []
    quarantineListFull = []
    rowsNum = len(state)
    colsNum = len(state[0])

    for (row, col) in zoc:
        if state[row][col] == 'H':
            vaccinateListFull.append(("vaccinate", (row, col)))
            if row - 1 >= 0:
                if 'S' in state[row - 1][col]:
                    vaccinateList.append(("vaccinate", (row, col)))
                    continue
            if row + 1 <= rowsNum - 1:
                if 'S' in state[row + 1][col]:
                    vaccinateList.append(("vaccinate", (row, col)))
                    continue
            if col - 1 >= 0:
                if 'S' in state[row][col - 1]:
                    vaccinateList.append(("vaccinate", (row, col)))
                    continue
            if col + 1 <= colsNum - 1:
                if 'S' in state[row][col + 1]:
                    vaccinateList.append(("vaccinate", (row, col)))
                    continue

        elif 'S' in state[row][col]:
            quarantineListFull.append(("quarantine", (row, col)))
            if row - 1 >= 0:
                if 'H' in state[row - 1][col]:
                    quarantineList.append(("quarantine", (row, col)))
                    continue
            if row + 1 <= rowsNum - 1:
                if 'H' in state[row + 1][col]:
                    quarantineList.append(("quarantine", (row, col)))
                    continue
            if col - 1 >= 0:
                if 'H' in state[row][col - 1]:
                    quarantineList.append(("quarantine", (row, col)))
                    continue
            if col + 1 <= colsNum - 1:
                if 'H' in state[row][col + 1]:
                    quarantineList.append(("quarantine", (row, col)))
                    continue

            # quarantineList.append(("quarantine", (row, col)))

    allCombinations = []

    if not vaccinateList and not quarantineList:
        if len(vaccinateListFull) > 5:
            vaccinateListFull1 = random.sample(vaccinateListFull, 5)
            print("1")
            for vaccinate in vaccinateListFull1:
                allCombinations.append([vaccinate])
            return allCombinations
        elif quarantineListFull:
            if len(quarantineList) > 5:
                quarantineListFull1 = random.sample(quarantineListFull, 5)
            print("2")
            for quarantine in quarantineListFull1:
                allCombinations.append([quarantine])
            return allCombinations
        else:
            print("3")
            return []

    elif not vaccinateList:
        if vaccinateListFull:
            if len(vaccinateListFull) > 5:
                vaccinateListFull1 = random.sample(vaccinateListFull, 5)
            vaccinateList = vaccinateListFull1
        else:
            for quarantine in quarantineList:
                allCombinations.append([quarantine])
            return allCombinations

    elif not quarantineList:
        for vaccinate in vaccinateList:
            allCombinations.append([vaccinate])
        return allCombinations


    for vaccinate in vaccinateList:
        allCombinations.append([vaccinate])

    list_one = [i for i in product(vaccinateList, quarantineList)]
    allCombinations.extend(list_one)

    list_two_temp = [i for i in combinations(quarantineList, 2)]
    list_two = [i for i in product(vaccinateList, list_two_temp)]
    list_two = [(i[0], i[1][0], i[1][1]) for i in list_two]
    allCombinations.extend(list_two)

    allCombinations = [list(i) for i in allCombinations]
    #print(len(allCombinations))
    return allCombinations


def apply_actions(state, actions):
    new_state = deepcopy(state)
    for atomic_action in actions:
        # print('atomic_action', atomic_action)
        effect, location = atomic_action[0], (atomic_action[1][0], atomic_action[1][1])
        row = location[0]
        col = location[1]
        if 'v' in effect:
            new_state[row][col] = 'I'
        else:
            new_state[row][col] = 'Q0'
    return new_state


def change_state(state):
    rowsNum = len(state)
    colsNum = len(state[0])
    new_state = deepcopy(state)
    #print(new_state)
    # virus spread
    for i in range(1, rowsNum):
        for j in range(1, colsNum):
            if state[i][j] == 'H':
                if i - 1 >= 0:
                    if 'S' in state[i - 1][j]:
                        new_state[i][j] = 'S0'
                if i + 1 <= rowsNum - 1:
                    if 'S' in state[i + 1][j]:
                        new_state[i][j] = 'S0'
                if j - 1 >= 0:
                    if 'S' in state[i][j - 1]:
                        new_state[i][j] = 'S0'
                if j + 1 <= colsNum - 1:
                    if 'S' in state[i][j + 1]:
                        new_state[i][j] = 'S0'

    # advancing sick counters
    for i in range(1, rowsNum):
        for j in range(1, colsNum):
            if 'S' in state[i][j]:
                if len(state[i][j]) > 1:
                    turnS = int(state[i][j][1])
                else:
                    turnS = 0

                if turnS < 3:
                    new_state[i][j] = 'S' + str(turnS + 1)
                else:
                    new_state[i][j] = 'H'

            # advancing quarantine counters
            elif 'Q' in state[i][j]:
                if len(state[i][j]) > 1:
                    turnQ = int(state[i][j][1])
                else:
                    turnQ = 0

                if turnQ < 2:
                    new_state[i][j] = 'Q' + str(turnQ + 1)
                else:
                    new_state[i][j] = 'H'
    return new_state


def allPossibleChildrenFromState(state, zoc):
    allPossibleChildStatesList = {}

    allActions = all_actions(state, zoc)
    #print('num of allActions:', len(allActions))

    for actions in allActions:
        stateAfterActions = apply_actions(state, actions)
        allPossibleChildStatesList[tuple(actions)] = stateAfterActions

    return allPossibleChildStatesList


def eval_state(state, zoc):
    """ returns my point minus rival's points """
    myPoints = 0
    rivalPoints = 0
    for row in range(len(state)):
        for col in range(len(state[row])):
            if state[row][col] == 'H' or state[row][col] == 'I':
                if (row, col) in zoc:
                    myPoints = myPoints + 1
                else:
                    rivalPoints = rivalPoints + 1
            elif 'S' in state[row][col]:
                if (row, col) in zoc:
                    myPoints = myPoints - 1
                else:
                    rivalPoints = rivalPoints - 1
            elif 'Q' in state[row][col]:
                if (row, col) in zoc:
                    myPoints = myPoints - 5
                else:
                    rivalPoints = rivalPoints - 5
    return myPoints - rivalPoints


def miniMax(state, zoc, notZoc, order, depth, alpha, beta, maximizingPlayer, action_org):
    posInfinity = float('inf')
    negInfinity = float('-inf')
    best_child = state
    best_action = action_org
    if depth == 0:
        return eval_state(state, zoc), state, action_org

    if maximizingPlayer and order == 'first':
        maxEval = negInfinity
        allMaxPlayerChildren = allPossibleChildrenFromState(state, zoc)
        #print('len(All max players children when Im first)', len(allMaxPlayerChildren))
        best_val = maxEval
        if not allMaxPlayerChildren:
            return maxEval,allMaxPlayerChildren,action_org
        for actions, child in allMaxPlayerChildren.items():
            #print("in max first")
            GrandchildVal, grandChild, GChildAction = miniMax(child, zoc, notZoc, order, depth - 1, alpha, beta, False,actions)
            best_val, best_child, best_action = max_child_and_val(child, maxEval, actions, grandChild, GrandchildVal, GChildAction)
            #best_val,best_child = max_child_and_val(child, maxEval, grandChild, GrandchildVal)
            #maxEval = max(maxEval, GrandchildVal)
            alpha = max(alpha, GrandchildVal)
            if beta <= alpha:
                break
        return best_val, best_child, best_action

    elif maximizingPlayer and order == 'second':
        maxEval = negInfinity
        allMaxPlayerChildren = allPossibleChildrenFromState(state, zoc)
        #print('len(All max players children when Im second)', len(allMaxPlayerChildren))
        best_val = maxEval
        if not allMaxPlayerChildren:
            return maxEval,allMaxPlayerChildren,action_org
        for actions, child in allMaxPlayerChildren.items():
            #print("in max second")
            childAfterChange = change_state(child)
            GrandchildVal, grandChild, GChildAction = miniMax(childAfterChange, zoc, notZoc, order, depth - 1, alpha, beta, False, actions)
            #maxEval = max(maxEval, GrandchildVal)
            best_val, best_child, best_action = max_child_and_val(childAfterChange, maxEval,actions, grandChild, GrandchildVal,GChildAction)
            alpha = max(alpha, GrandchildVal)
            if beta <= alpha:
                break
        return best_val, best_child, best_action

    elif not maximizingPlayer and order == 'second':  # rival is first
        minEval = posInfinity
        allMinPlayerChildren = allPossibleChildrenFromState(state, notZoc)
        #print('len(allMinPlayerChildren when Im second)', len(allMinPlayerChildren))
        best_val = minEval
        if not allMinPlayerChildren:
            return minEval,allMinPlayerChildren,action_org
        for actions, child in allMinPlayerChildren.items():
            #print("in min second")
            GrandchildVal,grandChild,GChildAction = miniMax(child, zoc, notZoc, order, depth - 1, alpha, beta, True,actions)
            #minEval = min(minEval, GrandchildVal)
            best_val,best_child,best_action = min_child_and_val(child,minEval,actions,grandChild,GrandchildVal,GChildAction)
            beta = min(beta, GrandchildVal)
            if beta <= alpha:
                break
        return best_val, best_child, action_org

    elif not maximizingPlayer and order == 'first':  # rival is second
        minEval = posInfinity
        allMinPlayerChildren = allPossibleChildrenFromState(state, notZoc)
        #print('len(allMinPlayerChildren when Im first)', len(allMinPlayerChildren))
        best_val = minEval
        if not allMinPlayerChildren:
            return minEval,allMinPlayerChildren,action_org
        for actions, child in allMinPlayerChildren.items():
            #print("in min first")
            childAfterChange = change_state(child)
            GrandchildVal,grandChild,GChildAction = miniMax(childAfterChange, zoc, notZoc, order, depth - 1, alpha, beta, True,actions)
            #minEval = min(minEval, GrandchildVal)
            best_val, best_child, best_action = min_child_and_val(childAfterChange, minEval, actions, grandChild, GrandchildVal, GChildAction)
            beta = min(beta, GrandchildVal)
            if beta <= alpha:
                break
        return best_val, best_child, action_org

def max_child_and_val(child1, val1, action1, child2, val2, action2):
    if val1 > val2:
        return val1, child1, action1
    else:
        return val2, child2, action2

def min_child_and_val(child1, val1, action1, child2, val2, action2):
    if val1 < val2:
        return val1, child1, action1
    else:
        return val2, child2, action2

class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        print("initial")
        startingTime = time.time()
        self.order = order
        self.zoc = zone_of_control
        self.notZoc = []
        self.initialState = initial_state
        print(self.initialState)
        self.initialStateAsPaddedDict = main.pad_the_input(initial_state)
        #self.action_state_dict = allPossibleChildrenFromState(initial_state,zone_of_control)

        for i in range(len(initial_state)):
            for j in range(len(initial_state[0])):
                if 'S' in initial_state[i][j]:
                    self.initialStateAsPaddedDict[(i, j)] = 'S0'
                if (i, j) not in zone_of_control:
                    self.notZoc.append((i, j))

        #self.action_state_dict = self.get_action_state_dict()

        posInfinity = float('inf')
        negInfinity = float('-inf')
        if self.order == 'first':
            self.evalMax, self.nextState, self.nextAction = miniMax(initial_state, self.zoc, self.notZoc, self.order, 2, negInfinity, posInfinity,
                                                 True, [])

        print("end initial")
        print('initial time: ', time.time() - startingTime)

    def act(self, state):
        startingTime = time.time()
        posInfinity = float('inf')
        negInfinity = float('-inf')

        if state == self.initialState:
            print("returning pre-calculated")
            return self.nextAction

        else:
            if self.order == 'second':
            #    self.(self.initialState
                evalMax, nextState, nextAction = miniMax(state, self.zoc, self.notZoc, self.order, 1, negInfinity, posInfinity,
                                                 True, [])
            else:
                evalMax, nextState, nextAction = miniMax(state, self.zoc, self.notZoc, self.order, 2, negInfinity, posInfinity, True, [])
        '''
        allActions = all_actions(state,self.zoc)
        for action in allActions:
            new_state = apply_actions(state,action)
            if new_state == nextState:
                nextAction = action
                break
        '''


        print('evalMax:', evalMax)
        print('nextState', nextState)
        #print("jjj",self.zoc)
        print('nextAction', nextAction)
        print("zoc",self.zoc)
        #self.currentState = main.pad_the_input(state)

        print('act time:', time.time() - startingTime)

        return nextAction

    '''
    def get_action_state_dict(self):
        zoc = self.zoc
        state = self.initialState
        action_state_dict = {}
        state_action_state_dict = {}
        action_state_dict = allPossibleChildrenFromState(state,zoc)
        for action,children in action_state_dict.items():
            action_state_dict[(state, action)] = children

        print(action_state_dict)
    '''






# implementation of a random agent
# class Agent:
#     def __init__(self, initial_state, zone_of_control, order):
#         self.zoc = zone_of_control
#         self.order = order
#         print('initial_state:')
#         for row in range(len(initial_state)):
#             print(initial_state[row])
#         print('\n')
#
#     def act(self, state):
#         print(self.order)
#         print('state in act:')
#         for row in range(len(state)):
#             print(state[row])
#         print('\n')
#         action = []
#         healthy = set()
#         sick = set()
#         for (i, j) in self.zoc:
#             if 'H' in state[i][j]:
#                 healthy.add((i, j))
#             if 'S' in state[i][j]:
#                 sick.add((i, j))
#         try:
#             to_quarantine = random.sample(sick, 2)
#         except ValueError:
#             to_quarantine = []
#         try:
#             to_vaccinate = random.sample(healthy, 1)
#         except ValueError:
#             to_vaccinate = []
#         for item in to_quarantine:
#             action.append(('quarantine', item))
#         for item in to_vaccinate:
#             action.append(('vaccinate', item))
#
#         return action

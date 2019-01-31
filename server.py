import operator
import random
import math
import numpy as np
import matplotlib.pyplot as plt
from graphics import *
import time

# possible actions
ACTION_NORTH = 0
ACTION_NORTH_EAST = 1
ACTION_EAST = 2
ACTION_SOUTH_EAST = 3
ACTION_SOUTH = 4
ACTION_SOUTH_WEST = 5
ACTION_WEST = 6
ACTION_NORTH_WEST = 7
ACTION_SKIP = 8

W_AGENT = -2
W_EMPTY = 1
W_OBSTACLE = -1
W_CORRAL = 1


class Server:
    __GRID_WIDTH = 5
    __GRID_HEIGHT = 5
    __CORRAL = [__GRID_WIDTH - 1, 0]
    __WEIGHT_DICT = {-1: -1,
                     100: 0,
                     1: -2,
                     2: -2,
                     0: 1}
    __OBSTACLES = [[1, 1], [1, 2]]
    __SKIP_NO = 8
    __Action_DICT = {0: (1, 0),
                     1: (1, 1),
                     2: (0, 1),
                     3: (-1, 1),
                     4: (-1, 0),
                     5: (-1, -1),
                     6: (0, -1),
                     7: (1, -1),
                     __SKIP_NO: (0, 0)}

    __AGENT_NO = 2

    def __init__(self):
        self.__goal_state = False
        self.__agent_state_1 = [0, self.__GRID_HEIGHT - 1]
        self.__agent_state_2 = [self.__GRID_WIDTH - 1, self.__GRID_HEIGHT - 1]
        self.__cow_state = [2, self.__GRID_HEIGHT - 1]
        self.__cow_counter = 0
        self.__grid = [[-1 if [i, j] in self.__OBSTACLES else 0 for j in range(self.__GRID_WIDTH)]
                       for i in range(self.__GRID_HEIGHT)]
        self.__grid[self.__CORRAL[0]][self.__CORRAL[1]] = 100
        self.__reset_action_dict()
        self.__refresh_grid()

    def __reset_action_dict(self):
        self    .__actions_dict = dict()
        self.__actions_dict.setdefault(1, self.__SKIP_NO)
        self.__actions_dict.setdefault(2, self.__SKIP_NO)

    def start_simulation(self):
        # self.__init__()
        self.step()
        return self.__agent_state_1, self.__agent_state_2, self.__cow_state, self.__goal_state

    def send_action(self, action, agent_number):
        if agent_number > self.__AGENT_NO:
            print(str(agent_number), " is not registered in server")
        else:
            self.__actions_dict[agent_number] = action

    def step(self):
        action_1 = self.__actions_dict[1]
        action_2 = self.__actions_dict[2]
        if random.random() > 0.5:
            self.__move_agent(action_1, 1)
            self.__move_agent(action_2, 2)
        else:
            self.__move_agent(action_2, 2)
            self.__move_agent(action_1, 1)
        if self.__cow_counter % 2 == 0:
            self.__move_cow()
        self.__cow_counter += 1
        self.__refresh_grid()
        self.__reset_action_dict()
        return self.__goal_state

    def get_precept(self, agent):
        # print(agent)
        try:
            if agent.name == 1:
                agent.state_prime = self.__agent_state_1
                agent.cow_state_prime = self.__cow_state
            elif agent.name == 2:
                agent.state_prime = self.__agent_state_2
                agent.cow_state_prime = self.__cow_state
        except:
            print("agent is not registered in server")

    def show_states(self):
        print('***************************************')
        for row in self.__grid:
            str_ = ",".join("{:4d}".format(col) for col in row)
            print(str_)

    def __get_cell_value(self, cell_i, cell_j):
        value = 0
        if self.__CORRAL == [cell_i, cell_j]:
            value = -100
        else:
            for i in [-1, 0, 1]:
                for j in [-1, 0, 1]:
                    if i == 0 and j == 0:
                        continue
                    try:
                        value += self.__WEIGHT_DICT[self.__grid[cell_i + i][cell_j + j]]
                    except:
                        pass
        return value

    def __move_cow(self):
        grid = self.__grid
        cow_i, cow_j = self.__cow_state
        around_cell_lst = []
        for i, j in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            try:
                neighbour_i = cow_i + i
                neighbour_j = cow_j + j
                if neighbour_j >= 0 and neighbour_i >= 0:
                    if grid[neighbour_i][neighbour_j] in [0, 100]:
                        around_cell_lst.append((neighbour_i, neighbour_j))
            except:
                pass
        pos_value_dict = {}
        for i, j in around_cell_lst:
            pos_value_dict[(i, j)] = self.__get_cell_value(i, j)
        if len(pos_value_dict):
            max_value = max(pos_value_dict.items(), key=operator.itemgetter(1))[1]
            positions = [key for key, value in pos_value_dict.items() if value == max_value]
            cow_move_i, cow_move_j = random.choice(positions)
            self.__cow_state[0] = cow_move_i
            self.__cow_state[1] = cow_move_j
            if self.__cow_state == self.__CORRAL:
                self.__goal_state = True

    def __move_agent(self, action, agent_number):
        move_i, move_j = self.__Action_DICT[action]
        if agent_number == 1:
            state = self.__agent_state_1
        else:
            state = self.__agent_state_2
        i_prime = state[0] + move_i
        j_prime = state[1] + move_j
        if i_prime >= 0 and j_prime >= 0:
            try:
                cell_content = self.__grid[i_prime][j_prime]
                if cell_content == 0:
                    state[0] += move_i
                    state[1] += move_j
            except:
                pass
            self.__refresh_grid()

    def __refresh_grid(self):
        self.__grid = [[-1 if [i, j] in self.__OBSTACLES else 0 for j in range(self.__GRID_WIDTH)]
                       for i in range(self.__GRID_HEIGHT)]
        self.__grid[self.__CORRAL[0]][self.__CORRAL[1]] = 100
        self.__grid[self.__agent_state_1[0]][self.__agent_state_1[1]] = 1
        self.__grid[self.__agent_state_2[0]][self.__agent_state_2[1]] = 2
        self.__grid[self.__cow_state[0]][self.__cow_state[1]] = 50

    def __go_loading(self, i, total, show):
        percentage = i * 100 / total
        p = percentage
        s = "["
        k = 0
        while percentage > 0:
            s += "*"
            percentage -= 2
            k += 1
        k_prime = k
        while k < 50:
            k += 1
            s += " "
        if not (show == k_prime):
            # os.system('cls' if os.name == 'nt' else 'clear')
            print(
                s + "]" + str("{:2.3f}".format(p)).zfill(6) + "%  -->  " + str(i).zfill(5) + "/" + str(total).zfill(4))
        return k_prime

    def test(self, agent1, agent2, maximum_movement=200):
        moves = []
        move1 = []
        move2 = []
        position_cowboy1 = []
        position_cowboy2 = []
        position_cow = []
        print("WTF")
        self.__init__()
        for i in np.arange(maximum_movement):
            print(i)
            self.get_precept(agent1)
            self.get_precept(agent2)
            agent1.message_passing(agent2.state_prime)
            agent2.message_passing(agent1.state_prime)
            mein_i_1 = agent1.state_prime[0]
            mein_j_1 = agent1.state_prime[1]
            position_cowboy1.append([mein_i_1, mein_j_1])
            friend_i_1 = agent1.ally_state_prime[0]
            friend_j_1 = agent1.ally_state_prime[1]
            position_cowboy2.append([friend_i_1, friend_j_1])
            cow_i_1 = agent1.cow_state_prime[0]
            cow_j_1 = agent1.cow_state_prime[1]
            position_cow.append([cow_i_1, cow_j_1])
            phase1 = np.argmax(agent1.Q[mein_i_1, mein_j_1, friend_i_1, friend_j_1, cow_i_1, cow_j_1])
            action_agent1 = self.__Action_DICT[phase1]

            mein_i_2 = agent2.state_prime[0]
            mein_j_2 = agent2.state_prime[1]
            friend_i_2 = agent2.ally_state_prime[0]
            friend_j_2 = agent2.ally_state_prime[1]
            cow_i_2 = agent2.cow_state_prime[0]
            cow_j_2 = agent2.cow_state_prime[1]
            phase2 = np.argmax(agent2.Q[mein_i_2, mein_j_2, friend_i_2, friend_j_2, cow_i_2, cow_j_2])
            action_agent2 = self.__Action_DICT[phase2]
            moves.append([{"first agent did": action_agent1}, {"second agent did": action_agent2}])
            move1.append(phase1)
            move2.append(phase2)
            self.send_action(phase1, 1)
            self.send_action(phase2, 2)
            xxx = self.start_simulation()
            finish = xxx[3]
            # print(finish)
            # self.show_states()
            if finish:
                break
        return moves, move1, move2, finish, position_cowboy1, position_cowboy2, position_cow

    def train(self, agent1, agent2, episodes=2000, maximum_movements=200, random=0.98, discount=0.99999, gamma=0.99):
        epsilon = 1
        lamda = 1
        maxxx = 200
        ans = []
        x = []
        save1 = []
        save2 = []
        pause = 'n'
        show = -1
        for i in np.arange(episodes):
            saves1 = 0
            saves2 = 0

            x.append(i+1)
            if i > 5000:
                pause = input()
            show = self.__go_loading(i, episodes, show)
            # print("============\n============\n")
            # print("episode number: ", i + 1, "/", episodes)
            self.__init__()
            fir = True
            # print("do you wanna pause?")
            # pause = input()

            for j in np.arange(maximum_movements):
                # print("++++++++++++++++\n++++++++++++++++\n")
                # print("movement: ", j + 1, "/", maximum_movements)
                # if i % 100 == 0 and i >100:
                #     # input()
                #     print()
                self.get_precept(agent1)
                self.get_precept(agent2)
                agent1.message_passing(agent2.state_prime)
                agent2.message_passing(agent1.state_prime)
                # print(agent1)
                # print(agent2)
                # print(agent1.state_prime)
                # print(agent1.ally_state_prime)
                # self.show_states()
                if i % 100 == 0 and fir:
                    # self.show_states()
                    # print(agent1.Q)
                    fir = False
                    # print(agent1)
                    # print(agent2)
                    # print(agent1.state_prime)
                    # print(agent1.ally_state_prime)
                    # input()
                if self.__goal_state:
                    break
                what = np.random.random(1)[0]
                # print("======================\n============\n====\n=\n")
                # print("agent 1 ")
                # print("what choice? ", what)
                # print("lambda is: ", lamda)
                # print("epsilon? ", epsilon)
                mein_i_1 = agent1.state_prime[0]
                mein_j_1 = agent1.state_prime[1]
                friend_i_1 = agent1.ally_state_prime[0]
                friend_j_1 = agent1.ally_state_prime[1]
                cow_i_1 = agent1.cow_state_prime[0]
                cow_j_1 = agent1.cow_state_prime[1]
                if what < epsilon:
                    phase1 = np.random.randint(0, 8)
                    # print("random it is")
                else:
                    # print(agent1.Q[mein_i_1, mein_j_1, friend_i_1, friend_j_1, cow_i_1, cow_j_1])
                    # print()
                    phase1 = np.argmax(agent1.Q[mein_i_1, mein_j_1, friend_i_1, friend_j_1, cow_i_1, cow_j_1])
                    # print(phase1)
                    # print()
                    # print("maximum it is")
                # if phase1 == 0:
                #     print("up")
                # elif phase1 == 1:
                #     print("up right")
                # elif phase1 == 2:
                #     print("right")
                # elif phase1 == 3:
                #     print("down right")
                # elif phase1 == 4:
                #     print("down")
                # elif phase1 == 5:
                #     print("down left")
                # elif phase1 == 6:
                #     print("left")
                # elif phase1 == 7:
                #     print("up left")
                # else:
                #     print("no move")
                action_agent1 = self.__Action_DICT[phase1]
                # print(action_agent1)
                # print(agent1.Q[mein_i_1, mein_j_1, friend_i_1, friend_j_1, cow_i_1, cow_j_1])

                what = np.random.random(1)[0]
                # print("======================\n============\n====\n=\n")
                # print("agent 2 ")
                # print("what choice? ", what)
                # print("lambda is: ", lamda)
                # print("epsilon? ", epsilon)
                mein_i_2 = agent2.state_prime[0]
                mein_j_2 = agent2.state_prime[1]
                friend_i_2 = agent2.ally_state_prime[0]
                friend_j_2 = agent2.ally_state_prime[1]
                cow_i_2 = agent2.cow_state_prime[0]
                cow_j_2 = agent2.cow_state_prime[1]
                if what < epsilon:
                    phase2 = np.random.randint(0, 8)
                    # print("random it is")
                else:
                    # print(agent2.Q[mein_i_2, mein_j_2, friend_i_2, friend_j_2, cow_i_2, cow_j_2])
                    # print()
                    phase2 = np.argmax(agent2.Q[mein_i_2, mein_j_2, friend_i_2, friend_j_2, cow_i_2, cow_j_2])
                    # print(phase2)
                    # print()
                    # print("maximum it is")
                # print(phase1)
                # print(phase2)
                # if phase2 == 0:
                #     print("up")
                # elif phase2 == 1:
                #     print("up right")
                # elif phase2 == 2:
                #     print("right")
                # elif phase2 == 3:
                #     print("down right")
                # elif phase2 == 4:
                #     print("down")
                # elif phase2 == 5:
                #     print("down left")
                # elif phase2 == 6:
                #     print("left")
                # elif phase2 == 7:
                #     print("up left")
                # else:
                #     print("no move")
                action_agent2 = self.__Action_DICT[phase2]
                # print(action_agent2)
                # print(agent2.Q[mein_i_2, mein_j_2, friend_i_2, friend_j_2, cow_i_2, cow_j_2])

                # print("stepping over")
                self.send_action(phase1, 1)
                self.send_action(phase2, 2)
                xxx = self.start_simulation()
                # print(xxx)
                next_1 = xxx[0]
                next_i_1 = next_1[0]
                next_j_1 = next_1[1]
                next_2 = xxx[1]
                next_i_2 = next_2[0]
                next_j_2 = next_2[1]
                next_cow = xxx[2]
                next_cow_i = next_cow[0]
                next_cow_j = next_cow[1]
                finish = xxx[3]
                if finish:
                    reward = 500
                    rew = 500
                    # print(maxxx)
                    # print("got there in episode " + str(i))
                    # print("in this many moves " + str(j))
                    # input()
                    if j < maxxx:
                        maxxx = j
                else:
                    reward = -1
                    rew = -1
                    if mein_i_1 == next_i_1 and mein_j_1 == next_j_1:
                        reward = -1.01
                        # print("I got burned")
                    if mein_i_2 == next_i_2 and mein_j_2 == next_j_2:
                        rew = -1
                        # print("you got burned")
                saves1 += agent1.Q[mein_i_1, mein_j_1, friend_i_1, friend_j_1, cow_i_1, cow_j_1, phase1]
                saves2 += agent2.Q[mein_i_2, mein_j_2, friend_i_2, friend_j_2, cow_i_2, cow_j_2, phase2]
                agent1.Q[mein_i_1, mein_j_1, friend_i_1, friend_j_1, cow_i_1, cow_j_1, phase1] = lamda * (reward + gamma * np.max(agent1.Q[next_i_1, next_j_1, next_i_2, next_j_2, next_cow_i, next_cow_j, phase1])) + (1 - lamda) * agent1.Q[mein_i_1, mein_j_1, friend_i_1, friend_j_1, cow_i_1, cow_j_1, phase1]
                agent2.Q[mein_i_2, mein_j_2, friend_i_2, friend_j_2, cow_i_2, cow_j_2, phase2] = lamda * (rew + gamma * np.max(agent2.Q[next_i_2, next_j_2, next_i_1, next_j_1, next_cow_i, next_cow_j, phase2])) + (1 - lamda) * agent2.Q[mein_i_2, mein_j_2, friend_i_2, friend_j_2, cow_i_2, cow_j_2, phase2]
                if pause == 'y':

                    print("this is new ")
                    self.show_states()
                    print(agent1.Q[mein_i_1, mein_j_1, friend_i_1, friend_j_1, cow_i_1, cow_j_1])
                    print(agent2.Q[mein_i_2, mein_j_2, friend_i_2, friend_j_2, cow_i_2, cow_j_2])
                    print(agent1)
                    print(agent2)
                    print(action_agent1)
                    print(action_agent2)
                    print()
                    input()
                if finish:
                    # print(agent1.Q)
                    # input()
                    # print(agent2.Q)
                    ans.append([{"episode": str(i)}, {"moves": str(j)}])
                    # print(ans)
                    # input()
                    break
            # print(agent1.Q)
            # if i % 100 == 0:
                # self.show_states()
                # print(agent1.Q)
                # input()
            lamda *= discount
            epsilon *= random
            save1.append([saves1])
            save2.append([saves2])
        # print(maxxx)
        print(ans)
        # input()
        # print(agent1.Q)
        # input()
        # print()
        # print(len(x))
        # print(len(save1))
        return x, save1, save2
        # print(agent2.Q)



class BaseAgent:
    def __init__(self, name, state, ally_state, cow_state):
        self.state = state
        self.ally_state_prime = self.state_prime = self.cow_state_prime = 0
        self.cow_state = cow_state
        self.ally_state = ally_state
        self.name = name

    def message_passing(self, ally_position):
        self.ally_state_prime = ally_position


class Agent(BaseAgent):
    def __init__(self, width, height, number_of_actions, name, state, ally_state, cow_state):
        self.name = name
        self.state = state
        self.ally_state = ally_state
        self.cow_state = cow_state
        self.width = width
        self.height = height
        self.number_of_actions = number_of_actions
        self.Q = np.zeros((self.width, self.height, self.width, self.height, self.width, self.height, self.number_of_actions))
        # first me, second him, third cow

    def __repr__(self):
        print("agent number " + str(self.name) + " in home " + str(self.state_prime) + " my friend is at " + str(self.ally_state_prime) + " and cow is " + str(self.cow_state_prime))

    def __str__(self):
        return "agent number " + str(self.name) + " in home " + str(self.state_prime) + " my friend is at " + str(self.ally_state_prime) + " and cow is " + str(self.cow_state_prime)


def i_got_the_move(shapeList, x, y, color):
    for shape in shapeList:
        shape.undraw()
    head = Circle(Point(450-(4-x)*100, 450-(4-y)*100), 25)
    head.setFill(color[0])
    head.draw(win)

    eye1 = Circle(Point(440-(4-x)*100, 445-(4-y)*100), 5)
    eye1.setFill(color[1])
    eye1.draw(win)

    eye2 = Circle(Point(460-(4-x)*100, 445-(4-y)*100), 5)
    eye2.setFill(color[2])
    eye2.draw(win)

    mouth = Oval(Point(440-(4-x)*100, 465-(4-y)*100), Point(460-(4-x)*100, 465-(4-y)*100))
    mouth.setFill(color[3])
    mouth.draw(win)

    shapeList = [head, eye1, eye2, mouth]
    return shapeList


if __name__ == '__main__':
    s = Server()
    whole = s.start_simulation()
    # print(whole)
    agent1 = Agent(5, 5, 8, 1, whole[0], whole[1], whole[2])
    agent2 = Agent(5, 5, 8, 2, whole[1], whole[0], whole[2])
    # print(agent1)
    # print(agent2)
    # s.show_states()
    # s.send_action(4, 1)
    # s.send_action(4, 2)
    # print(s.start_simulation())
    # # l = s.step()
    # # print(l)
    # s.show_states()
    # s.send_action(6, 1)
    # s.send_action(6, 2)
    # print(s.start_simulation())
    # # l = s.step()
    # # print(l)
    # s.show_states()
    # s.send_action(6, 1)
    # s.send_action(6, 2)
    # print(s.start_simulation())
    # # l = s.step()
    # # print(l)
    # s.show_states()
    # s.send_action(4, 1)
    # s.send_action(4, 2)
    # print(s.start_simulation())
    # # l = s.step()
    # # print(l)
    # s.show_states()
    # s.send_action(6, 1)
    # s.send_action(6, 2)
    # print(s.start_simulation())
    # # l = s.step()
    # # print(l)
    # s.show_states()
    # s.send_action(4, 1)
    # s.send_action(4, 2)
    # print(s.start_simulation())
    # # l = s.step()
    # # print(l)
    # s.show_states()
    # s.get_precept(agent1)
    # s.get_precept(agent2)
    # print(agent1.state_prime)
    # print(agent2.state_prime)
    x, save1, save2 = s.train(agent1=agent1, agent2=agent2, episodes=2000)
    print("dafaq")
    moves, move1, move2, finish, pos_cowboy1, pos_cowboy2, pos_cow = s.test(agent1=agent1, agent2=agent2)
    print(moves)
    print(move1)
    print(move2)
    print(finish)
    print(pos_cow)
    print(pos_cowboy1)
    print(pos_cowboy2)
    length = 500
    win = GraphWin('My WORLD', length, length)
    for i in range(6):
        l = Line(Point(100*i, length), Point(100*i, 0))
        l.setWidth(5)
        l.draw(win)
    for i in range(6):
        l = Line(Point(0, 100*i), Point(length, 100*i))
        l.setWidth(5)
        l.draw(win)

    obstacle1 = Rectangle(Point(100, 100), Point(200, 200))
    obstacle2 = Rectangle(Point(200, 100), Point(300, 200))
    goal = Rectangle(Point(0, 400), Point(100, 500))
    obstacle1.setFill("black")
    obstacle2.setFill("black")
    goal.setFill("cyan")
    obstacle2.draw(win)
    obstacle1.draw(win)
    goal.draw(win)

    head = Circle(Point(450, 50), 25)
    head.setFill("yellow")
    head.draw(win)

    eye1 = Circle(Point(440, 45), 5)
    eye1.setFill('blue')
    eye1.draw(win)

    eye2 = Circle(Point(460, 45), 5)
    eye2.setFill('blue')
    eye2.draw(win)

    mouth = Oval(Point(440, 65), Point(460, 65))
    mouth.setFill("red")
    mouth.draw(win)
    color_cowboy1 = ["yellow", "blue", "blue", "red"]
    cowboy1 = [head, eye1, eye2, mouth]

    head = Circle(Point(450, 450), 25)
    head.setFill("green")
    head.draw(win)

    eye1 = Circle(Point(440, 445), 5)
    eye1.setFill('blue')
    eye1.draw(win)

    eye2 = Circle(Point(460, 445), 5)
    eye2.setFill('blue')
    eye2.draw(win)

    mouth = Oval(Point(440, 465), Point(460, 465))
    mouth.setFill("red")
    mouth.draw(win)

    color_cowboy2 = ["green", "blue", "blue", "red"]
    cowboy2 = [head, eye1, eye2, mouth]

    head = Circle(Point(450, 250), 25)
    head.setFill("brown")
    head.draw(win)

    eye1 = Circle(Point(440, 245), 5)
    eye1.setFill('red')
    eye1.draw(win)

    eye2 = Circle(Point(460, 245), 5)
    eye2.setFill('red')
    eye2.draw(win)

    mouth = Oval(Point(440, 260), Point(460, 270))
    mouth.setFill("green")
    mouth.draw(win)

    color_cow = ["brown", "red", "red", "green"]
    cow = [head, eye1, eye2, mouth]

    # moveAllOnLine(cowboy1, 5, 0, 46, .05)
    time.sleep(1)
    for m in range(len(pos_cow)):
        cowboy2 = i_got_the_move(cowboy2, pos_cowboy2[m][1], pos_cowboy2[m][0], color_cowboy2)
        cowboy1 = i_got_the_move(cowboy1, pos_cowboy1[m][1], pos_cowboy1[m][0], color_cowboy1)
        cow = i_got_the_move(cow, pos_cow[m][1], pos_cow[m][0], color_cow)
        time.sleep(.4)
    if finish:
        win.close()
        win = GraphWin('You Solved the problem', length, 200)
        win.setBackground("yellow")
        text = Text(Point(length/2, 100), "The Cow is Resting Now")
        text.setFill("red")
        text.draw(win)
        time.sleep(.8)
    time.sleep(.5)
    win.close()

    plt.figure()
    plt.subplot(211)
    plt.plot(x, save1, 'r')
    plt.subplot(212)
    plt.plot(x, save2, 'blue')
    plt.show()


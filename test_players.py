from random import randint
import random
from isolation import Board, game_as_text
import time



class OpenMoveEvalFn:

    def score(self, game, maximizing_player_turn=True):
        """Score the current game state

        Evaluation function that outputs a score equal to how many
        moves are open for AI player on the board minus how many moves
        are open for Opponent's player on the board.
        Note:
            1. Be very careful while doing opponent's moves. You might end up
               reducing your own moves.
            3. If you think of better evaluation function, do it in CustomEvalFn below.

            Args
                param1 (Board): The board and game state.
                param2 (bool): True if maximizing player is active.

            Returns:
                float: The current state's score. MyMoves-OppMoves.

            """

        score=-10000.00
        # TODO: finish this function!
        if maximizing_player_turn:
            score=len(game.get_legal_moves())- len(game.get_opponent_moves())
        else:
            score=len(game.get_opponent_moves()) - len(game.get_legal_moves())

        return score





class AIPlayer:
    # TODO: finish this class!
    """Player that chooses a move using your evaluation function
    and a minimax algorithm with alpha-beta pruning.
    You must finish and test this player to make sure it properly
    uses minimax and alpha-beta to return a good move."""

    def __init__(self, search_depth=4, eval_fn=OpenMoveEvalFn()):
        """Initializes your player.

        if you find yourself with a superior eval function, update the default
        value of `eval_fn` to `CustomEvalFn()`

        Args:
            search_depth (int): The depth to which your agent will search
            eval_fn (function): Utility function used by your agent
        """
        self.eval_fn = eval_fn
        self.search_depth = search_depth
        self.best_move_max_player={}
        self.best_move_min_player={}
        self.matching_arr=None
        self.rotations=[]
        self.find_Q2= False
        self.find_Q1 = False
        self.count_Q1_moves = 0
        self.count_Q2_moves = 0
        self.marked={}
        self.first_round = True


    def move(self, game, legal_moves, time_left):
        """Called to determine one move by your agent

            Note:
                1. Do NOT change the name of this 'move' function. We are going to call
                the this function directly.
                2. Change the name of minimax function to alphabeta function when
                required. Here we are talking about 'minimax' function call,
                NOT 'move' function name.
                Args:
                game (Board): The board and game state.
                legal_moves (dict): Dictionary of legal moves and their outcomes
                time_left (function): Used to determine time left before timeout

            Returns:
                tuple: best_move
            """
        if self.matching_arr is None:
            width= game.width
            height = game.height
            self.matching_arr = []
            total = width*height
            temp=[]
            for i in range(1,total+1):
                temp.append(i)
                if i%width==0:
                    self.matching_arr.append(temp)
                    temp=[]
            rot90 = zip(*self.matching_arr[::-1])
            self.rotations.append(rot90)
            rot180 = zip(*rot90[::-1])
            self.rotations.append(rot180)

            rot270 = zip(*rot180[::-1])
            self.rotations.append(rot270)
            if width==height:
                aux_arr= [x[:] for x in self.matching_arr]
                idx=[(i,j) for i in range(len(self.matching_arr)) for j in range(i)]
                for i,j in idx:
                    aux_arr[i][j]= self.matching_arr[j][i]
                    aux_arr[j][i]= self.matching_arr[i][j]
                self.rotations.append(aux_arr)

        if self.first_round:
            self.first_round = False
            return random.choice(game.get_legal_moves())
        best_move, utility = self.alphabeta(game, time_left, depth=self.search_depth)
        return best_move

    def utility(self, game, maximizing_player):
        """Can be updated if desired. Not compulsory. """
        return self.eval_fn.score(game)

    def equi_states(self,arr,move,score,max_player=True):

        states_list=[]
        row,col= move[0],move[1]
        push = move[2]
        pivot = self.matching_arr[row][col]
        rot90 = zip(*arr[::-1])
        rot180 = zip(*rot90[::-1])
        rot270 = zip(*rot180[::-1])
        states_list.append(rot90)
        states_list.append(rot180)
        states_list.append(rot270)
        if len(arr)== len(arr[0]):
            aux_arr = [x[:] for x in arr]
            idx=[(i,j) for i in range(len(arr)) for j in range(i)]
            for i,j in idx:
                aux_arr[i][j]= arr[j][i]
                aux_arr[j][i]= arr[i][j]
            states_list.append(aux_arr)
        if max_player:
            for idx,state in enumerate(states_list):
                state = self.to_tuple(state)
                ix,iy= [(ix,iy) for ix, row in enumerate(self.rotations[idx]) for iy, i in enumerate(row) if i == pivot][0]
                self.best_move_max_player[state]= ((ix,iy,push),score)
        elif not max_player:
            for idx,state in enumerate(states_list):
                state = self.to_tuple(state)

                ix,iy= [(ix,iy) for ix, row in enumerate(self.rotations[idx]) for iy, i in enumerate(row) if i == pivot][0]
                self.best_move_min_player[state]= ((ix,iy,push),score)

    def to_tuple(self,l):
        return tuple([tuple(x[:]) for x in l])

    def get_idx(self,game_state,name='Q1'):
        return [(ix,iy) for ix, row in enumerate(game_state) for iy, i in enumerate(row) if i == name][0]


    def neighbor(self,idx,width,height,game_state):
        neigh = [(0,1),(0,-1),(1,0),(1,0),(1,1),(1,-1),(-1,1),(-1,-1)]
        neigh_idx =set()
        for row,col in neigh:
            y= idx[0]-row
            x= idx[1]-col
            if y >= 0 and y<height and x>=0 and x<width:
                if game_state[y][x]!= 'X':
                    neigh_idx.add((y,x))
        return neigh_idx

    def dfs(self,game_state,idx,path=None,lookfor='Q2',width=5,height=5):
        self.marked[idx] = 1
        if lookfor == 'Q2':
            if self.find_Q2 == True:
                return
            for row,col in self.neighbor(idx,width,height,game_state):
                if game_state[row][col] == lookfor:
                    self.find_Q2 = True
                    return
                if self.marked.setdefault((row,col),0)==0 and game_state[row][col]!='X':
                    self.count_Q1_moves +=1
                    self.dfs(game_state,(row,col),path,lookfor,width,height)
                    if path is not None:
                        path[idx] = (row,col)

        if lookfor == 'Q1':
            if self.find_Q1 == True:
                return
            for row,col in self.neighbor(idx,width,height,game_state):
                if game_state[row][col] == lookfor:
                    self.find_Q1 = True
                    return

                if self.marked.setdefault((row,col),0)==0 and game_state[row][col]!='X':
                    self.count_Q2_moves +=1
                    self.dfs(game_state,(row,col),path,lookfor,width,height)
                    if path is not None:
                        path[idx] = (row,col)


    def get_block_num(self,game_state,height,width):
        return len([(i,j) for i in range(height) for j in range(width) if game_state[i][j]=='X'])

    def minimax(self, game, time_left, depth, maximizing_player=True):
        """Implementation of the minimax algorithm

        Args:
            game (Board): A board and game state.
            time_left (function): Used to determine time left before timeout
            depth: Used to track how deep you are in the search tree
            maximizing_player (bool): True if maximizing player is active.

        Returns:
            (tuple, int): best_move, val
        """
        # TODO: finish this function!


        if time_left()<30 and depth < self.search_depth:
            # print ('time left:',time_left())
            return None,self.eval_fn.score(game, maximizing_player_turn= maximizing_player)
        if depth ==0:
            return None,self.eval_fn.score(game, maximizing_player_turn= maximizing_player)
        AI_player = game.__queen_1__ if 'CustomPlayer' in game.__queen_1__ else game.__queen_2__
        Opponent = game.__queen_1__ if AI_player == game.__queen_2__ else game.__queen_2__

        game_state = self.to_tuple(game.get_state())
        width= game.width
        height = game.height

        if maximizing_player and game_state in self.best_move_max_player:
            return self.best_move_max_player[game_state]
        if maximizing_player==False and game_state in self.best_move_min_player:
            return self.best_move_min_player[game_state]

        blocks_num = self.get_block_num(game_state,height,width)
        self.find_Q2 = False
        self.find_Q1 = False
        self.count_Q2_moves = 0
        self.count_Q1_moves = 0

        if blocks_num >= max(width,height)+1 and depth< self.search_depth:
            self.marked={}
            if AI_player[-2:] == 'Q1':
                Q1_idx = self.get_idx(game_state,name='Q1')
                self.dfs(game_state,Q1_idx,None,'Q2',width,height)
                self.marked={}
                if not self.find_Q2:
                    Q2_idx = self.get_idx(game_state,name='Q2')
                    self.dfs(game_state,Q2_idx,None,'Q1',width,height)
                    Q1_more_moves = self.count_Q1_moves - self.count_Q2_moves

                    # print 'I AM Q1:',Q1_more_moves
                    self.marked = {}

                    return None,20*Q1_more_moves

            elif AI_player[-2:] == 'Q2':
                Q2_idx = self.get_idx(game_state,name='Q2')
                self.dfs(game_state,Q2_idx,None,'Q1',width,height)
                self.marked = {}
                if not self.find_Q1:
                    Q1_idx = self.get_idx(game_state,name='Q1')
                    self.dfs(game_state,Q1_idx,None,'Q2',width,height)
                    Q2_more_moves = self.count_Q2_moves - self.count_Q1_moves

                    # print 'I AM Q2:',Q2_more_moves
                    self.marked = {}
                    # move = (move[0],move[1],False) if move is not None else None

                    return None,20*Q2_more_moves


            self.find_Q2 = False
            self.find_Q1 = False
            self.count_Q2_moves = 0
            self.count_Q1_moves = 0

        if maximizing_player == True:
            best_score = float('-inf')
            best_move = None
            try:
                AI_idx = self.get_idx(game_state,name= AI_player[-2:])
            except:
                AI_idx=None
            if AI_idx is None:
                for max_player_moves in game.get_legal_moves():
                    new_board, is_over, winner = game.forecast_move(max_player_moves)
                    if is_over and winner == AI_player:
                        self.best_move_max_player[game_state]= (max_player_moves,9999)
                        return max_player_moves,9999
                    if is_over and winner == Opponent:
                        return max_player_moves,-9999
                    _,score = self.minimax(new_board, time_left, depth-1, maximizing_player=False)

                    if score>best_score:
                        best_score = score
                        best_move = max_player_moves

            elif AI_idx is not None:
                for max_player_moves in sorted(game.get_legal_moves(),key=lambda x:(x[0]-AI_idx[0])**2+ (x[1]-AI_idx[1])**2):
                    new_board, is_over, winner = game.forecast_move(max_player_moves)
                    if is_over and winner == AI_player:
                        self.best_move_max_player[game_state]= (max_player_moves,9999)
                        return max_player_moves,9999
                    if is_over and winner == Opponent:
                        return max_player_moves,-9999
                    _,score = self.minimax(new_board, time_left, depth-1, maximizing_player=False)

                    if score>best_score:
                        best_score = score
                        best_move = max_player_moves

            self.best_move_max_player[game_state]= (best_move,best_score)
            if blocks_num< max(width,height) and best_move is not None:
                self.equi_states(game.get_state(),best_move,best_score,True)


            return best_move,best_score

        elif maximizing_player == False:
            best_score = float('inf')
            best_move = None
            try:
                Oppo_idx = self.get_idx(game_state,name= Opponent[-2:])
            except:
                Oppo_idx=None
            if Oppo_idx is None:
                for min_player_moves in game.get_legal_moves():
                    new_board, is_over, winner = game.forecast_move(min_player_moves)
                    if is_over and winner == AI_player:
                        self.best_move_min_player[game_state]= (min_player_moves,9999)
                        return min_player_moves,9999
                    if is_over and winner == Opponent:
                        return min_player_moves,-9999

                    _,score = self.minimax(new_board, time_left, depth-1, maximizing_player=True)

                    if score<best_score:
                        best_score = score
                        best_move = min_player_moves
            elif Oppo_idx is not None:
                for min_player_moves in sorted(game.get_legal_moves(),key=lambda x:(x[0]-Oppo_idx[0])**2+ (x[1]-Oppo_idx[1])**2):
                    new_board, is_over, winner = game.forecast_move(min_player_moves)
                    if is_over and winner == AI_player:
                        self.best_move_min_player[game_state]= (min_player_moves,9999)
                        return min_player_moves,9999
                    if is_over and winner == Opponent:
                        return min_player_moves,-9999

                    _,score = self.minimax(new_board, time_left, depth-1, maximizing_player=True)

                    if score<best_score:
                        best_score = score
                        best_move = min_player_moves

            self.best_move_min_player[game_state]= (best_move,best_score)
            if blocks_num< max(width,height) and best_move is not None:
                self.equi_states(game.get_state(),best_move,best_score,False)

            return best_move,best_score

    def alphabeta(self, game, time_left, depth, alpha=-9000, beta=9000, maximizing_player=True):
        """Implementation of the alphabeta algorithm

        Args:
            game (Board): A board and game state.
            time_left (function): Used to determine time left before timeout
            depth: Used to track how deep you are in the search tree
            alpha (float): Alpha value for pruning
            beta (float): Beta value for pruning
            maximizing_player (bool): True if maximizing player is active.

        Returns:
            (tuple, int): best_move, val
        """
        # TODO: finish this function!
        if time_left()<30 and depth < self.search_depth:
            # print ('time left:',time_left())
            return None,self.eval_fn.score(game, maximizing_player_turn= maximizing_player)

        if depth ==0:
            return None,self.eval_fn.score(game, maximizing_player_turn= maximizing_player)
        AI_player = game.__queen_1__ if 'AIPlayer' in game.__queen_1__ else game.__queen_2__
        Opponent = game.__queen_1__ if AI_player == game.__queen_2__ else game.__queen_2__

        game_state = self.to_tuple(game.get_state())
        width= game.width
        height = game.height

        if maximizing_player and game_state in self.best_move_max_player:
            return self.best_move_max_player[game_state]
        if maximizing_player==False and game_state in self.best_move_min_player:
            return self.best_move_min_player[game_state]

        blocks_num = self.get_block_num(game_state,height,width)
        self.find_Q2 = False
        self.find_Q1 = False
        self.count_Q2_moves = 0
        self.count_Q1_moves = 0

        if blocks_num >= max(width,height)+1000 and depth< self.search_depth:
            self.marked={}
            if AI_player[-2:] == 'Q1':
                Q1_idx = self.get_idx(game_state,name='Q1')
                self.dfs(game_state,Q1_idx,None,'Q2',width,height)
                self.marked={}
                if not self.find_Q2:
                    Q2_idx = self.get_idx(game_state,name='Q2')
                    self.dfs(game_state,Q2_idx,None,'Q1',width,height)
                    Q1_more_moves = self.count_Q1_moves - self.count_Q2_moves

                    # print 'I AM Q1:',Q1_more_moves
                    self.marked = {}

                    return None,20*Q1_more_moves

            elif AI_player[-2:] == 'Q2':
                Q2_idx = self.get_idx(game_state,name='Q2')
                self.dfs(game_state,Q2_idx,None,'Q1',width,height)
                self.marked = {}
                if not self.find_Q1:
                    Q1_idx = self.get_idx(game_state,name='Q1')
                    self.dfs(game_state,Q1_idx,None,'Q2',width,height)
                    Q2_more_moves = self.count_Q2_moves - self.count_Q1_moves

                    # print 'I AM Q2:',Q2_more_moves
                    self.marked = {}
                    # move = (move[0],move[1],False) if move is not None else None

                    return None,20*Q2_more_moves



        if maximizing_player == True:
            best_move = None
            for max_player_moves in game.get_legal_moves():
                new_board, is_over, winner = game.forecast_move(max_player_moves)
                if is_over and winner == AI_player:
                    self.best_move_max_player[game_state]= (max_player_moves,9999)
                    return max_player_moves,9999
                if is_over and winner == Opponent:
                    return max_player_moves,-9999
                _,score = self.alphabeta(new_board, time_left, depth-1,alpha,beta, maximizing_player=False)

                if score>alpha:
                    alpha = score
                    best_move = max_player_moves
                if alpha>=beta:
                    break

            self.best_move_max_player[game_state]= (best_move,alpha)
            if blocks_num< max(width,height) and best_move is not None:
                self.equi_states(game.get_state(),best_move,alpha,True)


            return best_move,alpha

        elif maximizing_player == False:

            best_move = None
            for min_player_moves in game.get_legal_moves():
                new_board, is_over, winner = game.forecast_move(min_player_moves)
                if is_over and winner == AI_player:
                    self.best_move_min_player[game_state]= (min_player_moves,9999)
                    return min_player_moves,9999
                if is_over and winner == Opponent:
                    return min_player_moves,-9999

                _,score = self.alphabeta(new_board, time_left, depth-1,alpha,beta, maximizing_player=True)

                if score<beta:
                    beta = score
                    best_move = min_player_moves

                if alpha>=beta:
                    break

            self.best_move_min_player[game_state]= (best_move,beta)
            if blocks_num< max(width,height) and best_move is not None:
                self.equi_states(game.get_state(),best_move,beta,False)

            return best_move,beta











class RandomPlayer():

    def __init__(self, name="RandomPlayer"):
        self.name = name

    """Player that chooses a move randomly."""    

    def move(self, game, legal_moves, time_left):
        if not legal_moves:
            return None, None, False
        else:
            return random.choice(legal_moves)

    def get_name(self):
        return self.name



class HumanPlayer():

    def __init__(self, name="HumanPlayer"):
        self.name = name

    """Player that chooses a move according to user's input."""
    def move(self, game, legal_moves, time_left):
        choice = {}

        if not len(legal_moves):
            print "No more moves left."
            return None, None

        counter = 1
        for move in legal_moves:
            choice.update({counter: move})
            if not move[2]:
                print('\t'.join(['[%d] (%d,%d)'%(counter, move[0], move[1])]))
            else:
                print('\t'.join(['[%d] (%d,%d) - push' % (counter, move[0], move[1])]))
            counter += 1

        print "-------------------------"
        print game.print_board(legal_moves)
        print "-------------------------"
        print ">< - impassable, o - valid move"
        print "-------------------------"

        valid_choice = False

        while not valid_choice:
            try:
                index = int(input('Select move index [1-'+str(len(legal_moves))+']:'))
                valid_choice = 1 <= index <= len(legal_moves)

                if not valid_choice:
                    print('Illegal move of queen! Try again.')
            except Exception:
                print('Invalid entry! Try again.')

        return choice[index]

    def get_name(self):
        return self.name
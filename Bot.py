###### This programm contains class that can play Connect6
### import---------------------------------------------------------------------
import numpy as np  # math
import random       # random numbers
import time         # for measuting time performance

### classes--------------------------------------------------------------------
# bot to play cleverly
class E6:
    """class decides which move the bot makes"""
    def __init__(self, which_player, bs, c6, grphx):
        self.which_player = which_player # lets instance know which player it is ('PLayer1' or 'Player2')

        # c6 --> ?
        self.c6 = c6  # instance of connect6 class of the main program, includes various useful functions
        self.bs = bs  # board size
        self.turn = 0 # turn of game
        self.timeleft = 0 # time that passed

        # Tree? --> We have to know about this
        self.eval_pri = (10,10) # moves that are evaluated at each tree-level
        self.eval_pos = 1
        self.level = 30 # number of tree-levels

        # coefficients for evaluation
        self.me_pri_1 = np.array([2, 6, 0, 1000]).reshape(4,1,1) # My priority on first rock
        self.op_pri_1 = np.array([1, 4, 10, 100]).reshape(4,1,1) # Opponent priority on first rock
        self.me_pri_2 = np.array([2, 1, 6, 0, 1000]).reshape(5,1,1) # My priority on second rock
        self.op_pri_2 = np.array([1, 4, 6, 100, 100]).reshape(5,1,1) # Opponent priority on second rock
        self.me_pos = [0, 3/4, 8/5, 13/3, 12/2, 10000]
        self.op_pos = [1/5, 1, 12/4, 1000, 1000, 1000]

        # only for debugging
        self.grphx = grphx

    def getmove(self, board_me, board_op, turn, timeleft):
        """ returns calculated move"""
        t = time.time()
        self.board_me, self.board_op, self.turn, self.timeleft = board_me, board_op, turn, timeleft

        # first move is in middle of board
        if self.turn==1:
            move1 = (int(self.bs/2),int(self.bs/2))
            return move1

        # tree search
        bestmove = self.tree()
        elapsed = time.time()-t
        print('Elapsed time is:',elapsed)
        return bestmove[0], bestmove[1]

    def tree(self):

        """ does a tree search and gives back the best move"""
        board_me_all = np.zeros((self.eval_pos**self.level, self.bs, self.bs)) # 내가 둘 수 있는 수 // 4**depth개 봄
        board_op_all = np.zeros((self.eval_pos**self.level, self.bs, self.bs)) # 상대방이 둘 수 있는 수 // 4**depth개봄

        scores_moves = [(None, None)] * self.eval_pos**self.level # score on each move
        null_el = np.zeros((self.bs,self.bs)) # ?
        board_me_all[0, :, :] = null_el + self.board_me # 내 board + null_el
        board_op_all[0, :, :] = np.zeros((self.bs,self.bs)) + self.board_op  # 상대 board + null_el

        # create tree
        for ii in range(self.level):
            for jj in range(self.eval_pos**ii):
                root_num = jj*self.eval_pos**(self.level-ii)
                board_me_root = null_el + board_me_all[root_num, :, :]
                board_op_root = null_el + board_op_all[root_num, :, :]
                # me or op?
                #print('ii, jj', ii, jj)
                if ii % 2==0:
                    #print('if, ii, jj', ii, jj)
                    #bestmoves, scores = self.find_best_mvs(self.board_me, self.board_op)
                    bestmoves, scores = self.find_best_mvs(board_me_all[root_num, :, :], board_op_all[root_num, :, :])
                    pp = 0
                    for move in bestmoves:
                        branch_num = root_num + pp*self.eval_pos**(self.level-ii-1)
                        if ii==0:
                            scores_moves[branch_num] = (scores[pp],  move)
                        else:
                            scores_moves[branch_num]=(scores[pp], scores_moves[branch_num][1])
                        board_me_all[branch_num, :, :] = null_el + board_me_root
                        board_op_all[branch_num, :, :] = null_el + board_op_root
                        # self.grphx.draw_board(board_me_all[branch_num, :, :], board_op_all[branch_num, :, :])
                        # self.grphx.get_input()
                        # print('===========================')
                        # print('critical check start')
                        #print(board_me_all[branch_num, :, :])
                        board_me_all[branch_num, :, :][move[0]] = 1
                        board_me_all[branch_num, :, :][move[1]] = 1
                        #print(board_me_all[branch_num, :, :])
                        # print('critical check end')
                        # print('===========================')
                        # print('my turn, root, branch:',root_num, branch_num)
                        # self.grphx.draw_board(board_me_all[branch_num, :, :], board_op_all[branch_num, :, :])
                        # self.grphx.get_input()
                        pp += 1
                else:
                    #print('else, ii, jj', ii, jj)
                    bestmoves, scores = self.find_best_mvs(board_op_all[root_num, :, :], board_me_all[root_num, :, :])
                    pp = 0
                    for move in bestmoves:
                        branch_num = root_num + pp*self.eval_pos**(self.level-ii-1)
                        scores_moves[branch_num]=(scores[pp], scores_moves[branch_num][1])
                        board_me_all[branch_num, :, :] = null_el + board_me_root
                        board_op_all[branch_num, :, :] = null_el + board_op_root
                        # self.grphx.draw_board(board_me_all[branch_num, :, :], board_op_all[branch_num, :, :])
                        # self.grphx.get_input()
                        # print('===========================')
                        # print('critical check start')
                        # print(board_op_all[branch_num, :, :])
                        board_op_all[branch_num, :, :][move[0]] = 1
                        board_op_all[branch_num, :, :][move[1]] = 1
                        # print(board_op_all[branch_num, :, :])
                        # print('critical check end')
                        # print('===========================')
                        # print('opponent turn, root, branch:',root_num, branch_num)
                        # self.grphx.draw_board(board_me_all[branch_num, :, :], board_op_all[branch_num, :, :])
                        # self.grphx.get_input()
                        pp += 1
        # evaluate tree
        pp = 0
        print(scores_moves)
        while len(scores_moves)>1:
            for ii in range(int(len(scores_moves)/self.eval_pos)):
                pos_1 = ii*self.eval_pos
                if pp % 2==0:
                    for jj in range(self.eval_pos):
                        pos_2 = ii*self.eval_pos+jj
                        if scores_moves[pos_2][0]<scores_moves[pos_1][0]:
                            scores_moves[pos_1] = (scores_moves[pos_2][0],scores_moves[pos_1][1])
                            scores_moves[ii] = (scores_moves[pos_2][0], scores_moves[ii][1])
                else:
                    for jj in range(self.eval_pos):
                        pos_2 = ii*self.eval_pos+jj
                        if scores_moves[ii*self.eval_pos+jj][0]>scores_moves[ii*self.eval_pos][0]:
                            scores_moves[pos_1] = (scores_moves[pos_2][0],scores_moves[pos_1][1])
                            scores_moves[ii] = (scores_moves[pos_2][0], scores_moves[ii][1])
            del scores_moves[int(len(scores_moves)/self.eval_pos):]
            pp += 1
        print(scores_moves)
        return scores_moves[0][1]

    def find_best_mvs(self, board_me, board_op):
        """finds best local moves"""
        moves = []
        best1 = self.apriori_1(board_me, board_op)
        #print("Best 1", best1)
        for ii in range(self.eval_pri[0]):
            best2 = self.apriori_2(board_me, board_op,best1[ii])
         #   print("Best 2", best2)
            for jj in range(self.eval_pri[1]):
                moves.append((best1[ii],best2[jj]))
        bestmoves, scores = self.aposteriori(board_me, board_op, moves)
        return bestmoves, scores

    def apriori_1(self, board_me, board_op):
        """evaluate board before making 1st move"""
        B_M, B_O = self.count_mat(board_me, board_op, 4)
        B_eval = sum(B_M*self.me_pri_1 + B_O*self.op_pri_1)
        bestmoves = self.top_n_indexes(B_eval, self.eval_pri[0])
        return bestmoves

    def apriori_2(self, board_me, board_op, move1):
        """evaluate board before making 2nd move"""
        board_me_virt = np.zeros((self.bs,self.bs)) + board_me
        board_me_virt[move1] = 1
        B_M, B_O = self.count_mat(board_me_virt, board_op, 5)
        B_eval = sum(B_M*self.me_pri_2 + B_O*self.op_pri_2)
        bestmoves = self.top_n_indexes(B_eval, self.eval_pri[1])
        return bestmoves

    def count_mat(self, board_me, board_op, n_max):
        """evaluate board by checking the number of stones adjacent to each
        point of the board. outpiut are 5 matrices"""
        B_M = np.zeros((n_max,self.bs,self.bs))
        B_O = np.zeros((n_max,self.bs,self.bs))
        for ind_list in self.c6.ind_list_collect:
            B_M_loop = np.zeros((n_max,self.bs,self.bs))
            B_O_loop = np.zeros((n_max,self.bs,self.bs))
            for slot in ind_list:
                check_me = min(int(sum(board_me[slot])),n_max)
                check_op = min(int(sum(board_op[slot])),n_max)
                if check_me>=1 and check_op==0:
                    B_M_loop[check_me-1,:,:][slot] = 1
                elif check_op>=1 and check_me==0:
                    B_O_loop[check_op-1,:,:][slot] = 1
            B_M += B_M_loop
            B_O += B_O_loop
        B_M = self.only_free(B_M, board_me, board_op)
        B_O = self.only_free(B_O, board_me, board_op)
        return B_M, B_O

    def count_num(self, board_me, board_op):
        """evaluate board by counting total number of slots with numbers up to
        n_max. output are n_max numbers"""
        B_M = np.zeros((6))
        B_O = np.zeros((6))
        for ind_list in self.c6.ind_list_collect:
            for slot in ind_list:
                check_me = int(sum(board_me[slot]))
                check_op = int(sum(board_op[slot]))
                if check_me>=1 and check_me<=6 and check_op==0:
                    B_M[check_me-1] += 1
                elif check_op>=1 and check_op<=6 and check_me==0:
                    B_O[check_op-1] += 1
        return B_M, B_O

    def only_free(self,B, board_me, board_op):
        """gets rid of occupied spaces"""
        # multiply with free spaces
        board_free = np.remainder(board_me + board_op + np.ones((self.bs,self.bs)),2)
        B *= board_free
        return B

        return bestmoves

    def aposteriori(self, board_me, board_op, moves):
        """evaluate board after making two moves"""
        # only unique moves
        ii = 0
        while ii<len(moves):
            moves[ii] = (moves[ii][1],moves[ii][0])
            moves = list(set(moves))
            ii += 1
        # evaluate moves
        checklist = []
        scores = []
        for checkmove in moves:
            board_me_virt = np.zeros((self.bs,self.bs)) + board_me
            board_me_virt[checkmove[0]] = 1
            board_me_virt[checkmove[1]] = 1
            B_M, B_O = self.count_num(board_me_virt, board_op)
            score = sum(B_M*self.me_pos-B_O*self.op_pos)
            checklist.append(checkmove)
            scores.append(-score)
        if len(checklist)>0:
                moves = checklist
                moves = [x for y, x in sorted(zip(scores,checklist))]
                scores=sorted(scores)
                del moves[self.eval_pos:]
                del scores[self.eval_pos:]
        return moves, scores

    @ staticmethod
    def top_n_indexes(array, n):
        """function gets indices in form of tuples of n largest entries of array"""
        inds = np.argpartition(array, array.size-n, axis=None)[-n:]
        width = array.shape[1]
        return [divmod(i, width) for i in inds]

# bot to play random moves
class PlayRand:
    """class decides which move the bot makes"""
    def __init__(self, which_player, bs, c6, grpxh):
        self.which_player=which_player # lets instance know which player it is ('PLayer1' or 'Player2')
        self.bs=bs
        self.c6=c6

    def getmove(self, board_me, board_opponent, turn, time):
        if turn==1:
            move1=(int(self.bs/2),int(self.bs/2))
            return move1
        elif turn==int(self.bs**2/2)+1 and self.bs**2%2==0:
            valid1=False
            while not valid1:
                move1=(random.randint(0,self.bs),random.randint(0,self.bs))
                valid1=self.c6.is_valid_location(move1, board_me, board_opponent)
            return move1
        valid1=valid2=False
        move1=move2=[0,0]
        while not valid1 or not valid2 or move1==move2:
            move1=(random.randint(0,self.bs),random.randint(0,self.bs))
            move2=(random.randint(0,self.bs),random.randint(0,self.bs))
            valid1=self.c6.is_valid_location(move1, board_me, board_opponent)
            valid2=self.c6.is_valid_location(move2, board_me, board_opponent)
        return move1, move2



### end-----------------------------------------------------------------------

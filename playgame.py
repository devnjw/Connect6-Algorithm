###### This programm plays connect6
### import---------------------------------------------------------------------
import numpy as np  # math
import pickle       # saving and loading
import random       # random numbers
import contextlib
import pygame as pg # graphics without pygame output
import sys  # system for exiting the game

# import bot class
from Bot import PlayRand
from Bot import E6

### fixed global variables-----------------------------------------------------
bs=19   # size of board
win=6   # streak of stones needed to win
num_obstacle=4
cnt = 1

### define colors--------------------------------------------------------------
yellow=(200,200,0)
green=(82, 255, 177)
orange=(255, 177, 82)
red=(200,0,0)
blue=(89, 139, 255)
white=(255,255,255)
darkwhite=(190,190,190)
lightgrey=(70,70,70)
darkgrey=(25,25,25)
black=(0,0,0)

### dictionaries----------------------------------------------------------------
# variables dict
var_dic={}
# bot dict: specifies which bot is used for each Player
bot_dic={}
bot_dic['Player1']=[E6,'Bot1']
bot_dic['Player2']=[E6,'Bot2']

### classes---------------------------------------------------------------------
# organize variables
class Init_all:
    """class intitializes everything"""
    def __init__(self):
        var_dic['pre']='new'    # load or new
        var_dic['nog']='game1'  # name of game
        var_dic['max_time']=10  # time limit
        var_dic['Player1']=Bot    # player1 human or bot
        var_dic['Player2']=Human  # player2 human or bot
        var_dic['char_obstacle']='0'

    def prepare(self):
        # initialize home screen, get variables
        home=HomeGraphics()
        var_dic=home.get_vars()
        # initialize and load game if necessary
        savegame=LoadSave()
        if var_dic['pre']=='load':
            game=savegame.load()
            p1, p2, c6, grphx=game.initialize()
        else:
            game=Gameplay()
            p1, p2, c6, grphx=game.initialize()
        # pass on instances
        return game, savegame, p1, p2, c6, grphx

# load and save
class LoadSave:
    """class loads and saves games"""
    def __init__(self):
        self.nog=var_dic['nog']

    def load(self):
        """load saved game"""
        f = open(self.nog, 'rb')
        game = pickle.load(f)
        f.close()
        return  game

    def save(self):
        """save game"""
        # save variables
        f = open(self.nog, 'wb')
        pickle.dump(game, f)
        f.close()

# Gameplay
class Gameplay:
    """class enables gameplay"""
    def __init__(self):
        self.max_time=var_dic['max_time']   # time limit for each player
        self.player1=var_dic['Player1']     # name of player1 (class)
        self.player2=var_dic['Player2']     # name of player2 (class)
        self.board_p1=np.zeros((bs,bs))     # set board for moves of player1
        self.board_p2=np.zeros((bs,bs))     # set board for moves of player2

        # for i in [(6,10), (10,11), (11, 9)]:
        #     self.board_p1[i] = 2
        #     self.board_p2[i] = 2

        self.hist=[]    # history of game
        self.turn=0     # turn number
        self.time_p1=0  # time of player1
        self.time_p2=0  # time of player2
        self.winner=None# winner of game,
        self.move=None  # last move made

    def initialize(self):
        """initialize the instances of player1 and player2"""
        c6=Connect6()   # inialize connect6 class
        c6.slot()       # initize list of indices
        grphx=GameGraphics()    # initialize game graphics
        p1=self.player1('Player1', c6, grphx)
        p2=self.player2('Player2', c6, grphx)
        return p1, p2, c6, grphx

    def make_obs(self):

        move_x=grphx.get_input()

        self.board_p1[move_x]=2
        self.board_p2[move_x]=2
x
    def make_move(self):
        """gets move from the player at turn"""
        # which players turn?
        px, board_px, board_py, time_px, which_player=self.which_player()

        # put the move on the board

        if self.turn==1:
            # get the move
            move_x=px.getmove(board_px, board_py, self.turn, time_px)

            self.move=(move_x,'--')
            if not c6.is_valid_location(move_x, board_px, board_py):
                self.winner=which_player
            board_px[move_x]=1
        else:
            # get the move
            move_x=px.getmove(board_px, board_py, self.turn, time_px)

            self.move=(move_x[0], move_x[1])
            if not (c6.is_valid_location(move_x[0], board_px, board_py) and c6.is_valid_location(move_x[1], board_px, board_py)):
                self.winner=which_player
            board_px[move_x[0]]=1
            board_px[move_x[1]]=1

    def which_player(self):
        """determine which players turn"""
        if (self.turn)%2==1:
            px=p1
            board_px=self.board_p1
            board_py=self.board_p2
            time_px=self.time_p1
            which_player='Player1'
        else:
            px=p2
            board_px=self.board_p2
            board_py=self.board_p1
            time_px=self.time_p2
            which_player='Player2'
        return px, board_px, board_py, time_px, which_player

    def visualize(self, move1=None, which_player=None):
        """plots current board"""
        if self.turn==1 or (self.turn==int(bs**2/2)+1 and bs**2%2==0) or move1==-1:
            grphx.draw_board(self.board_p1, self.board_p2)
        else:
            if move1==None:
                grphx.draw_board(self.board_p1, self.board_p2, self.move)
            else:
                grphx.draw_board(self.board_p1, self.board_p2, move1,which_player)
        pg.display.update()

    def save_hist(self):
        """adds move to history and saves variables"""
        self.hist.append(self.move)
        savegame.save() # save variables

    def over(self):
        """checks is game is over and stops game"""
        if self.winner != None:
            return True
        if c6.is_won(self.board_p1):
            self.winner='Player1'
            return True
        elif c6.is_won(self.board_p2):
            self.winner='Player2'
            return True
        if self.turn>bs**2/2:
            return True
        return False

    def after_eval(self):
        """output if game is over"""
        grphx.end_output(self.winner)
        grphx.get_input()

# Bot player
class Bot:
    """class decides which move the bot makes"""
    def __init__(self, which_player, c6, grphx):
        self.which_player=which_player # lets instance know which player it is ('PLayer1' or 'Player2')
        self.ext_bot=bot_dic[which_player][0](which_player, bs, c6, grphx)

    def getmove(self, board_me, board_opponent, turn, timeleft):
        """communicate to external bot"""
        if game.turn==1 or (turn==int(bs**2/2)+1 and bs**2%2==0):
            move1=self.ext_bot.getmove(board_me, board_opponent, turn, timeleft)
            return move1
        else:
            move1, move2=self.ext_bot.getmove(board_me, board_opponent, turn, timeleft)
            return move1, move2

# Human player
class Human:
    """class enables human  to play"""
    def __init__(self, which_player, c6, grphx):
        self.which_player=which_player # lets instance know which player it is ('PLayer1' or 'Player2')

    def getmove(self,board_me, board_opponent, turn, timeleft):
        """gets the move"""
        sure=False
        # self.which_player, turn: First move
        while not sure:
            sure=True
            valid=False
            # first move, yellow dot
            while not valid:
                move1=grphx.get_input()
                valid=c6.is_valid_location(move1, board_me, board_opponent)
            # visualize first move
            game.visualize(move1,self.which_player)
            if not turn==1 and not (turn==int(bs**2/2)+1 and bs**2%2==0):
                valid=False
                # Second move
                move2=[-1,-1]
                while not valid:
                    move2=grphx.get_input()
                    valid=c6.is_valid_location(move2, board_me, board_opponent)
                    # if same move, undo first one
                    if move2==move1:
                        sure=False
                        # yellow dot gone
                        game.visualize(-1)
        if not turn==1 and not (turn==int(bs**2/2)+1 and bs**2%2==0):
            return move1, move2
        else:
            return move1


# connect6 functions
class Connect6:
    """class contains functions about how to evaluate the board of connect6"""
    def __init__(self):
        self.ind_list_diag1=[]  # list of diagonal slots (first)
        self.ind_list_diag2=[]  # list of diagonal slots (second)
        self.ind_list_hor=[]    # list of horizontal slots
        self.ind_list_ver=[]    # list of vertical slots
        self.ind_list_collect=[]# list of lists above
        self.ind_list=[]        # list of all slots

    def is_won(self,board):
        """checks if the game is won for the player this board belongs to"""
        for slot in self.ind_list:
            board2 = np.where(board == 2, 0, board)
            # print(board)
            # print(board2)
            check= sum(board2[slot])
            if check>=win:
                return True
        return False

    def slot(self):
        """gives back a list of all indices for each slot. just needs to be ran
        one time"""
        indices_row, indices_col= np.indices((bs,bs))
        for ii in range(bs):
            for jj in range(bs-win+1):
                a = jj
                b = jj+win
                #horizontals
                rows=indices_row[ii,a:b]
                cols=indices_col[ii,a:b]
                self.ind_list.append((rows,cols))
                self.ind_list_hor.append((rows,cols))
                #verticals
                rows=indices_row[a:b,ii]
                cols=indices_col[a:b,ii]
                self.ind_list.append((rows,cols))
                self.ind_list_ver.append((rows,cols))
        #diagonals
        for ii in range(-(bs-win),bs-win+1):
            for jj in range(len(indices_row.diagonal(ii))-win+1):
                a = jj
                b = jj+win
                rows=indices_row.diagonal(ii)[a:b]
                cols=indices_col.diagonal(ii)[a:b]
                self.ind_list.append((rows,cols))
                self.ind_list_diag1.append((rows,cols))
                rows=indices_row[::-1,:].diagonal(ii)[a:b]
                cols=indices_col[::-1,:].diagonal(ii)[a:b]
                self.ind_list.append((rows,cols))
                self.ind_list_diag2.append((rows,cols))

        # put lists together
        self.ind_list_collect=[self.ind_list_hor, self.ind_list_ver, self.ind_list_diag1, self.ind_list_diag2]

    def is_valid_location(self, move, board_me, board_opponent):
        """checks if the input was a valid location"""
        board=board_me+board_opponent
        if move[0] <= bs-1 and move[1] <= bs-1 and move[0]>=0 and move[1]>=0:
            if board_me[move]==0 and board_opponent[move]==0:
                return True
            else:
                # Spot is taken
                return False
        else:
            #  Move not within board
            return False

#  game graphics
class GameGraphics:
    """everything that is needed for the graphics while playing"""
    def __init__(self, windowsize=None):
        if windowsize==None:
            self.windowsize=780 # size of the displayed window
        else:
            self.windowsize=windowsize
        self.squaresize=round(self.windowsize/bs) # size of stones
        # initialize screen
        self.size=(self.windowsize,self.windowsize+50)
        pg.init()
        pg.display.set_mode(self.size)
        self.screen=pg.display.set_mode(self.size)

    def draw_board(self, board_p1, board_p2, move=None, which_player=None):
        """draw board"""
        a=self.squaresize
        # draw background
        self.screen.fill(darkgrey)
        for ii in range(bs):
            for jj in range(bs):
                # draw lines
                pg.draw.line(self.screen, lightgrey,(int((ii+0.5)*a), jj*a), (int((ii+0.5)*a), (jj+1)*a) ,1)
                pg.draw.line(self.screen, lightgrey,(ii*a,int((jj+0.5)*a)), ((ii+1)*a, int((jj+0.5)*a)) ,1)

                if ii in [3,9, 15 ]:
                    if jj in [3,9,15]:
                        pg.draw.circle(self.screen,darkwhite,(int((ii+0.5)*a),int((jj+0.5)*a)),int(a/(5)))

                # draw stones
                if board_p1[ii,jj]==1:
                    pg.draw.circle(self.screen,green,(int((ii+0.5)*a),int((jj+0.5)*a)),int(a/(2.1)))
                elif board_p2[ii,jj]==1:
                    pg.draw.circle(self.screen,orange,(int((ii+0.5)*a),int((jj+0.5)*a)),int(a/(2.1)))
                elif board_p2 [ii,jj] == 2:
                    pg.draw.circle(self.screen, blue, (int((ii + 0.5) * a), int((jj + 0.5) * a)), int(a / (2.1)))
        # highlite current move
        if move !=None and which_player==None:
            move1=move[0]
            move2=move[1]
            pg.draw.circle(self.screen, yellow,(int((move1[0]+0.5)*a),int((move1[1]+0.5)*a)), int(a/(5)))
            pg.draw.circle(self.screen, yellow,(int((move2[0]+0.5)*a),int((move2[1]+0.5)*a)), int(a/(5)))
        elif move !=None and which_player!=None:
            if which_player=='Player1':
                pg.draw.circle(self.screen,green,(int((move[0]+0.5)*a), int((move[1]+0.5)*a)),int(a/(2.1)))
            elif which_player=='Player2':
                pg.draw.circle(self.screen,orange,(int((move[0]+0.5)*a), int((move[1]+0.5)*a)),int(a/(2.1)))
            pg.draw.circle(self.screen, yellow,(int((move[0]+0.5)*a),int((move[1]+0.5)*a)), int(a/(5)))
        #update window
        pg.display.update()
        self.dummyinput()

    def get_input(self):
        """gets the input using pygame"""
        check=False
        while not check:
            for event in pg.event.get():
                if event.type==pg.QUIT:
                    sys.exit()
                if event.type==pg.MOUSEBUTTONDOWN:
                    move=(int(event.pos[0]/self.squaresize),int(event.pos[1]/self.squaresize))
                    pg.event.clear()
                    check=True
        return move

    def end_output(self,winner):
        # text for name of game input
        if winner==None:
            text='Game ended in draw. Click to play again'
        else:
            text=winner+' won! Click to play again'
        font=pg.font.SysFont('sathu', 28)
        txt_surface = font.render(text, True, blue)
        self.screen.blit(txt_surface, (0, self.squaresize*bs))
        #update window
        pg.display.update()

    def dummyinput(self):
        """function to solve problem of display for bot vs bot"""
        time_dummy=pg.time.get_ticks()
        while pg.time.get_ticks()<time_dummy+0.1:
            for event in pg.event.get():
                if event.type==pg.QUIT:
                    sys.exit()

# home screen graphics
class HomeGraphics:
    """graphics of home screen"""
    def __init__(self):
        self.width=600
        self.height=400
        pg.init()
        self.screen = pg.display.set_mode((self.width, self.height)) # set home screen
        self.font=pg.font.SysFont('sathu', 20)
        self.font1=pg.font.SysFont('sathu', 13)
        self.font2=pg.font.SysFont('sathu', 20)

        self.var_dic=var_dic
        self.start_box=pg.Rect(235, 300, 130, 32) # box for strating game
        self.input_box=pg.Rect(50, 80, 140, 32) # box for input nog
        self.obstacle_box=pg.Rect(400, 300, 80, 32) # box for obstacle number
        # positions for click choicers
        self.save_pos=(390, 100)
        self.load_pos=(460, 100)
        self.p1h_pos=(140, 200)
        self.p1b_pos=(240, 200)
        self.p2h_pos=(360, 200)
        self.p2b_pos=(460, 200)
        self.botswitch_box=pg.Rect(285,190,30,12)
        self.new_but=pg.Rect(0,0,0,0)
        self.load_but=pg.Rect(0,0,0,0)
        self.p1h_but=pg.Rect(0,0,0,0)
        self.p1b_but=pg.Rect(0,0,0,0)
        self.p2h_but=pg.Rect(0,0,0,0)
        self.p2b_but=pg.Rect(0,0,0,0)
        self.obstacle_but=pg.Rect(400,300,80,32)

    def get_vars(self):
        """display home screeen and gets input"""
        done=False
        # vars for input_box
        color_inactive = lightgrey
        color_active = white
        color = color_inactive
        active = False
        o_active = False # active for obstacle
        # var_dic entries
        nog = self.var_dic['nog']
        char_obstacle = self.var_dic['char_obstacle']

        # home screen
        self.home_screen()

        while not done:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    done = True
                    sys.exit()
                if event.type == pg.MOUSEBUTTONDOWN:
                    # start game?
                    if self.start_box.collidepoint(event.pos):
                        self.var_dic['nog']=nog
                        global num_obstacle
                        num_obstacle = int(char_obstacle)
                        done=True

                    # load or new?
                    if self.load_but.collidepoint(event.pos):
                        self.var_dic['pre']='load'
                    elif self.new_but.collidepoint(event.pos):
                        self.var_dic['pre']='new'
                        pg.draw.circle(self.screen, black, self.load_pos, 3)
                    # player1
                    if self.p1h_but.collidepoint(event.pos):
                        self.var_dic['Player1']=Human
                    elif self.p1b_but.collidepoint(event.pos):
                        self.var_dic['Player1']=Bot
                    # player2
                    if self.p2h_but.collidepoint(event.pos):
                        self.var_dic['Player2']=Human
                    elif self.p2b_but.collidepoint(event.pos):
                        self.var_dic['Player2']=Bot
                    # botswitch
                    if self.botswitch_box.collidepoint(event.pos):
                        bot_dic['Player1'], bot_dic['Player2']=bot_dic['Player2'], bot_dic['Player1']
                    # name of game
                    if self.input_box.collidepoint(event.pos):
                        # Toggle the active variable
                        active = not active
                    else:
                        active = False
                    # obstacle
                    if self.obstacle_box.collidepoint(event.pos):
                        # Toggle the active variable
                        o_active = not o_active
                    else:
                        o_active = False
                    # Change the current color of the input box
                    color = color_active if active else color_inactive
                if event.type == pg.KEYDOWN:
                    if active:
                        if event.key == pg.K_BACKSPACE:
                            nog = nog[:-1]
                        else:
                            nog += event.unicode
                    if o_active:
                        if event.key == pg.K_BACKSPACE:
                            char_obstacle = char_obstacle[:-1]
                        else:
                            char_obstacle += event.unicode

            # Render the current nog
            txt_surface = self.font.render(nog, True, color)


            # Resize the box if the nog is too long
            width = max(200, txt_surface.get_width()+10)
            self.input_box.w = width
            # home screen
            self.home_screen()
            # Blit the nog
            self.screen.blit(txt_surface, (self.input_box.x+5, self.input_box.y+5))

            # Render the current obstacle
            txt_surface = self.font.render(char_obstacle, True, color)
            # Blit the obs
            self.screen.blit(txt_surface, (self.obstacle_box.x+5, self.obstacle_box.y+5))

            # Blit the input_box rect
            pg.draw.rect(self.screen, color, self.input_box, 2)
            # update display
            pg.display.update()

        #self.name_to_player_class()
        return self.var_dic

    def home_screen(self):
        """creates home screen"""
        # background
        self.screen.fill(darkgrey)
        # start game button
        pg.draw.rect(self.screen, darkwhite, self.start_box)
        pg.draw.rect(self.screen, lightgrey, self.start_box,2)
        txt_surface = self.font.render('Start Game', True, blue)
        self.screen.blit(txt_surface, (self.start_box.x+5, self.start_box.y+5))

        # text for name of game input
        txt_surface = self.font.render('Save as:', True, green)
        self.screen.blit(txt_surface, (self.input_box.x+5, self.input_box.y-30))

        # text for the number of obstacle
        pg.draw.rect(self.screen, white, self.obstacle_box)
        txt_surface = self.font.render('Obstacle Number:', True, white)
        self.screen.blit(txt_surface, (self.obstacle_box.x + 5, self.obstacle_box.y - 30))

        # click choicers
        # save, load
        self.new_but=pg.draw.circle(self.screen, white, self.save_pos, 10)
        txt_surface = self.font.render('New', True, green)
        self.screen.blit(txt_surface, (self.new_but.x-10, self.new_but.y-30))
        self.load_but=pg.draw.circle(self.screen, white, self.load_pos, 10)
        txt_surface = self.font.render('Load', True, green)
        self.screen.blit(txt_surface, (self.load_but.x-10, self.load_but.y-30))
        if self.var_dic['pre']=='load':
            pg.draw.circle(self.screen, black, self.load_pos, 3)
        elif self.var_dic['pre']=='new':
            pg.draw.circle(self.screen, black, self.save_pos, 3)
        # player1
        self.p1h_but=pg.draw.circle(self.screen, white, self.p1h_pos, 10)
        self.p1b_but=pg.draw.circle(self.screen, white, self.p1b_pos, 10)
        txt_surface = self.font.render('Player1', True, red)
        self.screen.blit(txt_surface, (self.p1h_but.x+22, self.p1h_but.y-25))
        txt_surface = self.font.render('Human', True, green)
        self.screen.blit(txt_surface, (self.p1h_but.x-20, self.p1h_but.y+25))
        txt_surface = self.font.render(bot_dic['Player1'][1], True, green)
        self.screen.blit(txt_surface, (self.p1b_but.x-10, self.p1h_but.y+25))
        if self.var_dic['Player1']==Human:
            pg.draw.circle(self.screen, black, self.p1h_pos, 3)
        elif self.var_dic['Player1']==Bot:
            pg.draw.circle(self.screen, black, self.p1b_pos, 3)
        # player2
        self.p2h_but=pg.draw.circle(self.screen, white, self.p2h_pos, 10)
        self.p2b_but=pg.draw.circle(self.screen, white, self.p2b_pos, 10)
        txt_surface = self.font.render('Player2', True, red)
        self.screen.blit(txt_surface, (self.p2h_but.x+22, self.p2h_but.y-25))
        txt_surface = self.font.render('Human', True, green)
        self.screen.blit(txt_surface, (self.p2h_but.x-20, self.p1h_but.y+25))
        txt_surface = self.font.render(bot_dic['Player2'][1], True, green)
        self.screen.blit(txt_surface, (self.p2b_but.x-10, self.p1h_but.y+25))
        if self.var_dic['Player2']==Human:
            pg.draw.circle(self.screen, black, self.p2h_pos, 3)
        elif self.var_dic['Player2']==Bot:
            pg.draw.circle(self.screen, black, self.p2b_pos, 3)
        # botswitch
        pg.draw.rect(self.screen,blue,self.botswitch_box)
        txt_surface = self.font1.render('Switch', True, lightgrey)
        self.screen.blit(txt_surface,(self.botswitch_box.x-8,self.botswitch_box.y-15))

### game-----------------------------------------------------------------------
# initialize game
start=Init_all()
game, savegame, p1, p2, c6, grphx=start.prepare()
game.visualize()

# make move
#game.make_obstacle()
#game.make_obstacle()
# visualize move
#game.visualize()
# save history
#game.save_hist()
for _ in range(num_obstacle):
    game.make_obs()
    game.visualize()

# play game
while game.turn<int(bs**2/2)+2:
    # start new game
    if game.over():
        game.after_eval()
        game, savegame, p1, p2, c6, grphx=start.prepare()
        game.visualize()
    if not game.over():
        # turn
        game.turn+=1
        # make move
        game.make_move()
        # visualize move
        game.visualize()
        # save history
        game.save_hist()

### end------------------------------------------------------------------------

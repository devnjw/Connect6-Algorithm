# ====================
# 컨넥트4
# ====================

# 패키지 임포트
import random
import math
import numpy as np


# 게임 상태
class State:
    # 초기화
    def __init__(self, pieces=None, enemy_pieces=None, obstacle_pieces=None, legal_area=None, last_two=None, isFive=None):
        # 돌의 배치
        self.pieces = pieces if pieces != None else [0] * (361)
        self.enemy_pieces = enemy_pieces if enemy_pieces != None else [0] * (361)
        self.obstacle_pieces = obstacle_pieces if obstacle_pieces != None else [0] * (361)
        self.isFive = isFive if isFive != None else [0] * (3) # isFive, next action 1, next action 2

        self.legal_area = legal_area if legal_area != None else [0] * (361)
        self.last_two = last_two if last_two != None else [0] * (2)

    # 돌의 수 얻기
    def piece_count(self, pieces):
        count = 0
        for i in pieces:
            if i == 1:
                count += 1
        return count

    def is_risk(self):
        def put_case(x, y, dx, dy):
            for k in range(6):
                if y < 0 or 18 < y or x < 0 or 18 < x or \
                        self.enemy_pieces[x + y * 19] == 0:
                    return False
                x, y = x + dx, y + dy

        last_two = self.last_two.copy()
        x1, y1 = last_two[0]%19, last_two[0]//19
        x2, y2 = last_two[1]%19, last_two[1]//19


        return False


    # 패배 여부 판정
    def is_lose(self):
        last_two = self.last_two.copy()
        x1, y1 = last_two[0]%19, last_two[0]//19
        x2, y2 = last_two[1]%19, last_two[1]//19

        # 돌 6개 연결 여부 판정
        def is_comp(x, y, dx, dy):
            cnt = 0
            for _ in range(11):
                if y < 0 or 18 < y or x < 0 or 18 < x or \
                        self.enemy_pieces[x + y * 19] == 0:
                    cnt = 0
                else:
                    cnt += 1
                    if cnt >= 6: return True
                x, y = x + dx, y + dy
            return False

        # 패배 여부 판정
        if self.enemy_pieces[last_two[0]] == 1:
            if is_comp(x1-5, y1, 1, 0) or is_comp(x1, y1-5, 0, 1) or \
                    is_comp(x1-5, y1+5, 1, -1) or is_comp(x1-5, y1-5, 1, 1):
                    return True
        # 패배 여부 판정
        if self.enemy_pieces[last_two[1]] == 1:
            if is_comp(x2-5, y2, 1, 0) or is_comp(x2, y2-5, 0, 1) or \
                        is_comp(x2-5, y2+5, 1, -1) or is_comp(x2-5, y2-5, 1, 1):
                    return True

        return False

    # 무승부 여부 판정
    def is_draw(self):
        return self.piece_count(self.pieces) + self.piece_count(self.enemy_pieces) + self.piece_count(self.obstacle_pieces) == 361

    # 게임 종료 여부 판정
    def is_done(self):
        return self.is_lose() or self.is_draw()

    def put_obstacles(self):
        obstacle_pieces = self.obstacle_pieces.copy()
        for _ in range(0):
            action = np.random.choice(self.legal_actions())
            obstacle_pieces[action] = 1

        return State(self.enemy_pieces, self.pieces, obstacle_pieces)

    def expand_legal_area(self, action):
        legal_area = self.legal_area.copy()
        total_num_piece = self.piece_count(self.pieces) + self.piece_count(self.enemy_pieces)
        diff = 1 if total_num_piece <= 10 else 2

        x = action%19
        y = action//19
        for i in range(x-diff, x+diff+1):
            for j in range(y-diff, y+diff+1):
                if (i + j*19) >= 0 and (i + j*19) < 361:
                    legal_area[i + j*19] = 1
        return legal_area

    def update_last_two(self, action):
        last_two = self.last_two.copy()
        last_two[0] = last_two[1]
        last_two[1] = action
        return last_two

    # 다음 상태 얻기
    def next(self, action):
        pieces = self.pieces.copy()
        last_two = self.update_last_two(action)
        legal_area = self.expand_legal_area(action)

        pieces[action] = 1

        total_num_piece = self.piece_count(self.pieces) + self.piece_count(self.enemy_pieces)

        if total_num_piece % 4 == 0 or total_num_piece % 4 == 2:
            return State(self.enemy_pieces, pieces, self.obstacle_pieces, legal_area, last_two)
        else:
            return State(pieces, self.enemy_pieces, self.obstacle_pieces, legal_area, last_two)

    # 합법적인 수 리스트 얻기
    def legal_actions(self):
        actions = []

        total_num_piece = self.piece_count(self.pieces) + self.piece_count(self.enemy_pieces)
        if total_num_piece is 0:
            actions.append(180)
            return actions

        for i in range(361):
            if self.legal_area[i] == 1:
                if self.pieces[i] == 0 and self.enemy_pieces[i] == 0 and self.obstacle_pieces[i] == 0:
                    actions.append(i)
        return actions

    # 선 수 여부 확인
    def is_first_player(self):
        total_num_piece = self.piece_count(self.pieces) + self.piece_count(self.enemy_pieces)

        if total_num_piece % 4 == 0 or total_num_piece % 4 == 3:
            return True
        else: return False

    def was_first_player(self):
        total_num_piece = self.piece_count(self.pieces) + self.piece_count(self.enemy_pieces)
        return total_num_piece % 4 == 0 or total_num_piece % 4 == 1

    # 문자열 표시
    def __str__(self):
        ox = ('o', 'x', 'b') if self.is_first_player() else ('x', 'o', 'b')
        str = ''
        for i in range(361):
            if self.pieces[i] == 1:
                str += ox[0]
            elif self.enemy_pieces[i] == 1:
                str += ox[1]
            elif self.obstacle_pieces[i] == 1:
                str += ox[2]
            else:
                str += '-'
            if i % 19 == 18:
                str += '\n'
        return str


# 랜덤으로 행동 선택
def random_action(state):
    legal_actions = state.legal_actions()
    return legal_actions[random.randint(0, len(legal_actions) - 1)]


# 동작 확인
if __name__ == '__main__':
    # 상태 생성
    state = State()
    state = state.put_obstacles()

    # 게임 종료 시까지 반복
    while True:
        # 게임 종료 시
        if state.is_done():
            break

        # 다음 상태 얻기
        state = state.next(random_action(state))

        # 문자열 표시
        print(state)
        print()

import random
import math

def new_game(self,sizes,mines):
    self.rows=sizes[0]
    self.cols=sizes[1]
    self.mines=mines
    # 首次点击需保证开空
    self.first_click = True
    self.create_widgets()
    self.mine_coords = set()
    self.revealed = set()
    self.marked = set()
    self.place_mines()
    self.calculate_numbers()
    self.mode="tradition"
    self._update_training_panel_visibility()
    
def find_mine(self):
    # 读取面板参数
    try:
        fm_rows = max(2, int(self.find_mine_rows_var.get()))
    except Exception:
        fm_rows = 16
    try:
        fm_cols = max(2, int(self.find_mine_cols_var.get()))
    except Exception:
        fm_cols = 30
    try:
        fm_mines = max(1, min(int(self.find_mine_mines_var.get()), fm_rows * fm_cols - 1))
    except Exception:
        fm_mines = 99
    # 回写栄位（确保显示尺寸一致）
    try:
        self.find_mine_rows_var.set(fm_rows)
        self.find_mine_cols_var.set(fm_cols)
        self.find_mine_mines_var.set(fm_mines)
    except Exception:
        pass


    self.new_game((fm_rows, fm_cols), fm_mines)
    for r in range(16):
        for c in range(30):
            if self.numbers.get((r,c),None)==0:
                self.reveal(r,c)
    optional_lst=[]
    for r in range(16):
        for c in range(30):
            if (r,c) in self.revealed or (r,c) in self.mine_coords:
                continue
            else:
                optional_lst.append((r,c))
    choice_coord=random.choice(optional_lst)        
    optional_lst.remove(choice_coord)
    for coord in optional_lst:
        self.reveal(coord[0],coord[1])
    

        '''
        def unique():
            infor_lst=[]
            array_lst=[]
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    array_lst.append((dr,dc))
                    nr, nc = r+dr, c+dc
                    if 0 <= nr < self.rows and 0 <= nc < self.cols and (nr, nc) in self.revealed:
                        infor_lst.append((nr,nc))
            if len(infor_lst)==0

            
            for (dr,dc) in array_lst:
                judge_coord=(infor_lst[0][0]+dr,infor_lst[0][1]+dc)
                for i in range(1,len(infor_lst))
        '''

        
        
        
    self.mode="find_mine"
    self._update_training_panel_visibility()

def exercise1(self):
    sizes=(4,30)
    self.rows=sizes[0]
    self.cols=sizes[1]
    self.create_widgets()
    self.mine_coords = set()
    self.revealed = set()
    self.marked = set()
    self.mines=0
    def generate_binary_list(k):
        #没有三连0
        lst = []
        # 第一位
        lst.append(random.choice([0,1]))            
        # 第二位
        lst.append(1 if lst[0] == 0 else random.choice([0,1]))            
        for _ in range(k):
            if len(lst) >= 2 and lst[-1] == 0 and lst[-2] == 0:
                lst.append(1)                    
            else:
                lst.append(random.choice([0,1]))
        return lst
    frmine_lst=generate_binary_list(30)
    for c in range(30):
        if not frmine_lst[c]:
            self.mine_coords.add((0,c))
#         while len(self.mine_coords) < self.mines-10: #特殊布雷
#             r = random.randint(0, 1)
#             c = random.randint(0, self.cols-1)
#             if r==0:
#                 self.mine_coords.add((0, c))
#             else:
#                 self.mine_coords.add((2, c))
    srmine_lst = generate_binary_list(28)
    self.mine_coords.add((2,1))
    for c in range(28):
        if srmine_lst[c]:            
            self.mine_coords.add((2,c+2))
    for _ in range(10):
        self.mine_coords.add((3,3*_+1))
    self.calculate_numbers()
    self.reveal(2,0)
    for c in range(self.cols):
        self.reveal(1,c)
        if (0,c) in self.mine_coords:
            self.mark_mine(0,c)
        else:
            self.reveal(0,c)
    self.mode="exercise1"    
    self._update_training_panel_visibility()
    
def exercise2(self):
    self.mines=0
    sizes=(5,6)
    self.rows=sizes[0]
    self.cols=sizes[1]
    self.create_widgets()
    self.mine_coords = set()
    self.revealed = set()
    self.marked = set()
    def generate_binary_list(k):
        lst = []
        # 第一位
        lst.append(random.choice([0,1]))            
        # 第二位
        lst.append(1 if lst[0] == 0 else random.choice([0,1]))            
        for _ in range(k):
            if len(lst) >= 2 and lst[-1] == 0 and lst[-2] == 0:
                lst.append(1)                    
            else:
                lst.append(random.choice([0,1]))
        return lst
    srmine_lst=generate_binary_list(4)
    for c in range(4):
        if not srmine_lst[c]:
            self.mine_coords.add((1,c))
    mine_lsts=[[0,1],[0,2],[1,2],[1]]
    mine_lst=random.choice(mine_lsts)
    for c in mine_lst:
        self.mine_coords.add((3,c))
    self.mine_coords.add((4,4))
    self.mine_coords.add((2,3))
    self.calculate_numbers()
    for c in range(self.cols):
        self.reveal(0,c)
        if (1,c) in self.mine_coords:
            self.mark_mine(1,c)
        else:
            self.reveal(1,c)
            
        if (2,c) in self.mine_coords:
            self.mark_mine(2,c)
        else:
            self.reveal(2,c)
    self.reveal(3,3)
    self.mode="exercise2" 
    self._update_training_panel_visibility()

def exercise3(self):
    self.mines=0
    sizes=(5,7)
    self.rows=sizes[0]
    self.cols=sizes[1]
    self.create_widgets()
    self.mine_coords = set()
    self.revealed = set()
    self.marked = set()
    def generate_binary_list(k):
        lst = []           
        # 第一位
        lst.append(random.choice([0,1]))            
        # 第二位
        lst.append(1 if lst[0] == 0 else random.choice([0,1]))            
        for _ in range(k):
            if len(lst) >= 2 and lst[-1] == 0 and lst[-2] == 0:
                lst.append(1)                    
            else:
                lst.append(random.choice([0,1]))
        return lst
    srmine_lst=generate_binary_list(5)
    for c in range(5):
        if not srmine_lst[c]:
            self.mine_coords.add((1,c))
    mine_lsts=[[1,2],[0,3],[1,3],[0,2],[1,2,3],[0,1,2],[0,1,3],[0,2,3]]
    mine_lst=random.choice(mine_lsts)
    for c in mine_lst:
        self.mine_coords.add((3,c))  #第四行布雷
    self.mine_coords.add((4,5))
    self.mine_coords.add((2,4))
    self.calculate_numbers()
    for c in range(self.cols):
        self.reveal(0,c)
        if (1,c) in self.mine_coords:  #处理第二行
            self.mark_mine(1,c)
        else:
            self.reveal(1,c)
            
        if (2,c) in self.mine_coords:   #处理第三行
            self.mark_mine(2,c)
        else:
            self.reveal(2,c)
    self.reveal(3,4)
    self.mode="exercise3" 
    self._update_training_panel_visibility()







#高级训练！！！
def training_mode(self, n=None, s1=None, s2=None, d=None, p=None, three_con=None,
                  lst=None,lst2=None,mine_left=None,mine_right=None):

    cfg = self._sanitize_training_settings()
    random_mode = cfg.get('random_mode', False)
    if random_mode:
        if n is None:
            n = self._sample_random_training_n()
        if s1 is None:
            s1 = random.choice((1, 2, 3))
        if s2 is None:
            s2 = random.choice((1, 2, 3))
    else:
        if n is None:
            n = cfg['n']
        if s1 is None:
            s1 = cfg['s1']
        if s2 is None:
            s2 = cfg['s2']
    if d is None:
        d = cfg['d']
    if p is None:
        p = cfg['p']

    if three_con is None:
        three_con = cfg['three_con']
    if random_mode:
        try:
            # 随机模式下将本题参数写回设置变量，而不是仅用临时局部变量
            self.training_n_var.set(int(n))
            self.training_s1_var.set(int(s1))
            self.training_s2_var.set(int(s2))
            self._sync_training_label_vars()
            self.save_settings()
        except Exception:
            pass
    self._set_training_case_info(n, s1, s2, d, p, three_con, random_mode)
    #0
    self.mines=0
    self.rows=6
    col=n
    k=0
    k1=0
    if s1==1:
        t1=0
        col+=t1
        k1+=1
        k+=1
    elif s1==2:
        t1=3
        col+=t1
        k+=1
    elif s1==3:
        t1=5
        col+=t1
    if s2==1:
        t2=0
        k1+=1
        k+=1
    elif s2==2:
        t2=3
        col+=t2
        k+=1
    elif s2==3:
        t2=5
        col+=t2
    self.cols=col   
    self.create_widgets()
    #清盘
    self.mine_coords = set()
    self.revealed = set()
    self.marked = set()

    #1 雷行算法
    n1=n+2-k1 
   


    def generate_sequence(n, p, constraint_type=1):
        """
        n: 序列长度
        p: 密度参数 [0, 1]
        constraint_type: 
            1 - 仅满足：没有连续三个 1
            2 - 满足：没有连续三个 1；且 1与2不能同时选中
            3 - 满足：没有连续三个 1；且 1与2不能同时选中，且 n-1与n不能同时选中
        """
        if n <= 0: return []
        if n == 1: return [1] if random.random() < p else [0]

        # 将 p 映射为权重 w (exp映射使 p 在 [0.1, 0.9] 之间时密度变化更线性)
        w = math.exp(p * 6 - 3) 

        # dp[i][j] 表示前 i 个数，末尾连续选了 j 个 1 的权重
        dp = [[0.0] * 3 for _ in range(n + 1)]
        
        # 初始化 i=1
        dp[1][0] = 1.0
        dp[1][1] = w
        
        # 正向计算权重
        for i in range(2, n + 1):
            # 状态 0: 当前不选
            dp[i][0] = dp[i-1][0] + dp[i-1][1] + dp[i-1][2]
            
            # 状态 1: 当前选，前一个没选
            dp[i][1] = dp[i-1][0] * w
            
            # 状态 2: 当前选，前一个也选了
            if (constraint_type >= 2) and (i == 2):
                # 情况2和3：强制 1,2 不同选
                dp[i][2] = 0.0
            else:
                dp[i][2] = dp[i-1][1] * w

        # 
        if (constraint_type == 3):
            # 强制 n-1, n 不同选 (即不能以状态2结束)
            dp[n][2] = 0.0

        # 反向回溯采样
        sequence = [0] * n
        total_w = sum(dp[n])
        if total_w <= 0: return [0] * n
        
        # 抽取最后一个位置的状态
        r = random.uniform(0, total_w)
        if r < dp[n][0]: curr_state = 0
        elif r < dp[n][0] + dp[n][1]: curr_state = 1
        else: curr_state = 2
            
        for i in range(n, 0, -1):
            sequence[i-1] = 1 if curr_state > 0 else 0
            if i == 1: break
            
            if curr_state == 2:
                curr_state = 1
            elif curr_state == 1:
                curr_state = 0
            else:
                # 当前没选，按比例回溯上一个状态
                prev_sum = sum(dp[i-1])
                r_p = random.uniform(0, prev_sum)
                if r_p < dp[i-1][0]: curr_state = 0
                elif r_p < dp[i-1][0] + dp[i-1][1]: curr_state = 1
                else: curr_state = 2
                    
        return sequence

    if lst is None:
        lst=[]
        if three_con:
            for _ in range(k):
                if random.random()<p:
                    lst.append(1)
                else:
                    lst.append(0)
        else:
            if s1==1 and s2==1:
                lst=generate_sequence(n1,p,3)
            elif s1==1 or s2==1:
                lst=list(reversed(generate_sequence(n1,p,2))) if s2==1 else generate_sequence(n1,p,2)
            else:
                lst=generate_sequence(n1,p,1)
        
    
          

        
    #2难度选择

    def generate_sequence_advanced(n, p, d, constraint_type):
        """
        n: 长度
        p: 1的密度参数 [0, 1]
        d: 模式 (1:禁111, 2:禁000, 3:双禁)
        constraint_type: 
            1 - 无边际限制
            2 - 限制1&2: d=1时不能同为1, d=2时不能同为0, d=3时既不能同1也不能同0
            3 - 限制1&2 且 n-1&n: 规则同上
        """
        if n <= 0: return []
        if n == 1: return [1] if random.random() < p else [0]
        
        # 权重分配
        w = math.exp(p * 6 - 3)
        
        # 状态定义：-2(连00), -1(单0), 1(单1), 2(连11)
        all_states = [-2, -1, 1, 2]
        dp = [ {s: 0.0 for s in all_states} for _ in range(n + 1) ]
        
        # 初始化 i=1
        dp[1][-1] = 1.0  # 第一个选0
        dp[1][1] = w     # 第一个选1

        for i in range(2, n + 1):
            # --- 转移逻辑 ---
            # 变成单0 (-1): 前一个状态必须是 1 或 2
            dp[i][-1] = dp[i-1][1] + dp[i-1][2]
            
            # 变成连00 (-2): 前一个状态必须是 -1
            # 如果 d=1，-2代表“2个或更多0”；如果 d=2/3，最多只能连两个0
            dp[i][-2] = dp[i-1][-1]
            if d == 1: dp[i][-2] += dp[i-1][-2]

            # 变成单1 (1): 前一个状态必须是 -1 或 -2
            dp[i][1] = (dp[i-1][-1] + dp[i-1][-2]) * w
            
            # 变成连11 (2): 前一个状态必须是 1
            # 如果 d=2，2代表“2个或更多1”；如果 d=1/3，最多只能连两个1
            dp[i][2] = dp[i-1][1] * w
            if d == 2: dp[i][2] += dp[i-1][2] * w

            # --- 处理限制 2 (1&2 的边际约束) ---
            if i == 2 and constraint_type >= 2:
                if d == 1 or d == 3:
                    dp[2][2] = 0.0  # 禁止 1,2 同时为 1
                if d == 2 or d == 3:
                    dp[2][-2] = 0.0 # 禁止 1,2 同时为 0

        # --- 处理限制 3 (n-1&n 的边际约束) ---
        if constraint_type == 3:
            if d == 1 or d == 3:
                dp[n][2] = 0.0  # 禁止最后两个同为 1
            if d == 2 or d == 3:
                dp[n][-2] = 0.0 # 禁止最后两个同为 0

        # --- 反向回溯采样 ---
        sequence = [0] * n
        def get_state(weights_dict):
            s_list = list(weights_dict.keys())
            w_list = list(weights_dict.values())
            if sum(w_list) <= 0: return random.choice(s_list)
            return random.choices(s_list, weights=w_list)[0]

        curr_s = get_state(dp[n])
        for i in range(n, 0, -1):
            sequence[i-1] = 1 if curr_s > 0 else 0
            if i == 1: break
            
            prev_w = {s: 0.0 for s in all_states}
            if curr_s == -1:
                prev_w[1], prev_w[2] = dp[i-1][1], dp[i-1][2]
            elif curr_s == -2:
                prev_w[-1] = dp[i-1][-1]
                if d == 1: prev_w[-2] = dp[i-1][-2]
            elif curr_s == 1:
                prev_w[-1], prev_w[-2] = dp[i-1][-1], dp[i-1][-2]
            elif curr_s == 2:
                prev_w[1] = dp[i-1][1]
                if d == 2: prev_w[2] = dp[i-1][2]
                
            curr_s = get_state(prev_w)
                
        return sequence
                        

    #有解分析
    def judge(lst):
        #如果列表全为1
        if sum(lst)==len(lst):
            return False
        
        solu=False            
        if (s1==1 or s1==2) and (s2==1 or s2==2):
            if len(lst)%3!=2:
                solu=True
            else:
                k1,k2=0,1
                if lst[0]==lst[1]:
                    solu=True
                else:
                    while k1<len(lst):
                        if lst[k1]==lst[0]:
                            k1+=3
                        else:
                            solu=True
                            break
                    while k2<len(lst):
                        if lst[k2]==lst[1]:
                            k2+=3
                        else:
                            solu=True
                            break



        else:
            if s1==1 or s1 ==2:
                k1,k2=0,1
                if lst[0]==lst[1]:
                    solu=True
                else:
                    while k1<len(lst):
                        if lst[k1]==lst[0]:
                            k1+=3
                        else:
                            solu=True
                            break
                    while k2<len(lst):
                        if lst[k2]==lst[1]:
                            k2+=3
                        else:
                            solu=True
                            break
            elif s2==1 or s2==2:
                reve_lst=list(reversed(lst))
                k1,k2=0,1
                if reve_lst[0]==reve_lst[1]:
                    solu=True
                else:
                    while k1<len(lst):
                        if reve_lst[k1]==reve_lst[0]:
                            k1+=3
                        else:
                            solu=True
                            break
                    while k2<len(lst):
                        if reve_lst[k2]==reve_lst[1]:
                            k2+=3
                        else:
                            solu=True
                            break
            elif s1==3 and s2==3:
                if lst[0]==lst[1]==lst[2]:
                    solu=True
                solu_lst=[0,0,0]
                k1,k2,k3=0,1,2
                while k1<len(lst):
                    if lst[k1]==lst[0]:
                        k1+=3
                    else:
                        solu_lst[0]=1
                        break
                while k2<len(lst):
                    if lst[k2]==lst[1]:
                        k2+=3
                    else:
                        solu_lst[1]=1
                        break
                while k3<len(lst):
                    if lst[k3]==lst[2]:
                        k3+=3
                    else:
                        solu_lst[2]=1
                        break
                if sum(solu_lst)==0:
                    return False
                elif sum(solu_lst)==1:
                    if solu_lst[0]==1 and lst[1]!=lst[2]:
                        return False
                    elif solu_lst[1]==1 and lst[0]!=lst[2]:
                        return False
                    elif solu_lst[2]==1 and lst[0]!=lst[1]:
                        return False
                    else:
                        solu=True
                else:
                    solu=True
        return solu

    n2=n+2-k
    def generate2():
        if (s1==1 or s1==2) and (s2==1 or s2==2):
            lst2=generate_sequence_advanced(n2, 0.5, d, 3)
        elif s1==1 or s1==2:
            lst2=generate_sequence_advanced(n2, 0.5, d, 2)
        elif s2==1 or s2==2:
            lst2=list(reversed(generate_sequence_advanced(n2, 0.5, d, 2)))
        else:
            lst2=generate_sequence_advanced(n2, 0.5, d, 1)            
        return lst2
    
    if lst2 is None:        
        solu=False
        while not solu :
            lst2=generate2()
            solu=judge(lst2)
        


    #开始布雷
    #雷行，墙从0开始， 闭从2开始，开从4开始
    if s1==1:
        mine_dist=0
    if s1==2:
        mine_dist=2
    if s1==3:
        mine_dist=4
    
    for c in range(len(lst)):
        if lst[c] :
            self.mine_coords.add((2,c+mine_dist))
    
    #第四行小雷

    if s1==1:
        pass
    if s1==2:
        self.mine_coords.add((3,mine_dist))
    if s1==3:
        self.mine_coords.add((3,mine_dist))
    if s2==1:
        pass
    if s2==2:
        self.mine_coords.add((3,self.cols-1-2))
    if s2==3:
        self.mine_coords.add((3,self.cols-1-4))

    #第五行判雷区域

    if s1==1:
        train_dist=0
    if s1==2:
        train_dist=3
    if s1==3:
        train_dist=4
    for c in range(len(lst2)):
        if lst2[c] :
            self.mine_coords.add((4,c+train_dist))
    #第五行可选雷

    if s1==2:
        if mine_left is None:
            if random.random()<p:
                self.mine_coords.add((4,2))
        else:
            if mine_left:
                self.mine_coords.add((4,2))
    if s2==2:
        if mine_right is None:
            if random.random()<p:
                self.mine_coords.add((4,self.cols-1-2))
        else:
            if mine_right:
                self.mine_coords.add((4,self.cols-1-2))


    #泛化最后一行

    if col%3==0:
        fan=1
        while fan<col:
            self.mine_coords.add((5,fan))
            fan+=3
            
    if col%3!=0:
        fan=0
        while fan<col:
            self.mine_coords.add((5,fan))
            fan+=3
            
    #泛化倒数第二行

    if s1==3:
        if (4,4) not in self.mine_coords:
            self.mine_coords.add((4,0))
            self.mine_coords.add((4,3))
        else:
            self.mine_coords.add((4,1))
        if random.random()<0.5:
            self.mine_coords.add((4,2))
    if s2==3:
        if (4,col-5) not in self.mine_coords:
            self.mine_coords.add((4,col-1))
            self.mine_coords.add((4,col-4))
        else:
            self.mine_coords.add((4,col-2))
        if random.random()<0.5:
            self.mine_coords.add((4,col-3))

    self.calculate_numbers()

    #最后进行揭开和标旗操作
    self.reveal(0,0)
    for c in range(col):
        if (2,c) in self.mine_coords:  #处理第三行
            self.mark_mine(2,c)
        else:
            self.reveal(2,c)
            
        if (3,c) in self.mine_coords:   #处理第四行
            self.mark_mine(3,c)
        else:
            self.reveal(3,c)
    if s1==2:
        self.reveal(4,0)
        self.reveal(4,1)
        if (4,2) not in self.mine_coords:   
            self.reveal(4,2)
        else:
            self.mark_mine(4,2) 
    if s2==2:
        self.reveal(4,col-1)
        self.reveal(4,col-2)
        if (4,col-3) not in self.mine_coords:
            self.reveal(4,col-3)
        else:
            self.mark_mine(4,col-3)


    self.mode="training_mode" 
    self._update_training_panel_visibility()
    self._refresh_training_win_highlight({'s1': s1, 's2': s2})
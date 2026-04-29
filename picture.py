from minesweeper import Minesweeper
import tkinter as tk
import random
import math 
from save_image import save_board_canvas_image



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
    w = math.exp(p * 6 - 2) 

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



s1=2
s2=2
n=4 #n
lst2=[0,0,1,1,0,0] #lst2
dir_name="1221" #dir_name

mine_lst_n = n + (1 if s1 == 2 or s1==3 else 0) + (1 if s2 == 2 or s2 ==3 else 0)

lsts = []
seen_bases = set()

if s1==s2:
    rever=True
else:
    rever=False

if s1==1 and s2==1:
    constraint_type=3
elif s1==1:
    constraint_type=2
else:
    constraint_type=1


for i in range(2000):
    lst=generate_sequence(mine_lst_n, 0.5, constraint_type=constraint_type)
    if rever:
        base_key = min(tuple(lst), tuple(reversed(lst)))
    else:
        base_key = tuple(lst)
    if base_key not in seen_bases:
        print(base_key)
        seen_bases.add(base_key)

        left_options = [0, 1] if s1 == 2 else [0]
        right_options = [0, 1] if s2 == 2 else [0]
        for mine_left in left_options:
            for mine_right in right_options:
                lsts.append({
                    "lst": lst[:],
                    "mine_left": mine_left,
                    "mine_right": mine_right,
                })

#按lst的元素和排序
lsts.sort(key=lambda x: (
    sum(x["lst"]) + x["mine_left"] + x["mine_right"],   # 第一排序依据
    x["lst"]                                            # 第二排序依据
))
print(f"共生成 {len(lsts)} 个独特的样本")



root = tk.Tk()
root.title("闪电扫雷")
game = Minesweeper(master=root)



index = 0
root.after(1000, lambda: print("开始训练..."))
def run_next():
    global index
    if index >= len(lsts):
        return

    sample = lsts[index]
    new_lst = sample["lst"][:]
    mine_left = sample["mine_left"]
    mine_right = sample["mine_right"]

    game.training_mode(
        n=n, s1=s1, s2=s2, d=3, p=0.5, three_con=True,
        lst=new_lst, lst2=lst2, mine_left=mine_left, mine_right=mine_right
    )

    save_board_canvas_image(game.canvas, output_dir=dir_name, prefix=f'board_{index}')
    index += 1
    root.after(150, run_next)  # 替代 time.sleep(2)

root.after(100, run_next)
root.mainloop()
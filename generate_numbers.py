import random
import re

MAX_NUMBER = 52  # Lotto Max 号码范围 1-52

# 行首日期，如 "24th April 2026"；号码之间可能是 Tab、单空格或多空格
DATE_RE = re.compile(r'^\s*\d{1,2}(?:st|nd|rd|th)\s+[A-Za-z]+\s+\d{4}')


def load_past_results(file_path):
    """从文件中加载历史开奖号码，用于去重检查"""
    past_sets = set()
    try:
        with open(file_path, 'r') as f:
            f.readline() # 跳过表头
            for line in f:
                m = DATE_RE.match(line)
                if not m:
                    continue
                nums = [int(x) for x in re.findall(r'\d+', line[m.end():])]
                if len(nums) >= 7:
                    # 取前 7 个常规号码（第 8 个是特别号）排序存入集合
                    past_sets.add(tuple(sorted(nums[:7])))
    except FileNotFoundError:
        pass
    return past_sets

def generate_lotto_max(past_results):
    """
    根据历史规律生成 Lotto Max 号码:
    1. 奇偶比 4:3 或 3:4 (占比 ~58%)
    2. 包含且仅包含 1 组连号 (占比 ~41%)
    3. 和值在 160-190 之间 (接近历史平均值 175)
    4. 尽量覆盖所有号段 (1-10, 11-20, 21-30, 31-40, 41-52)
    5. **排除历史上已经出现过的完全相同的组合**
    """
    
    while True:
        # 1. 随机选择 7 个不重复的号码
        numbers = sorted(random.sample(range(1, MAX_NUMBER + 1), 7))
        
        # 排除已出现过的历史组合
        if tuple(numbers) in past_results:
            continue
            
        # 2. 检查连号情况 (规律: 最好只有 1 组连号)
        consec_count = 0
        for i in range(len(numbers) - 1):
            if numbers[i+1] == numbers[i] + 1:
                consec_count += 1
        
        if consec_count != 1:
            continue
            
        # 3. 检查奇偶分布 (规律: 4O:3E 或 3O:4E)
        odds = [n for n in numbers if n % 2 != 0]
        if len(odds) not in [3, 4]:
            continue
            
        # 4. 检查和值范围 (规律: 160 - 190)
        total_sum = sum(numbers)
        if not (160 <= total_sum <= 190):
            continue
            
        # 5. 检查号段覆盖 (尽量不出现断区)
        ranges = [0] * 5
        for n in numbers:
            ranges[min((n-1)//10, 4)] += 1  # 51、52 归入 41-52 段
        
        # 如果有超过 1 个号段断区，则重试
        if ranges.count(0) > 1:
            continue
            
        return numbers

if __name__ == "__main__":
    past_results = load_past_results('/opt/project/lottery/pastresult.txt')
    print(f"--- 已加载 {len(past_results)} 期历史数据进行比对 ---")
    print("--- 基于历史规律生成的 Lotto Max 推荐号码 ---")
    for i in range(5):
        nums = generate_lotto_max(past_results)
        print(f"推荐组合 {i+1}: {', '.join(map(str, nums))} (和值: {sum(nums)})")

import collections
import re

def analyze_lottery(file_path):
    data = []
    with open(file_path, 'r') as f:
        header = f.readline()
        for line in f:
            line = line.strip()
            if not line:
                continue
            # Split by tabs or multiple spaces
            parts = re.split(r'\t+|\s{2,}', line)
            if len(parts) < 9:
                # Try simple split if above fails
                parts = line.split()
                # If it's something like "13th February 2026 3 13 ..."
                # The date part is "13th February 2026" (3 words)
                if len(parts) >= 11:
                    date = " ".join(parts[:3])
                    nums = parts[3:]
                    parts = [date] + nums
            
            if len(parts) >= 9:
                try:
                    date = parts[0]
                    numbers = [int(x) for x in parts[1:8]]
                    bonus = int(parts[8])
                    data.append({
                        'date': date,
                        'numbers': numbers,
                        'bonus': bonus
                    })
                except ValueError:
                    continue

    if not data:
        print("No data found.")
        return

    all_numbers = []
    bonuses = []
    for entry in data:
        all_numbers.extend(entry['numbers'])
        bonuses.append(entry['bonus'])

    num_counts = collections.Counter(all_numbers)
    bonus_counts = collections.Counter(bonuses)

    print(f"Total draws analyzed: {len(data)}")
    
    # 1. Frequency
    all_numbers = []
    bonuses = []
    for entry in data:
        all_numbers.extend(entry['numbers'])
        bonuses.append(entry['bonus'])
    num_counts = collections.Counter(all_numbers)
    
    # 2. Odd/Even Distribution
    odd_even_dist = collections.Counter()
    
    # 3. Sum of Regular Numbers
    sums = []
    
    # 4. Number Pairs (Combinations)
    pairs = collections.Counter()
    
    # 5. Consecutive Numbers
    consecutive_counts = collections.Counter() # 0 = no consecutive, 1 = one pair (e.g., 4,5), etc.
    
    # 6. Range Distribution (1-10, 11-20, 21-30, 31-40, 41-52)
    ranges = {
        '1-10': 0, '11-20': 0, '21-30': 0, '31-40': 0, '41-52': 0
    }
    
    for entry in data:
        nums = sorted(entry['numbers'])
        # Odd/Even
        odds = sum(1 for n in nums if n % 2 != 0)
        evens = 7 - odds
        odd_even_dist[f"{odds}O:{evens}E"] += 1
        
        # Sum
        sums.append(sum(nums))
        
        # Pairs
        for i in range(len(nums)):
            for j in range(i + 1, len(nums)):
                pairs[(nums[i], nums[j])] += 1

        # Consecutive Numbers Analysis
        consec_sets = 0
        i = 0
        while i < len(nums) - 1:
            if nums[i+1] == nums[i] + 1:
                consec_sets += 1
                # Check for longer sequences (e.g., 4,5,6)
                # For simplicity, we count "pairs of neighbors"
            i += 1
        consecutive_counts[consec_sets] += 1

        # Range Distribution
        for n in nums:
            if 1 <= n <= 10: ranges['1-10'] += 1
            elif 11 <= n <= 20: ranges['11-20'] += 1
            elif 21 <= n <= 30: ranges['21-30'] += 1
            elif 31 <= n <= 40: ranges['31-40'] += 1
            elif 41 <= n <= 52: ranges['41-52'] += 1

    print("\n--- Consecutive Numbers Analysis ---")
    for count, freq in sorted(consecutive_counts.items()):
        percentage = (freq / len(data)) * 100
        label = "No consecutive" if count == 0 else f"{count} consecutive pair(s)/link(s)"
        print(f"{label}: {freq} times ({percentage:.2f}%)")

    print("\n--- Number Range Distribution (Global) ---")
    total_nums = len(data) * 7
    for r, count in ranges.items():
        percentage = (count / total_nums) * 100
        print(f"Range {r}: {count} numbers ({percentage:.2f}%)")

    print("\n--- Odd/Even Distribution ---")
    for ratio, count in odd_even_dist.most_common():
        percentage = (count / len(data)) * 100
        print(f"{ratio}: {count} times ({percentage:.2f}%)")

    print("\n--- Sum Value Analysis ---")
    avg_sum = sum(sums) / len(sums)
    print(f"Average Sum: {avg_sum:.2f}")
    print(f"Min Sum: {min(sums)}")
    print(f"Max Sum: {max(sums)}")
    # Last 10 sums for trend
    print(f"Sums of last 10 draws: {sums[:10]}")

    print("\n--- Most Frequent Number Pairs ---")
    for pair, count in pairs.most_common(10):
        print(f"Pair {pair}: {count} times")

    print("\n--- Frequency (Top 10) ---")
    for num, count in num_counts.most_common(10):
        print(f"Number {num}: {count} times")

if __name__ == "__main__":
    analyze_lottery('/opt/project/lottery/pastresult.txt')

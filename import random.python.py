import random

# 1〜10のランダムな数を生成
answer = random.randint(1, 10)

print("1〜10の数字を当ててください。")

# 最大3回のチャンス
for i in range(3):
    guess = int(input(f"{i+1}回目の予想: "))
    if guess == answer:
        print("正解です！おめでとう！")
        break
    elif guess < answer:
        print("もっと大きい数字です。")
    else:
        print("もっと小さい数字です。")
else:
    print(f"残念！正解は {answer} でした。")
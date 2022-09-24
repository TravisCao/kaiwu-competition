import numpy as np
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

with open('./rewards.log') as f:
    rewards = [eval(line.rstrip()) for line in f]

rewards = np.array(rewards)

df = pd.DataFrame(rewards, columns=['dead', 'ep_rate', 'exp', 'hp_point',
                  'kill', 'last_hist', 'money', 'tower_hp_point', 'reward_sum'])

sns.boxplot(df).set(ylabel="reward")
plt.xticks(
    rotation=45,
    horizontalalignment='right',
    fontweight='light',
    fontsize='x-large'
)
plt.title("0-7-1 luban vs 0-4-1 luban")
plt.tight_layout()
plt.show()

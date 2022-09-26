import numpy as np
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

with open('./rewards_0-8-3.log') as f:
    rewards = [eval(line.rstrip()) for line in f]

rewards = np.array(rewards)

df = pd.DataFrame(rewards, columns=['dead', 'ep_rate', 'exp', 'hp_point',
                  'kill', 'last_hist', 'money', 'tower_hp_point', 'reward_sum'])

df_win = df[df['reward_sum'] > 0].drop(columns=['reward_sum'])
df_loss = df[df['reward_sum'] < 0].drop(columns=['reward_sum'])

sns.boxplot(df_win).set(ylabel="reward")
plt.xticks(
    rotation=45,
    horizontalalignment='right',
    fontweight='light',
    fontsize='x-large'
)
plt.title("0-8-3 luban vs 0-4-1 luban, win")
plt.tight_layout()
plt.show()

sns.boxplot(df_loss).set(ylabel="reward")
plt.xticks(
    rotation=45,
    horizontalalignment='right',
    fontweight='light',
    fontsize='x-large'
)
plt.title("0-8-3 luban vs 0-4-1 luban, loss")
plt.tight_layout()
plt.show()

df_win.describe(), df_loss.describe()

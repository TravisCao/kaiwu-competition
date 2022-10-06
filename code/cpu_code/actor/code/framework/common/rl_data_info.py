# -*- coding: utf-8 -*-
class RLDataInfo:
    def __init__(self):
        self.frame_no = -1
        self.feature = b""
        self.next_feature = b""
        self.reward = 0
        self.reward2 = 0
        self.reward_farming = 0
        self.reward_farming2 = 0
        self.reward_KDA = 0
        self.reward_KDA2 = 0
        self.reward_damage = 0
        self.reward_damage2 = 0
        self.reward_pushing = 0
        self.reward_pushing2 = 0
        self.reward_win_lose = 0
        self.reward_win_lose2 = 0
        self.reward_sum = 0
        self.reward_sum2 = 0
        self.reward_sum_farming = 0
        self.reward_sum_farming2 = 0
        self.reward_sum_KDA = 0
        self.reward_sum_KDA2 = 0
        self.reward_sum_damage = 0
        self.reward_sum_damage2 = 0
        self.reward_sum_pushing = 0
        self.reward_sum_pushing2 = 0
        self.reward_sum_win_lose = 0
        self.reward_sum_win_lose2 = 0
        self.action = 0
        self.action_list = []
        self.done = 0
        self.info = None
        self.value_farming = 0
        self.value_KDA = 0
        self.value_damage = 0
        self.value_pushing = 0
        self.value_win_lose = 0
        self.value_farming2 = 0
        self.value_KDA2 = 0
        self.value_damage2 = 0
        self.value_pushing2 = 0
        self.value_win_lose2 = 0
        self.value = 0
        self.value2 = 0
        # self.neg_log_pis = 0
        self.advantage = 0
        self.game_id = b""
        self.is_train = False
        self.is_game_over = 0
        self.task_uuid = b""
        self.next_Q_value = b""
        self.gamma_pow = 1

        self.prob = None
        self.sub_action = None
        self.next_value = 0
        self.next_value2 = 0
        self.next_value_farming = 0
        self.next_value_KDA = 0
        self.next_value_damage = 0
        self.next_value_pushing = 0
        self.next_value_win_lose = 0
        self.next_value_farming2 = 0
        self.next_value_KDA2 = 0
        self.next_value_damage2 = 0
        self.next_value_pushing2 = 0
        self.next_value_win_lose2 = 0

        self.lstm_info = None

    def struct_to_pb(self, off_policy_rl_info):
        off_policy_rl_info.frame_no = self.frame_no
        off_policy_rl_info.feature = self.feature
        off_policy_rl_info.next_feature = self.next_feature
        off_policy_rl_info.reward_sum = self.reward_sum
        off_policy_rl_info.reward_sum_farming = self.reward_sum_farming
        off_policy_rl_info.reward_sum_KDA = self.reward_sum_KDA
        off_policy_rl_info.reward_sum_damage = self.reward_sum_damage
        off_policy_rl_info.reward_sum_pushing = self.reward_sum_pushing
        off_policy_rl_info.reward_sum_win_lose = self.reward_sum_win_lose
        
        off_policy_rl_info.reward = self.reward
        off_policy_rl_info.reward_farming = self.reward_farming
        off_policy_rl_info.reward__KDA = self.reward_KDA
        off_policy_rl_info.reward__damage = self.reward_damage
        off_policy_rl_info.reward_pushing = self.reward_pushing
        off_policy_rl_info.reward_win_lose = self.reward_win_lose

        off_policy_rl_info.done = self.done
        
        off_policy_rl_info.value = self.value
        off_policy_rl_info.value_farming = self.value_farming
        off_policy_rl_info.value_KDA = self.value_KDA
        off_policy_rl_info.self.value_damage = self.value_damage
        off_policy_rl_info.value_pushing = self.value_pushing 
        off_policy_rl_info.value_win_lose = self.value_win_lose

        off_policy_rl_info.neg_log_pis = self.neg_log_pis
        off_policy_rl_info.action = self.action
        off_policy_rl_info.action_list.extend(self.action_list)
        off_policy_rl_info.advantage = self.advantage
        # off_policy_rl_info.advantage_farming = self.advantage_farming
        # off_policy_rl_info.advantage_KDA =self.advantage_KDA
        # off_policy_rl_info.advantage_pushing =self.advantage_pushing
        # off_policy_rl_info.advantage_win_lose =self.advantage_win_lose
        # off_policy_rl_info.advantage_damage =self.advantage_damage
        
        off_policy_rl_info.game_id = self.game_id
        off_policy_rl_info.is_train = self.is_train
        off_policy_rl_info.is_game_over = self.is_game_over
        off_policy_rl_info.uuid = self.task_uuid
        off_policy_rl_info.next_Q_value = self.next_Q_value
        off_policy_rl_info.gamma_pow = self.gamma_pow

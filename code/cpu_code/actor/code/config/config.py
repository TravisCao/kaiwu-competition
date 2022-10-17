# -*- coding:utf-8 -*-
import json
import os
import sys

import numpy as np

if os.getenv("UPD_DICT") is not None and len(os.getenv("UPD_DICT")) > 0:
    update_dict = json.loads(os.getenv("UPD_DICT"))
else:
    update_dict = {}
from common_config import ModelConfig
from common_config import DimConfig


class Config:
    TRAIN_MODE = 0
    EVAL_MODE = 1
    BATTLE_MODE = 2
    AISERVERPORT = [10010, 10011]
    ALPHA = 0.5
    BETA = 0.01
    EPSILON = 1e-5
    INIT_CLIP_PARAM = 0.1
    BATCH_SIZE = 1

    GAMMA = 0.998
    LAMDA = 0.95
    STEPS = 128
    ENV_NAME = "kh-1v1"
    TASK_NAME = "test"
    ACTION_DIM = 79
    UPDATE_PATH = "../model/update"
    INIT_PATH = "../model/init"
    MEM_POOL_PATH = "./config/mem_pool.host_list"
    TASK_UUID = "123"
    IS_TRAIN = True
    SINGLE_TEST = False
    IS_CHECK = False
    ENEMY_TYPE = "network"
    EVAL_FREQ = 5


    distillation = ModelConfig.distillation
    hero_names = ['luban', 'houyi', 'direnjie', 'gongsunli', 'makeboluo']
    teacher_model_paths = ["teachers/teacher_" + hero for hero in hero_names]
    teacher_model_paths = dict(zip(hero_names, teacher_model_paths))
    reward_win = 5.0 
    eval_ai = False

    reward = json.load(open("/code/code/cpu_code/actor/code/config.json"))

    reward_after = {
        "reward_money": "0.006",
        "reward_exp": "0.006" ,
        "reward_hp_point": "2.0",
        "reward_ep_rate": "0.75",
        "reward_kill": "-0.6",
        "reward_dead": "-1.0",
        "reward_tower_hp_point": "6.0", # increase 20%
        "reward_last_hit": "0.5",
        "log_level": "8"
    }

if __name__ == "__main__":
    print(
        np.sum(
            [
                [12944],
                [16],
                [16],
                [16],
                [16],
                [16],
                [16],
                [16],
                [16],
                [192],
                [256],
                [256],
                [256],
                [256],
                [128],
                [16],
                [16],
                [16],
                [16],
                [16],
                [16],
                [16],
                [512],
                [512],
            ]
        )
    )

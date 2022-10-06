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

    GAMMA = 0.995
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
    
    reward_win = 5.0
    eval_ai = False
    distillation = ModelConfig.distillation
    hero_names = ['luban', 'houyi', 'direnjie', 'gongsunli', 'makeboluo']
    teacher_model_paths = ["teachers/teacher_" + hero for hero in hero_names]
    teacher_model_paths = dict(zip(hero_names, teacher_model_paths))

if __name__ == "__main__":
    print(
        np.sum(
            data_shapes = [
                [12944], # observation
                [16],    # reward_farming
                [16],    # reward_KDA
                [16],    # reward_damage
                [16],    # reward_pushing
                [16],    # reward_win_lose
                [16],    # advantage
                [16],    # label0
                [16],    # label1
                [16],    # label2
                [16],    # label3
                [16],    # label4
                [16],    # label5
                [192],   # prob0
                [256],   # prob1
                [256],   # prob2
                [256],   # prob3
                [256],   # prob4
                [128],   # prob5
                [16],    # weight0
                [16],    # weight1
                [16],    # weight2
                [16],    # weight3
                [16],    # weight4
                [16],    # weight5
                [16],    # is_train
                [512],   # lstm_cell
                [512],   # lstm_hidden_state
            ]
        )
    )

# -*- coding: utf-8 -*-
"""
    KingHonour Data production process
"""
from operator import le
import os
from re import I
import traceback
import numpy as np
from config.config import Config
from framework.common.common_log import CommonLogger
from framework.common.common_log import g_log_time
from framework.common.common_func import log_time_func
from actor import Actor
import time
import json
import struct
import socket
import multiprocessing
import json
from operator import add

IS_TRAIN = Config.IS_TRAIN
LOG = CommonLogger.get_logger()
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
OS_ENV = os.environ
IS_DEV = OS_ENV.get("IS_DEV")

with open("./config.json") as json_file:
    reward_coef = json.load(json_file)
reward_coef = dict(zip(reward_coef.keys(), map(float, reward_coef.values())))


class RemoteAiServer():
    def __init__(self, host, port, player_id=141):
        self.player_id = player_id
        self.host = host
        self.port = port
        self.sock = socket.socket()
        self.sock.connect((host, port))
        self.hero_camp = 1
        self.is_latest_model = False
        self.keep_latest = False
        self.agent_type = "network"

    def reset(self, camp, player_id, agent_type):
        self.hero_camp = camp
        self.player_id = player_id
        self.agent_type = agent_type

    def set_game_info(self, hero_camp, player_id):
        self.hero_camp = hero_camp
        self.player_id = player_id

    def closeGame(self):
        self.sock.close()


def remote_predict(input_queue, sock, output_queue, iq_lock, oq_lock):
    time.sleep(2)
    while True:
        state = input_queue.get()
        if state["game_done"]:
            break
        frame_no = state["frame_no"]
        send_data_bytes = json.dumps(state).encode("utf-8")
        empty_bytes = b" "
        data_len = len(send_data_bytes)
        all_data_bytes = send_data_bytes + \
            (8192 - (len(send_data_bytes) + 4 * 3) % 8192) * empty_bytes
        pkg_len = len(all_data_bytes)
        data_len_bytes = struct.pack("I", data_len)
        pkg_len_bytes = struct.pack("I", pkg_len)
        frame_no_bytes = struct.pack("I", frame_no)
        send_data = pkg_len_bytes + frame_no_bytes + data_len_bytes + all_data_bytes
        sock.send(send_data)
        data = sock.recv(8192)
        pkg_len = struct.unpack("I", data[:4])[0]
        frame_no = struct.unpack("I", data[4:8])[0]
        data = data[8:pkg_len]
        act = json.loads(data)
        return_dict = {}
        return_dict["act"] = act
        return_dict["frame_no"] = frame_no
        # oq_lock.acquire()
        output_queue.put(return_dict)
        # oq_lock.release()


class BattleActor(Actor):
    """
    used for sample logic
        run 1 episode
        save sample in sample manager
    """

    # def __init__(self, id, type):
    def __init__(self, id, agents, max_episode: int = 0, hero_configs=None, env=None):
        Actor.__init__(self, id, agents, max_episode,
                       env)

        if len(agents) != 2 or len(hero_configs) != 2:
            raise Exception(
                "BattleActor only support 2 agents and 3 hero_configs")

        self.hero1_config = hero_configs[0]
        self.hero2_config = hero_configs[1]
        self.episode_infos = []
        self.input_queues = []
        self.input_queues.append(multiprocessing.Queue())
        self.input_queues.append(multiprocessing.Queue())
        self.output_queues = []
        self.output_queues.append(multiprocessing.Queue())
        self.output_queues.append(multiprocessing.Queue())
        self.input_queue_locks = [
            multiprocessing.Lock(), multiprocessing.Lock()]
        self.output_queue_locks = [
            multiprocessing.Lock(), multiprocessing.Lock()]
        self.processings = []
        for i, agent in enumerate(self.agents):
            p = multiprocessing.Process(target=remote_predict, args=(
                self.input_queues[i], agents[i].sock, self.output_queues[i], self.input_queue_locks[i],
                self.output_queue_locks[i]))
            p.start()
            self.processings.append(p)

    def get_predict_result(self, agents, state_dict, req_pbs):

        acts = []
        for i, agent in enumerate(agents):
            state = state_dict[i]
            req_pb = req_pbs[i]
            frame_no = req_pb.frame_no
            input = {}
            # print("start predict",frame_no)
            input["observation"] = list(state_dict[i]["observation"])
            input["legal_action"] = list(state_dict[i]["legal_action"])
            input["frame_no"] = frame_no
            input["game_done"] = False
            self.input_queue_locks[i].acquire()
            # print("frame_no:{},input".format(frame_no),input)
            self.input_queues[i].put(input)
            self.input_queue_locks[i].release()
        for i, agent in enumerate(self.agents):
            # self.output_queue_locks[i].acquire()
            return_dict = self.output_queues[i].get()
            # self.output_queue_locks[i].release()
            acts.append(return_dict["act"])
        for i in range(len(acts)):
            for j in range(len(acts[i])):
                acts[i][j] = int(acts[i][j])

        return acts

    def _run_episode(self, env_config, mode=True, load_models=None, eval_info="", game_id=""):

        LOG.info("run episode")

        for item in g_log_time.items():
            g_log_time[item[0]] = []
        sample_manager = self.m_sample_manager
        done = False
        reward_details = []
        log_time_func('reset')
        log_time_func('one_episode')
        LOG.debug("reset env")
        use_common_ai = [False, False]

        render = None
        eval = True
        _, r, d, state_dict = self.env.reset(
            env_config, use_common_ai=use_common_ai, eval=eval, render=render, game_id=game_id
        )

        # LOG.info(r)
        # if state_dict[0] is None:
        #     game_id = state_dict[1]['game_id']
        # else:
        #     game_id = state_dict[0]['game_id']

        for i, agent in enumerate(self.agents):
            player_id = self.env.player_list[i]
            camp = self.env.player_camp.get(player_id)
            agent.set_game_info(camp, player_id)

        LOG.debug("reset sample_manager")
        sample_manager.reset(agents=self.agents, game_id=game_id)
        rewards = [[], []]
        step = 0
        log_time_func('reset', end=True)
        game_info = {}
        self.episode_infos = [{"h_act_num": 0} for _ in self.agents]

        while not done:
            log_time_func('one_frame')
            # while True:
            actions = []
            log_time_func("predict_result")
            req_pbs = self.env.cur_req_pb
            # print("req_pbs",req_pbs)
            actions = self.get_predict_result(self.agents, state_dict, req_pbs)
            # print("actions:",actions)
            log_time_func("predict_result", end=True)
            for i, agent in enumerate(self.agents):
                rewards[i].append(state_dict[i]['reward'])

            # print("step: ", step)
            # print("start env step")
            o, r, d, state_dict = self.env.step(actions)

            # print("step end")
            req_pbs = self.env.cur_req_pb
            if req_pbs[0] is None:
                req_pb = req_pbs[1]
            else:
                req_pb = req_pbs[0]
            LOG.debug("step: {}, frame_no: {}, reward: {}, {}".format(step, req_pb.frame_no,
                                                                      r[0], r[1]))
            step += 1
            done = d[0] or d[1]

            if req_pb.gameover:
                print("really gameover!!!")
                done = True

            # for npc_state in req_pb.organ_list:
            #     # if npc_state.camp != camp:
            #     #     continue
            #     # TODO: how to get common_ai tower info?
            #     if npc_state.type == 24:
            #         loss_camp = npc_state.camp
            # print("crystal: {} {}".format(npc_state.camp, npc_state.hp))
            # print("step", step)
            # if step > 5:
            #     break

            log_time_func('one_frame', end=True)

        self.env.close_game()

        # log accumulated rewards
        # LOG.info(rewards)

        rewards = np.array(rewards)
        if rewards.shape[-1] == 10:
            # https://git.code.tencent.com/aiarena/competition-3rd/issues/32
            rewards = np.delete(rewards, 6, axis=2)
        r_array_sum = np.array(rewards).sum(axis=1)
        print("Agent0_original: [dead, ep_rate, exp, hp_point, kill, last_hit, money, tower_hp_point, reward_sum]:{}".format(
            list(r_array_sum[0])))
        print("Agent1_original: [dead, ep_rate, exp, hp_point, kill, last_hit, money, tower_hp_point, reward_sum]:{}".format(
            list(r_array_sum[1])))

        rewards[:, :, 0] *= reward_coef['reward_dead']
        rewards[:, :, 1] *= reward_coef['reward_ep_rate']
        rewards[:, :, 2] *= reward_coef['reward_exp']
        rewards[:, :, 3] *= reward_coef['reward_hp_point']
        rewards[:, :, 4] *= reward_coef['reward_kill']
        rewards[:, :, 5] *= reward_coef['reward_last_hit']
        # rewards[ :,:, 6] *= reward_coef['reward_money']
        rewards[:, :, 6] *= reward_coef['reward_money']
        rewards[:, :, 7] *= reward_coef['reward_tower_hp_point']
        r_array_sum = np.array(rewards).sum(axis=1)

        print("Agent0: [dead, ep_rate, exp, hp_point, kill, last_hit, money, tower_hp_point, reward_sum]:{}".format(
            list(r_array_sum[0])))
        print("Agent1: [dead, ep_rate, exp, hp_point, kill, last_hit, money, tower_hp_point, reward_sum]:{}".format(
            list(r_array_sum[1])))

        # if aiprocess._model_manager.latest_version and int(self.m_config_id) != 0:
        # why self.m_config_id != 0?
        # TODO: update latest model info???
        game_info['length'] = req_pb.frame_no
        # TODO: fix common_ai bug
        for i, agent in enumerate(self.agents):
            if use_common_ai[i]:
                continue
            self.episode_infos[i]['reward'] = np.sum(rewards[i])
            self.episode_infos[i]['h_act_rate'] = self.episode_infos[i]['h_act_num'] / step
        log_time_func('one_episode', end=True)
        # print game information

    def run(self, mode=True, eval_number=-1, load_models=[], game_id="", battle_dict=[]):

        self.render = None
        self._last_print_time = time.time()
        self._episode_num = 0
        MAX_REPEAT_ERR_NUM = 2
        repeat_num = MAX_REPEAT_ERR_NUM

        all_config_dicts = \
            {
                "luban": [{"hero": "luban", "skill": "frenzy"} for _ in range(2)],
                "miyue": [{"hero": "miyue", "skill": "frenzy"} for _ in range(2)],
                "lvbu": [{"hero": "lvbu", "skill": "flash"} for _ in range(2)],
                "libai": [{"hero": "libai", "skill": "flash"} for _ in range(2)],
                "makeboluo": [{"hero": "makeboluo", "skill": "stun"} for _ in range(2)],
                "direnjie": [{"hero": "direnjie", "skill": "frenzy"} for _ in range(2)],
                "guanyu": [{"hero": "guanyu", "skill": "sprint"} for _ in range(2)],
                "diaochan": [{"hero": "diaochan", "skill": "purity"} for _ in range(2)],
                "luna": [{"hero": "luna", "skill": "intimidate"} for _ in range(2)],
                "hanxin": [{"hero": "hanxin", "skill": "flash"} for _ in range(2)],
                "huamulan": [{"hero": "huamulan", "skill": "flash"} for _ in range(2)],
                "buzhihuowu": [{"hero": "buzhihuowu", "skill": "execute"} for _ in range(2)],
                "jvyoujing": [{"hero": "jvyoujing", "skill": "flash"} for _ in range(2)],
                "houyi": [{"hero": "houyi", "skill": "frenzy"} for _ in range(2)],
                "zhongkui": [{"hero": "zhongkui", "skill": "stun"} for _ in range(2)],
                "ganjiangmoye": [{"hero": "ganjiangmoye", "skill": "flash"} for _ in range(2)],
                "kai": [{"hero": "kai", "skill": "intimidate"} for _ in range(2)],
                "gongsunli": [{"hero": "gongsunli", "skill": "frenzy"} for _ in range(2)],
                "peiqinhu": [{"hero": "peiqinhu", "skill": "flash"} for _ in range(2)],
                "shangguanwaner": [{"hero": "shangguanwaner", "skill": "heal"} for _ in range(2)
                                   ],
            }
        config_dicts = [self.hero1_config, self.hero2_config]
        LOG.info("battle_mode start with config: {}".format(config_dicts))
        agent_0, agent_1 = 0, 1
        cur_battle_cnt = 1
        while True:
            try:
                # provide a init eval value at the first episode
                battle_info = "{} vs {}, {}/{}".format(
                    agent_0, agent_1, cur_battle_cnt, eval_number)
                self._run_episode(config_dicts, True, load_models=load_models,
                                  game_id=game_id + "-{}".format(cur_battle_cnt), eval_info=battle_info)
                # battle_result[str(self._episode_num)]=str(self.episode_infos[0]["win"])+"-"+str(self.episode_infos[1]["win"])
                if self.env.render is not None:
                    self.env.render.dump_one_round()
                self._episode_num += 1
                repeat_num = MAX_REPEAT_ERR_NUM
            except Exception as e:
                LOG.error(
                    "_run_episode err: {}/{}".format(repeat_num, MAX_REPEAT_ERR_NUM))
                LOG.error(e)
                traceback.print_tb(e.__traceback__)
                # print(e.__traceback__.tb_frame.f_globals["__file__"])
                # print(e.__traceback__.tb_lineno)
                repeat_num -= 1
                if repeat_num == 0:
                    raise e
            cur_battle_cnt += 1

            if cur_battle_cnt > eval_number:
                for agent in self.agents:
                    agent.closeGame()
                for q in self.input_queues:
                    state = {}
                    state["game_done"] = True
                    q.put(state)
                break
            if 0 < self._max_episode <= self._episode_num:
                break

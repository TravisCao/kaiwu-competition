import os
import os.path
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
# root path
root_dir = os.path.dirname(current_dir)
common_dir = os.path.join(root_dir, "common")
sys.path.append(common_dir)

# cpu_code
actor_dir = os.path.join(root_dir, "cpu_code", "actor", "code")
sys.path.append(actor_dir)


import random

import numpy as np
from hok import HoK1v1

from absl import app as absl_app
from absl import flags

FLAGS = flags.FLAGS

flags.DEFINE_integer("actor_id", 0, "actor id")
flags.DEFINE_integer("max_step", 500, "max step of one round")
flags.DEFINE_string("mem_pool_addr", "localhost:35200", "address of memory pool")
flags.DEFINE_string("model_pool_addr", "localhost:10016", "address of model pool")
flags.DEFINE_string("gamecore_ip", "localhost", "address of gamecore")
flags.DEFINE_integer("thread_num", 1, "thread_num")

flags.DEFINE_string("agent_models", "", "agent_model_list")
flags.DEFINE_integer("eval_number", -1, "battle number for evaluation")
flags.DEFINE_boolean("single_test", 0, "test_mode")

def _generate_legal_action(env, states, common_ai):
    actions = []
    shapes = env.action_space()

    split_array = shapes.copy()[:-1]
    for i in range(1, len(split_array)):
        split_array[i] = split_array[i - 1] + split_array[i]

    for i in range(2):
        if common_ai[i]:
            actions.append(tuple([0] * 6))
            continue
        legal_action = np.split(states[i]["legal_action"], split_array)
        # print("legal_action", i, legal_action[0])
        act = []
        for j, _ in enumerate(shapes):
            tmp = []
            for k, la in enumerate(legal_action[j]):
                if la == 1:
                    tmp.append(k)
            a = random.randint(0, len(tmp) - 1)
            # print("for act id {}, avialiable action is {}".format(j, tmp))
            a = tmp[a]
            act.append(a)
            if j == 0:
                if legal_action[0][8]:
                    act[0] = 8
                    a = 8
                legal_action[5] = legal_action[5].reshape(-1, shapes[-1])[a]

        actions.append(tuple(act))
    return actions


def test_send_action(env, common_ai=None, eval=False, config_dicts=None):
    import pickle
    import numpy as np
    import pdb
    reward_list = [[], []]
    while True:
        if config_dicts is None:
            config_dicts = [{"hero": "luban", "skill": "rage"} for _ in range(2)]
        print("======= test_send_action")
        print("try to get first state...", common_ai)
        obs, reward, done, state = env.reset(
            use_common_ai=common_ai, eval=eval, config_dicts=config_dicts, render=None
        )
        reward_list[0].append(reward)
        if common_ai[0]:
            print("first state: ", state[1].keys())
        else:
            print("first state: ", state[0].keys())
        i = 0
        print("first frame:", env.cur_frame_no)

        while True:
            print("----------------------run step ", i)
            actions = _generate_legal_action(env, state, common_ai)
            obs, reward, done, state = env.step(actions)
            if done[0] or done[1]:
                break
            i += 1
            # if i > 10:
            #     break
        env.close_game()
        pdb.set_trace()
        print(state)
        return 

def test_agent_action(env, config_dicts=None):
    import pickle
    import pdb
    from agent import Agent as Agent
    from algorithms.model.sample_manager import SampleManager as SampleManager
    from algorithms.model.model import Model
    _, reward, done, state = env.reset(
        use_common_ai=[False, False], eval=False, config_dicts=config_dicts, render=None
    )
    env.close_game()
    pdb.set_trace()
    agent = Agent(
            Model,
            ['localhost:35200'],
            keep_latest=True,
            local_mode=False,
        )
    agent.reset("network", "eval_ai")
    action, d_action, sample = agent.process(state[0])
    # pdb.set_trace()
    print()


if __name__ == "__main__":
    CONFIG_PATH = "config.dat"
    # GC_SERVER_ADDR = os.getenv('GAMECORE_SERVER_ADDR')#
    # # please replace the *ai_server_addr* with your ip address.
    # AI_SERVER_ADDR = os.getenv('AI_SERVER_ADDR')
    # assert (
    #     AI_SERVER_ADDR is not None
    # ), "Set your IP address at environment variable AI_SERVER_ADDR."
    # if (
    #     GC_SERVER_ADDR is None
    #     or len(GC_SERVER_ADDR) == 0
    # ):
    #     # local gc server
    #     GC_SERVER_ADDR = "127.0.0.1:8011"
    #     AI_SERVER_ADDR = "0.0.0.0"
    #     remote_mode = 2
    # else:
    #     # remote gc server
    #     remote_mode = 2
    # # remote_mode = 2
    # remote_param = {
    #     "remote_mode": remote_mode,
    #     "gc_server_addr": GC_SERVER_ADDR,
    #     "ai_server_addr": AI_SERVER_ADDR,
    # }
    # print(GC_SERVER_ADDR,AI_SERVER_ADDR)
    # gc_mode = os.getenv("GC_MODE")
    # if gc_mode is not None and gc_mode == "local":
    #     remote_param = None

    # env = HoK1v1.load_game(
    #     runtime_id=0,
    #     game_log_path="./game_log",
    #     gamecore_path="./hok",
    #     config_path=CONFIG_PATH,
    #     eval_mode=False,
    #     remote_param=remote_param,
    # )

    gc_server_addr = os.getenv("GAMECORE_SERVER_ADDR")
    ai_server_addr = os.getenv("AI_SERVER_ADDR")
    if os.getenv("GC_MODE") == "remote":
        gc_server_addr = os.getenv("GAMECORE_SERVER_ADDR")
        ai_server_addr = os.getenv("AI_SERVER_ADDR", "127.0.0.1")
        remote_mode = 2
        remote_param = {
            "remote_mode": remote_mode,
            "gc_server_addr": gc_server_addr,
            "ai_server_addr": ai_server_addr,
        }
    gamecore_path = "~/.hok"
    game_log_path = "./game_log"
    env = HoK1v1.load_game(
        runtime_id=0,
        gamecore_path=gamecore_path,
        game_log_path=game_log_path,
        eval_mode=False,
        config_path="config.dat",
        remote_param=remote_param,
    )

    # test all 18 heros
    hero_list = [
        "luban",
        "miyue",
        "lvbu",
        "libai",
        "makeboluo",
        "direnjie",
        "guanyu",
        "diaochan",
        "luna",
        "hanxin",
        "huamulan",
        "buzhihuowu",
        "jvyoujing",
        "houyi",
        "zhongkui",
        "ganjiangmoye",
        "kai",
        "gongsunli",
        "peiqinhu",
        "shangguanwaner",
    ]
    # for i, h in enumerate(hero_list):
    #     print("=" * 15 + "test hero {}, {}/{}".format(h, i, len(hero_list)))

    test_send_action(
        env,
        common_ai=[False, False],
        eval=False,
        config_dicts=[{"hero": "diaochan","skill":"rage"} for _ in range(2)],
    )

    # test_agent_action(
    #     env,
    #     config_dicts=[{"hero": "diaochan","skill":"rage"} for _ in range(2)],
    # )

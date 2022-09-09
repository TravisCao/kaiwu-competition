from multiprocessing import Process
import os.path
import sys
from time import sleep
from unicodedata import name

# 当前文件的上级目录: code/cpu_code/actor/code
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# 根路径
root_dir = os.path.dirname(current_dir)
common_dir = os.path.join(root_dir, "common")
sys.path.append(common_dir)

# cpu_code
actor_dir = os.path.join(root_dir, "cpu_code", "actor", "code")
sys.path.append(actor_dir)

from absl import app as absl_app
from absl import flags
import json
from battle_actor import BattleActor, RemoteAiServer
from algorithms.model.sample_manager import SampleManager as SampleManager
from config.config import Config
from hok import HoK1v1 as HoK1v1

battle_json_file = "./battle.json"
battle_dict = []

FLAGS = flags.FLAGS
flags.DEFINE_string("gamecore_path", "~/.hok", "installation path of gamecore")
flags.DEFINE_string("gamecore_ip", "127.0.0.1", "address of gamecore")
flags.DEFINE_string("mem_pool_addr", "localhost:35200", "address of memory pool")
flags.DEFINE_integer("actor_id", 0, "actor id")
flags.DEFINE_string("game_log_path", "./game_log", "log path for game information")

flags.DEFINE_string("game_id", "test-game", "game_id")
flags.DEFINE_list("heroes", ["luban", "luban"], "2 player heros")
flags.DEFINE_list("aiserver_paths", ["./remote_aiserver/aiserver0", "./remote_aiserver/aiserver1"],
                  "2 player code path")
flags.DEFINE_integer("battle_num", 1, "battle num")

AGENT_NUM = 2


# gamecore as lib
def gc_as_lib(argv):
    hero_configs = []
    agents = []

    actor_id = FLAGS.actor_id
    port = 10010 + actor_id * 2
    for i, path in enumerate(FLAGS.aiserver_paths):
        port = port + i
        agents.append(RemoteAiServer("127.0.0.1", port))
        hero_conf_path = os.path.join(path, "cpu_code", "actor", "code", "hero_config.json")
        hero_configs.append(get_hero_config(hero_conf_path, FLAGS.heroes[i]))

    remote_param = None
    if os.getenv("GC_MODE") == "remote":
        gc_server_addr = os.getenv("GAMECORE_SERVER_ADDR")
        ai_server_addr = os.getenv("AI_SERVER_ADDR", "127.0.0.1")
        remote_mode = 2
        remote_param = {
            "remote_mode": remote_mode,
            "gc_server_addr": gc_server_addr,
            "ai_server_addr": ai_server_addr,
        }
    env = HoK1v1.load_game(runtime_id=actor_id,
                           gamecore_path=FLAGS.gamecore_path, game_log_path=FLAGS.game_log_path,
                           eval_mode=True, config_path="config.dat", remote_param=remote_param)

    sample_manager = SampleManager(mem_pool_addr=FLAGS.mem_pool_addr, mem_pool_type="mcp++",
                                   num_agents=AGENT_NUM, game_id=FLAGS.game_id, local_mode=True)
    actor = BattleActor(id=actor_id, agents=agents, hero_configs=hero_configs, env=env)
    actor.set_sample_managers(sample_manager)
    actor.set_env(env)
    actor.run(mode=Config.BATTLE_MODE, eval_number=FLAGS.battle_num, game_id=FLAGS.game_id, battle_dict=battle_dict)


def get_hero_config(path, hero_id):
    if not os.path.exists(path):
        raise Exception("hero config file not exists! {}".format(path))
    config = json.loads(open(path, "r").read())
    name = get_hero_name("{}".format(hero_id))
    if name not in config:
        raise Exception("cat not find hero {} skill in config {}".format(name, path))
    return dict({"hero": name, "skill": config[name]})


def get_hero_name(hero_id):
    hero_names = dict({
        "112": "luban", "121": "miyue", "123": "lvbu", "131": "libai", "132": "makeboluo",
        "133": "direnjie", "140": "guanyu", "141": "diaochan", "146": "luna", "150": "hanxin",
        "154": "huamulan", "157": "buzhihuowu", "163": "jvyoujing", "169": "houyi", "175": "zhongkui",
        "182": "ganjiangmoye", "193": "kai", "199": "gongsunli", "502": "peiqinhu", "513": "shangguanwaner",
    })
    if hero_id in hero_names:
        return hero_names[hero_id]
    return hero_id


if __name__ == '__main__':
    absl_app.run(gc_as_lib)

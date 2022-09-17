import os.path
import sys


# ports=Config.AISERVERPORT
if __name__ == '__main__':
    port=int(sys.argv[1])
    path= sys.argv[2]

    actor_code_dir=os.path.join(path,"cpu_code", "actor", "code")
    sys.path.append(actor_code_dir)

    common_dir=os.path.join(path, "common")
    sys.path.append(common_dir)

    from algorithms.model.model import Model as Model
    from config.config import Config
    from aiserver import AIServer

    ai_server = AIServer(port, Model, os.path.join(actor_code_dir,"algorithms","checkpoint"))
    ai_server.prepare_connection()
    ai_server.handle_request()
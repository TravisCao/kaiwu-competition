# 对战

注意: 请勿修改这个文件夹内的脚本，可以使用这个文件夹下的脚本进行本地对战，验证模型是否正确

## 使用方法

```bash
Usage: start_battle.sh CAMP_BLUE_MODEL CAMP_RED_MODEL CAMP_BLUE_HERO CAMP_RED_HERO GAME_ID

Example: start_battle.sh ./code_1.tgz ./code_2.tgz houyi houyi gameid-20220905-164749-3
```

日志路径: `/code/logs/battle/<game_id>`

## 教程

1. 启动本地客户端，并且启动开发环境，打开 VSCode
   ![](https://prod-kaiwu-1258344700.file.myqcloud.com/image/1v1/start_env.jpg)

2. 在 VSCode 中打开终端输入以下命令进入容器内，或者使用其他终端工具进入容器也可以
   ```bash
   docker exec -it kaiwu-container bash
   ```

3. 将集群训练下载下来的默认放置到 `code/battle/` 目录下
   ![](https://prod-kaiwu-1258344700.file.myqcloud.com/image/1v1/move_model.jpg)

4. 在容器内执行命令，进行对战
   ```bash
   cd /code/code/battle

   # 注意参数需要替换成你自己的参数
   ./start_battle.sh ./code_20220827_051231.tgz ./code_20220827_051231.tgz houyi houyi gameid-20220906001
   ```

5. 出现报错，查看日志，如下图所示，终端出现报错，查看报错日志
   ![](https://prod-kaiwu-1258344700.file.myqcloud.com/image/1v1/battle_log.png)
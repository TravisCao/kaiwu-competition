#!/bin/bash
function log(){
    now=$(date +"%Y-%m-%d %H:%M:%S")
    echo "[$now] $1"
}

function kill_process() {
    ps -aux | grep $1 | grep -v grep | awk '{print $2}' | xargs --no-run-if-empty kill -9 > /dev/null 2>&1
}

function stop() {
    kill_process python
    kill_process sgame
}

function waiting_port(){
    port=${1:-10010}
    n=${2:-30}
    log "will check port: $port, max: $n"

    for (( i = 0; i < n; i++ )); do
        a=$(lsof -i:"$port" | wc -l)
        log "check port $port res: $a, count: $i"

        if [ "$a" -gt "0" ];then
            return 0
        fi
        sleep 1s
    done

    log "ai server start timeout, max start time: $n s"
    exit 1
}

function download_model(){
    file=$1
    output=$2

    tar xf $file
    rm -rf $output
    mv ./code $output
}

function start_ai_server(){
    camp_code=${1:-"A"}
    camp_port=${2:-10010}
    game_id=${3:-"test-game"}
    camp_model=${4:-""}

    aiserver_dir=remote_aiserver/aiserver_$camp_code

    download_model $camp_model $aiserver_dir

    nohup python3 start_ai_server.py $camp_port $aiserver_dir/ > \
     $ROOT_LOG_DIR/$game_id/Camp_"$camp_code"_AIServer.log 2>&1 &
}


# set -x
CAMP_BLUE_MODEL=${1:-"./code_1.tgz"}
CAMP_RED_MODEL=${2:-"./code_2.tgz"}
CAMP_BLUE_HERO=${3:-"houyi"}
CAMP_RED_HERO=${4:-"houyi"}
GAME_ID=${5:-"gameid-20220905-164749-3"}

if [[ $# -lt 2 ]]
then
    echo Usage: $0 CAMP_BLUE_MODEL CAMP_RED_MODEL CAMP_BLUE_HERO CAMP_RED_HERO GAME_ID
    echo Example: $0 $CAMP_BLUE_MODEL $CAMP_RED_MODEL $CAMP_BLUE_HERO $CAMP_RED_HERO $GAME_ID
    exit -1
fi

CAMP_BLUE_PORT=10010
CAMP_RED_PORT=10011

MEM_POOL_PORT=0
KAIWU_INDEX=0
CAMP_BLUE_CODE=blue
CAMP_RED_CODE=red

# 初始化操作
ROOT_LOG_DIR=/code/logs/battle
mkdir -p $ROOT_LOG_DIR/$GAME_ID/
mkdir -p /code/code/battle/remote_aiserver /code/logs/cpu_log
stop

# 启动 AIServer
start_ai_server $CAMP_BLUE_CODE $CAMP_BLUE_PORT $GAME_ID $CAMP_BLUE_MODEL
start_ai_server $CAMP_RED_CODE $CAMP_RED_PORT $GAME_ID $CAMP_RED_MODEL
waiting_port $CAMP_BLUE_PORT 30
waiting_port $CAMP_RED_PORT 30

# 启动对局
log "start game $GAME_ID"
python battle_entry.py \
                --heroes="$CAMP_BLUE_HERO,$CAMP_RED_HERO" \
                --game_id=$GAME_ID \
                --game_log_path=$ROOT_LOG_DIR/game_log/ \
                --mem_pool_addr="localhost:$MEM_POOL_PORT" \
                --actor_id="$KAIWU_INDEX" \
                --aiserver_paths="remote_aiserver/aiserver_$CAMP_BLUE_CODE,remote_aiserver/aiserver_$CAMP_RED_CODE" \
                --battle_num=1 > $ROOT_LOG_DIR/"$GAME_ID"/battle.log
                

# 按照年月划分文件夹
result_dir=${RESULT_PREFIX:-"$(date +"%Y%m")"}

echo "success"
stop

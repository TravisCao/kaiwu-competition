function log(){
  now=`date +"%Y-%m-%d %H:%M:%S"`
  echo "[$now] $1"
}


function check(){
    id=$1;
    updated=`stat -c %Y /code/logs/cpu_log/actor_$id.log`;
    current=`date +%s`
    change=$[ $current - $updated ]

    if [ $change -gt 180 ];then
        log "actor_$id no update for more than $change sec."
        kill_actor $id
        start $id
    fi
}

function kill_actor(){
    log "will kill and stop game for actor $1"

    # kill 进程
    ps -ef | grep actor_id=$1 | grep -v grep | awk '{print $2}' | xargs --no-run-if-empty kill
    ps -ef | egrep gameid-.*-$1 | grep -v grep | awk '{print $2}' | xargs --no-run-if-empty kill
    
    if [ "$GC_MODE" = "remote" ];then
        # 获取 token
        TOKEN=$(echo ${AI_SERVER_ADDR} | awk '{ gsub(/\./,"D"); print $0 }')
        curl -k http://${GAMECORE_SERVER_ADDR}/v1/stopGame -d '{"Token": "'"${TOKEN}"'","CustomConfig": "{\"runtime_id\":'$1'}"}'
    fi
    
    current=`date +%s`
    cp /code/logs/cpu_log/actor_$1.log /code/logs/cpu_log/actor_$1.$current.log;
    cat /dev/null > /code/logs/cpu_log/actor_$1.log
}

function start(){
    mem_pool_addr=`cat ../actor/config/mem_pool.host_list |xargs |sed 's/ /;/g'`
    echo $mem_pool_addr

    log "will start actor $1"
    cd /code/code/cpu_code/actor/code/ && \
    nohup python entry.py --actor_id=$1 \
                        --mem_pool_addr="$mem_pool_addr" \
                        --model_pool_addr="localhost:10016" \
                        --thread_num=1 \
                        --game_log_path "/code/logs/game_log" \
                        >> /code/logs/cpu_log/actor_$1.log 2>&1 &
}


while true; do
    log "will check actor status, num: $CPU_NUM"

    for((i=0;i<$CPU_NUM;i++)); do   
        check $i
    done

    sleep 30;
done

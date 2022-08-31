#!/bin/bash
export GC_MODE="remote"
USE_GPU=true
if [ $use_gpu ];then
    USE_GPU=$use_gpu
fi
Max_test_time=300
if [ $max_test_time ];then
    Max_test_time=$max_test_time
fi
if [ ! $CPU_NUM ];then
    export CPU_NUM=2
fi
if [[ $USE_GPU == false  &&  `pip list |grep -c tensorflow ` -eq 2 ]];then
    cd /;
    pip install tensorflow-1.14.0-cp36-cp36m-manylinux1_x86_64.whl
fi

rm -rf /code/logs
mkdir -p /code/logs/start_log

echo "---------------------------testing start----------------------------"
echo "---------------------------starting gpu-----------------------------"
if [[ -e "default.conf" ]];then
    display_every=`cat default.conf | awk '{print $1}'`
    store_max_sample=`cat default.conf | awk '{print $2}'`
else
    display_every=`awk -F'[=;[:space:]]+' '$1=="display_every"{print $2}' /code/code/gpu_code/learner/code/common.conf`
    store_max_sample=`awk -F'[=;[:space:]]+' '$1=="store_max_sample"{print $2}' /code/code/gpu_code/learner/code/common.conf`
    echo $display_every $store_max_sample > /code/default.conf
fi
sed -i "s/display_every = $display_every/display_every = 1/" /code/code/gpu_code/learner/code/common.conf
sed -i "s/store_max_sample = $store_max_sample/store_max_sample = 100/" /code/code/gpu_code/learner/code/common.conf
cd /code/code/gpu_code/script
nohup sh start_gpu.sh >/code/logs/start_log/start_gpu.log 2>&1 &

echo "---------------------------starting cpu-----------------------------"
function init(){
  rm -rf  /code/logs/cpu_log /code/logs/game_log
  mkdir -p /code/logs/cpu_log /code/logs/game_log

  # set cpu.iplist
  echo "$POD_IP root 36001 $CPU_NUM" > /code/code/cpu_code/script/cpu.iplist

  # set config conf
  sed -i "s/mem_pool_num=.*/mem_pool_num=$CARD_NUM/g" /code/code/gpu_code/script/config.conf
  sed -i "s/mem_pool_num=.*/mem_pool_num=$CARD_NUM/g" /code/code/cpu_code/script/config.conf
  task_uuid=$TASK_ID
  echo task_id=$TASK_ID >> /code/code/cpu_code/script/config.conf
  echo task_uuid=$task_uuid >> /code/code/cpu_code/script/config.conf

  echo "start setup param"
  cd /code/code/cpu_code/script
  python parse_iplist.py /code/code/cpu_code/script/gpu.iplist /code/code/cpu_code/script/gpu.iplist.new 1
  bash /code/code/cpu_code/script/setup_param.sh \
                      /code/code/cpu_code/script/gpu.iplist.new \
                      /code/code/cpu_code/script/cpu.iplist \
                      $CARD_NUM $TASK_ID $task_uuid
}

# 等待的 learner 启动，通过探测 model pool 端口实现
function wait_learner() {
  ip=$(cat /code/code/cpu_code/script/gpu.iplist | awk '{print $1}' | sed -n '1p')
  echo "learner ip: $ip"
  while true; do
      code=$(curl -sIL -w "%{http_code}\n" -o /dev/null http://$ip:10016)
      if [ $code -gt 200 ]; then
          echo "learner is ok"
          break
      fi
      echo "learner is not ok, wait for ready"
      sleep 1
  done
}


function start(){
  echo "start model_pool"
  if [ ` ps -ef |grep -v "grep" | grep -c "start_gpu.sh" ` -gt 0 ];then
    train_type="gpu"
  else
    train_type="cpu"
  fi
  cd /rl_framework/model_pool/pkg/model_pool_pkg/op; bash stop.sh; bash start.sh $train_type

  echo "start actor"
  sleep 10
  cd /code/code/cpu_code/actor/; bash start.sh $CPU_NUM
}
wait_learner
init
start



start_time=` date  +%s`
# Code testing
cd /code/logs/gpu_log;
while [ $[` date  +%s` - $start_time] -lt $Max_test_time ]
do   
    if [[  ` grep -c "entry.py" /code/logs/cpu_log/actor_0.log ` -ne 0 && ` grep -c "InitChangeType" /code/logs/cpu_log/actor_0.log ` -eq 0 ]] || [[ ` grep -c "train.py" /code/logs/gpu_log/trace1.log ` -ne 0 ]]
    then
        echo "$[` date  +%s` - $start_time]"
        echo "---------------------------testing fail------------------------------"
        ts_tag=1
        echo "---------------------------testing finish----------------------------"
        cd /code/; bash stop_dev.sh
        break
    elif [[ ` grep -c "too much init move" /code/logs/cpu_log/actor_0.log ` -ne 0 ]] || [[ ` grep -c "get_model error, try again" /code/logs/cpu_log/actor_0.log ` -ne 0 ]] || [[ ` grep -c "ConnectionError" /code/logs/cpu_log/actor_0.log ` -ne 0 ]]
    then
        echo "$[` date  +%s` - $start_time]"
        echo "---------------------------testing fail------------------------------"
        ts_tag=2
        echo "---------------------------testing finish----------------------------"
        cd /code/; bash stop_dev.sh
        break        
    elif [[ -e "loss.txt" && ` ls -l loss.txt | awk '{print $5}' ` -ne 0 ]]
    then
        echo "$[` date  +%s` - $start_time]"
        echo "---------------------------testing success----------------------------"
        sleep 2s
        ts_tag=0
        echo "---------------------------testing finish----------------------------"
        cd /code/; bash stop_dev.sh
        break
    fi
done
if [ $[` date  +%s` - $start_time] -gt $Max_test_time ]
then 
    echo "$[` date  +%s` - $start_time]"
    echo "---------------------------testing fail------------------------------"
    sleep 2s
    ts_tag=3
    echo "---------------------------testing finish----------------------------"
    cd /code/; bash stop_dev.sh
fi

sed -i "s/display_every = 1/display_every = $display_every/" /code/code/gpu_code/learner/code/common.conf
sed -i "s/store_max_sample = 100/store_max_sample = $store_max_sample/" /code/code/gpu_code/learner/code/common.conf
rm /code/default.conf
if [[ $ts_tag -eq 0 ]]
then
    exit 0
elif [[ $ts_tag -eq 1 ]]
then
    exit 1
elif [[ $ts_tag -eq 2 ]]
then
    exit 202
else
    exit 203
fi
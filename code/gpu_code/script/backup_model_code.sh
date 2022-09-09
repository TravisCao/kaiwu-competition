# 备份模型和模型文件

checkpoint_dir=/code/code/gpu_code/send_model/model
backup_dir=/code/model_bkup

function log(){
  now=`date +"%Y-%m-%d %H:%M:%S"`
  echo "[$now] $1"
}

# 打包模型文件
function pack(){
    model_file=$1
    
    # 解压
    mkdir -p /tmp/checkpoint
    tar xf $model_file -C /tmp/checkpoint
    fullname=`basename $model_file`
    model_name=${fullname%.*}

    # 构造模型包
    mkdir -p /code/build/code/cpu_code/
    rm -rf /code/code/cpu_code/actor/code/algorithms/checkpoint/*
    mkdir -p /code/code/cpu_code/actor/code/algorithms/checkpoint/
    mv /tmp/checkpoint/$model_name/* /code/code/cpu_code/actor/code/algorithms/checkpoint/
    cp -r /code/code/cpu_code/actor/ /code/build/code/cpu_code/
    cp -r /code/code/common /code/build/code/
    
    # 打包
    now=`date +"%Y%m%d_%H%M%S"`
    code_name="code_$now.tgz"
    cd /code/build/
    tar zcf $code_name code 
    mv $code_name $backup_dir
}


function run_backup(){
    log "will get last back checkpoint file"
    cd $checkpoint_dir

    file=`ls -lth | grep done | head -n 1 | awk '{print $9}' | sed 's/\.done//g'`
    if [ ! -n "$file" ];then
        log "no checkpoint file"
        return
    fi

    file="$checkpoint_dir/$file"
    log "find last file: $file"

    if [ -z "$file" ];then
        log "$file is not exist"
        return
    fi

    log "will pack file: $file"
    pack $file
}


function delete() {
    if [ -f "$1" ];then
        log "will delete file: $1"
        rm -f $1
    fi
}

function clean_dir(){
    dir=$1
    num=${BKUP_NUM:-20}

    log "will clean dir: $dir, num: $num"
    if [ ! -d "$dir" ];then
        log "$dir is not exist"
        mkdir -p $dir
        return
    fi

    
    size=`ls $dir | wc -l`
    log "find $dir files num: $size"
    while(( $size > $num )); do
        old=$(ls -rth $dir | grep -v done | head -n 1)
        delete $dir/$old
        delete $dir/$old.done
        size=$(( $size-1 ))
    done
}

# 上传模型到 cos
# https://cloud.tencent.com/document/product/436/63144#alias
function upload(){
    touch /root/.cos.yaml

    # 同步文件
    /rl_framework/coscli sync -r \
        $backup_dir cos://$COS_BUCKET/$COS_DIR/$TASK_UUID/ \
        -e cos.$COS_REGION.myqcloud.com -i $COS_SECRET_ID -k $COS_SECRET_KEY  > /dev/null 2>&1
}

# for loop not done
while true; do
    log "will run backup"
    run_backup
    sleep 1

    if [ -n "$BKUP_UPLOAD" ];then
        log "will upload"
        upload
    fi

    clean_dir $checkpoint_dir
    sleep 1
    log ""

    clean_dir $backup_dir
    sleep 1
    log ""

    # 默认 30 min 备份一次
    interval=${BKUP_INTERVAL:-1800}
    sleep $interval
done

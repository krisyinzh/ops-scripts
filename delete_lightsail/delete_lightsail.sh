#!/bin/bash

REGIONS=(
  "ap-southeast-1"   # 新加坡
  "ap-east-1"        # 香港
  "ap-northeast-1"   # 东京
  "ap-northeast-2"   # 首尔
)

process_region() {
  local REGION=$1
  echo "[开始] $REGION"

  # ---- 1. 并发删除所有实例（触发后不等结果）----
  INSTANCES=$(aws lightsail get-instances \
    --region "$REGION" \
    --no-cli-pager \
    --query 'instances[].name' \
    --output text 2>/dev/null)

  if [ -n "$INSTANCES" ]; then
    for INSTANCE in $INSTANCES; do
      echo "[实例] 触发删除: $INSTANCE ($REGION)"
      aws lightsail delete-instance \
        --instance-name "$INSTANCE" \
        --region "$REGION" \
        --no-cli-pager &   # 不等结果，直接下一个
    done
  else
    echo "[实例] $REGION 无实例"
  fi

  # ---- 2. 并发释放所有静态 IP（触发后不等结果）----
  STATIC_IPS=$(aws lightsail get-static-ips \
    --region "$REGION" \
    --no-cli-pager \
    --query 'staticIps[].name' \
    --output text 2>/dev/null)

  if [ -n "$STATIC_IPS" ]; then
    for IP_NAME in $STATIC_IPS; do
      echo "[静态IP] 触发释放: $IP_NAME ($REGION)"
      aws lightsail release-static-ip \
        --static-ip-name "$IP_NAME" \
        --region "$REGION" \
        --no-cli-pager &   # 不等结果，直接下一个
    done
  else
    echo "[静态IP] $REGION 无静态IP"
  fi

  echo "[触发完成] $REGION 所有删除命令已发出"
}

export -f process_region

# 所有区域并发执行
for REGION in "${REGIONS[@]}"; do
  process_region "$REGION" &
done

# 等待所有触发命令发出完毕
wait

echo ""
echo "========================================"
echo "所有删除命令已全部发出，AWS 后台处理中"
echo "========================================"

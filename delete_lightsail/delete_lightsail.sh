cat > delete_lightsail.sh << 'EOF'
#!/bin/bash

REGIONS=(
  "ap-southeast-1"
  "ap-east-1"
  "ap-northeast-1"
  "ap-northeast-2"
)

process_region() {
  local REGION=$1
  echo "========================================"
  echo "[开始] 处理区域: $REGION"
  echo "========================================"

  INSTANCES=$(aws lightsail get-instances \
    --region "$REGION" \
    --query 'instances[].name' \
    --output text 2>/dev/null)

  if [ -n "$INSTANCES" ]; then
    for INSTANCE in $INSTANCES; do
      echo "[实例] 正在删除: $INSTANCE ($REGION)"
      aws lightsail delete-instance --instance-name "$INSTANCE" --region "$REGION"
      echo "[实例] 已删除: $INSTANCE ($REGION)"
    done
  else
    echo "[实例] $REGION 无实例"
  fi

  STATIC_IPS=$(aws lightsail get-static-ips \
    --region "$REGION" \
    --query 'staticIps[].name' \
    --output text 2>/dev/null)

  if [ -n "$STATIC_IPS" ]; then
    for IP_NAME in $STATIC_IPS; do
      echo "[静态IP] 正在释放: $IP_NAME ($REGION)"
      aws lightsail release-static-ip --static-ip-name "$IP_NAME" --region "$REGION"
      echo "[静态IP] 已释放: $IP_NAME ($REGION)"
    done
  else
    echo "[静态IP] $REGION 无静态IP"
  fi

  echo "[完成] 区域 $REGION 清理完毕"
}

export -f process_region

for REGION in "${REGIONS[@]}"; do
  process_region "$REGION" &
done

wait
echo "========================================"
echo "所有区域并发清理完成"
echo "========================================"
EOF

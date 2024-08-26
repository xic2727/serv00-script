#!/bin/bash

# ANSI颜色码
GREEN='\033[0;32m'
NC='\033[0m'  # 恢复默认颜色

# 检查vless的状态
check_vless_status() {
    status=$(pm2 status vless | grep -w 'vless' | awk '{print $18}')
    if [[ "$status" == "online" ]]; then
        echo "vless进程正在运行。"
    else
        echo "vless进程未运行或已停止，正在重启..."
        pm2 restart vless
        echo -e "${GREEN}vless进程已重启。${NC}"
    fi
}

# 检查pm2 vless的状态
check_pm2_vless_status() {
    pm2 describe vless &>/dev/null
    if [[ $? -eq 0 ]]; then
        check_vless_status
    else
        echo "未找到pm2 vless进程，检查是否有快照..."
        check_pm2_vless_snapshot
    fi
}
# 主函数
main() {
    echo "开始检查pm2 vless进程..."
    check_pm2_vless_status
}

# 执行主函数
main "$@"

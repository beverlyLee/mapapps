#!/usr/bin/env bash
# cicada-map 一键启动脚本
# 用法: ./start.sh [start|stop|restart|status]

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"
PID_DIR="$PROJECT_DIR/.pids"
BACKEND_PORT=8000
FRONTEND_PORT=5173
BACKEND_PID="$PID_DIR/backend.pid"
FRONTEND_PID="$PID_DIR/frontend.pid"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info()  { echo -e "${GREEN}[INFO]${NC} $*"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*"; }
log_step()  { echo -e "${CYAN}  → $*${NC}"; }

mkdir -p "$PID_DIR"

# ---------- 工具函数 ----------
# 在 Mac 多 Python 环境中，优先选已装 fastapi/uvicorn 的解释器，避免 pip 装错位置
_pick_python() {
  local candidates=()
  # 正在运行的 uvicorn 用的解释器（优先级最高，避免新旧进程解释器不一致）
  local running_py
  running_py=$(ps -o comm= -p "$(pgrep -f 'uvicorn app.main' 2>/dev/null | head -1)" 2>/dev/null | awk '{print $1}')
  if [ -n "$running_py" ] && [[ "$running_py" == *python* ]]; then
    candidates+=("$running_py")
  fi
  candidates+=(
    "$(command -v python3 2>/dev/null)"
    "$(command -v python  2>/dev/null)"
    "/opt/homebrew/bin/python3"
    "/usr/local/bin/python3"
    "/Library/Developer/CommandLineTools/usr/bin/python3"
  )
  local best="" best_score=-1
  local py
  for py in "${candidates[@]}"; do
    [ -z "$py" ] && continue
    [ ! -x "$py" ] && continue
    local score=0
    if $py -c "import fastapi, uvicorn, openpyxl, sqlalchemy, pydantic" 2>/dev/null; then
      score=100
    elif $py -c "import fastapi, uvicorn" 2>/dev/null; then
      score=60
    elif $py -c "import pip" 2>/dev/null; then
      score=10
    fi
    if (( score > best_score )); then
      best_score=$score
      best=$py
    fi
  done
  if [ -z "$best" ]; then
    echo ""
    return 1
  fi
  echo "$best"
  return 0
}

_pip_install() {
  local py="$1" req="$2"
  local extra_flags=()
  # Homebrew / macOS 系统 Python 需要 PEP 668 绕过标志
  if "$py" -m pip install --help 2>/dev/null | grep -q break-system-packages; then
    extra_flags+=("--break-system-packages")
  fi
  (cd "$BACKEND_DIR" && "$py" -m pip install --user "${extra_flags[@]}" -r "$req")
}

# ---------- 前置检查 ----------
check_deps() {
  log_info "检查依赖..."

  PYTHON_CMD=$(_pick_python)
  if [ -z "$PYTHON_CMD" ]; then
    log_error "未找到可用的 Python，请先安装 Python 3.10+"
    exit 1
  fi
  log_step "Python: $($PYTHON_CMD --version 2>&1)  →  $PYTHON_CMD"

  if ! command -v node &>/dev/null; then
    log_error "未找到 Node.js，请先安装 Node.js 18+"
    exit 1
  fi
  log_step "Node.js: $(node --version)"

  if ! command -v npm &>/dev/null; then
    log_error "未找到 npm"
    exit 1
  fi
  log_step "npm: $(npm --version)"

  if ! $PYTHON_CMD -c "import fastapi, uvicorn, openpyxl, sqlalchemy, pydantic, httpx" 2>/dev/null; then
    log_warn "缺少 Python 依赖，正在安装（--user）..."
    if ! _pip_install "$PYTHON_CMD" "$BACKEND_DIR/requirements.txt"; then
      log_error "Python 依赖安装失败，请手动执行："
      log_error "  $PYTHON_CMD -m pip install -r $BACKEND_DIR/requirements.txt"
      exit 1
    fi
  fi

  if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
    log_warn "缺少前端依赖，正在安装..."
    (cd "$FRONTEND_DIR" && npm install --silent)
  fi

  if [ ! -f "$BACKEND_DIR/data/cicada_points.xlsx" ]; then
    log_warn "缺少 Excel 数据源，正在生成..."
    (cd "$BACKEND_DIR" && $PYTHON_CMD gen_excel.py)
  fi

  if [ ! -f "$FRONTEND_DIR/.env" ]; then
    log_warn "缺少 .env 文件，正在从模板复制..."
    cp "$FRONTEND_DIR/.env.example" "$FRONTEND_DIR/.env"
    log_warn "请编辑 frontend/.env 填入高德地图 Key"
  fi
}

# ---------- 启动服务 ----------
start_backend() {
  if [ -f "$BACKEND_PID" ] && kill -0 "$(cat "$BACKEND_PID")" 2>/dev/null; then
    log_warn "后端已在运行 (PID $(cat "$BACKEND_PID"))"
    return 0
  fi

  log_info "启动后端服务 (端口 $BACKEND_PORT)..."
  (
    cd "$BACKEND_DIR"
    nohup $PYTHON_CMD -m uvicorn app.main:app --reload --port "$BACKEND_PORT" \
      > "$PID_DIR/backend.log" 2>&1 &
    echo $! > "$BACKEND_PID"
  )
  sleep 2
  if curl -s "http://localhost:$BACKEND_PORT/api/health" >/dev/null 2>&1; then
    log_step "后端已启动 → http://localhost:$BACKEND_PORT"
  else
    log_warn "后端可能未就绪，查看日志: $PID_DIR/backend.log"
  fi
}

start_frontend() {
  if [ -f "$FRONTEND_PID" ] && kill -0 "$(cat "$FRONTEND_PID")" 2>/dev/null; then
    log_warn "前端已在运行 (PID $(cat "$FRONTEND_PID"))"
    return 0
  fi

  log_info "启动前端服务 (端口 $FRONTEND_PORT)..."
  (
    cd "$FRONTEND_DIR"
    nohup npm run dev -- --host \
      > "$PID_DIR/frontend.log" 2>&1 &
    echo $! > "$FRONTEND_PID"
  )
  sleep 3
  if curl -s "http://localhost:$FRONTEND_PORT" >/dev/null 2>&1; then
    log_step "前端已启动 → http://localhost:$FRONTEND_PORT"
  else
    log_warn "前端可能未就绪，查看日志: $PID_DIR/frontend.log"
  fi
}

stop_backend() {
  if [ -f "$BACKEND_PID" ]; then
    local pid
    pid=$(cat "$BACKEND_PID")
    if kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null && log_step "后端已停止 (PID $pid)" || true
    fi
    rm -f "$BACKEND_PID"
  else
    local pid
    pid=$(lsof -ti:"$BACKEND_PORT" 2>/dev/null || true)
    if [ -n "$pid" ]; then
      kill "$pid" 2>/dev/null && log_step "后端已停止 (PID $pid)" || true
    fi
  fi
}

stop_frontend() {
  if [ -f "$FRONTEND_PID" ]; then
    local pid
    pid=$(cat "$FRONTEND_PID")
    if kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null && log_step "前端已停止 (PID $pid)" || true
    fi
    rm -f "$FRONTEND_PID"
  else
    local pid
    pid=$(lsof -ti:"$FRONTEND_PORT" 2>/dev/null || true)
    if [ -n "$pid" ]; then
      kill "$pid" 2>/dev/null && log_step "前端已停止 (PID $pid)" || true
    fi
  fi
}

show_status() {
  echo ""
  echo -e "${CYAN}══════════════════════════════════════════${NC}"
  echo -e "${CYAN}  cicada-map 服务状态${NC}"
  echo -e "${CYAN}══════════════════════════════════════════${NC}"

  if [ -f "$BACKEND_PID" ] && kill -0 "$(cat "$BACKEND_PID")" 2>/dev/null; then
    echo -e "  后端:  ${GREEN}运行中${NC} (PID $(cat "$BACKEND_PID")) → http://localhost:$BACKEND_PORT"
  else
    echo -e "  后端:  ${RED}已停止${NC}"
  fi

  if [ -f "$FRONTEND_PID" ] && kill -0 "$(cat "$FRONTEND_PID")" 2>/dev/null; then
    echo -e "  前端:  ${GREEN}运行中${NC} (PID $(cat "$FRONTEND_PID")) → http://localhost:$FRONTEND_PORT"
  else
    echo -e "  前端:  ${RED}已停止${NC}"
  fi

  echo -e "${CYAN}══════════════════════════════════════════${NC}"
  echo ""
}

do_start() {
  check_deps
  echo ""
  start_backend
  start_frontend
  echo ""
  show_status

  if [ -f "$FRONTEND_DIR/.env" ] && grep -q "your_amap" "$FRONTEND_DIR/.env" 2>/dev/null; then
    log_warn "请先配置 frontend/.env 中的高德地图 Key"
  else
    log_info "所有服务已就绪，正在打开浏览器..."
    sleep 1
    open "http://localhost:$FRONTEND_PORT" 2>/dev/null || true
  fi
}

do_stop() {
  log_info "正在停止所有服务..."
  stop_backend
  stop_frontend
  rm -rf "$PID_DIR"
  log_info "已停止全部服务"
}

do_restart() {
  do_stop
  sleep 1
  do_start
}

# ---------- 入口 ----------
case "${1:-start}" in
  start)   do_start ;;
  stop)    do_stop ;;
  restart) do_restart ;;
  status)  show_status ;;
  *)
    echo "用法: $0 [start|stop|restart|status]"
    echo ""
    echo "  start    启动前后端服务（默认）"
    echo "  stop     停止所有服务"
    echo "  restart  重启所有服务"
    echo "  status   查看服务状态"
    exit 1
    ;;
esac
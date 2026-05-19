#!/usr/bin/env bash
# run-dev.sh — start the full Marketing Pipeline development stack.
#
# Usage:  ./run-dev.sh
#
# What this does:
#   1. Starts all Docker Compose services (postgres, redis, seaweedfs, qdrant, etc.)
#   2. Waits for PostgreSQL to be healthy (up to 60 s)
#   3. Installs backend Python deps via uv
#   4. Runs Alembic migrations
#   5. Starts the FastAPI backend (uvicorn, port 8000) in the background
#   6. Installs frontend npm deps if needed
#   7. Starts the Vite dev server (port 5173) in the background
#   8. Prints service URLs and tails both logs
#   9. Ctrl-C cleanly stops backend + frontend (Docker containers keep running)
#
# To also stop Docker containers on exit, run:  ./run-dev.sh --stop-docker

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$REPO_ROOT/src/backend"
FRONTEND_DIR="$REPO_ROOT/src/frontend/web"
COMPOSE_FILE="$REPO_ROOT/devops/docker-compose.yml"
LOG_DIR="$REPO_ROOT/.dev-logs"
STOP_DOCKER=false

for arg in "$@"; do
  [[ "$arg" == "--stop-docker" ]] && STOP_DOCKER=true
done

# ── colours ─────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; RESET='\033[0m'

log()  { echo -e "${CYAN}[run-dev]${RESET} $*"; }
ok()   { echo -e "${GREEN}[run-dev]${RESET} $*"; }
warn() { echo -e "${YELLOW}[run-dev]${RESET} $*"; }
err()  { echo -e "${RED}[run-dev]${RESET} $*" >&2; }

# ── PIDs of background processes ────────────────────────────────────────────
BACKEND_PID=""
FRONTEND_PID=""

cleanup() {
  echo ""
  warn "Shutting down..."
  [[ -n "$BACKEND_PID" ]]  && kill "$BACKEND_PID"  2>/dev/null && log "Backend stopped"
  [[ -n "$FRONTEND_PID" ]] && kill "$FRONTEND_PID" 2>/dev/null && log "Frontend stopped"
  if $STOP_DOCKER; then
    log "Stopping Docker containers..."
    docker compose -f "$COMPOSE_FILE" down
    ok "Docker containers stopped."
  else
    warn "Docker containers still running. Run 'docker compose -f devops/docker-compose.yml down' to stop them."
  fi
  ok "Done."
}
trap cleanup EXIT INT TERM

mkdir -p "$LOG_DIR"

# ── 1. Docker Compose ────────────────────────────────────────────────────────
log "Starting Docker Compose services..."
docker compose -f "$COMPOSE_FILE" up -d --remove-orphans 2>&1 | sed "s/^/  /"
ok "Docker Compose services started."

# ── 2. Wait for PostgreSQL ────────────────────────────────────────────────────
log "Waiting for PostgreSQL to be healthy..."
MAX_WAIT=60
WAITED=0
until docker exec mp_postgres pg_isready -U mp_user -d marketing_pipeline -q 2>/dev/null; do
  if (( WAITED >= MAX_WAIT )); then
    err "PostgreSQL did not become healthy within ${MAX_WAIT}s."
    err "Check: docker logs mp_postgres"
    exit 1
  fi
  sleep 2
  (( WAITED += 2 ))
done
ok "PostgreSQL is healthy (${WAITED}s)."

# ── 3. Backend Python deps ────────────────────────────────────────────────────
log "Syncing backend Python dependencies (uv)..."
cd "$BACKEND_DIR"
uv sync --all-groups 2>&1 | grep -v "^warning:" | grep -v "^$" | sed "s/^/  /" || true
ok "Backend dependencies ready."

# ── 4. Alembic migrations ────────────────────────────────────────────────────
log "Running Alembic migrations..."
DATABASE_URL="postgresql+psycopg://mp_user:mp_password@localhost:5432/marketing_pipeline" \
  uv run alembic upgrade head 2>&1 | sed "s/^/  /"
ok "Database schema is up to date."

# ── 5. FastAPI backend ────────────────────────────────────────────────────────
log "Starting FastAPI backend on http://localhost:8000 ..."
DATABASE_URL="postgresql+psycopg://mp_user:mp_password@localhost:5432/marketing_pipeline" \
  uv run uvicorn api.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload \
    --log-level info \
  >"$LOG_DIR/backend.log" 2>&1 &
BACKEND_PID=$!

# wait until the backend responds
MAX_WAIT=30; WAITED=0
until curl -sf http://localhost:8000/health >/dev/null 2>&1; do
  if ! kill -0 "$BACKEND_PID" 2>/dev/null; then
    err "Backend process died. Logs:"
    tail -30 "$LOG_DIR/backend.log" >&2
    exit 1
  fi
  if (( WAITED >= MAX_WAIT )); then
    err "Backend did not respond within ${MAX_WAIT}s. Logs:"
    tail -20 "$LOG_DIR/backend.log" >&2
    exit 1
  fi
  sleep 1
  (( WAITED += 1 ))
done
ok "Backend is up (${WAITED}s).  http://localhost:8000/docs"

# ── 6. Frontend npm deps ──────────────────────────────────────────────────────
cd "$FRONTEND_DIR"
if [[ ! -d node_modules ]]; then
  log "Installing frontend npm dependencies..."
  npm install --silent 2>&1 | sed "s/^/  /"
  ok "Frontend dependencies installed."
else
  log "Frontend node_modules present — skipping npm install."
fi

# ── 7. Vite dev server ────────────────────────────────────────────────────────
log "Starting Vite dev server on http://localhost:5173 ..."
npm run dev >"$LOG_DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!

# wait until Vite prints its ready line
MAX_WAIT=30; WAITED=0
until grep -q "Local:" "$LOG_DIR/frontend.log" 2>/dev/null; do
  if ! kill -0 "$FRONTEND_PID" 2>/dev/null; then
    err "Frontend process died. Logs:"
    tail -20 "$LOG_DIR/frontend.log" >&2
    exit 1
  fi
  if (( WAITED >= MAX_WAIT )); then
    err "Vite did not start within ${MAX_WAIT}s. Logs:"
    tail -20 "$LOG_DIR/frontend.log" >&2
    exit 1
  fi
  sleep 1
  (( WAITED += 1 ))
done
ok "Frontend is up (${WAITED}s).  http://localhost:5173"

# ── 8. Summary ────────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "${BOLD}  Marketing Pipeline — dev stack is ready${RESET}"
echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "  ${GREEN}Frontend${RESET}        http://localhost:5173"
echo -e "  ${GREEN}Backend API${RESET}     http://localhost:8000"
echo -e "  ${GREEN}API docs${RESET}        http://localhost:8000/docs"
echo -e "  ${GREEN}PostgreSQL${RESET}      localhost:5432  (mp_user / mp_password)"
echo -e "  ${GREEN}Redis${RESET}           localhost:6379"
echo -e "  ${GREEN}Qdrant${RESET}          http://localhost:6333"
echo -e "  ${GREEN}SeaweedFS S3${RESET}    http://localhost:8333"
echo -e "  ${GREEN}Prefect UI${RESET}      http://localhost:4200"
echo -e "  ${GREEN}Prometheus${RESET}      http://localhost:9090"
echo -e "  ${GREEN}Grafana${RESET}         http://localhost:3000"
echo -e ""
echo -e "  Logs → ${LOG_DIR}/"
echo -e "  Press ${BOLD}Ctrl-C${RESET} to stop backend + frontend."
echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo ""

# ── 9. Tail both logs ─────────────────────────────────────────────────────────
tail -f "$LOG_DIR/backend.log" "$LOG_DIR/frontend.log" &
TAIL_PID=$!

# wait for backend or frontend to die, then exit so trap fires
wait "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
kill "$TAIL_PID" 2>/dev/null || true

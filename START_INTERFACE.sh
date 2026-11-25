#!/bin/bash
# Notes2PDF - start everything on the GPU machine.
# Run:  bash ~/workspace/ie643/ie643_final/START_INTERFACE.sh
#   or copy-paste the whole file into the terminal.

# Rebuilt environment (21 Nov). Do NOT use the old ie643_env.sh: its Python was deleted.
source ~/workspace/ie643/env.sh    # sets Python, HF cache, and cd's to ie643_final
cd ~/workspace/ie643/ie643_final
export PATH="$HOME/.local/bin:$PATH"     # cloudflared lives here

echo "== GPU =="
nvidia-smi --query-gpu=memory.used,memory.total --format=csv

echo "== stopping any old interface =="
python3 06_interface/manage.py stop 2>/dev/null

echo "== health check =="
python3 06_interface/manage.py doctor --adapter runs/final_clean/final_adapter || { echo "DOCTOR FAILED - see message above"; exit 1; }

echo "== starting server + Cloudflare tunnel =="
python3 06_interface/manage.py start --tunnel cloudflare || {
  echo "START FAILED. Last log lines:"
  tail -30 out/interface_service/web.log 2>/dev/null
  tail -20 out/interface_service/tunnel.log 2>/dev/null
  exit 1; }

echo "== status (public URL below) =="
python3 06_interface/manage.py status

echo "== access key (do NOT show on screen) =="
python3 06_interface/manage.py token

echo
echo "Done. Open the URL, paste the key, upload 1 page to warm the models (~1 min)."
echo "Stop later with:  cd ~/workspace/ie643/ie643_final && python3 06_interface/manage.py stop"

# ---------------- IF SOMETHING FAILS ----------------
# Logs:          tail -50 ~/workspace/ie643/ie643_final/out/interface_service/web.log
#                tail -30 ~/workspace/ie643/ie643_final/out/interface_service/tunnel.log
# Full reset:    python3 06_interface/manage.py stop
#                ps aux | grep -E "vllm|recognition_worker|waitress" | grep -v grep
#                kill <PID>        (kill -9 <PID> if it will not stop)
#                then run this script again (the URL will change)
# Port busy:     lsof -i :7860   then  kill <PID>
# Out of memory: nvidia-smi, kill leftover python/vllm PIDs, run again
# No flask/torch:you skipped "source ~/workspace/ie643/env.sh"
# URL won't open:try phone hotspot (campus Wi-Fi may block trycloudflare.com)

#!/bin/bash
# Notes2PDF v2 (novelty pipeline) - start on the GPU machine.
# Run:  bash ~/workspace/ie643_final/START_INTERFACE_V2.sh
# v2 = Surya 2.5 layout + Method B figure choice (Qwen grounding, shared-box fix, fixed verifier,
# recovered drawings) + crop cleaning + structure clean-up. Port 7861, Surya on 8002.
# v1 (START_INTERFACE.sh, port 7860) is unchanged and stays the fallback. Run only ONE of them:
# both load the models on the same 16 GB GPU.

source ~/workspace/ie643_final_env.sh    # rebuilt env; also cd's to ie643_final
cd ~/workspace/ie643_final
export PATH="$HOME/.local/bin:$PATH"     # cloudflared

echo "== GPU =="
nvidia-smi --query-gpu=memory.used,memory.total --format=csv

echo "== stopping old interfaces (v1 and v2) =="
python3 06_interface/manage.py stop 2>/dev/null
python3 06_interface_v2/manage.py stop 2>/dev/null

echo "== health check =="
python3 06_interface_v2/manage.py doctor --adapter runs/final_clean/final_adapter || { echo "DOCTOR FAILED"; exit 1; }

echo "== starting v2 server + Cloudflare tunnel =="
python3 06_interface_v2/manage.py start --tunnel cloudflare || {
  echo "START FAILED. Last log lines:"
  tail -30 out/interface_service_v2/web.log 2>/dev/null
  tail -20 out/interface_service_v2/tunnel.log 2>/dev/null
  exit 1; }

echo "== status (public URL below) =="
python3 06_interface_v2/manage.py status
echo "== access key (do NOT show on screen) =="
python3 06_interface_v2/manage.py token
echo
echo "Done. Open the URL, paste the key, upload 1 page to warm the models (~1 min)."
echo "Each upload now takes a little longer (drawing placement, about 5-15 s per page with drawings)."
echo "Stop later with:  cd ~/workspace/ie643_final && python3 06_interface_v2/manage.py stop"
# Logs: out/interface_service_v2/web.log, tunnel.log; jobs: out/upload_jobs_v2/<id>/ (figure_choice.json
# lists every figure decision). If v2 fails during the demo, stop it and run START_INTERFACE.sh (v1).

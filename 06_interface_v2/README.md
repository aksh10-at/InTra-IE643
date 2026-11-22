# Notes2PDF v2: the web interface with the novelty pipeline

Web page to upload handwritten notes (PDF, HEIC/HEIF, JPG, PNG, WebP, BMP, TIFF), up to 20 pages and
25 MiB. You download a searchable PDF, the Markdown, an editable bundle and a conversion report.
Access is by a private key, and files are deleted after 24 hours. This is the version used in the
demo video. The first version stays in [`../06_interface/`](../06_interface/) as a fallback.

## What v2 adds to the first version

Each upload runs preprocessing, layout and recognition as before, then places the figures with the
novelty pipeline ([`figures_v2.py`](figures_v2.py), steps in [`../novelty/NOTES.md`](../novelty/NOTES.md)):

1. **Surya 2.5** finds the figure boxes (its own vLLM server on port 8002, so v1 can keep Surya 2 on 8001).
2. **Grounding:** the base Qwen (adapter off) gives a rough box for each `[Diagram: ...]` line.
   Two descriptions with nearly the same box (IoU ≥ 0.7) are grounded again with one whole-page prompt.
3. **Method B:** the Hungarian algorithm pairs descriptions with Surya boxes by overlap with Qwen's
   boxes. Split pieces are joined, and Qwen's box is used when the overlap is below 0.2.
4. **Completeness check:** a larger crop that contains the chosen one is used only if Qwen finds it
   more complete by at least 0.05.
5. **Recovered drawings:** Surya figure boxes that no crop covers are added if Qwen calls them a sketch.
6. **PDF:** crop cleaning, one heading scale, side captions and the fixed LaTeX header.

Every figure decision is written to `figure_choice.json` in the job folder. Placing figures adds
about 5 to 15 s per page with drawings.

## Speed: models stay warm

The first upload loads the models (about a minute). They stay on the GPU while uploads keep coming
and are unloaded after **15 idle minutes** (`--idle-minutes`). Code: `engine.py` (warm models),
`recognition_worker.py` (persistent Qwen process), `layout.py` (Surya 2.5 server).
Run only one interface at a time, and **stop it before any training run** (one 16 GB GPU).

## Run (GPU machine, from the repo root)

```bash
bash 06_interface_v2/setup_gpu.sh                      # once: web + HEIC packages
python3 06_interface_v2/manage.py start --tunnel cloudflare   # uses runs/final_clean/final_adapter
python3 06_interface_v2/manage.py status               # public URL and state
python3 06_interface_v2/manage.py token                # access key to give to users
python3 06_interface_v2/manage.py stop
```

Or all at once: `bash START_INTERFACE_V2.sh`. The web server listens on port 7861 (v1: 7860).
Tunnel options: `--tunnel cloudflare` (random trycloudflare.com link), `--tunnel tailscale`
(fixed `https://notes2pdf.<your-tailnet>.ts.net`, needs the one-time Tailscale setup below) or
`--tunnel none` (localhost only). Other options: `--adapter <dir>`, `--idle-minutes N`, `--demo`
(UI test without models). Logs: `out/interface_service_v2/`, jobs: `out/upload_jobs_v2/<id>/`.

Command line, without the web page:

```bash
python3 06_interface_v2/pipeline.py my_notes.pdf --out out/my_notes --adapter runs/final_clean/final_adapter
```

### Tailscale Funnel (one-time setup)

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up --hostname notes2pdf          # opens a login link: sign in with your account
sudo tailscale set --operator=$USER             # lets manage.py switch Funnel on/off without sudo
```

## Files

| File | Purpose |
|---|---|
| `manage.py` | Start/stop the server and the public link in the background |
| `server.py` | Web server (Flask + Waitress): sign-in, uploads, job status, downloads, 24 h cleanup |
| `pipeline.py` | One upload: decode pages, preprocess, layout + recognition, figures, PDF, bundle |
| `figures_v2.py` | Novelty figure choice and PDF style (uses scripts from `../novelty/`) |
| `engine.py`, `recognition_worker.py`, `layout.py` | Warm models (see above) |
| `index.html`, `app.js`, `style.css` | The page |
| `demo.py` | Test mode without models |
| `tests/` | `python3 -m unittest discover -s 06_interface_v2/tests` |

Limits and extreme cases (more than 20 pages, size, formats, timeouts): [../docs/REPORT_NOTES.md](../docs/REPORT_NOTES.md).

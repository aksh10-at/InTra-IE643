"""Persistent Qwen recognition worker: loads the model once, then reads one JSON request
per line on stdin and answers one JSON line on stdout. Ending the process frees the GPU.

Request:  {"image": "/path/page.jpg", "out": "/path/page.md"}
v2 also:  {"kind": "ground" | "ground_page", "image": ..., "descs": [...]} -> {"ok": true, "boxes": [...]}
          {"kind": "p_yes", "image": "/path/crop.png", "question": "..."} -> {"ok": true, "p_yes": 0.93}
Answer:   {"ok": true, "generated_tokens": 812, "possibly_truncated": false}
          {"ok": false, "error": "..."}
The first line written is {"ready": true} once the model is loaded.
"""
import argparse
import json
from pathlib import Path
import sys

from pipeline import CleanRecognizer


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--adapter', required=True)
    p.add_argument('--max-pixels', type=int, default=1_000_000)
    p.add_argument('--max-new-tokens', type=int, default=2048)
    a = p.parse_args()
    out = sys.stdout
    sys.stdout = sys.stderr  # library prints must not corrupt the protocol
    recognizer = CleanRecognizer(a.adapter, a.max_pixels, a.max_new_tokens)
    recognizer.load()
    out.write(json.dumps({'ready': True}) + '\n'); out.flush()
    for line in sys.stdin:
        try:
            request = json.loads(line)
            kind = request.get('kind', 'page')
            if kind == 'ground':
                answer = {'ok': True, 'boxes': recognizer.ground(request['image'], request['descs'])}
            elif kind == 'ground_page':
                answer = {'ok': True, 'boxes': recognizer.ground_page(request['image'], request['descs'])}
            elif kind == 'p_yes':
                answer = {'ok': True, 'p_yes': recognizer.p_yes(request['image'], request['question'])}
            else:
                text, details = recognizer.predict(request['image'])
                Path(request['out']).write_text(text)
                answer = {'ok': True, **details}
        except Exception as error:  # report and keep serving
            answer = {'ok': False, 'error': f'{type(error).__name__}: {error}'}
        out.write(json.dumps(answer) + '\n'); out.flush()


if __name__ == '__main__':
    main()

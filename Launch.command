#!/bin/bash
set -e
cd "$(dirname "$0")"
if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv
  .venv/bin/python -m pip install -r requirements.txt
fi
export BALANCECHECK_LOCAL_SETUP=1
exec .venv/bin/python -m streamlit run app.py --server.address 127.0.0.1 --browser.gatherUsageStats false

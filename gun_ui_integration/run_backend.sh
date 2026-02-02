#!/bin/bash
# รันจาก root ของ gun_ui_integration
uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000

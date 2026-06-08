#!/usr/bin/env bash
# 示例：把 LoRA adapter 合并导出。

set -e

MODEL_PATH=${MODEL_PATH:-Qwen/Qwen2.5-0.5B-Instruct}
ADAPTER_PATH=${ADAPTER_PATH:-saves/qwen2_5_0_5b_sparkbot_lora}
EXPORT_DIR=${EXPORT_DIR:-exports/qwen2_5_0_5b_sparkbot_merged}

llamafactory-cli export \
  --model_name_or_path "$MODEL_PATH" \
  --adapter_name_or_path "$ADAPTER_PATH" \
  --template qwen \
  --finetuning_type lora \
  --export_dir "$EXPORT_DIR" \
  --export_size 2 \
  --export_legacy_format false

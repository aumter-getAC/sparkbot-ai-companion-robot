#!/usr/bin/env bash
# 示例：使用 LLaMA-Factory 做 Qwen LoRA SFT。
# 这是训练命令模板，不包含环境安装。请先安装 LLaMA-Factory，并把数据注册到 data/dataset_info.json。

set -e

MODEL_PATH=${MODEL_PATH:-Qwen/Qwen2.5-0.5B-Instruct}
DATASET=${DATASET:-sparkbot_sft_demo}
OUTPUT_DIR=${OUTPUT_DIR:-saves/qwen2_5_0_5b_sparkbot_lora}

llamafactory-cli train \
  --stage sft \
  --do_train true \
  --model_name_or_path "$MODEL_PATH" \
  --dataset "$DATASET" \
  --template qwen \
  --finetuning_type lora \
  --lora_target q_proj,v_proj \
  --output_dir "$OUTPUT_DIR" \
  --overwrite_output_dir true \
  --per_device_train_batch_size 1 \
  --gradient_accumulation_steps 8 \
  --learning_rate 2e-4 \
  --num_train_epochs 3 \
  --cutoff_len 1024 \
  --logging_steps 5 \
  --save_steps 50 \
  --plot_loss true

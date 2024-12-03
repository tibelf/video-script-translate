#!/bin/bash

# Conda 环境名称
CONDA_ENV_NAME="video-translate"

# 检查 Conda 是否可用
if ! command -v conda &> /dev/null
then
    echo "Conda 未找到，请确保 Conda 已正确安装并配置到系统路径"
    exit 1
fi

# 检查环境是否存在，不存在则创建
if ! conda env list | grep -q $CONDA_ENV_NAME; then
    echo "创建 Conda 环境 $CONDA_ENV_NAME"
    conda create -n $CONDA_ENV_NAME python=3.9 numpy=1.23 -y
fi

# 激活 Conda 环境
source $(conda info --base)/etc/profile.d/conda.sh
conda activate $CONDA_ENV_NAME

# 安装依赖
pip install -r requirements.txt

# 运行主脚本
python main.py "$@"

# 取消激活环境（可选）
conda deactivate

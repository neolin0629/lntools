#!/bin/bash

# 获取脚本所在目录
script_dir=$(dirname "$(realpath "$0")")
cd "$script_dir"

# 定义临时 whl 路径
DIR="$script_dir/dist"

# 清理掉之前构建的路径
echo "清理旧的构建目录..."
rm -rf "$DIR" "$script_dir/build" "$script_dir/lntools.egg-info"

# 使用 uv 打包成 whl 文件
# uv build 会自动处理构建依赖并生成 whl
echo "使用 uv 构建 wheel..."
uv build --wheel --out-dir "$DIR"

# 获取构建出的 whl 文件 (取最新的一个)
WHL_FILE=$(ls -t "$DIR"/lntools-*.whl 2>/dev/null | head -n 1)

if [ -z "$WHL_FILE" ]; then
  echo "错误: 未找到构建的 wheel 文件。"
  exit 1
fi

echo "使用 uv pip 安装 $WHL_FILE ..."
# --force-reinstall 确保即便版本号没变也会重新安装
uv pip install "$WHL_FILE" --force-reinstall

# 清理构建中间文件
echo "清理临时构建文件..."
rm -rf "$script_dir/build" "$script_dir/lntools.egg-info"

echo "安装完成。"

#!/bin/bash

echo "请先在 GitHub 创建仓库，然后输入你的 GitHub 用户名："
read -p "GitHub 用户名: " username

echo "正在配置 Git..."
git config --global user.name "$username"
git config --global user.email "$username@users.noreply.github.com"

echo "正在添加远程仓库..."
git remote add origin https://github.com/$username/report-app.git

echo "正在推送代码..."
git branch -M main
git push -u origin main

echo "代码已推送到: https://github.com/$username/report-app"
echo "现在可以去 Railway.app 部署了！"

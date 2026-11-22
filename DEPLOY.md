# 部署到 GitHub Pages

目標網址（QR Code 已編入）：`https://mathedu-prog.github.io/tracecam/`
若你的帳號或 repo 名稱不同，先重新產生 QR 與教學頁：

```bash
pip install pillow segno opencv-python-headless
python3 build_assets.py https://<帳號>.github.io/<repo>/
```

## 步驟（需要你本人授權的地方：GitHub 登入）

```bash
gh auth login                      # ← 需要你授權
gh repo create tracecam --public --source=. --remote=origin   # 或用你自己的 repo
git init -b main && git add . && git commit -m "TraceCam v1.0.0"
git push -u origin main
gh api -X POST repos/<帳號>/tracecam/pages -f "source[branch]=main" -f "source[path]=/"
```

約 1 分鐘後開啟 `https://<帳號>.github.io/tracecam/`。

## 每次更新
1. 修改檔案 2. **遞增 `sw.js` 的 `VERSION`**（例如 v1.0.0 → v1.0.1） 3. commit & push。
已安裝的使用者下次開啟會看到「有新版本可用．立即更新」。

## 驗收清單
- (a) 開啟一次後，DevTools → Network → Offline，重新整理仍可開啟
- (b) Chrome 網址列出現安裝圖示；Lighthouse PWA 通過
- (c) 手機掃 `qr-install.png` 開啟正確網址
- (d) 依 install.html 步驟實機安裝
- (e) 推送新 VERSION 後，已安裝的 App 出現更新提示

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
產生 PWA 需要的圖示、QR Code（PNG + 內嵌 SVG）與 install.html，並實際解碼驗證 QR 內容。
用法：python3 build_assets.py https://<帳號>.github.io/<repo>/
依賴：pip install pillow segno opencv-python-headless
"""
import sys, io, re, math
from PIL import Image, ImageDraw
import segno, cv2, numpy as np

URL = sys.argv[1] if len(sys.argv) > 1 else "https://mathedu-prog.github.io/tracecam/"
if not URL.endswith("/"):
    URL += "/"
APP_URL = URL                      # App 正式網址
INSTALL_URL = URL + "install.html" # QR 指向安裝教學頁：手機掃描後直接看到「一鍵安裝」

BG, ACCENT, WHITE = (11, 13, 16), (255, 107, 44), (242, 245, 248)

# ---------------------------------------------------------------- 圖示
def make_icon(size, maskable=False):
    S = size * 4  # 超取樣抗鋸齒
    img = Image.new("RGBA", (S, S), BG + (255,))
    d = ImageDraw.Draw(img)
    # maskable：內容需落在中央 80% 安全區；一般圖示用圓角並稍微放大內容
    scale = 0.62 if maskable else 0.74
    if not maskable:
        m = Image.new("L", (S, S), 0)
        ImageDraw.Draw(m).rounded_rectangle([0, 0, S - 1, S - 1], radius=int(S * 0.22), fill=255)
        img.putalpha(m)
    cx = cy = S / 2
    u = S * scale / 24.0
    ox, oy = cx - 12 * u, cy - 12 * u
    P = lambda x, y: (ox + x * u, oy + y * u)
    w = int(1.8 * u * 1.5)
    # 路線線條（Lucide route 風格）：由左下蜿蜒到右上
    pts = []
    for t in range(0, 101):
        t /= 100
        x = 6 + 12 * t
        y = 19 - 14 * t + 3.2 * math.sin(t * math.pi * 2.2)
        pts.append(P(x, y))
    d.line(pts, fill=ACCENT + (255,), width=w, joint="curve")
    for (px, py) in (pts[0], pts[-1]):
        r = 2.6 * u
        d.ellipse([px - r, py - r, px + r, py + r], fill=BG + (255,), outline=WHITE + (255,), width=int(w * 0.8))
    # 右上角錄影點
    rx, ry = P(20.2, 3.8); r = 1.7 * u
    d.ellipse([rx - r, ry - r, rx + r, ry + r], fill=(239, 68, 68, 255))
    return img.resize((size, size), Image.LANCZOS)

make_icon(192).save("icon-192.png")
make_icon(512).save("icon-512.png")
make_icon(512, maskable=True).save("icon-maskable-512.png")
make_icon(180, maskable=True).convert("RGB").save("apple-touch-icon.png")  # iOS 不支援透明，使用滿版
print("圖示完成")

# ---------------------------------------------------------------- QR Code
qr = segno.make(INSTALL_URL, error="m", micro=False)
# 內嵌 SVG（不依賴外部服務）
buf = io.BytesIO()
qr.save(buf, kind="svg", scale=1, border=2, dark="#000000", light="#ffffff", xmldecl=False, svgns=True, omitsize=True, nl=False)
svg_inline = buf.getvalue().decode("utf-8")
svg_inline = svg_inline.replace("<svg ", '<svg role="img" aria-label="安裝 QR Code" shape-rendering="crispEdges" ', 1)
# PNG（qr-install.png）：每模組 16px，含 4 模組安靜區
qr.save("qr-install.png", scale=16, border=4, dark="#000000", light="#ffffff")
print("QR 完成")

# ---------------------------------------------------------------- 解碼驗證
def decode_png(path):
    im = cv2.imread(path)
    val, _, _ = cv2.QRCodeDetector().detectAndDecode(im)
    return val

png_val = decode_png("qr-install.png")
# 另外把內嵌 SVG 轉成大圖後再解一次，確保 install.html 內的 SVG 與 PNG 一致
buf2 = io.BytesIO(); qr.save(buf2, kind="png", scale=12, border=4); buf2.seek(0)
svg_matrix_val = cv2.QRCodeDetector().detectAndDecode(cv2.cvtColor(np.array(Image.open(buf2).convert("L")), cv2.COLOR_GRAY2BGR))[0]
ok = (png_val == INSTALL_URL and svg_matrix_val == INSTALL_URL)
print("PNG 解碼 :", png_val)
print("SVG 來源 :", svg_matrix_val)
print("正式網址 :", INSTALL_URL)
print("驗證結果 :", "完全一致 ✓" if ok else "不一致 ✗")
if not ok:
    sys.exit("QR 驗證失敗")

# ---------------------------------------------------------------- install.html
html = r'''<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>安裝 跡錄 TraceCam｜安裝教學</title>
<meta name="theme-color" content="#0b0d10">
<meta name="color-scheme" content="light dark">
<link rel="icon" type="image/png" href="./icon-192.png">
<link rel="apple-touch-icon" href="./apple-touch-icon.png">
<link rel="manifest" href="./manifest.json">
<style>
:root{--bg:#f5f6f8;--card:#fff;--line:#e3e6ea;--text:#14181d;--sub:#5d6875;--accent:#e8561a;--soft:rgba(232,86,26,.1)}
@media (prefers-color-scheme:dark){:root{--bg:#0b0d10;--card:#14181d;--line:#2a313a;--text:#f2f5f8;--sub:#8b96a3;--accent:#ff6b2c;--soft:rgba(255,107,44,.14)}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,"PingFang TC","Noto Sans TC","Microsoft JhengHei",system-ui,sans-serif;line-height:1.7;
  padding:calc(env(safe-area-inset-top) + 20px) 16px calc(env(safe-area-inset-bottom) + 32px)}
.wrap{max-width:760px;margin:0 auto}
header{display:flex;align-items:center;gap:14px;margin-bottom:18px}
header img{width:60px;height:60px;border-radius:15px}
h1{margin:0;font-size:24px} header p{margin:2px 0 0;color:var(--sub);font-size:14px}
.card{background:var(--card);border:1px solid var(--line);border-radius:20px;padding:20px;margin-bottom:16px}
.qr{display:grid;grid-template-columns:200px 1fr;gap:22px;align-items:center}
.qr .code{background:#fff;border-radius:14px;padding:8px;width:200px;height:200px;border:1px solid var(--line)}
.qr .code svg{width:100%;height:100%;display:block}
.url{word-break:break-all;font-size:13px;color:var(--sub);background:var(--bg);padding:8px 10px;border-radius:10px;margin:8px 0 12px;user-select:all}
.btns{display:flex;flex-wrap:wrap;gap:8px}
button,a.b{font:inherit;font-size:14px;height:42px;padding:0 16px;border-radius:21px;border:1px solid var(--line);background:var(--card);color:var(--text);cursor:pointer;display:inline-flex;align-items:center;gap:7px;text-decoration:none}
button.p,a.p{background:var(--accent);border-color:var(--accent);color:#fff}
svg.i{width:18px;height:18px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}
h2{font-size:18px;margin:0 0 4px;display:flex;align-items:center;gap:9px}
h2 svg{color:var(--accent)}
.sub{color:var(--sub);font-size:13px;margin:0 0 10px}
ol{margin:10px 0 0;padding:0;list-style:none;counter-reset:s;display:grid;gap:10px}
li{counter-increment:s;display:flex;gap:12px;font-size:15px}
li::before{content:counter(s);flex:none;width:26px;height:26px;border-radius:50%;background:var(--soft);color:var(--accent);display:grid;place-items:center;font-size:13px;font-weight:600;margin-top:1px}
.tip{font-size:13px;color:var(--sub);margin-top:12px;padding-top:12px;border-top:1px dashed var(--line)}
b.k{background:var(--soft);color:var(--accent);padding:0 6px;border-radius:6px;font-weight:600}
.hero{display:flex;flex-direction:column;align-items:center;gap:10px;text-align:center;padding:24px 20px}
.hero .big{height:60px;padding:0 34px;border-radius:30px;font-size:19px;font-weight:700;width:100%;max-width:420px;justify-content:center;box-shadow:0 10px 28px rgba(232,86,26,.35)}
.hero .big:active{transform:scale(.97)}
.hero .st{font-size:13px;color:var(--sub);min-height:20px}
.hero .st.ok{color:#1a9c64;font-weight:600}
.mask{position:fixed;inset:0;background:rgba(0,0,0,.55);display:none;align-items:flex-end;justify-content:center;z-index:50;padding:16px;backdrop-filter:blur(4px)}
.mask.on{display:flex}
.sheet{background:var(--card);border:1px solid var(--line);border-radius:24px;width:100%;max-width:460px;padding:22px 20px calc(env(safe-area-inset-bottom) + 20px);animation:up .22s ease-out}
@keyframes up{from{transform:translateY(30px);opacity:0}to{transform:none;opacity:1}}
.sheet h3{margin:0 0 4px;font-size:19px}
.arrow{text-align:center;color:var(--accent);margin-top:10px;font-size:13px;animation:bob 1.2s infinite}
@keyframes bob{50%{transform:translateY(6px)}}
@media (max-width:600px){.qr{grid-template-columns:1fr;justify-items:center;text-align:center}.btns{justify-content:center}}
@media print{body{background:#fff;color:#000}.btns,.noprint{display:none!important}.card{break-inside:avoid;border-color:#ccc}}
</style>
</head>
<body>
<div class="wrap">
  <header><img src="./icon-192.png" alt="跡錄 TraceCam"><div><h1>安裝「跡錄」</h1><p>TraceCam・運動錄影疊加：即時地圖、速度、距離、海拔，拍完免後製</p></div></header>

  <section class="card hero">
    <button class="p big" id="oneclick"><svg class="i" viewBox="0 0 24 24" style="width:24px;height:24px"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="m7 10 5 5 5-5"/><path d="M12 15V3"/></svg>一鍵安裝</button>
    <div class="st" id="ost"></div>
  </section>

  <section class="card qr">
    <div class="code">__QR_SVG__</div>
    <div>
      <h2>掃描 QR Code 開啟</h2>
      <p class="sub">用手機相機掃描，開啟本頁後按上方「一鍵安裝」。</p>
      <div class="url" id="u">__URL__</div>
      <div class="btns">
        <button class="p" id="copy"><svg class="i" viewBox="0 0 24 24"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg><span id="ct">複製連結</span></button>
        <a class="b" href="__APP_URL__" target="_blank" rel="noopener"><svg class="i" viewBox="0 0 24 24"><path d="M15 3h6v6"/><path d="M10 14 21 3"/><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/></svg>直接開啟</a>
        <button id="print"><svg class="i" viewBox="0 0 24 24"><path d="M6 9V2h12v7"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect x="6" y="14" width="12" height="8"/></svg>列印此頁</button>
      </div>
    </div>
  </section>

  <section class="card">
    <h2><svg class="i" viewBox="0 0 24 24"><rect x="5" y="2" width="14" height="20" rx="2"/><path d="M12 18h.01"/></svg>iPhone／iPad（Safari）</h2>
    <p class="sub">iOS 僅有 Safari 能加入主畫面；若在其他瀏覽器開啟，請先複製連結改用 Safari。</p>
    <ol>
      <li><span>在 Safari 開啟上方網址，點選工具列的<b class="k">分享</b>圖示（方框加向上箭頭）。</span></li>
      <li><span>在選單中往下滑，點選<b class="k">加入主畫面</b>。</span></li>
      <li><span>確認名稱「跡錄」，點右上角<b class="k">新增</b>。</span></li>
      <li><span>從主畫面開啟，首次請允許<b class="k">相機</b>、<b class="k">麥克風</b>與<b class="k">定位</b>（建議選「使用 App 期間」）。</span></li>
    </ol>
    <div class="tip">錄影完成後，在行程詳情點「儲存／分享影片」→ 選擇「儲存視訊」即可存入相簿。</div>
  </section>

  <section class="card">
    <h2><svg class="i" viewBox="0 0 24 24"><rect x="5" y="2" width="14" height="20" rx="2"/><path d="M12 18h.01"/></svg>Android（Chrome）</h2>
    <ol>
      <li><span>用 Chrome 開啟上方網址。</span></li>
      <li><span>點選右上角<b class="k">⋮</b>選單。</span></li>
      <li><span>選擇<b class="k">安裝應用程式</b>（部分機型顯示為「加到主畫面」），再點<b class="k">安裝</b>。</span></li>
      <li><span>從桌面或應用程式列表開啟，並允許相機、麥克風與定位權限。</span></li>
    </ol>
  </section>

  <section class="card">
    <h2><svg class="i" viewBox="0 0 24 24"><rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8"/><path d="M12 17v4"/></svg>電腦（Chrome／Edge）</h2>
    <ol>
      <li><span>用 Chrome 或 Edge 開啟上方網址。</span></li>
      <li><span>點選網址列右側的<b class="k">安裝</b>圖示（螢幕加向下箭頭）。</span></li>
      <li><span>在彈出視窗按<b class="k">安裝</b>，即可像一般軟體從桌面或開始選單開啟。</span></li>
    </ol>
    <div class="tip">電腦沒有 GPS，定位會以網路估算，僅適合預覽介面；實際運動請使用手機。</div>
  </section>

  <p class="sub" style="text-align:center">安裝後可離線開啟。有新版本時，App 內會出現「有新版本可用．立即更新」。</p>
</div>
<div class="mask" id="mask"><div class="sheet" id="sheet">
  <h3 id="sh-t">加入主畫面</h3><p class="sub" id="sh-s"></p>
  <ol id="sh-o"></ol>
  <div class="arrow" id="sh-a"></div>
  <div class="btns" style="margin-top:16px"><button class="p" id="sh-ok" style="flex:1;justify-content:center">我知道了</button></div>
</div></div>
<script>
(function(){
  var url = document.getElementById('u').textContent.trim();
  var APP = "__APP_URL__";
  var ua = navigator.userAgent;
  var ios = /iPhone|iPad|iPod/.test(ua) || (navigator.platform==='MacIntel' && navigator.maxTouchPoints>1);
  var android = /Android/.test(ua);
  var safari = ios && /Safari/.test(ua) && !/CriOS|FxiOS|EdgiOS|OPiOS|Line|FBAN|FBAV|Instagram/.test(ua);
  var standalone = matchMedia('(display-mode: standalone)').matches || navigator.standalone;
  var deferred = null, btn = document.getElementById('oneclick'), st = document.getElementById('ost');

  /* 註冊 SW（僅 https / localhost），讓教學頁也符合安裝條件並順便快取 */
  try { if ('serviceWorker' in navigator && (location.protocol==='https:'||location.hostname==='localhost')) navigator.serviceWorker.register('./sw.js'); } catch(e){}

  function sheet(title, sub, steps, arrow){
    document.getElementById('sh-t').textContent = title;
    document.getElementById('sh-s').textContent = sub || '';
    document.getElementById('sh-o').innerHTML = steps.map(function(x){return '<li><span>'+x+'</span></li>';}).join('');
    document.getElementById('sh-a').textContent = arrow || '';
    document.getElementById('mask').classList.add('on');
  }
  document.getElementById('sh-ok').onclick = function(){ document.getElementById('mask').classList.remove('on'); };
  document.getElementById('mask').onclick = function(e){ if(e.target.id==='mask') e.currentTarget.classList.remove('on'); };

  function setStatus(msg, ok){ st.textContent = msg; st.className = 'st' + (ok ? ' ok' : ''); }

  if (standalone) { btn.innerHTML = btn.innerHTML.replace('一鍵安裝','開啟 跡錄'); setStatus('已安裝，正在 App 模式中', true); }
  else if (ios) { setStatus(safari ? 'iPhone 無法自動安裝，點按鈕會顯示 3 個步驟' : '請先用 Safari 開啟（目前不是 Safari）'); }
  else { setStatus('點一下即可安裝到主畫面'); }

  window.addEventListener('beforeinstallprompt', function(e){ e.preventDefault(); deferred = e; setStatus('瀏覽器已準備好，點一下即可安裝', true); });
  window.addEventListener('appinstalled', function(){ deferred=null; setStatus('安裝完成 ✓ 請從主畫面開啟 跡錄', true); });

  btn.onclick = async function(){
    try {
      if (standalone) { location.href = APP; return; }
      if (deferred) {                                   // Android / 電腦 Chrome、Edge：原生一鍵安裝
        deferred.prompt();
        var r = await deferred.userChoice; deferred = null;
        setStatus(r.outcome==='accepted' ? '安裝中… 完成後請從主畫面開啟' : '已取消，可再按一次', r.outcome==='accepted');
        return;
      }
      if (ios) {                                        // iOS 沒有安裝 API：以引導視窗取代
        if (!safari) { sheet('請改用 Safari 開啟','iOS 只有 Safari 能加入主畫面。',['點下方「複製連結」','打開 Safari，貼上網址並前往','回到本頁再按「一鍵安裝」'],''); return; }
        sheet('只要 3 步','請依序操作（畫面下方就是分享鈕）：',
          ['點 Safari 底部的<b class="k">分享</b>圖示（方框加向上箭頭）','往下滑，點<b class="k">加入主畫面</b>','右上角點<b class="k">新增</b>，完成'],'↓ 分享鈕在畫面最下方（iPad 在右上角）');
        return;
      }
      /* 尚未收到安裝事件：多半是已安裝過、或瀏覽器不支援，提供手動步驟 */
      if (android) sheet('手動安裝','請使用 Chrome：',['點右上角<b class="k">⋮</b>選單','選<b class="k">安裝應用程式</b>（或「加到主畫面」）','按<b class="k">安裝</b>'],'');
      else sheet('手動安裝','請使用 Chrome 或 Edge：',['點網址列右側的<b class="k">安裝</b>圖示','按<b class="k">安裝</b>'],'');
      setStatus('若已安裝過，請直接從主畫面／桌面開啟');
    } catch(err){ setStatus('安裝時發生問題：'+(err&&err.message||err)); }
  };
  document.getElementById('copy').onclick = function(){
    var done = function(){ var t=document.getElementById('ct'); t.textContent='已複製 ✓'; setTimeout(function(){t.textContent='複製連結';},1800); };
    try { navigator.clipboard.writeText(url).then(done, fallback); } catch(e){ fallback(); }
    function fallback(){ var r=document.createRange(); r.selectNodeContents(document.getElementById('u')); var s=getSelection(); s.removeAllRanges(); s.addRange(r); try{document.execCommand('copy'); done();}catch(e){} }
  };
  document.getElementById('print').onclick = function(){ window.print(); };
})();
</script>
</body>
</html>
'''
html = html.replace("__QR_SVG__", svg_inline).replace("__APP_URL__", APP_URL).replace("__URL__", INSTALL_URL)
open("install.html", "w", encoding="utf-8").write(html)
print("install.html 完成")

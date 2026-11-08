# Devpost 提交自助卡（目标：30 分钟内独立完成三件事）
> 适用场景：浏览器面板路线走不通时，用你自己的浏览器完成。截止：**北京时间 11-13 凌晨 4:00**。
> 材料：视频文件 `E:\AIworkspace\projects\Project 016-PayPal账单助手Agent\deliverables\demo-final-en.mp4`（1:44，已带英文配音）
> 仓库：https://github.com/guannan1031/paypal-bill-agent （已公开，MIT License 可见）

---

## 第 1 步｜YouTube 上传（约 10 分钟）
1. 浏览器打开 https://studio.youtube.com → 用你的 Google 账号登录
2. 左上角「创建」→「上传视频」→ 选择上面的 demo-final-en.mp4
3. 标题（复制粘贴）：
   ```
   AI Bill & Invoice Agent — pay bills & get paid with PayPal (human-in-the-loop)
   ```
4. 说明（复制粘贴）：
   ```
   PayPal AI Hackathon 2026 submission.
   Paste messy bills -> AI parses -> risk flags (overdue/large/duplicate) -> you confirm -> agent pays via PayPal Orders v2.
   The other direction: draft invoices via PayPal Invoicing v2, send, reconcile payments.
   Decision to the AI, execution to PayPal, control stays with the human.
   GitHub: https://github.com/guannan1031/paypal-bill-agent
   Demo mode: PayPal sandbox / mock, no real money moved.
   ```
5. 可见性选「公开」→ 发布 → 复制视频链接（形如 https://youtu.be/xxxx）
   □ 完成，链接记下：____________

## 第 2 步｜Render 部署（约 10 分钟，可选但强烈建议）
> 不部署也能合规提交（仓库含完整运行说明），但部署了才能进 Best Use of Render 奖池
1. 打开 https://render.com → **Sign in with GitHub**（用刚登录的 GitHub 授权）
2. 右上 **New +** → **Blueprint** → 选择仓库 `paypal-bill-agent` → **Apply**
   （render.yaml 在仓库根目录，会自动识别；免费实例首次访问约 50 秒唤醒属正常）
3. 部署完成后复制 URL（形如 https://paypal-bill-agent.onrender.com）
   □ 完成，链接记下：____________

## 第 3 步｜Devpost 报名+提交（约 15 分钟）
1. 打开 https://devpost.com → 右上 **Log in** → 选 **Log in with GitHub** 授权
2. 打开 https://paypalaihackathon.devpost.com → 点 **Join hackathon**（如已加入会显示 Registered）
3. 进入 https://paypalaihackathon.devpost.com/submissions （或项目页点 Submit）新建提交：

| 表单字段 | 粘贴内容 |
| --- | --- |
| Project title | AI Bill & Invoice Agent — pay bills & get paid with PayPal, human-in-the-loop |
| Tagline | One agent for both directions of your money flow: AI parses your bills and pays them via PayPal, then invoices your clients and reconciles who paid. |
| GitHub link | https://github.com/guannan1031/paypal-bill-agent |
| Demo video link | （第 1 步的 YouTube 链接） |
| Hosted URL（如有） | （第 2 步的 Render 链接） |

4. 「Story/About」等长文本：打开同目录文件复制 → `E:\AIworkspace\projects\Project 016-PayPal账单助手Agent\docs\devpost-submission.md`（Inspiration/What it does/How we built it/Challenges/Learned/What's next 六段全在里面）
5. Tools used 逐个添加：PayPal Orders API v2 / PayPal Invoicing API v2 / PayPal Developer Sandbox / paypal-agent-toolkit / Model Context Protocol / FastAPI / Python / httpx / Render / GitHub
6. 检查清单：
   □ 视频公开可看 □ 仓库公开+License □ 项目同时体现 AI 与 PayPal □ 全部字段填完
7. 点 **Submit / Publish submission** → 出现确认页即完成
   □ 完成，提交链接记下：____________

---

## 完成后回我一句，附上三个链接，我做最终核验（三链接可达性+规则合规复检）。
## 常见坑
- YouTube 上传后「公开」要等处理完才能分享，几分钟即可
- Render 免费实例会休眠：提交前先自己访问一次 URL 唤醒
- Devpost 表单里 YouTube 链接必须填完整 URL（含 https://）

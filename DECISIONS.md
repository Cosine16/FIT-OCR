# FIT-OCR 设计决策（grill-me 产出）

> 日期: 2026-06-07  
> 方法: mattpocock-skills:grill-me  
> 状态: 锁定 → 进入 prototype 阶段

## 项目目标
把纸质数学笔记（手写 + 印刷混排）通过拍照数字化为 **Markdown + LaTeX**。

## 硬件约束
- GPU: NVIDIA GTX 1650 (4GB, SM 7.5, Turing)
- 关键限制: 无 bf16 加速，vLLM/SGLang 内核要 SM 8.0+ → **大 VLM 物理上跑不了**
- 平台: WSL2 on Windows (driver 573.24, CUDA 12.8)

## 5 个决策

### Q1: 部署形态 = **本地小模型**
拒绝 DeepSeek-OCR (14GB 显存) / GLM-4V (20GB 显存)，这是硬件物理限制不是优化问题。

### Q2: 路线 = **纯本地，无云端**
隐私零外传。

### Q3: 模型选型 = **Pix2Text（主力） + UniMERNet（兜底）**
- **Pix2Text**: 中文友好，整页一站式（版面+OCR+公式→Markdown+LaTeX），1-2GB 显存
- **UniMERNet**: SOTA 公式专项，疑难公式用户手动框选重跑

### Q4: 前端 = **FastAPI Web UI（本地+局域网） + 保留 CLI**
- 一份代码同时服务电脑浏览器 + 手机浏览器（手机通过 Tailscale/局域网访问）
- 手机用 `<input capture="environment">` 调起后摄拍照
- Web UI 三栏: 原图 / KaTeX 渲染 / LaTeX 源码
- "框选重跑" 是核心 UX —— 主流程 Pix2Text 不准时，框出公式区域单独送 UniMERNet
- CLI 保留作批量处理快捷方式

### Q5: 后处理 + 落盘 = **轻量后处理 + .md 主格式**
- 后处理: 去瑕疵 + KaTeX 渲染校验（失败的标 ⚠️），**不做激进自动纠错**
- 主输出: 单图一个 .md，内部用 JSON 结构便于扩展
- 输出目录:
  ```
  output/
  ├─ photo_001.md     主格式
  ├─ photo_001.json   调试/二次处理
  └─ photo_001.png    原图副本
  ```

## 架构草图
```
                                    ┌─────────────────────┐
                            ┌──────►│ Pix2Text (主力)     │── 整页 → MD+LaTeX
                            │       └─────────────────────┘
   拍照/上传 ──► FastAPI ───┤
                            │       ┌─────────────────────┐
                            └──────►│ UniMERNet (兜底)    │── 单公式 → LaTeX
                                    └─────────────────────┘
                                            │
                                            ▼
                                   清洗 + KaTeX 校验
                                            │
                                            ▼
                                   .md / .json / 原图
```

## 不做的事（防止 scope creep）
- ❌ 自动公式纠错（短期聪明长期 bug 温床）
- ❌ Anki / Notion 集成（不在数字化笔记核心路径上）
- ❌ .tex 整文档导出（5 行代码包一层就够，等真有需求再说）
- ❌ 多用户 / 账号系统（本地工具）
- ❌ 数据库持久化（文件系统就够）

## Prototype 范围（throwaway）
原型只回答一个问题：**「4GB GTX 1650 + WSL2，Pix2Text + UniMERNet 真的能跑起来吗？以及对真实笔记效果如何？」**

如果跑不通或效果差，回到 grill-me 重新选型；跑通了再做真实工程化。

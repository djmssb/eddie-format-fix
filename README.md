# Eddie format · 第三方修复版

> **这不是官方版本。**
>
> 本仓库是社区用户对 [飞鼠格式 FlyingMouse Format](https://github.com/LaoFeng-mouse/flyingmouse-format)（作者：**牢蜂 LaoFeng**）的**本地修复补丁集**。它不包含任何原创的转换引擎，全部转换能力来自原项目及其内置的 FFmpeg / LibreOffice / Poppler / Tesseract。修复工作由本仓库维护者完成，**不代表原作者，也未获原作者背书**。
>
> 原项目声明：*仅供个人免费使用，禁止商业售卖 / 转卖 / 套壳。* 本仓库完全遵守这一条 —— **不收费、不售卖、不以此为商品**。如果你需要官方版本、最新功能或作者支持，请前往[原项目](https://github.com/LaoFeng-mouse/flyingmouse-format)。

---

## 这是什么

一个 Windows 上离线可用的文件格式转换工具的**修复版构建**，程序名 `Eddie format` 只是本地打包时用的标识，与原项目名称无关。

支持图片、Word/WPS 文档、电子表格、演示文稿、PDF、ZIP 和常见音视频格式互转，附带 OCR、批量转换、PDF 合并拆分、文件夹转 PDF、图片合成 PDF 等功能。

程序完全在本机运行，不联网、不上传文件。

## 修复了什么

上游 0.6.4 构建版在实际使用中存在几处问题，这个版本逐项修掉：

| # | 问题 | 修复方式 | 涉及文件 |
|---|---|---|---|
| 1 | 连续转换多份 Markdown 时，图片全被塞进同一个 `.assets` 文件夹，后一次覆盖前一次 | 每次转换生成独立的图片文件夹，并把该文件夹一路传回桌面端与 CLI 的保存逻辑（含重命名场景） | `server.js` `electron-main.js` `cli.js` |
| 2 | CLI 模式转换 Markdown 时不下载文中引用的网络图片 | 补齐 CLI 路径的图片抓取 | `cli.js` |
| 3 | 发行包没带 qpdf，但界面仍允许点 PDF 加密/解密，点了必报错 | 检测到 qpdf 缺失时直接在界面禁用相关选项 | `pdf.js` `public/app.js` |
| 4 | 没有结构化 PDF 引擎时，扫描版 PDF 转 Word 直接失败 | 改为走 OCR 兜底；纯文字 PDF 转 Word 时明确提示"图片与版式不保留" | `office-convert.js` `pdf.js` |
| 5 | 赞助弹窗最后一句带强迫意味的提示语 | 中英文同步删掉该句，保留"免费、自愿支持"的表述 | `public/app.js` |

原始压缩包保留为 `resources/app.asar.before-fix`，随时可回退。

## 下载与安装

到 [Releases](../../releases) 页面下载**全部 10 个分卷**（`.zip.001` ~ `.zip.010`）和 `合并并解压.bat`，放进同一个文件夹，双击 bat 即可 —— 它会自动合并、解压。

不想用脚本的话，在分卷所在文件夹打开命令提示符，手动合并：

```bat
copy /b Eddie-format-0.6.4-win-x64.zip.001+Eddie-format-0.6.4-win-x64.zip.002+Eddie-format-0.6.4-win-x64.zip.003+Eddie-format-0.6.4-win-x64.zip.004+Eddie-format-0.6.4-win-x64.zip.005+Eddie-format-0.6.4-win-x64.zip.006+Eddie-format-0.6.4-win-x64.zip.007+Eddie-format-0.6.4-win-x64.zip.008+Eddie-format-0.6.4-win-x64.zip.009+Eddie-format-0.6.4-win-x64.zip.010 Eddie-format-0.6.4-win-x64.zip
```

合并出来的 zip 约 775 MB，用 7-Zip 或 Windows 自带解压都行。

> **为什么分卷**：完整包 775 MB，GitHub 的上传通道单次 POST 有约 4 分钟硬超时，大文件必然传到一半被切断，只能切成小段逐段上传。分卷只是把原文件按字节切开，合并回来和原包完全一致（SHA-256 一样）。

- 解压后体积约 2 GB，因为内置了 LibreOffice、FFmpeg、Poppler、Tesseract 四套离线引擎，**不需要另外装 Office 或 Python**。
- 必须保留整个文件夹，`resources` 目录是转换引擎本体，只复制 exe 会缺功能。
- 首次启动 Windows SmartScreen 可能提示未知发布者 —— 这是未签名程序的正常现象，选择"更多信息 → 仍要运行"。

详细用法见仓库内 [`Eddie-format-使用说明.md`](Eddie-format-使用说明.md)。

## 自己打补丁

如果你已经持有官方 0.6.4 安装包，可以不用下载 2 GB 的完整包，只打补丁：

```powershell
# 1. 把 patch/ 里的文件按相同路径放进程序的 resources/app.asar.unpacked 对应位置
#    或者用 asar 工具重新打包：
npm i -g @electron/asar

# 2. 解包
asar extract resources/app.asar app_unpacked

# 3. 用 patch/ 中的文件覆盖 app_unpacked 里的同名文件
#    patch/server.js        -> app_unpacked/server.js
#    patch/cli.js           -> app_unpacked/cli.js
#    patch/pdf.js           -> app_unpacked/pdf.js
#    patch/office-convert.js-> app_unpacked/office-convert.js
#    patch/electron-main.js -> app_unpacked/electron-main.js
#    patch/public/app.js    -> app_unpacked/public/app.js

# 4. 重新打包（先备份原文件）
asar pack app_unpacked resources/app.asar
```

## 命令行用法

程序支持 `--cli`，可脚本化调用：

```powershell
Set-Location 'D:\路径\Eddie format'

# 查看可用引擎与格式
& '.\Eddie format.exe' --cli capabilities --json

# Word 转 PDF
& '.\Eddie format.exe' --cli convert '报告.docx' --to pdf --output '报告.pdf' --json

# 多张图片合成一个 PDF
& '.\Eddie format.exe' --cli images-to-pdf '1.png' '2.png' --output '合并.pdf' --json

# 多个 PDF 合并
& '.\Eddie format.exe' --cli merge-pdfs '上.pdf' '下.pdf' --output '合并.pdf' --json
```

## 已知限制

- 发行包未包含 qpdf，PDF 加密 / 解密不可用（本版已在界面禁用，不再报错）。
- PDF 转 Word 只保证文字可编辑，图片与原版式不保留；扫描件效果取决于清晰度和文字方向。
- AV1 编码依赖本机硬件，部分机器上会回退到软件编码，速度较慢。

## 许可证与致谢

- 原始软件版权归 **牢蜂（LaoFeng）** 所有，仓库：[LaoFeng-mouse/flyingmouse-format](https://github.com/LaoFeng-mouse/flyingmouse-format)。
- 内置引擎各自遵循其原有许可证：LibreOffice（MPL 2.0）、FFmpeg（LGPL/GPL）、Poppler（GPL-2.0）、Tesseract（Apache 2.0）。
- 本仓库仅包含修复补丁与说明文档，**不含官方源代码**，不主张对原软件的任何权利。
- 使用范围遵循原项目条款：**个人免费使用，禁止商业售卖、转卖、套壳**。

---

*If you are the original author and would prefer this mirror not exist, open an issue and it will be taken down immediately.*

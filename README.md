# nmbxd-downloader

A www.nmbxd1.com contents scrapper & downloader.

X岛揭示板小说下载器。也不限于小说。

免去手工复制粘贴+正则替换。

## Usage

- 注册X岛揭示板账号 (https://www.nmbxd1.com/) 并领取饼干
- 在 https://www.nmbxd1.com/ 上，`F12` 找到 `Cookies`-`https://www.nmbxd1.com/`，复制 `userhash` 中的 Cookie Value 到程序的 `YOUR_USER_HASH_HERE` 部分
- `python nmbxd_downloader.py`

## Note

支持两种模式获取：正常模式 `normal` 与仅看PO `po`。  
`normal`：浏览全部回复页，再按作者饼筛选，支持多饼获取；`po`：使用网站的“只看PO”页面。

## TODO

- [ ] 图片接入OCR，自动将图片转为文字
- [ ] 更多格式（如 `.docx`等）的输出功能

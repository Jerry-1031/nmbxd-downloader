# nmbxd-downloader

A www.nmbxd1.com contents scrapper & downloader.

X岛揭示板小说下载器。也不限于小说。

免去手工复制粘贴+正则替换。

## Usage

- `pip install -r requirements.txt`
- 注册X岛揭示板账号 (https://www.nmbxd1.com/) 并领取饼干
- 在 https://www.nmbxd1.com/ 上，`F12` 找到 `Cookies`-`https://www.nmbxd1.com/`，复制 `userhash` 中的 Cookie Value 到程序的 `YOUR_USER_HASH_HERE` 部分
- `python nmbxd_downloader.py`

> [!NOTE]
> 仅获取 `https://www.nmbxd1.com/Forum/po/id/{}/page/{}.html` 下的链接（仅看PO）。

## TODO

- [ ] 图片接入OCR，自动将图片转为文字
- [ ] 自动判断PO回复内容是否为小说正文，若否则不输出
- [ ] 更多格式（如 `.docx`等）的输出功能

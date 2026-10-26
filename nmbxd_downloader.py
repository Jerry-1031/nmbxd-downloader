import requests
from bs4 import BeautifulSoup, NavigableString, Comment
import re

# 串号
THREAD_ID = "50000001"

# userhash
USER_HASH = "YOUR_USER_HASH_HERE"

# 段间空行数
EMPTY_LINES = 2

# normal：浏览全部回复页，再按作者饼筛选；po：使用网站的“只看PO”
# 作者换过饼时，请使用 normal，网站的只看PO不会包含其他饼的回复
MODE = "po"
BASE_URL_TEMPLATES = {
    "normal": "https://www.nmbxd1.com/t/{}?page={}",
    "po": "https://www.nmbxd1.com/Forum/po/id/{}/page/{}.html",
}

# normal模式下，作者额外使用的饼；可填带 ID: 前缀或不带前缀的值
# 换串时请清空或替换，首帖作者的饼会自动加入。
EXTRA_PO_UIDS = {}


def normalize_uid(uid):
    """统一网页中的 ID: 前缀与手动配置。"""
    return re.sub(r"^ID\s*[:：]\s*", "", uid.strip()).strip()


def is_author_reply(uid, author_uids):
    normalized = normalize_uid(uid)
    return bool(normalized) and normalized in author_uids


def get_text_content(element):
    """提取文字内容并处理HTML换行"""
    if not element:
        return ""
    content = BeautifulSoup(str(element), "html.parser")
    for unwanted in content.select("script, style"):
        unwanted.decompose()
    for node in list(content.find_all(string=True)):
        if isinstance(node, Comment):
            node.extract()
        elif isinstance(node, NavigableString):
            node.replace_with(re.sub(r"[ \t\r\n\f]+", " ", str(node)))
    for br in content.find_all("br"):
        br.replace_with("\n")
    return "\n".join(line.strip() for line in content.get_text().split("\n")).strip()


def get_soup(url):
    """通用请求函数"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    cookies = {"userhash": USER_HASH}

    try:
        response = requests.get(url, headers=headers, cookies=cookies, timeout=10)
        response.raise_for_status()
        response.encoding = "utf-8"
        return BeautifulSoup(response.text, "html.parser")
    except requests.RequestException as e:
        print(f"请求失败 [{url}]: {e}")
        return None


def extract_image_link(container):
    """提取图片大图链接"""
    img_a = container.find("a", class_="h-threads-img-a")
    if img_a and img_a.get("href"):
        return img_a.get("href")
    return None


def get_total_pages(soup):
    """兼容正常模式的 ?page=N 和只看PO模式的 /page/N.html"""
    max_page = 1
    for pagination in soup.select("ul.uk-pagination"):
        for element in pagination.select("[href], li.uk-active"):
            href = element.get("href", "")
            for pattern in (
                r"[?&]page=(\d+)(?:[&#]|$)",
                r"/page/(\d+)\.html(?:[?#]|$)",
            ):
                match = re.search(pattern, href)
                if match:
                    max_page = max(max_page, int(match.group(1)))
            text = element.get_text(strip=True)
            if text.isdigit():
                max_page = max(max_page, int(text))
    return max_page


if __name__ == "__main__":
    base_url_template = BASE_URL_TEMPLATES[MODE]
    print(f"当前模式: {MODE}")

    all_content_blocks = []

    current_page = 1
    first_url = base_url_template.format(THREAD_ID, current_page)
    print(f"正在分析第 1 页: {first_url}")

    soup = get_soup(first_url)
    if not soup:
        print("无法获取网页，请检查网络或Cookie是否过期。")
        raise SystemExit(1)

    total_pages = get_total_pages(soup)
    print(f"检测到总页数: {total_pages}")

    main_item = soup.find("div", class_="h-threads-item")
    if not main_item:
        print("未找到内容，可能是Cookie无效或串已被删除。")
        raise SystemExit(1)

    main_div = main_item.find("div", class_="h-threads-item-main")
    info_div = main_div.find("div", class_="h-threads-info")

    title_span = info_div.find("span", class_="h-threads-info-title")
    title_text = title_span.get_text(strip=True) if title_span else "无标题"

    uid_span = info_div.find("span", class_="h-threads-info-uid")
    po_uid_text = uid_span.get_text(strip=True) if uid_span else ""
    author_uids = {normalize_uid(uid) for uid in EXTRA_PO_UIDS}
    author_uids.add(normalize_uid(po_uid_text))
    author_uids.discard("")

    time_span = info_div.find("span", class_="h-threads-info-createdat")
    time_text = time_span.get_text(strip=True) if time_span else ""

    no_a = info_div.find("a", class_="h-threads-info-id")
    no_text = no_a.get_text(strip=True) if no_a else f"No.{THREAD_ID}"

    header_line = f"{time_text} {po_uid_text} {no_text}"
    all_content_blocks.append(header_line)

    if title_text != "无标题":
        all_content_blocks.append(title_text)

    def extract_from_page(page_soup, is_first_page):
        blocks = []
        page_main_item = page_soup.find("div", class_="h-threads-item")
        if not page_main_item:
            return blocks

        if is_first_page:
            p_main_div = page_main_item.find("div", class_="h-threads-item-main")

            img_link = extract_image_link(p_main_div)

            p_content_div = p_main_div.find("div", class_="h-threads-content")
            text_content = get_text_content(p_content_div)

            full_content = ""
            if img_link:
                full_content += img_link + "\n"
            full_content += text_content

            blocks.append(full_content)

        replies_container = page_main_item.find("div", class_="h-threads-item-replies")
        if replies_container:
            replies = replies_container.find_all("div", class_="h-threads-item-reply")
            for reply in replies:
                reply_main = reply.find("div", class_="h-threads-item-reply-main")
                if not reply_main:
                    continue

                r_info = reply_main.find("div", class_="h-threads-info")
                if not r_info:
                    continue

                r_uid_span = r_info.find("span", class_="h-threads-info-uid")
                r_uid_text = r_uid_span.get_text(strip=True) if r_uid_span else ""

                if is_author_reply(r_uid_text, author_uids):
                    r_img_link = extract_image_link(reply_main)

                    r_content_div = reply_main.find("div", class_="h-threads-content")
                    r_text = get_text_content(r_content_div)

                    if r_text or r_img_link:
                        r_full = ""
                        if r_img_link:
                            r_full += r_img_link + "\n"
                        r_full += r_text
                        blocks.append(r_full)
        return blocks

    all_content_blocks.extend(extract_from_page(soup, is_first_page=True))

    for page_num in range(2, total_pages + 1):
        target_url = base_url_template.format(THREAD_ID, page_num)
        print(f"正在抓取第 {page_num}/{total_pages} 页: {target_url}")
        p_soup = get_soup(target_url)
        if p_soup:
            page_blocks = extract_from_page(p_soup, is_first_page=False)
            all_content_blocks.extend(page_blocks)

    if title_text == "无标题":
        file_name = f"No.{THREAD_ID}.txt"
    else:
        file_name = f"{title_text}.txt"

    separator = "\n" * (EMPTY_LINES + 1)

    try:
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(separator.join(all_content_blocks))
        print(f"\n完成！内容已保存至: {file_name}")
    except IOError as e:
        print(f"写入文件失败: {e}")

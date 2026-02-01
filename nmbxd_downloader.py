import requests
from bs4 import BeautifulSoup
import re
# import time

# 串号
THREAD_ID = "50000001"

USER_HASH = "YOUR_USER_HASH_HERE"

# 段间空行数
EMPTY_LINES = 1


def get_text_content(element):
    """提取文字内容并处理HTML换行"""
    if not element:
        return ""
    return element.get_text(separator="\n", strip=True)


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
    """解析总页数"""
    pagination = soup.find("ul", class_="uk-pagination")
    if not pagination:
        return 1

    last_page_link = pagination.find("a", string="末页")
    if last_page_link:
        href = last_page_link.get("href")
        match = re.search(r"/page/(\d+)\.html", href)
        if match:
            return int(match.group(1))

    page_links = pagination.find_all("a")
    max_page = 1
    for link in page_links:
        text = link.get_text(strip=True)
        if text.isdigit():
            p = int(text)
            if p > max_page:
                max_page = p

    active_span = pagination.find("li", class_="uk-active")
    if active_span:
        text = active_span.get_text(strip=True)
        if text.isdigit() and int(text) > max_page:
            max_page = int(text)

    return max_page


if __name__ == "__main__":
    base_url_template = "https://www.nmbxd1.com/Forum/po/id/{}/page/{}.html"

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

                # is_po_tag = False
                # po_tag_span = r_info.find("span", class_="uk-text-primary")
                # if po_tag_span and "(PO主)" in po_tag_span.get_text():
                #     is_po_tag = True

                # if is_po_tag or (r_uid_text == po_uid_text):
                if r_uid_text == po_uid_text:
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

        # time.sleep(0.5)

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

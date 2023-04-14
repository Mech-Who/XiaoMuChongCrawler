# 小木虫考研调剂信息爬虫

## 主要逻辑
1. 网页下载 download_content(url)
2. 爬取帖子网址 parse(soup, filename)
3. 爬取帖子内容 parse_post(address)
4. 根据关键字对内容进行过滤 line 138
5. 保存内容到文件 append_to_file(filename, content)

## 待完成
1. 后续的更新路线

## BUG
1. 基于关键字过滤帖子仍存在缺陷,最终仍然需要人工过滤,即一条一条的点进去查看
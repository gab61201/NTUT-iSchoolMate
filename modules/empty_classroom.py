from .web_scraper import WebScraper
import asyncio
import json
import re

url = "https://aps.ntut.edu.tw/course/tw/Croom.jsp?format=-3&year=114&sem=1&code=15"


def parse_table_with_regex(html_content):
    """使用正則表達式解析沒有完整標籤的表格"""
    # 找到第二個表格（課表資料）
    tables = re.findall(r"<table[^>]*>.*?</table>", html_content, re.DOTALL)
    if len(tables) < 2:
        return None

    schedule_table = tables[1]

    # 解析表格行
    rows = []

    # 使用正則表達式找到所有的 <tr> 開始標籤後的內容，直到下一個 <tr> 或 </table>
    tr_pattern = r"<tr[^>]*>(.*?)(?=<tr[^>]*>|</table>)"
    tr_matches = re.findall(tr_pattern, schedule_table, re.DOTALL | re.IGNORECASE)

    for tr_content in tr_matches:
        # 解析單元格內容
        # 匹配 <td> 或 <th> 標籤後的內容，直到下一個 <td>/<th> 或行結束
        cell_pattern = r"<t[dh][^>]*>(.*?)(?=<t[dh][^>]*>|$)"
        cells = re.findall(cell_pattern, tr_content, re.DOTALL | re.IGNORECASE)

        # 清理單元格內容
        cleaned_cells = []
        for cell in cells:
            # 移除 HTML 標籤
            clean_text = re.sub(r"<[^>]+>", "", cell)
            # 清理空白字元
            clean_text = " ".join(clean_text.split())
            cleaned_cells.append(clean_text)

        if cleaned_cells:  # 只添加非空的行
            rows.append(cleaned_cells)

    return rows


async def fetch_empty_classroom_data() -> dict | None:
    try:
        """fetch html from classroom usage page"""
        print("[empty_classroom] 開始抓取資料...")
        response = await WebScraper().get(url)

        if response is None:
            print("[empty_classroom] 網路請求失敗")
            return None
        print(f"[empty_classroom] 成功取得回應，長度: {len(response.text)}")

        with open("./data/test.html", "w", encoding="utf-8") as f:
            f.write(response.text)

        """使用 re 解析課表資料，因為 HTML 沒有結尾標籤 = ="""
        schedule_list = parse_table_with_regex(response.text)

        if not schedule_list:
            print("[empty_classroom] 正則表達式解析失敗")
            return None
        print(f"[empty_classroom] 課表有 {len(schedule_list)} 行")

        # for i, row in enumerate(schedule_list):
        #     if i < 5:  # 只印前 5 行避免輸出太多
        #         print(f"行 {i}: {row}")

        print(f"[empty_classroom] 總共解析了 {len(schedule_list)} 行資料")

        # 清理資料：移除空行和純空白行
        cleaned_schedule = []
        for row in schedule_list:
            # 過濾掉全為空白的行
            if any(cell.strip() for cell in row):
                # 清理每個單元格的內容
                cleaned_row = []
                for cell in row:
                    # 移除多餘的空白和換行
                    cleaned_cell = " ".join(cell.split())
                    cleaned_row.append(cleaned_cell)
                cleaned_schedule.append(cleaned_row)

        """解析課表資料為二維陣列"""
        schedule_2d = []
        weekdays = ["日", "一", "二", "三", "四", "五", "六"]

        # 從解析後的資料重新建構二維陣列
        current_time_slot = None
        current_row = None

        for row_data in cleaned_schedule:
            if not row_data:
                continue

            # 如果第一欄包含"第 X 節"，這是一個新的時段開始
            if len(row_data) > 0 and "第" in row_data[0] and "節" in row_data[0]:
                # 儲存之前的行（如果有的話）
                if current_row is not None:
                    schedule_2d.append(current_row)

                # 開始新的一行
                current_time_slot = row_data[0]
                current_row = [current_time_slot]  # 第一欄是時段

                # 處理這個時段各星期的資料
                for i in range(1, len(row_data)):
                    if i - 1 < len(weekdays):
                        current_row.append(row_data[i])

            elif current_row is not None and len(row_data) > 1:
                # 這是延續的課程資訊，附加到對應的星期欄位
                # 找到第一個非空白的單元格位置
                for i, cell in enumerate(row_data[1:], 1):  # 跳過第一欄（時段）
                    if cell.strip() and i <= len(current_row) - 1:
                        # 如果當前欄位已經有內容，合併起來
                        if current_row[i] and current_row[i] != "　":
                            current_row[i] += "\n" + cell
                        else:
                            current_row[i] = cell

        # 不要忘記最後一行
        if current_row is not None:
            schedule_2d.append(current_row)

        print(
            f"[empty_classroom] 二維陣列大小: {len(schedule_2d)} 行 x {len(schedule_2d[0])} 列"
        )

        # 印出前幾行檢查
        # for i, row in enumerate(schedule_2d[:3]):
        #     print(f"Row {i}: {row}")

        # 儲存為 JSON
        result = {
            "raw_schedule": schedule_list,
            "cleaned_schedule": cleaned_schedule,
            "final_schedule": schedule_2d,
            "weekdays": weekdays,
            "metadata": {
                "total_rows": len(schedule_list),
                "cleaned_rows": len(cleaned_schedule),
                "schedule_rows": len(schedule_2d),
                "schedule_cols": len(schedule_2d[0]) if schedule_2d else 0,
            },
        }

        with open("./data/table.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=4)

        print("[empty_classroom] 資料已儲存到 modules/data/table.json")
        return result

    except Exception as e:
        print(f"[empty_classroom] 發生錯誤: {e}")
        import traceback

        traceback.print_exc()
        return None


asyncio.run(fetch_empty_classroom_data())

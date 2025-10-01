import logging
import asyncio
import json
import urllib3
from urllib3.exceptions import InsecureRequestWarning
from typing import Literal

from bs4 import BeautifulSoup
import httpx
from nicegui import app

from .constants import *
# from .timetable import html_to_timetable


urllib3.disable_warnings(InsecureRequestWarning)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8',
    handlers=[
        logging.FileHandler("scraper.log", mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)


class WebScraper:

    def __init__(self) -> None:
        headers = {
            "User-Agent": "Direk android App",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        self.session = httpx.AsyncClient(verify=False)
        self.session.headers.update(headers)

    async def login(self, student_id: str, password: str) -> bool:
        """
        登入 nportal
        
        若成功則將登入狀態儲存於 app.storage 以及儲存密碼
        """
        post_data = {
            'muid': student_id,
            'mpassword': password,
            'forceMobile':'mobile'
        }
        login_response = None
        self.session.headers.update({"Referer": NPORTAL_LOGIN_PAGE_URL})
        try:
            logging.info(f"正在登入 {NPORTAL_LOGIN_URL}")
            login_response = await self.session.post(NPORTAL_LOGIN_URL, data=post_data, timeout=10)
            login_response.raise_for_status()

            logging.info("登入請求成功，正在解析 JSON 回應...")
            json_response = login_response.json()
            print(json_response)
            
            if json_response.get("success", False) :
                app.storage.general["login_status"] = True
                app.storage.general["last_user_id"] = student_id
                getattr(app, "credentials").save(student_id, password)
                logging.info(f"帳號 {student_id} 登入成功")
                return True
            else:
                logging.warning(f"帳號 {student_id} 登入失敗")
                return False

        except httpx.TimeoutException:
            logging.error(f"登入請求超時 ({NPORTAL_LOGIN_URL})")
            return False

        except httpx.HTTPStatusError as e:
            logging.error(
                f"HTTP 狀態碼錯誤: {e.response.status_code} {e.response.reason_phrase} "
                f"在請求 URL: {e.request.url}"
            )
            return False

        except json.JSONDecodeError:
            logging.error(f"JSON 解析失敗。伺服器回應的原始內容: {login_response.text if login_response else 'N/A'}")
            return False

        except httpx.RequestError as e:
            logging.error(f"發生網路請求錯誤: {e}")
            return False

        except Exception as e:
            logging.critical(f"發生未預期的嚴重錯誤: {e}", exc_info=True)
            return False
        
        finally:
            self.session.headers.pop("Referer", None)


    async def oauth(self, apOu: Literal["aa_0010-oauth", "ischool_plus_oauth"]) -> bool:
        """
        執行 SSO (單一登入) 流程以取得特定服務的 session, apOu 是目標服務的代碼

        課程系統 : "aa_0010-oauth"

        i學園 : "ischool_plus_oauth"
        """
        initial_oath_url = OAUTH_BASE_URL + apOu
        logging.info(f"正在執行 SSO 流程，目標: {apOu}")
        logging.debug(f"正在請求 SSO 初始頁面: {initial_oath_url}")
        self.session.headers.update({"Referer": NPORTAL_LOGIN_PAGE_URL})
        try:
            oath_page_response = await self.session.get(initial_oath_url, timeout=10)
            oath_page_response.raise_for_status()

            soup = BeautifulSoup(oath_page_response.text, "html.parser")
            inputs = soup.select("form[name='ssoForm'] input")
            if not inputs:
                logging.error("SSO 流程失敗：在 'ssoForm' 表單中找不到任何 <input> 標籤。")
                return False
            
            course_oath_data = {str(item.get("name")): item.get("value") for item in inputs}
            logging.debug(f"成功解析到 SSO 表單資料")

            self.session.headers.update({"Referer": initial_oath_url})
            logging.debug(f"正在向 {SSO_POST_URL} 提交 SSO 表單...")
            
            sso_post_response = await self.session.post(
                SSO_POST_URL,
                data=course_oath_data,
                follow_redirects=False,
                timeout=15
            )
            if not sso_post_response.is_redirect:
                sso_post_response.raise_for_status()

            redirect_url = sso_post_response.headers.get('Location')
            if not redirect_url:
                logging.error("SSO 流程失敗：伺服器 POST 回應中未包含 'Location' 重導向標頭。")
                logging.debug(f"POST 回應內容: {sso_post_response.text[:200]}") 
                return False
            
            logging.info(f"取得 SSO 重導向網址: {redirect_url}")
            logging.debug("正在訪問重導向網址以完成 SSO...")
            final_response = await self.session.get(redirect_url, follow_redirects=False, timeout=10)
            if not final_response.is_redirect:
                final_response.raise_for_status()

            logging.info(f"SSO 流程成功完成，已取得 {apOu} 的 session。")
            return True
        
        except httpx.TimeoutException as e:
            logging.error(f"SSO 流程請求超時: URL {e.request.url}")
            return False

        except httpx.HTTPStatusError as e:
            logging.error(
                f"SSO 流程中發生 HTTP 狀態碼錯誤: {e.response.status_code} {e.response.reason_phrase} "
                f"在請求 URL: {e.request.url}"
            )
            logging.debug(f"錯誤回應內容: {e.response.text[:200]}")
            return False

        except httpx.RequestError as e:
            logging.error(f"SSO 流程中發生網路請求錯誤: {e.__class__.__name__} - {e}")
            return False

        except Exception as e:
            logging.critical(f"SSO 流程中發生未預期的嚴重錯誤: {e}", exc_info=True)
            return False
        
        finally:
            self.session.headers.pop("Referer", None)
    

    async def fetch_seme_list_html(self) -> str|None:
        URL = "https://aps.ntut.edu.tw/course/tw/Select.jsp"
        try:
            logging.debug(f"正在請求 URL: {URL}")
            response = await self.session.get(URL, timeout=10)
            response.raise_for_status()
            logging.info("成功獲取學年學期列表頁面。")
            return response.text

        except httpx.TimeoutException:
            logging.error(f"請求超時: {URL}")
            return None

        except httpx.HTTPStatusError as e:
            logging.error(
                f"HTTP 狀態碼錯誤: {e.response.status_code} {e.response.reason_phrase} "
                f"在請求 URL: {e.request.url}"
            )
            return None

        except httpx.RequestError as e:
            logging.error(f"發生網路請求錯誤: {e.__class__.__name__} - {e}")
            return None

        except Exception as e:
            logging.critical(f"抓取學年學期列表時發生未預期的嚴重錯誤: {e}", exc_info=True)
            return None


    async def fetch_seme_course_and_timetable_html(self, seme: str) -> str|None:
        student_id = app.storage.general["last_user_id"]
        timetable_url = (f"https://aps.ntut.edu.tw/course/tw/Select.jsp?format=-2&code={student_id}&year={seme[:3]}&sem={seme[-1]}")

        try:
            response = await self.session.get(timetable_url, timeout=10)
            response.raise_for_status()
            logging.info("成功獲取學年學期列表頁面。")
            return response.text
        
        except httpx.TimeoutException:
            logging.error(f"請求超時: {timetable_url}")
            return None

        except httpx.HTTPStatusError as e:
            logging.error(
                f"HTTP 狀態碼錯誤: {e.response.status_code} {e.response.reason_phrase} "
                f"在請求 URL: {e.request.url}"
            )
            return None

        except httpx.RequestError as e:
            logging.error(f"發生網路請求錯誤: {e.__class__.__name__} - {e}")
            return None

        except Exception as e:
            logging.critical(f"抓取學年學期列表時發生未預期的嚴重錯誤: {e}", exc_info=True)
            return None

    # async def keep_login_status(self):
    #     user_id = app.storage.general.get("last_user_id")

    #     user_password = CredentialsManager().load(user_id)

    #     if not user_password:

    #     if await self.login(user_id, user_password):
            



if __name__ == "__main__":
    async def main():
        scraper = WebScraper()
        if not await scraper.login(input(), input()):
            print("登入 failed")
            return
        else:
            print("登入成功")
        if not await scraper.oauth("ischool_plus_oauth"):
            print("oauth error")
            return
        
        data={
            "action":"getSearchCourses",
            "id":"345918",
            "perpage":"20"
        }
        response = await scraper.session.post(ISCHOOL_SEARCH_URL, data=data)
        print(response.json())
        with open("howmanyseme.html", 'w', encoding='utf-8') as f:
            f.write(response.text)
            
    asyncio.run(main())
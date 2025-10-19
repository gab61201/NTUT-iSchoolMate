import logging
import asyncio
import json
import urllib3
from urllib3.exceptions import InsecureRequestWarning
from typing import Literal

from bs4 import BeautifulSoup
import httpx
from httpx import Response
from nicegui import app

# from .timetable import html_to_timetable


urllib3.disable_warnings(InsecureRequestWarning)
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class WebScraper:

    def __init__(self) -> None:
        headers = {
            "User-Agent": "Direk android App",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        self.session = httpx.AsyncClient(verify=False, headers=headers, follow_redirects=True, timeout=None)

    async def login(self, student_id: str, password: str) -> dict|None:
        """
        登入 nportal
        """
        NPORTAL_LOGIN_PAGE_URL = "https://nportal.ntut.edu.tw/index.do"
        NPORTAL_LOGIN_URL = 'https://nportal.ntut.edu.tw/login.do'

        self.session.headers.update({"Referer": NPORTAL_LOGIN_PAGE_URL})
        
        try:
            post_data = {
                'muid': student_id,
                'mpassword': password,
                'forceMobile':'mobile'
            }
            login_response = await self.session.post(NPORTAL_LOGIN_URL, data=post_data, timeout=10)
            login_response.raise_for_status()
            response_json = login_response.json()
            return response_json
            
        except Exception as e:
            print(f"web_scraper.login error:\n{e}")
            return None

        finally:
            self.session.headers.pop("Referer", None)


    async def oauth(self, apOu: Literal["aa_0010-oauth", "ischool_plus_oauth"]) -> bool:
        """
        執行 SSO (單一登入) 流程以取得特定服務的 session, apOu 是目標服務的代碼

        課程系統 : "aa_0010-oauth"

        i學園 : "ischool_plus_oauth"
        """
        OAUTH_BASE_URL = "https://nportal.ntut.edu.tw/ssoIndex.do?apOu="
        SSO_POST_URL = "https://nportal.ntut.edu.tw/oauth2Server.do"
        NPORTAL_LOGIN_PAGE_URL = "https://nportal.ntut.edu.tw/index.do"
        
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
        
        except Exception as e:
            print(f"WebScraper.oauth({apOu} error:\n{e})")
            return False
        
        finally:
            self.session.headers.pop("Referer", None)


    async def get(self, url) -> Response|None:
        try:
            response = await self.session.get(url, timeout=10)
            response.raise_for_status()
            return response
        
        except httpx.TimeoutException as e:
            print(e)
            return None

        except httpx.HTTPStatusError as e:
            print(e)
            return None

        except httpx.RequestError as e:
            print(e)
            return None

        except Exception as e:
            print(e)
            return None


    async def post(self, url, data) -> Response|None:
        try:
            response = await self.session.post(url, data=data, timeout=10)
            response.raise_for_status()
            return response
        
        except httpx.TimeoutException as e:
            print(e)
            return None

        except httpx.HTTPStatusError as e:
            print(e)
            return None

        except httpx.RequestError as e:
            print(e)
            return None

        except Exception as e:
            print(e)
            return None


if __name__ == "__main__":
    async def main():
        scraper = WebScraper()
        await scraper.login(input(), input())
            
    asyncio.run(main())
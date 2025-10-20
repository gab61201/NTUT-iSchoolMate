import re
import asyncio
from .web_scraper import WebScraper
from .semester import Semester


class UserManager:
    def __init__(self) -> None:
        self.scraper = WebScraper()

        self.student_id = ""
        self.password = ""
        self.semesters: list[Semester] = []


    async def login(self, student_id, password) -> str:
        """
        登入成功回傳空字串

        登入失敗回傳失敗訊息
        """
        login_response_json = await self.scraper.login(student_id, password)
        if type(login_response_json) != dict:
            print(f"UserManager.login login_response_json error:\n{login_response_json}")
            return "登入失敗，未知錯誤"
        
        login_sucess =  login_response_json.get("success", False)
        if not login_sucess:
            return login_response_json.get("errorMsg", "登入失敗")
        
        if not await self.scraper.oauth('aa_0010-oauth'):
            return "課程系統驗證失敗"
        if not await self.scraper.oauth('ischool_plus_oauth'):
            return "i 學園驗證失敗"

        self.student_id = student_id
        self.password = password

        return ""


    def get_semester(self, seme: str) -> Semester|None:
        for s in self.semesters:
            if s.semester == seme:
                return s
        print(f'user.get_semester({seme} failed!)')
        return None

    async def _fetch_semester_list(self) -> bool:
        """
        取得使用者讀了那些學期
        完成後 ex: self.seme_list = {"1141":Semester("1141")}
        """
        if self.semesters:
            return True

        SEMESTER_LIST_URL = "https://aps.ntut.edu.tw/course/tw/Select.jsp"
        response = await self.scraper.get(SEMESTER_LIST_URL)
        if not response:
            return False
        seme_info = re.findall(r'year=(\d{3})&sem=(\d)', response.text)
        for s in seme_info:
            year, sem = s
            semester = Semester(self.scraper, self.student_id, year + sem)
            self.semesters.append(semester)
        return True


    async def _fetch_all_course_file_url(self) -> bool:
        """
        到i學園取得全部學期 Course 的 file_url
        """
        ISCHOOL_COURSE_LIST_URL = "https://istudy.ntut.edu.tw/learn/mooc_sysbar.php"
        response = await self.scraper.get(ISCHOOL_COURSE_LIST_URL)
        if not response:
            print("UserManager._fetch_all_course_file_url html_text failed!")
            return False
        
        course_list = re.findall(r'<option value="(\d{8})">(\d{4})_.+?_(\d{6})</option>', response.text)
        if not course_list:
            print(f'UserManager._fetch_all_course_file_url mooc_sysbar.php failed!')
            return False

        ISCHOOL_FILE_BASE_URL = "https://istudy.ntut.edu.tw/xmlapi/index.php?action=my-course-path-info&onlyProgress=0&descendant=1&cid="
        for course_data in course_list:
            if not course_data:
                print("UserManager.fetch_course_list data failed!")
                return False
            semester = self.get_semester(course_data[1])
            if not semester:
                continue
            course = semester.get_course(course_data[2])
            if not course:
                continue
            course._file_url = ISCHOOL_FILE_BASE_URL + course_data[0]
        
        return True


    async def fetch_user_course_data(self) -> bool:
        """
        建立所有 Semester及 Course 物件
        """
        if not self.semesters and not await self._fetch_semester_list():
            print(f'user.fetch_user_course_data() failed!')
            return False
        
        task_list = [asyncio.create_task(seme.fetch_data()) for seme in self.semesters]
        results = await asyncio.gather(*task_list)
        if not all(results):
            print(f'user.fetch_user_course_data results:\n{results}')
            return False
        
        if not await self._fetch_all_course_file_url():
            return False
        
        return True




if __name__ == "__main__":
    # user = User()
    ...
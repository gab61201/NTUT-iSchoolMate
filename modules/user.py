import re
from nicegui import app
from .course import Course
from .web_scraper import WebScraper
from .constants import *

class UserManager:
    def __init__(self, scraper: WebScraper) -> None:
        self.scraper = scraper
        self.student_id = ""
        self.seme_list = []
        self.timetable: dict = {}
        self.course_list: dict = {} #course_list[seme][couse_id]: Course()

    async def fetch_year_seme_list(self) -> bool:
        """
        取得使用者讀了那些學期
        完成後 ex: self.seme_list = ["1132", "1131"]
        """
        if self.seme_list:
            return True

        html_text = await self.scraper.fetch_seme_list_html()
        if not html_text:
            return False
        seme_info = re.findall(r'year=\d+?&sem=\d', html_text)

        if not seme_info:
            return False
        for semester in seme_info:
            result = re.search(r"year=(\d+?)&sem=(\d)", semester)
            if result:
                self.seme_list.append(result.group(1) + result.group(2))
        print("fetch_year_seme_list 結果 :", self.seme_list)
        return True

    async def fetch_seme_timetable(self, seme: str) -> bool:
        """
        取得使用者某學期的課程物件及課表
        self.course_list
        self.timetable

        course.name
        course.id
        course.seme
        course.description_url
        course.syllabus_url
        """
        if self.timetable.get(seme, None):
            return True
        
        html_text = await self.scraper.fetch_seme_timetable_html(seme)
        self.course_list[seme] = {}

        title = ["MENU", "一", "二", "三", "四", "五"]
        self.timetable[seme] = []
        self.timetable[seme].append(title)
        for i in range(1, 10):
            self.timetable[seme].append([str(i)]+[None]*5)
        
        html_text = re.search(r"<table border=1>.+</table>", html_text, re.DOTALL).group() #type:ignore
        if not html_text:
            return False
        all_classes:list[str] = re.findall(r"<tr>\s*<td>\d{6}.+?</tr>", html_text, re.DOTALL)

        for class_html in all_classes:
            course = Course(self.scraper)
            course.seme = seme
            course_id = re.search(r"<td>(\d{6})", class_html)
            if not course_id:
                return False
            course.id = course_id.group(1)
            
            credits = re.search(r"<td align=CENTER>(\d.\d)", class_html)
            if not credits:
                return False
            course.credits = credits.group(1)

            course_info = re.search(r'<A href="Curr.jsp.format=-2&code=(.{7})">(.+?)</A>', class_html)
            if not course_info:
                return False
            description_url = 'https://aps.ntut.edu.tw/course/tw/Curr.jsp?format=-2&code=' + course_info.group(1)
            course_name = course_info.group(2)
            course.description_url = description_url
            course.name = course_name

            syllabus_url = re.search(r'ShowSyllabus.jsp.snum=(\d{6})&code=(\d{5})', class_html)
            if not syllabus_url:
                return False
            course.syllabus_url = 'https://aps.ntut.edu.tw/course/tw/' + syllabus_url.group()
            
            hour_list = class_html.split("<td>")[6:13]
            for i in range(7):
                if hour_list[i] == "　":
                    continue
                hour = hour_list[i].split()
                for h in hour:
                    self.timetable[seme][int(h)][i] = course

            self.course_list[seme][course.id] = course

        return True


    async def fetch_course_list(self) -> bool:
        """
        取得全部 Course 的 file_url
        """
        html_text = await self.scraper.fetch_course_list_html()
        if not html_text:
            return False
        course_list = re.findall(r'<option value="\d{8}">\d{4}_.+?_\d{6}</option>', html_text)

        for course_data in course_list:
            data = re.search(r'<option value="(\d{8})">(\d{4})_(.+?)_(\d{6})</option>', course_data)
            if not data:
                return False
            course: Course = self.course_list[data.group(2)][data.group(4)]
            course.file_url = ISCHOOL_FILE_BASE_URL + data.group(1)
        
        return True

if __name__ == "__main__":
    # user = User()
    ...
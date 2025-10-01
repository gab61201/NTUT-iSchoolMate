from .course import Course
from .web_scraper import WebScraper
from nicegui import app
import re

class UserManager:
    def __init__(self, scraper: WebScraper) -> None:
        self.scraper = scraper
        self.student_id = ""
        self.seme_list = []
        self.timetable: dict = {}
        self.course_list: dict = {}

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

    async def fetch_seme_course_and_timetable(self, seme: str) -> bool:
        """
        取得使用者某學期的課程物件及課表
        """
        if self.course_list.get(seme, None):
            return True
        
        html_text = await self.scraper.fetch_seme_course_and_timetable_html(seme)
        self.course_list[seme] = []

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
            course = Course()
            course_id = re.search(r"<td>(\d{6})", class_html)
            if not course_id:
                return False
            course.id = course_id.group(1)
            
            course_info = re.search(r'<A href="Curr.jsp.format=-2&code=(.{7})">(.+?)</A>', class_html)
            if not course_info:
                return False
            curriculum_url = 'https://aps.ntut.edu.tw/course/tw/Curr.jsp?format=-2&code=' + course_info.group(1)
            course_name = course_info.group(2)
            course.curriculum_url = curriculum_url
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

            self.course_list[seme].append(course)

        return True




if __name__ == "__main__":
    # user = User()
    ...
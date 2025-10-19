import re

from course import Course
from web_scraper import WebScraper


course_pattern = r"""<tr>
<td>(\d{6})
<td><A href="(Curr\.jsp\?format=-2&code=.+?)">(.+?)</A>
<td align=CENTER>(\d)
<td align=CENTER>(\d.\d)
<td align=CENTER>(\d)
<td><div align=center>(.+?)</div>
<td>(.+?)\n
<td>(.+?)\n
<td>(.+?)<td>(.+?)<td>(.+?)<td>(.+?)<td>(.+?)<td>(.+?)<td>(.+?)<td>(.+?)
<td><div align=center>(.+?)</div>
<td align=CENTER>(.+?)
<td align=center><A href="(ShowSyllabus\.jsp\?snum=\d{6}&code=\d+?)">查詢</A><BR>
<td>(.+?)
</tr>"""

class Semester:
    def __init__(self, scraper: WebScraper, student_id: str, semester: str) -> None:
        self.scraper = scraper
        self.semester = semester
        self.student_id = student_id
        self.timetable: dict[str, list[Course|None]] = {
            "日": [None] * 10,
            "一": [None] * 10,
            "二": [None] * 10,
            "三": [None] * 10,
            "四": [None] * 10,
            "五": [None] * 10,
            "六": [None] * 10
        }
        self.courses: dict[str, Course|None] = {}
        self.credits = ""
        self.hours = ""

    async def fetch_data(self) -> bool:
        """
        這裡是獲取 https://aps.ntut.edu.tw/course/tw/Select.jsp 能取得的資料

        本學期所有資料以及建立本學期所有 Course

        只需要執行一次
        """
        course_form_url = f"https://aps.ntut.edu.tw/course/tw/Select.jsp\
            ?format=-2&code={self.student_id}&year={self.semester[:3]}&sem={self.semester[-1]}"
        Select_jsp = await self.scraper.get(course_form_url)
        if not Select_jsp:
            return False
        
        all_courses = re.findall(course_pattern, Select_jsp.text, re.DOTALL|re.IGNORECASE)
        for c in all_courses:
            course = Course(self.scraper, self.semester, c[0])
            course.description_url = 'https://aps.ntut.edu.tw/course/tw/' + c[1]
            course.name = c[2]
            course.stage = c[3]
            course.credits = c[4]
            course.hours = c[5]
            credit_type = c[6]

            all_teachers = re.findall(r'<A href="Teach\.jsp\?format=-3&year=\d{3}&sem=\d&code=\d+">(.+?)</A><BR>', c[7])
            course.teachers = "、".join(all_teachers)

            all_classes = re.findall(r'<A href="Subj\.jsp\?format=-4&year=\d{3}&sem=\d&code=\d+">(.+?)</A><BR>', c[8])
            course.classes = "、".join(all_classes)

            course.time = {
                "日": c[9].strip() if c[9] != "\u3000" else '',
                "一": c[10].strip() if c[10] != "\u3000" else '',
                "二": c[11].strip() if c[11] != "\u3000" else '',
                "三": c[12].strip() if c[12] != "\u3000" else '',
                "四": c[13].strip() if c[13] != "\u3000" else '',
                "五": c[14].strip() if c[14] != "\u3000" else '',
                "六": c[15].strip() if c[15] != "\u3000" else ''
            }

            all_classrooms = re.findall(r'<A href="Croom\.jsp\?format=-3&year=\d{3}&sem=\d&code=\d+">(.+?)</A><BR>', c[16])
            course.classrooms = "、".join(all_classrooms) if all_classrooms else "無"

            course.isQuit = c[17]
            course.language = c[18]
            course.syllabus_url = 'https://aps.ntut.edu.tw/course/tw/' + c[19]
            course.note = c[20]

            self.courses[c[0]] = course
            for day, time in course.time.items():
                if not time:
                    continue
                for h in time.split():
                    self.timetable[day][int(h)] = course

        total = re.search(r'<td><div align=center>(.+?)</div><td><div align=center>(\d+)</div>', course_form_url)
        if not total:
            return False
        self.credits = total.group(1)
        self.hours = total.group(2)

        return True


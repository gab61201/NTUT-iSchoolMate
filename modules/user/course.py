import re
import json
from typing import Literal
from web_scraper import WebScraper


class Course:
    def __init__(self, scraper: WebScraper, semester: str, id: str) -> None:
        self.scraper = scraper
        self.semester = semester
        self.id = id
        
        """init"""
        self.name = ""
        self.time = {}
        self.stage = ""
        self.credits = ""
        self.hours = ""
        self.teachers = ""
        self.classes = ""
        self.classrooms = ""
        self.note = ""
        self.isQuit = ""
        self.language = ""
        self.syllabus_url = ""
        self.description_url = ""

        """description"""
        self._ch_description = ""
        self._en_description = ""

        """syllabus"""
        self.credit_type = ""
        self.num_of_students = ""
        self.num_of_quit = ""
        self.teacher_email = ""
        self.syllabus = ""
        self.schedule = ""
        self.evaluation = ""
        self.textbook = ""
        self.consult = ""
        self.syllabus_note = ""

        """
        file_list

        example:
        video_dict =
        {"I_SCO_10097882_1757382960215230": {
            "identifier": "I_SCO_10097882_1757382960215230",
            "text": "Chap02_Operational Amplifiers (71)",
            "href": url,
            "itemDisabled": false,
            "readed": true,
            "item": [],
            "leaf": true
            }
        }
        """
        self.file_url = ""
        self.video_dict = {}  # video_dict[identifier]
        self.file_dict = {}


    async def get_description(self, language: Literal['ch', 'en']) -> str|None:
        """
        ch_description = get_description('ch')
        """
        if not (self._ch_description and self._ch_description):
            response = await self.scraper.get(self.description_url)
            if not response:
                return
            description = re.findall(r'<td colspan=4>(.+)', response.text)
            if len(description) != 2:
                return
        
        self._ch_description = description[0]
        self._en_description = description[1]

        if language == 'ch' and self._ch_description:
            return self._ch_description
        elif language == 'en' and self._ch_description:
            return self._ch_description
        else:
            return


    async def fetch_syllabus(self) -> bool:
        response = await self.scraper.get(self.syllabus_url)
        if not response:
            return False

        info = re.findall(r'<td align="center">(.+?)</td>', response.text)
        email_search = re.search(r'<a href="mailto:(.+?)">', response.text)
        text_areas = re.findall(r'<textarea.+?>(.+?)</textarea>', response.text, re.DOTALL)
        search_consult = re.search(r'<tr><th>課程諮詢管道<td>(.+?)</tr>', response.text)
        search_syllabus_note = re.search(r'<div.+?>(.+?)</div>', response.text)

        if not (info and email_search and text_areas and search_consult and search_syllabus_note):
            return False
        
        credit_convert = {
            "○":"部訂共同必修",
            "△":"校訂共同必修",
            "☆":"共同選修",
            "●":"部訂專業必修",
            "▲":"校訂專業必修",
            "★":"專業選修"
        }
        self.credit_type = info[5] + " " + credit_convert[info[5]]
        self.num_of_students = info[8]
        self.num_of_quit = info[9]
        self.teacher_email = email_search.group(1)
        self.syllabus = text_areas[0]
        self.schedule = text_areas[1]
        self.evaluation = text_areas[2]
        self.textbook = text_areas[3]
        self.consult = search_consult.group(1).replace("<br>", "\n")
        self.syllabus_note = search_syllabus_note.group(1).replace("<br>", "\n")

        return True
    

    async def fetch_course_file_url(self) -> bool:
        ISCHOOL_COURSE_LIST_URL = "https://istudy.ntut.edu.tw/learn/mooc_sysbar.php"
        response = await self.scraper.get(ISCHOOL_COURSE_LIST_URL)
        if not response:
            return False
        
        find_course = re.findall(rf'<option value="(\d+)">{self.semester}_.+?_{self.id}</option>', response.text)
        if not find_course:
            return False
        
        ISCHOOL_FILE_BASE_URL = "https://istudy.ntut.edu.tw/xmlapi/index.php?action=my-course-path-info&onlyProgress=0&descendant=1&cid="
        self.file_url = ISCHOOL_FILE_BASE_URL + find_course[0]

        return True


    async def fetch_file_list(self) -> bool:
        if not self.file_url and not await self.fetch_course_file_url():
            return False

        response = await self.scraper.get(self.file_url)
        if not response:
            return False
        self.file_tree = response.json()["data"]["path"]["item"]

        def parse_tree(tree: list):
            for i in range(len(tree) - 1, -1, -1):
                if tree[i]["item"]:
                    parse_tree(tree[i]["item"])
                elif re.match(r'istream://', tree[i]["href"]):
                    self.video_dict[tree[i]["identifier"]] = tree[i]
                    del tree[i]
                else:
                    self.file_dict[tree[i]["identifier"]] = tree[i]

        parse_tree(self.file_tree)
        return True
    

    async def fetch_video(self, identifier: str) -> bool:
        """
        執行完此函式後瀏覽 url: "/video?channel=1"
        """
        response = await self.scraper.get('https://istudy.ntut.edu.tw/learn/path/m_pathtree.php')
        if not response:
            return False
        
        encoded_course_id_html = re.search(r'<input type="hidden" name="course_id"       value="(.+?)">', response.text)
        read_key_html = re.search(r'<input type="hidden" name="read_key"       value="(.+?)">', response.text)
        if not encoded_course_id_html or not read_key_html:
            return False

        encoded_course_id = encoded_course_id_html.group(1)
        read_key = read_key_html.group(1)

        all_videos_html = await self.scraper.get('https://istudy.ntut.edu.tw/learn/path/SCORM_loadCA.php')
        if not all_videos_html:
            return False

        all_video_href = re.findall(r'<resource identifier="(.+?)".+?href="(.+?)"/>', all_videos_html.text)
        href = ''
        for v in all_video_href:
            if identifier == 'I_' + v[0]:
                href = ' @' + v[1]
                break
        if not href:
            return False

        post_data = {
            "href": href,
            "course_id": encoded_course_id,
            "read_key": read_key,
        }
        fetch_url = await self.scraper.post('https://istudy.ntut.edu.tw/learn/path/SCORM_fetchResource.php', data=post_data)
        if not fetch_url:
            return False

        url = re.search(r"'(.+?)'", fetch_url.text)
        if not url:
            return False
        print(url.group(1))

        if await self.scraper.session.get(url.group(1)):
            return True
        else:
            return False
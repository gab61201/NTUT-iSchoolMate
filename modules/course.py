import re
import json
from .web_scraper import WebScraper


class Course:
    def __init__(self, scraper: WebScraper) -> None:
        self.scraper = scraper

        self.seme = ""
        self.name = ""
        self.id = ""
        self.bid = ""
        self.credits = ""
        self.data = {}

        self.description_url = ""
        self.syllabus_url = ""
        self.file_url = ""
        self.file_tree = []
        self.file_dict = {}
        self.video_dict = {}
    
    async def fetch_syllabus(self) -> dict|None:
        response = await self.scraper.get(self.syllabus_url)
        if not response:
            return None
        
        tr_labels = re.findall(r"<tr>.+?</tr>", response.text, re.DOTALL)
        index = ["學年學期",
                "課號",
                "課程名稱",
                "階段",
                "學分",
                "時數",
                "必/選",
                "教師",
                "班級",
                "修課人數",
                "撤選人數",
                "備註",
                "email",
                "課程大綱",
                "課程進度",
                "評分標準",
                "教科書",
                "課程諮詢管道"]

        info = re.findall(r'">\s*.+?</td>', tr_labels[1])
        info_list = [re.search(r'">\s*(.+?)</td>', i).group(1) for i in info] #type:ignore

        email = re.search(r'<a href="mailto:(.+?)">', tr_labels[3]).group(1) #type:ignore
        syllabus = re.search(r'">(.+?)</textarea>', tr_labels[5], re.DOTALL).group(1) #type:ignore
        schedule = re.search(r'">(.+?)</textarea>', tr_labels[6], re.DOTALL).group(1) #type:ignore
        score = re.search(r'">(.+?)</textarea>', tr_labels[7], re.DOTALL).group(1) #type:ignore
        textbook = re.search(r'">(.+?)</textarea>', tr_labels[8], re.DOTALL).group(1) #type:ignore
        consult = re.search(r'<td>(.+?)</tr>', tr_labels[9]).group(1) #type:ignore

        info_list.extend([email, syllabus, schedule, score, textbook, consult])
        data = dict(zip(index, info_list))

        credit_type = {"○":"部訂共同必修",
                       "△":"校訂共同必修",
                       "☆":"共同選修",
                       "●":"部訂專業必修",
                       "▲":"校訂專業必修",
                       "★":"專業選修"}

        data["班級"] = data["班級"].replace("<BR>", "、")
        data["必/選"] = f'{data["必/選"]} {credit_type[data["必/選"]]}'

        self.data.update(data)


    async def fetch_description(self) -> dict|None:
        response = await self.scraper.get(self.description_url)
        if not response:
            return None
        
        ch_search = re.search(r'<td colspan=4>(.+?)<tr>', response.text, re.DOTALL)
        ch_description = ch_search.group(1).rstrip("\n")  #type:ignore

        en_search = re.search(r'English Description\s+<td colspan=4>(.+?)</table>', response.text, re.DOTALL)
        en_description = en_search.group(1).rstrip("\n")  #type:ignore

        self.data.update({"ch_description": ch_description, "en_description": en_description})

    
    async def fetch_files(self) -> bool:
        if not self.file_url:
            print("未知 i學園 file_url")
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
        response = await self.scraper.session.get('https://istudy.ntut.edu.tw/learn/path/m_pathtree.php')
        encoded_course_id_html = re.search(r'<input type="hidden" name="course_id"       value="(.+?)">', response.text)
        read_key_html = re.search(r'<input type="hidden" name="read_key"       value="(.+?)">', response.text)
        if not encoded_course_id_html or not read_key_html:
            return False
        encoded_course_id = encoded_course_id_html.group(1)
        read_key = read_key_html.group(1)

        all_videos_html = await self.scraper.session.get('https://istudy.ntut.edu.tw/learn/path/SCORM_loadCA.php')
        all_video_href = re.findall(r'<resource identifier.+?"/>', all_videos_html.text)
        href = ''
        for v in all_video_href:
            s = re.search(r'<resource identifier="(.+?)" type="webcontent" href="(.+?)"/>', v)
            if not s:
                return False
            if identifier == 'I_' + s.group(1):
                href = ' @' + s.group(2)
                break

        post_data = {
            "href": href,
            "course_id": encoded_course_id,
            "read_key": read_key,
        }
        fetch_url = await self.scraper.session.post('https://istudy.ntut.edu.tw/learn/path/SCORM_fetchResource.php', data=post_data)
        url = re.search(r"'(.+?)'", fetch_url.text)
        if not url:
            return False
        print(url.group(1))

        if await self.scraper.session.get(url.group(1)):
            return True
        else:
            return False


    async def get_bulletin(self) -> dict|None:
        response = await self.scraper.get('https://istudy.ntut.edu.tw/learn/path/m_pathtree.php')
        if not response:
            return None
        
        search = re.search(r"var courseBulletin = '(\d+?)';", response.text)
        if not search:
            return None
        self.bid = search.group(1)

        post_data = {
            "bid": self.bid,
            "action": "getNews",
            "tpc": "1",
            "selectPage": "0",
            "inputPerPage": "100"
        }
        all_bulletin_html = await self.scraper.session.post('https://istudy.ntut.edu.tw/mooc/controllers/forum_ajax.php', data=post_data)
        # with open('bulletin.html', 'w', encoding='utf-8') as f:
        #     f.write(all_bulletin_html.text)
        return all_bulletin_html.json().get("data")
        

    async def get_bulletin_reply(self, nid: str) -> dict|None:
        post_data = {
            "action": "getReply",
            "bid": self.bid,
            "nid": nid,
            "selectPage": "0",
            "inputPerPage": "100"
        }
        bulletin_reply_html = await self.scraper.session.post('https://istudy.ntut.edu.tw/mooc/controllers/forum_ajax.php', data=post_data)
        # with open('bulletin_reply.html', 'w', encoding='utf-8') as f:
        #     f.write(bulletin_reply_html.text)
        return json.loads(bulletin_reply_html.text)
        


if __name__ == "__main__":
    ...
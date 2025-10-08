import re
from .web_scraper import WebScraper


class Course:
    def __init__(self, scraper: WebScraper) -> None:
        self.scraper = scraper

        self.seme = ""
        self.name = ""
        self.id = ""
        self.data = {}

        self.description_url = ""
        self.syllabus_url = ""
        self.file_url = ""
    
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
        data["必/選"] = credit_type[data["必/選"]]

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


if __name__ == "__main__":
    ...
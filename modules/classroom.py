import re
import asyncio
import json
from .web_scraper import WebScraper


class ClassroomManager:
    def __init__(self) -> None:
        self.scraper = WebScraper()
        self.current_semester = ""


    async def get_current_semester(self)-> str|None:
        if not self.current_semester:
            response = await self.scraper.get(f'https://aps.ntut.edu.tw/course/tw/course.jsp')
            if not response:
                return None
            search = re.search(r'Croom\.jsp\?format=-2&year=(\d)+&sem=(\d)', response.text)
            if not search:
                return None
        
        self.current_semester = search.group(0) + search.group(1)
        return self.current_semester


    async def _get_all_room_codes(self, semester: str) -> list|None:
        year, seme = semester[:3], semester[-1]
        response = await self.scraper.get(f'https://aps.ntut.edu.tw/course/tw/Croom.jsp?format=-2&year={year}&sem={seme}')
        if not response:
            return None
        all_room_codes = re.findall(rf'Croom\.jsp\?format=-3&year={year}&sem={seme}&code=(\d+)', response.text)
        return all_room_codes
    

    async def get_empty_rooms(self, semester: str) -> list|None:
        """
        三維串列

        empty_room[weekday][lesson_time] = [room1, room2......]
        """
        try:
            with open(f'data/classrooms/{semester}_empty_rooms.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(e)

        empty_room = [
            [[] for day in range(7)] for lesson in range(14)
        ]
        year, seme = semester[:3], semester[-1]
        room_codes = await self._get_all_room_codes(semester)
        if not room_codes:
            return None
        responses = []
        for code in room_codes:
            responses.append(self.scraper.get(f'https://aps.ntut.edu.tw/course/tw/Croom.jsp?format=-3&year={year}&sem={seme}&code={code}'))
        htmls = await asyncio.gather(*responses)

        for html in htmls:
            room_name = re.search(r'<tr><td>(.+)', html.text).group(1)
            pattern = r'<tr><td align=center>.+?<td>(.+?)<td>(.+?)<td>(.+?)<td>(.+?)<td>(.+?)<td>(.+?)<td>(.+?)'
            search = re.findall(pattern, html.text, re.DOTALL)
            for lesson in range(14):
                for day in range(7):
                    if search[lesson][day] == '\n\u3000\n':
                        empty_room[lesson][day].append(room_name)
        
        with open(f'data/classrooms/{semester}_empty_rooms.json', 'w', encoding='utf-8') as f:
            json.dump(empty_room, f, indent=4, ensure_ascii=False)
        
        return empty_room


if __name__ == "__main__":
    rooms = ClassroomManager()
    empty_rooms = asyncio.run(rooms.get_empty_rooms('1141'))
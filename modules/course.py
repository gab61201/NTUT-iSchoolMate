class Course:
    def __init__(self) -> None:
        self.seme = ""
        self.name = ""
        self.id = ""
        self.class_ = ""

        self.curriculum_url = ""
        self.syllabus_url = ""
        self.file_url = ""
    # async def fetch_data_from_ischool(self):
    #     data={ㄦ
    #         "action":"getSearchCourses",
    #         "id":self.course_id,
    #         "perpage":"20"
    #     }
    #     if not await self.scraper.oauth("ischool_plus_oauth"):
    #         return False
    #     response = await self.scraper.session.post(ISCHOOL_SEARCH_URL)
    #     data = response.json()
    #     if len(data) != 1:
    #         return False
    #     course_info = data[0].popitem()[1]
    #     course_title = course_info["caption"].split("_")

    #     self.year_seme = course_title[0]
    #     self.course_name = course_title[1]
    #     self.cid = course_info["cid"]
    #     self.teacher = course_info["teacher"]
    #     self.file_url = ISCHOOL_FILE_BASE_URL + self.cid
    #     ...



if __name__ == "__main__":
    ...
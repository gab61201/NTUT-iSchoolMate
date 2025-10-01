import re
from course import Course

def html_to_timetable(html_text:str) -> dict|None:
    table= []
    title = ["MENU", "一", "二", "三", "四", "五"]
    table.append(title)
    for i in range(1, 10):
        table.append([str(i)]+[None]*5)
    
    html_text = re.search(r"<table border=1>.+</table>", html_text, re.DOTALL).group() #type:ignore
    if not html_text:
        return None
    all_classes:list[str] = re.findall(r"<tr>\s*<td>\d{6}.+?</tr>", html_text, re.DOTALL)
    with open("output5.html", 'w', encoding='utf-8') as f:
        f.write(all_classes[5])

    for class_html in all_classes:
        course = Course()
        course_id = re.search(r"<td>(\d{6})", class_html)
        if not course_id:
            return None
        course.id = course_id.group(1)
        
        course_info = re.search(r'<A href="Curr.jsp.format=-2&code=(.{7})">(.+?)</A>', class_html)
        if not course_info:
            return None
        curriculum_url = 'https://aps.ntut.edu.tw/course/tw/Curr.jsp?format=-2&code=' + course_info.group(1)
        course_name = course_info.group(2)
        course.curriculum_url = curriculum_url
        course.name = course_name

        syllabus_url = re.search(r'ShowSyllabus.jsp.snum=(\d{6})&code=(\d{5})', class_html)
        if not syllabus_url:
            return None
        course.syllabus_url = 'https://aps.ntut.edu.tw/course/tw/' + syllabus_url.group()
        
        hour_list = class_html.split("<td>")[6:13]
        for i in range(7):
            if hour_list[i] == "　":
                continue
            hour = hour_list[i].split()
            for h in hour:
                table[int(h)][i] = course_name

        print(course.__dict__)
        print("-"*50)

        for t in table:
            print(t)
        

        


    # print(all_classes.split(""))


if __name__ =="__main__":
    from pprint import pprint
    with open("tt.html", 'r', encoding='utf-8') as f:
        html_text = f.read()
    courses = html_to_timetable(html_text)
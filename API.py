import requests
import os
from datetime import datetime, timedelta

access_token = os.getenv('CANVAS_ACCESS_TOKEN')


def get_json(url,params):
    response = requests.get(
    url,
    params=params,
    headers={"Authorization": "Bearer {}".format(access_token)},
    )

    json_response = response.json()

    return json_response

#print(get_json("https://canvas.instructure.com/api/v1/courses?per_page=1000", {}))

# response = requests.get(
# "https://canvas.instructure.com/api/v1/courses",
# headers={"Authorization": "Bearer {}".format(access_token)},
# )

# json_response = response.json()
# repository = json_response[1]
# print("Dictionary: {}".format(repository))

def get_courses():
    response=get_json("https://canvas.instructure.com/api/v1/courses?per_page=1000", {})
    courses={}
    for item in response:
        id=item["id"]
        name=item["name"]
        courses[id]=name
    return courses
#print(get_courses())
def get_assignments(param):
    course_ids=get_courses().keys()
    master_list=[]
    for course_id in course_ids:
        response=get_json("https://canvas.instructure.com/api/v1/courses/{}/assignments".format(course_id), param)
        for item in response:
            id=course_id
            name=item["name"]
            due_date=item["due_at"]

            if due_date is None:
                continue

            assignment_id=item["id"]
            master_list.append({"course_id": id,"due_date": due_date,"assignment_id": assignment_id,"name": name})
    return master_list
def get_assignments_day(date):
    date=datetime.strptime(date,"%Y-%m-%d")
    date=date.replace(hour=0, minute=0, second=0, microsecond=0)
    assignments=get_assignments({"per_page": 50})
    upcoming_assignments=[]
    for assignment in assignments:
        assignment_due_date=datetime.strptime(assignment["due_date"], "%Y-%m-%dT%H:%M:%SZ")
        assignment_due_date=assignment_due_date.replace(hour=0, minute=0, second=0, microsecond=0)
        if date==assignment_due_date:
            upcoming_assignments.append({"due_date": assignment_due_date.strftime("%d %B, %Y"),"name": assignment["name"]})
    return upcoming_assignments
# print(get_assignments_day("2019-10-25"))
def get_assignments_soon():
    date=datetime.now()
    date=date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_date=date + timedelta(days=7)
    assignments=get_assignments({"per_page": 50})
    upcoming_assignments=[]
    for assignment in assignments:
        assignment_due_date=datetime.strptime(assignment["due_date"], "%Y-%m-%dT%H:%M:%SZ")
        assignment_due_date=assignment_due_date.replace(hour=0, minute=0, second=0, microsecond=0)
        if assignment_due_date<end_date and assignment_due_date>date:
            upcoming_assignments.append({"due_date": assignment_due_date.strftime("%d %B, %Y"),"name": assignment["name"]})
    return upcoming_assignments
#print(get_assignments_soon())
#print(get_assignments_day("2019-10-18"))
#  #https://canvas.instructure.com/api/v1/courses/{courseid}/assignments?per_page=1000
#  #https://canvas.instructure.com/doc/api/assignments.html
#2019-10-29T19:45:00Z
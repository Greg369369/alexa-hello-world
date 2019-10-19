import requests
import os

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
            assignment_id=item["id"]
            master_list.append({"course_id": id,"due_date": due_date,"assignment_id":assignment_id,"name":name})
    return master_list
print(get_assignments({"per_page": 1000}))

 #https://canvas.instructure.com/api/v1/courses/{courseid}/assignments?per_page=1000
 #https://canvas.instructure.com/doc/api/assignments.html
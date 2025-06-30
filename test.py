import requests

# def get_all_users():
#     url = "http://127.0.0.1:8000/users"
#     response = requests.get(url)
#     return response.json()

# users = get_all_users()
# for i in users:
#     print(i)

# def get_all_users_with_params(enrollment_year : int):
#     url = "http://127.0.0.1:8000/users"
#     response = requests.get(url, params={"enrollment_year" : enrollment_year})
#     return response.json()

# users_with_params  = get_all_users_with_params(enrollment_year=2018)
# for o in users_with_params:
#     print(o)

# def get_all_users_with_params_mix (enrollment_year : int, major : str, special_notes : str):
#     url = f"http://127.0.0.1:8000/users/{enrollment_year}"
#     response = requests.get(url, params={"major" : major, "special_notes" : special_notes})
#     return response.json()

# users_with_params_mix = get_all_users_with_params_mix(2018, major="Экология", special_notes="Без особых примет")

# print(users_with_params_mix)


# def get_all_users_id (user_id : int):
#     url="http://127.0.0.1:8000/users"
#     response = requests.get(url, params={"user_id" : user_id})
#     return response.json()
# all_users_id = get_all_users_id(user_id=3)

# print(all_users_id)


# def get_all_users_id(user_id: int):
#     url = "http://127.0.0.1:8000/users"
#     response = requests.get(url, params={"user_id": user_id})
#     return response.json()

# all_users_id = get_all_users_id(user_id=3)
# print(all_users_id)


def get_all_users_id(user_id: int):
    url = f"http://127.0.0.1:8000/users/{user_id}"
    response = requests.get(url)
    return response.json()

all_users_id = get_all_users_id(3)
print(all_users_id)



# def get_all_users_with_params_mix (enrollment_year : int, major : str, special_notes : str):
#     url = f"http://127.0.0.1:8000/users/{enrollment_year}"
#     response = requests.get(url, params={"major" : major, "special_notes" : special_notes})
#     return response.json()

# users_with_params_mix = get_all_users_with_params_mix(2018, major="Экология", special_notes="Без особых примет")

# print(users_with_params_mix)
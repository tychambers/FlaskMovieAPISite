import requests

api_key = "G0MMmBEs8ib90PwAHCSXK12yzDRFcE0w"

url = 'http://127.0.0.1:5000/authenticate'
my_obj = {'api_key': f'{api_key}'}

x = requests.post(url, json=my_obj)

access_token = x.json()
access_token = access_token['access_token']
headers = {
    "Authorization": f"Bearer {access_token}"
}

movie = requests.get("http://127.0.0.1:5000/movies/fight%20club", headers=headers)
print(movie.json())


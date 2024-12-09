from dotenv import load_dotenv
import os
import requests
import json
import time
import paramiko
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

cookies = None
able_to_download = []

load_dotenv()
openaiApiKey = os.getenv("openaiApiKey")
bitorDomain = os.getenv("bitorDomain")
bitorUsername = os.getenv("bitorUsername")
bitorPassword = os.getenv("bitorPassword")
jellyDomain = os.getenv("jellyDomain")
jellyApiKey = os.getenv("jellyApiKey")
movieDomain = os.getenv("movieDomain")
sshHost = os.getenv("sshHost")
sshPort = os.getenv("sshPort")
sshUsername = os.getenv("sshUsername")
sshPassword = os.getenv("sshPassword")
emailHost = os.getenv("emailHost")
emailPort = os.getenv("emailPort")
emailUsername = os.getenv("emailUsername")
emailPassword = os.getenv("emailPassword")
emailFromEmail = os.getenv("emailFromEmail")
emailToEmail = os.getenv("emailToEmail")

def email(subject, body, type='plain'):
    try:
        # Create the email
        msg = MIMEMultipart()
        msg['From'] = emailFromEmail
        msg['To'] = emailToEmail
        msg['Subject'] = subject
        msg.attach(MIMEText(body, type))
        # Send the email
        with smtplib.SMTP(emailHost, emailPort) as server:
            server.starttls()
            server.login(emailUsername, emailPassword)
            server.sendmail(emailFromEmail, emailToEmail, msg.as_string())
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")

def openAI(selection, title,year,list=[],movies=[],shows=[]):
    if selection == "Do we own it":    
        system_content = (
            "You are a helpful assistant for seeing if we own a movie or show. "
            "You will be given a list of movies and shows that we own, and then "
            "the movie or show that we are checking. If we already own the movie "
            "or show, respond with 'true', and if we do not own the movie or show"
            ", respond with 'false'. Please only respond with 'true' or 'false'. "
            "Thank you."
        )
        user_content = (
            f"Here is the movie or show Title & release date: \"{title}\" ({year}). "
            f"Here is the list of movies we own: {movies}, and here is the list "
            f"of shows we own: {shows}"
        )
    elif selection == "Select torrent":
        system_content = (
            "You are a helpful assistant for selecting the correct movie. You "
            "will be given a list of movies, and the original title and date, "
            "and need to select the most correct movie. If there are multiple "
            "options, Prioritize 1080p over 720p, and 4K last. After that, "
            "prioritize a movie that is not an obnoxious size, don’t download "
            "a 20GB file if it is only an hour long movie. Then choose the one "
            "with the most seeders. Please just return the index of the item on "
            "the list. (You will get up to 40 objects, return the number only, "
            "i.e. “4”). Never include additional text, explanations, or "
            "formatting—just respond with the number. \n"
            "If it is a TV Show, choose the one that is a 'COMPLETE' download. If "
            "the show has 5 seasons, make sure it sayssomething along the lines of "
            "'seasons 1,2,3,4,5' or '1-5', or something. If there is not a download "
            "of all seasons, please respond '-2'. Thank you so much."
        )
        user_content = (
            "Please select the best one. You will get up to 40, return "
            "the index number only, i.e. “4”. Please only respond with one number. "
            f"Title & Year(s): \"{title}\" ({year}), List of downloads: {list}"
        )
    elif selection == "What location":
        system_content = (
            "You are a helpful assistant for categorizing movies. "
            "You will be given a movie title and the year it was released, "
            "and you are incharge of deciding which category it should go in: "
            "'Adults', 'Harry Potter', 'Hunger Games', 'James Bond', 'Kids', "
            "'Marvel Cinematic Universe', 'Maze Runner', 'Murder Mysteries', "
            "'Pirates of the Caribbean', 'Star Wars', 'X-Men', 'Adventure', 'Action', "
            "or 'Other'. Please respond ONLY with the category. Thank you."
        )
        user_content = f"Categorize the movie \"{title}\" ({year})."
    elif selection == "Is it downloading":
        system_content = (
            "You are a helpful assistant for seeing if we are currently "
            "downloading a movie or show. You will be given a list of "
            "torrents, and then the movie or show that we are checking. "
            "If we already downloading it , respond with 'true', and if "
            "we do not downloading it, respond with 'false'. Please only "
            "respond with 'true' or 'false'. Thank you."
        )
        user_content = (
            f"Here is the movie or show Title & release date: \"{title}\" ({year}). "
            f"Here is the list of torrents: {list}"
        )
    else:
        return -7
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openaiApiKey}"
    }
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system", "content": system_content
            },
            {
                "role": "user", "content": user_content
            }
        ]
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        result = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        return result
    except requests.exceptions.RequestException as e:
        return -3
    
def jelly():
    all_movies = []
    all_shows = []
    url = f"https://{jellyDomain}/Items"
    headers = {
        "X-MediaBrowser-Token": jellyApiKey,
    }
    lib_params = {
        "IncludeItemTypes": "Collection",
        "Fields": "Name"
    }
    lib_response = requests.get(url, headers=headers, params=lib_params)
    if lib_response.status_code == 200:
        libraries = lib_response.json().get("Items", [])
        for library in libraries[1:-1]:
            id = library["Id"]
            movie_params = {"ParentId": id,"IncludeItemTypes": "Movie"}
            movies_response = requests.get(url,headers=headers, params=movie_params)
            if movies_response.status_code == 200:
                for movie in movies_response.json().get("Items", []):
                    title = movie["Name"]
                    try:
                        year = str(movie["ProductionYear"])
                    except:
                        year = "Unknown"
                    all_movies.append([title,year])    
            else:
                print(f"Faild request 2: {movies_response.status_code} - {movies_response.text}")
        shows = libraries[-1]
        show_params = {"ParentId": shows["Id"],"IncludeItemTypes": "Series"}
        shows_response = requests.get(url,headers=headers, params=show_params)
        if shows_response.status_code == 200:
            for show in shows_response.json().get("Items", []):
                title = show["Name"]
                try:
                    year = str(show["ProductionYear"])
                except:
                    year = "Unknown"
                try:
                    if(show["Status"] == "Ended"):
                        end = str(show["EndDate"])[0:4]
                    else:
                        end = "Current"
                except:
                    end = "Unknown"
                all_shows.append([title,year,end])    
        else:
            print(f"Faild request 3: {shows_response.status_code} - {shows_response.text}")
    else:
        print(f"Faild request 1: {lib_response.status_code} - {lib_response.text}")
    return all_movies, all_shows

def qBitt_login():
    global cookies
    url = f"https://{bitorDomain}/api/v2/auth/login"
    credentials = {"username": bitorUsername, "password": bitorPassword}
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(url, headers=headers, data=credentials)
    if response.status_code == 200:
        print("Login successful")
        cookies = response.cookies  # Save cookies for future requests
    else:
        print("Login failed:", response.text)
    
# type: start / status / stop / results
# media: TV / Movie
def qBitt_search(type,id=None,title=None,media="all"):
    global cookies
    url = f"https://{bitorDomain}/api/v2/search/{type}"
    if (type == "start" and title):   
        payload = {"pattern": title, "plugins": "all", "category": media}
    elif (type == ("status" or "stop") and id):
        payload = {"id": id}
    elif (type == "results" and id):
        payload = {"id": id,"limit": 40}
    else:
        return None
    response = requests.post(url, data=payload, cookies=cookies)
    if response.status_code == 200:
        print(f"Ran command: {type}")
        return json.loads(response.text)
    else:
        print(f"Failed to {type} search:", response.text)

def qBitt_torr(type,file=None,location=None):
    global cookies
    url = f"https://{bitorDomain}/api/v2/torrents/{type}" # add
    if type == "add":
        payload = {
            "urls": file,
            "savepath": f"/media/{location}",
            "paused": "false",
            "autoTMM": "false"
        }
        response = requests.post(url, data=payload, cookies=cookies)
        if response.status_code == 200:
            print("Torrent added successfully")
        else:
            print("Failed to add torrent:", response.text)
    elif type == "info":
        payload = {}
        response = requests.post(url, data=payload, cookies=cookies)
        if response.status_code == 200:
            print("Torrents loaded")
            return response.json()
        else:
            print("Failed to get torrent:", response.text)

def ssh(command):
    return_values = [False,None]
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        # Connect to the server
        ssh_client.connect(hostname=sshHost, port=sshPort, username=sshUsername, password=sshPassword)
        print(f"Connected to {sshHost}:{sshPort}")
        # Execute the command
        stdin, stdout, stderr = ssh_client.exec_command(command)
        # Read the command's output and error
        output = stdout.read().decode()
        # output = stdout.read().decode()
        error = stderr.read().decode()
        if output:
            return_values = [True, output]
        if error:
            return_values = [False, error]
    except Exception as e:
        return_values = [False, e]
    finally:
        ssh_client.close()
        print("Connection closed.")
        return return_values[0], return_values[1] 

def get_new_movies():
    global able_to_download
    command = (
        "cd /home/nafzigers.us/movie.nafzigers.us/ && "
        "mv ToDownload.json old_ToDownload.json && "
        "touch ToDownload.json && "
        "chmod 666 ToDownload.json && "
        "cat old_ToDownload.json"
    )
    sshWorked, sshResults = ssh(command)
    try:
        jsonSshResults = json.loads(sshResults)
    except:
        jsonSshResults = False

    if(sshWorked and jsonSshResults):
        able_to_download.append(len(jsonSshResults))
        return jsonSshResults, True
    else:
        return None, False

new_movies_list, new_movies = get_new_movies()
if not new_movies:
    exit()

owned = jelly()
owned_movies = owned[0]
owned_shows = owned[1]
qBitt_login()

for item_index, movie in enumerate(new_movies_list):
    if movie["type"] == "movie":
        media = "Movies"
    elif movie["type"] == "series":
        media = "TV shows"
    own_it = openAI("Do we own it",movie["title"],movie["year"],movies=owned_movies,shows=owned_shows) == "true"
    if own_it:
        movie['reason'] = 'Own it'
        continue   
    download_names = [item["name"] for item in qBitt_torr("info")]
    downloading = openAI("Is it downloading",movie["title"],movie["year"],list=download_names) == "true"
    if downloading:
        movie['reason'] = 'Downloading it'
        continue
    location = openAI("What location",movie["title"],movie["year"]) 
    id = qBitt_search("start",title=movie["title"],media=media)['id']
    for moment in range(10):
        status = qBitt_search("status",id=id)
        if status[0]["status"] == "Running":
            time.sleep(1)
    results = qBitt_search("results",id=id)
    if results['total'] == 0:
        movie['reason'] = 'Could not find it'
        continue
    file_names = [item["fileName"] for item in results["results"]]
    index = int(openAI("Select torrent",movie["title"],movie["year"],list=file_names)) -1
    if (index < -1):
        movie['reason'] = 'Could not find all seasons'
        continue
    if (movie["type"] == "series"):
        folder = "TV Shows"
    elif (movie["type"] == "movie"):
        folder = "Movies"
    qBitt_torr("add",results["results"][index]["fileUrl"],f"{folder}/{location}")
    able_to_download.append(item_index)

email_list_good = []
email_list_bad = []
downloaded = False

for item_index, movie in enumerate(new_movies_list):
    if item_index not in able_to_download[1:]:
        if movie['reason'] != 'Own it':
            email_list_bad.append(movie)
    else:
        email_list_good.append(movie["title"])
        downloaded = True

if downloaded:
    if email_list_bad:
        content = f"""
        <html>
        <head></head>
        <body>
            <p><b>Downloaded these movies:</b></p>
            <ul>
                {''.join(f"<li>{movie}</li>" for movie in email_list_good)}
            </ul>
            <br>
            <p><b>Did not download these movies:</b></p>
            <ul>
                {''.join(f"<li>{movie}</li>" for movie in email_list_bad)}
            </ul>
        </body>
        </html>
        """
    else:
        content = f"""
        <html>
        <head></head>
        <body>
            <p><b>Downloaded these movies:</b></p>
            <ul>
                {''.join(f"<li>{movie}</li>" for movie in email_list_good)}
            </ul>
        </body>
        </html>
        """
else:
    content = f"""
    <html>
    <head></head>
    <body>
        <p><b>Was not able to download any movies.</b></p>
        <br>
        <p><b>List:</b></p>
        <ul>
            {''.join(f"<li>{movie}</li>" for movie in email_list_bad)}
        </ul>
    </body>
    </html>
    """

email("Movie Download Overview",content,type='html')
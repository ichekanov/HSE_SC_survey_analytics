import csv
import requests
from os import mkdir
import sys
import os
import time
from progress.bar import IncrementalBar
from twocaptcha import TwoCaptcha
# from private_data import VK_personal_token
# from private_data import CAPTCHA_TOKEN
VK_personal_token = "YOUR VK TOKEN"
CAPTCHA_TOKEN = "YOUR RUCAPTCHA TOKEN"

def get_polls(owner_id, start, end):
    ID = []
    k = 0
    url = "https://api.vk.com/method/wall.get?v=5.131"
    print("Поначалу может ничего не происходить: ищем начало временного промежутка.")
    wait()
    req = requests.get(
        url, params={'access_token': VK_personal_token, 'owner_id': owner_id})
    src = req.json()
    post_date = src["response"]["items"][0]["date"]
    mx = src["response"]["count"]
    while post_date > end and k+20 < mx:
        k += 20
        wait()
        req = requests.get(url, params={
                           'access_token': VK_personal_token, 'owner_id': owner_id, 'offset': k})
        src = req.json()
        post_date = src["response"]["items"][0]["date"]
    print(f"Total number of posts: {mx-k}")
    bar = IncrementalBar('Posts', max=(mx-k))
    while k < mx and post_date > start:
        wait()
        req = requests.get(url, params={
                           'access_token': VK_personal_token, 'owner_id': owner_id, 'offset': k})
        src = req.json()
        posts = src["response"]["items"]
        post_date = src["response"]["items"][0]["date"]
        for post in posts:
            if "attachments" in post:
                for x in post["attachments"]:
                    if "poll" in x:
                        ID.append(
                            (x["poll"]["id"], x["poll"]["question"], x["poll"]["created"], post["id"]))
            k += 1
            bar.next()
    bar.finish()
    print("Done parsing!\n")
    return ID  # [(poll_id, poll_name, poll_timestamp, post_id), ...]


def get_poll_results(poll_id, owner_id):
    variants = []

    def get_poll_data():
        url = "https://api.vk.com/method/polls.getById?v=5.131"
        wait()
        req = requests.get(url, params={
            'access_token': VK_personal_token, 'owner_id': owner_id, 'poll_id': poll_id})
        poll_data = req.json()["response"]
        return poll_data

    def get_voters():
        url = "https://api.vk.com/method/polls.getVoters?v=5.131"
        var = str(variants).replace(" ", "")[1:-1]
        wait()
        req = requests.get(url, params={
            'access_token': VK_personal_token, 'owner_id': owner_id, 'poll_id': poll_id, 'answer_ids': var})
        votes = req.json()
        if "error" in votes:
            if votes["error"]["error_msg"] == 'Access denied, please vote first':
                return False
            else:
                raise votes
        else:
            return votes["response"]

    def vote():
        wait()
        done = False
        captcha = False
        text = ""
        captcha_sid = ""
        while not done:
            if not captcha:
                url = "https://api.vk.com/method/polls.addVote?v=5.131"
                wait()
                req = requests.get(url, params={
                                   'access_token': VK_personal_token, 'owner_id': owner_id, 'poll_id': poll_id, 'answer_ids': variants[-1]})
                ans = req.json()
            else:
                url = "https://api.vk.com/method/polls.addVote?v=5.131"
                wait()
                req = requests.get(url, params={'access_token': VK_personal_token, 'owner_id': owner_id,
                                   'poll_id': poll_id, 'answer_ids': variants[-1], 'captcha_sid': captcha_sid, 'captcha_key': text})
                ans = req.json()
            if 'response' in ans:
                print(
                    f"Successfully voted in {poll_id} for {variants_with_names[-1][1]}")
                done = True
            else:
                try:
                    captcha_sid = ans['error']['captcha_sid']
                    pic = requests.get(ans['error']['captcha_img']) 
                    with open('captcha.jpg', 'wb') as f:
                        f.write(pic.content)
                    text = solver.normal('captcha.jpg')['code']
                    print("Successfully resolved captcha!")
                    captcha = True
                except Exception as e:
                    print(ans)
                    sys.exit(e)

    poll_data = get_poll_data()
    variants = [x['id'] for x in poll_data['answers']]
    variants_with_names = [(x['id'], x['text']) for x in poll_data['answers']]
    votes = get_voters()
    if not votes:
        vote()
        votes = get_voters()
    # print(poll_data)
    # print(variants)
    # print(variants_with_names)
    # print(votes)
    users_by_variants = {}
    with open("data/users.txt", "a", encoding="utf-8") as f:
        for k in range(len(variants_with_names)-1):
            users_by_variants[variants_with_names[k]
                              ] = votes[k]['users']['items']
            f.writelines([str(m)+"\n" for m in votes[k]['users']['items']])
    return users_by_variants  # {(variant_id, variant_name): [voters], ...}


def get_names(path="data/users.txt"):
    with open(path, "r", encoding="utf-8") as file:
        ids = str(set([int(x) for x in file.readlines()])).replace(" ", "")
    url = "https://api.vk.com/method/users.get?v=5.131"
    wait()
    req = requests.get(
        url, params={'access_token': VK_personal_token, "user_ids": ids[1:-1]})
    data = req.json()
    with open(path.replace(".txt", ".csv"), "w", newline='', encoding="utf-8") as file:
        file.write("id,имя,фамилия,ссылка\n")
        writer = csv.writer(file, delimiter=',')
        for guy in data["response"]:
            writer.writerow([guy["id"],  guy["first_name"],
                            guy["last_name"], f"vk.com/id{guy['id']}"])


def write_csv(poll, results, group, path="data/votes.csv"):
    # poll: (poll_id, poll_name, poll_timestamp, post_id)
    # results: {(variant_id, variant_name): [voters], ...}
    # запись: дата, ссылка, название, вариант, id пользователя, наличие голоса
    date = time.strftime("%d.%m.%Y", time.gmtime(poll[2]+10800))
    link = f"https://vk.com/wall{group}_{poll[3]}"
    voters = set()
    # (voters.add(y) for x in results.values() for y in x)
    for x in results.values():
        for y in x:
            voters.add(y)
    with open(path, "a", newline='', encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        for id in results.keys():
            for guy in voters:
                data = [date, link, poll[1], id[1],
                        guy, 1 if guy in results[id] else 0]
                writer.writerow(data)
    print(f'Successfully recorded poll "{poll[1]}"')


def wait():  # блокируем выполнение программы для сохранения задержек между запросами
    global last_request
    while (time.time() - last_request) < 0.4:
        time.sleep(0.05)
    last_request = time.time()


def makefiles():
    try:
        mkdir("data")
    except FileExistsError:
        pass
    open("data/users.txt", "w", encoding="utf-8").close()
    f = open("data/votes.csv", "w", encoding="utf-8")
    f.write(
        "дата,ссылка на пост,название голосования,вариант,id депутата,наличие голоса\n")
    f.close()


def main():
    makefiles()
    # group_id = "-206802048"  # тестовая группа
    # group_id = "-207790088" # тестовая группа 2
    group_id = "-90904335"  # группа СС
    start = "01.01.2019"  # самая ранняя дата, за которую надо получить данные
    end = "01.01.2020"  # самая поздняя дата, за которую надо получить данные
    min_date = time.mktime(time.strptime(start, "%d.%m.%Y"))
    max_date = time.mktime(time.strptime(end, "%d.%m.%Y"))
    if min_date >= max_date:
        print("Дата начала промежутка (start) должна быть меньше даты конца (end)!")
        return
    polls = get_polls(group_id, min_date, max_date)
    for poll in polls:
        results = get_poll_results(poll[0], group_id)
        write_csv(poll, results, group_id)
    get_names()


if __name__ == "__main__":
    voters = []
    last_request = time.time()
    sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    api_key = os.getenv('APIKEY_RUCAPTCHA', CAPTCHA_TOKEN)
    solver = TwoCaptcha(api_key)
    main()

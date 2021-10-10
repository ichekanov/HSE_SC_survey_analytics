import requests
from time import sleep
import vk
from private_data import VK_personal_token


def get_polls(owner_id):
    ID = []
    k = 0
    url = f"https://api.vk.com/method/wall.get?owner_id={owner_id}&access_token={VK_personal_token}&v=5.131"
    req = requests.get(
        url, params={'owner_id': owner_id, 'count': 100, 'offset': k})
    src = req.json()
    mx = src["response"]["count"]
    print(f"Number of posts: {mx}")
    while k < mx and k<100:
        sleep(0.4)
        req = requests.get(url, params={'owner_id': owner_id, 'offset': k})
        src = req.json()
        posts = src["response"]["items"]
        for post in posts:
            if "attachments" in post:
                for x in post["attachments"]:
                    if "poll" in x:
                        ID.append((x["poll"]["id"], x["poll"]["question"]))
            k += 1
        print(f"k = {k}")
    print("Done parsing!\n")
    print(ID)
    return ID  # [(vote_id, vote_name), ...]


def vote(poll_id):
    sleep(0.4)
    poll_data = api.polls.getById(poll_id=poll_id[0])
    variant = [(x['id'], x['text']) for x in poll_data['answers']]
    sleep(0.4)
    api.polls.addVote(poll_id=poll_id[0], answer_ids=variant[-1][0])
    print(f"Voted in {poll_id[1]} for {variant[-1][1]}")


def main():
    # public = "-206802048" # тестовая группа
    public = "-207790088" # тестовая группа 2
    # public = "-90904335" # группа СС
    [vote(x) for x in get_polls(public)]


if __name__ == "__main__":
    session = vk.Session(access_token=VK_personal_token)
    api = vk.API(session, v='5.131', lang='ru')
    main()

import requests
from time import sleep
import vk
from private_data import VK_personal_token


def get_polls(owner_id):
    ID = []
    k = 0
    url = f"https://api.vk.com/method/wall.get?owner_id={owner_id}&access_token={VK_personal_token}&v=5.131"
    req = requests.get(
        url, params={'owner_id': owner_id, 'count': 5, 'offset': k})
    src = req.json()
    print(src)
    mx = src["response"]["count"]
    print(f"Number of posts: {mx}")
    while k < mx and src["response"]["items"][0]["date"] > 1609459200:
        sleep(0.5)
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
    # file = open("1.txt", "w")
    # file.write(str(ID))
    # file.close()
    print(len(ID))
    return ID  # [(vote_id, vote_name), ...]


def vote(poll_id, owner_id):
    poll_data = api.polls.getById(poll_id=poll_id[0], owner_id=owner_id)
    variant = [(x['id'], x['text']) for x in poll_data['answers']]
    # url = f"https://api.vk.com/method/polls.getById?owner_id={owner_id}&poll_id={poll_id[0]}&access_token={VK_personal_token}&v=5.131"
    # req = requests.get(url)
    # poll_data = req.json()
    # print(poll_data)
    # print()
    # variant = [(x['id'], x['text']) for x in poll_data['response']['answers']]
    sleep(0.5)
    done = False
    captcha = False
    text = ""
    captcha_sid = ""
    while not done:
        # api.polls.addVote(poll_id=poll_id[0], answer_ids=variant[-1][0])
        if not captcha:
            url = f"https://api.vk.com/method/polls.addVote?owner_id={owner_id}&poll_id={poll_id[0]}&answer_ids={variant[-1][0]}&access_token={VK_personal_token}&v=5.131"
            req = requests.get(url)
            ans = req.json()
        else:
            url = f"https://api.vk.com/method/polls.addVote?owner_id={owner_id}&poll_id={poll_id[0]}&answer_ids={variant[-1][0]}&access_token={VK_personal_token}&captcha_sid={captcha_sid}&captcha_key={text}&v=5.131"
            req = requests.get(url)
            ans = req.json()
        if 'response' in ans:
            print(f"Voted in {poll_id[1]} for {variant[-1][1]}")
            done = True
            sleep(0.5)
        else:
            try:
                captcha_sid = ans['error']['captcha_sid']
                print(ans['error']['captcha_img'])
                text = input("Input captcha: ")
                captcha = True
            except:
                print(ans)

    # done = False
    # while not done:
    #     try:
    #         sleep(1)
    #         poll_data = api.polls.getById(poll_id=poll_id[0], owner_id=owner_id)
    #         # url = f"https://api.vk.com/method/polls.getById?owner_id={owner_id}&poll_id={poll_id[0]}&access_token={VK_personal_token}&v=5.131"
    #         # req = requests.get(url)
    #         # poll_data = req.json()
    #         print(poll_data)
    #         print()
    #         variant = [(x['id'], x['text']) for x in poll_data['response']['answers']]
    #         sleep(1)
    #         # api.polls.addVote(poll_id=poll_id[0], answer_ids=variant[-1][0])
    #         url = f"https://api.vk.com/method/polls.addVote?owner_id={owner_id}&poll_id={poll_id[0]}&answer_ids={variant[-1][0]}&access_token={VK_personal_token}&v=5.131"
    #         req = requests.get(url)
    #         ans = req.json()
    #         print(ans)
    #         print()
    #         print(f"Voted in {poll_id[1]} for {variant[-1][1]}")
    #         done = True
    #     except Exception as exc:
    #         print(f"Ошибка: {exc}")
    #         print(req.json())
    #         print()
    #         sleep(60)


def main():
    public = "-206802048" # тестовая группа
    # public = "-207790088" # тестовая группа 2
    # public = "-90904335"  # группа СС
    [vote(x, public) for x in get_polls(public)]
    # get_polls(public)


if __name__ == "__main__":
    session = vk.Session(access_token=VK_personal_token)
    api = vk.API(session, v='5.131', lang='ru')
    main()

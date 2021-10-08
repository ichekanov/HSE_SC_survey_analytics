import vk
from private_data import VK_personal_token

session = vk.Session(access_token=VK_personal_token)
api = vk.API(session, v='5.131', lang='ru')

poll_id = "637266255"

pollData = api.polls.getById(poll_id=poll_id)
variants = [x['id'] for x in pollData['answers']]
votes = api.polls.getVoters(poll_id=poll_id, answer_ids=variants)
usersByVariants = {x['answer_id']: x['users']['items'] for x in votes}

for k in usersByVariants:
    print(k, usersByVariants[k], sep=': ', end='\n')
# script output in output.txt

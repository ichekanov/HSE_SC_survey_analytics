import vk
from private_data import VK_personal_token


def get_poll_results(VK_access_token, poll_id):
    session = vk.Session(access_token=VK_access_token)
    api = vk.API(session, v='5.131', lang='ru')
    poll_data = api.polls.getById(poll_id=poll_id)
    variants = [x['id'] for x in poll_data['answers']]
    variants_with_names = [(x['id'], x['text']) for x in poll_data['answers']]
    votes = api.polls.getVoters(poll_id=poll_id, answer_ids=variants)
    users_by_variants = {}
    for k in range(len(variants_with_names)):
        users_by_variants[variants_with_names[k]] = votes[k]['users']['items']
    return users_by_variants  # {(variant_id, variant_name): [voters], ...}


if __name__ == "__main__":
    poll_id = "637266255"
    print(get_poll_results(VK_personal_token, poll_id))

# script output in output.txt

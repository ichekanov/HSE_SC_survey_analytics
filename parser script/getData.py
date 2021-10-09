import csv
import vk
from private_data import VK_personal_token


def get_poll_results(poll_id):
    poll_data = api.polls.getById(poll_id=poll_id)
    variants = [x['id'] for x in poll_data['answers']]
    variants_with_names = [(x['id'], x['text']) for x in poll_data['answers']]
    votes = api.polls.getVoters(poll_id=poll_id, answer_ids=variants)
    users_by_variants = {}
    for k in range(len(variants_with_names)):
        users_by_variants[variants_with_names[k]] = votes[k]['users']['items']
    return users_by_variants  # {(variant_id, variant_name): [voters], ...}


def get_names(ids):
    # max number of requested users - 1000
    names = sorted([(x['last_name'], x['first_name'], x['id'])
                    for x in api.users.get(user_ids=ids)])
    return names  # [(last_name, first_name, id), ...]


def write_to_csv(names, users_by_variants, path="output.csv"):
    ids = [x[3] for x in names]
    with open(path, "w", newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerow(['']+[x[0]+" "+x[1] for x in names])


def main():
    poll_id = "637266255"
    results = list(get_poll_results(poll_id).values())
    answers = list(get_poll_results(poll_id))
    voters_ids = set()
    for i in range(len(results)):
        for x in results[i]:
            voters_ids.add(x)
    voters = sorted(get_names(list(voters_ids)))
    # print(voters)
    print(answers)
    # write_to_csv(voters, results)


if __name__ == "__main__":
    session = vk.Session(access_token=VK_personal_token)
    api = vk.API(session, v='5.131', lang='ru')
    main()

# script output in output.txt

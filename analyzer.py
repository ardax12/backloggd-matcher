import exporter
import math

def calculateSimilarity(username1,username2):

    driver = createDriver()

    user1data = exporter.fetch_all_game_data_with_driver(f"https://backloggd.com/u/{username1}/games/", driver)
    user2data = exporter.fetch_all_game_data_with_driver(f"https://backloggd.com/u/{username2}/games/", driver)

    driver.quit()

    lookup = {k: v for k, v in user2data}

    intersection = [(k, v1, lookup[k]) for k, v1 in user1data if k in lookup]

    intersectionLength = len(intersection)

    if(intersectionLength ==0):
        return 0

    intersection_len = len(intersection)
    union_len = len(user1data) + len(user2data) - intersection_len
    overlap_fraction = intersection_len / union_len
    baseScore = overlap_fraction * 100

    user1Avg = sum(t[1] for t in intersection) / intersection_len
    user2Avg = sum(t[2] for t in intersection) / intersection_len

    user1_diffs = [t[1] - user1Avg for t in intersection]
    user2_diffs = [t[2] - user2Avg for t in intersection]

    dot_product = sum(a * b for a, b in zip(user1_diffs, user2_diffs))
    mag1 = math.sqrt(sum(a ** 2 for a in user1_diffs))
    mag2 = math.sqrt(sum(b ** 2 for b in user2_diffs))

    if mag1 == 0 or mag2 == 0:
        cosine_similarity = 0
    else:
        cosine_similarity = dot_product / (mag1 * mag2)

    ratingBonus = cosine_similarity * 100

    final_score = baseScore + ratingBonus
    final_score = max(0, min(100, final_score))

    return round(final_score, 2)

def createDriver():
    return exporter.init_driver_with_cookies()

print(calculateSimilarity("cangaz","Rotary"))

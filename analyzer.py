import exporter
from PIL import Image, ImageDraw

score = 0
intersectionLength = 0

def calculateSimilarity(username1,username2):

    user1data = exporter.fetch_all_game_data(f"https://backloggd.com/u/{username1}/games/")
    user2data = exporter.fetch_all_game_data(f"https://backloggd.com/u/{username2}/games/")

    lookup = {k: v for k, v in user2data}

    intersection = [(k, v1, lookup[k]) for k, v1 in user1data if k in lookup]

    intersectionLength = len(intersection)

    if(intersectionLength ==0):
        return

    totalLen = len(user1data) + len(user2data) - intersectionLength

    gameOverlap = intersectionLength/totalLen

    gameOverlapScore = gameOverlap * 50

    reviewOverlapScore = 50

    user1TotalReview = 0
    user2TotalReview = 0

    for tup in intersection:
        if(tup[1] == 0 or tup[2] == 0):
            intersection.remove(tup)
        else:
            user1TotalReview += tup[1]
            user2TotalReview += tup[2]

    user1Avg = user1TotalReview/len(intersection)
    user2Avg = user2TotalReview/len(intersection)

    for tup in intersection:
        user1Score = tup[1] - user1Avg 
        user2Score = tup[2] - user2Avg
        dif = abs(user1Score - user2Score)
        reviewOverlapScore -= (dif / 4.5) * (50 / len(intersection))

        score = max(0, score)

    score = reviewOverlapScore + gameOverlapScore



image = Image.new('RGB', (360, 540), color='black')
draw = ImageDraw.Draw(image)
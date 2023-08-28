from ossapi import Ossapi, UserLookupKey, Domain, enums, mod
from timeconversion import convert_to_unix_time, convert_to_format

import skinnables

clientID = 23657
clientSecret = "6mSPhvot25X99yRSdZPYThVSZTJm8SOc4UjNFSy6"

gradeValues = {enums.Grade.F: 1,
               enums.Grade.D: 1,
               enums.Grade.C: 2,
               enums.Grade.B: 3,
               enums.Grade.A: 4,
               enums.Grade.S: 5,
               enums.Grade.SH: 6,
               enums.Grade.SS: 7,
               enums.Grade.SSH: 8}


class Lazer:
    def __init__(self, domain):
        self.domain = domain
        self.api = None
        self.apiCalls = 0
        self.user = None
        self.recentPlays = None
        self.scores = []

    def needsToCreateAPI(self):
        if self.api is None and self.user is None:
            return True

        else:
            return False

    def createAPI(self, target):
        if self.needsToCreateAPI():
            self.api = Ossapi(client_id=clientID, client_secret=clientSecret, domain=self.domain)
            self.user = self.api.user(target, key=UserLookupKey.USERNAME)
            self.apiCalls += 1
            print(f"[API] Created ossapi for {self.domain.name.lower()} for {target}. "
                  f"{self.apiCalls} API calls made")

    def getRecentPlays(self):
        # Uses osu!api to fetch all recent scores
        if self.recentPlays is None:
            self.recentPlays = self.api.user_scores(self.user.id, type='recent', include_fails=True)
            self.apiCalls += 1
            print(f"[API] Used ossapi for {self.domain.name.lower()} to fetch recent scores. "
                  f"{self.apiCalls} API calls made")

        return self.recentPlays

    def getScores(self):
        # Uses osu!api to fetch all scores set on the recently played map
        if not self.scores:
            self.scores = self.api.beatmap_user_scores(beatmap_id=self.getRecentPlay().beatmap.id, user_id=self.user.id)
            self.apiCalls += 1
            print(f"[API] Used ossapi for {self.domain.name.lower()} to fetch all scores on recent map. "
                  f"{self.apiCalls} API calls made")

        return self.scores

    def getInheritedModScores(self):
        # Returns a list of scores that have the same mods as the recent play
        inheritedModScores = []
        for score in self.getScores():
            if score.mods.value == self.getRecentPlay().mods.value:
                inheritedModScores.append(score)

        return inheritedModScores

    def getRecentPlay(self):
        recentPlays = self.getRecentPlays()

        if recentPlays:
            return recentPlays[0]

        return

    def getInheritedModPlayCount(self):
        return len(self.getInheritedModScores())

    def getRecentPlayStats(self):
        recentPlay = self.getRecentPlay()

        if recentPlay:
            recentPlayAccuracy = recentPlay.accuracy
            recentPlayMissCount = recentPlay.statistics.count_miss
            recentPlayPP = recentPlay.pp
            recentPlayGrade = recentPlay.rank
            recentPlayDate = recentPlay.created_at

            if recentPlay.pp is None:
                recentPlayPP = 0

            return recentPlayAccuracy, recentPlayMissCount, recentPlayPP, recentPlayGrade, recentPlayDate

        return [None for _ in range(4)]

    def getBestStats(self, plays):
        # Aims to get the relative statistics for scores on the same map
        bestAccuracy, bestAccuracyDate = self.getBestAccuracy(plays=plays)
        bestMissCount, bestMissCountDate = self.getBestMissCount(plays=plays)
        bestPP, bestPPDate = self.getBestPP(plays=plays)
        bestGrade, bestGradeDate = self.getBestGrade(plays=plays)

        return bestAccuracy, bestAccuracyDate, \
            bestMissCount, bestMissCountDate, \
            bestPP, bestPPDate, \
            bestGrade, bestGradeDate

    def getAverageStats(self, plays):
        # Aims to get the relative statistics for scores on the same map
        # After passing plays, plays could or could be filtered by mods

        accuracies = []
        missCounts = []
        pps = []
        grades = []

        for score in plays:
            accuracies.append(score.accuracy)
            missCounts.append(score.statistics.count_miss)
            pps.append(score.pp)
            grades.append(score.rank)

        return self.getAverage(accuracies), self.getAverage(missCounts), \
            self.getAverage(pps), self.getModeGrade(grades)

    def getBestPlay(self):
        recentPlay = self.getRecentPlay()
        print(recentPlay)
        print(recentPlay.mods) #TODO: WTF If this shows nm why does the next todo say hd
        self.apiCalls += 1
        print(f"[API] Used ossapi for {self.domain.name.lower()} to fetch best score on recent map "
              f"{self.apiCalls} API calls made")
        return self.api.beatmap_user_score(beatmap_id=recentPlay.beatmap.id,
                                           user_id=recentPlay.user_id,
                                           mods=recentPlay.mods)

    def getBestPlayStats(self):
        bestPlay = self.getBestPlay().score
        bestPlayPP = bestPlay.pp

        print(bestPlay)

        print(bestPlay.mods) # TODO: Mods are not inherited from recentplay

        if bestPlay.pp is None:
            bestPlayPP = 0 # TODO: Add a global method for this

        return bestPlay.accuracy, bestPlay.statistics.count_miss, \
            bestPlayPP, bestPlay.rank, bestPlay.created_at

    @staticmethod
    def getBestAccuracy(plays):
        bestAccuracy, bestAccuracyDate = None, None

        for score in plays:
            # TODO: Verify "best" statistics are as recent as possible
            if score is None:
                break

            if bestAccuracy is None or score.accuracy > bestAccuracy:
                bestAccuracy = score.accuracy
                bestAccuracyDate = score.created_at

                for internalScore in plays:
                    if internalScore.accuracy == bestAccuracy:
                        if convert_to_unix_time(internalScore.created_at) > convert_to_unix_time(bestAccuracyDate):
                            print(f"Replaced matching accuracy {bestAccuracyDate}")
                            bestAccuracyDate = internalScore.created_at

        return bestAccuracy, bestAccuracyDate

    @staticmethod
    def getBestMissCount(plays):
        bestMissCount, bestMissCountDate = None, None

        for score in plays:
            # TODO: Verify "best" statistics are as recent as possible
            if score is None:
                break

            if bestMissCount is None or score.statistics.count_miss < bestMissCount:
                bestMissCount = score.statistics.count_miss
                bestMissCountDate = score.created_at

                for internalScore in plays:
                    if internalScore.statistics.count_miss == bestMissCount:
                        if convert_to_unix_time(internalScore.created_at) > convert_to_unix_time(bestMissCountDate):
                            print(f"Replaced matching miss count {bestMissCountDate}")
                            bestMissCountDate = internalScore.created_at

        return bestMissCount, bestMissCountDate

    @staticmethod
    def getBestPP(plays):
        bestPP, bestPPDate = None, None

        for score in plays:
            # TODO: Verify "best statistics are as recent as possible
            if score is None:
                break

            if score.pp is not None and (bestPP is None or score.pp > bestPP):
                bestPP = score.pp
                bestPPDate = score.created_at

                for internalScore in plays:
                    if internalScore.pp == bestPP:
                        if convert_to_unix_time(internalScore.created_at) > convert_to_unix_time(bestPPDate):
                            print(f"Replaced matching pp {bestPP}")
                            bestPPDate = internalScore.created_at

        if bestPP is None:
            bestPP = 0

        return bestPP, bestPPDate

    @staticmethod
    def getBestGrade(plays):
        bestGrade, bestGradeDate = None, None

        for score in plays:
            # TODO: Verify "best" statistics are as recent as possible
            if score is None:
                break

            if bestGrade is None or gradeValues[score.rank] > gradeValues[bestGrade]:
                bestGrade = score.rank
                bestGradeDate = score.created_at
                print(f"Best grade changed to {bestGrade}")

                for internalScore in plays:
                    if internalScore.rank == bestGrade:
                        if convert_to_unix_time(internalScore.created_at) > convert_to_unix_time(bestGradeDate):
                            print(f"Replaced matching rank {bestGradeDate}")
                            bestGradeDate = internalScore.created_at
                            print(f"With {bestGradeDate}")

        return bestGrade, bestGradeDate

    @staticmethod
    def getAverage(values):
        total = 0
        for value in values:
            if value:
                total += value

        return total / len(values) if len(values) != 0 else 0

    @staticmethod
    def getModeGrade(grades):
        modeGrade = None
        modeGradeCount = 0

        print(f"Comparing {grades}")

        for grade in grades:
            gradeCount = grades.count(grade)

            if gradeCount > modeGradeCount:
                modeGrade = grade
                modeGradeCount = gradeCount

            elif gradeCount == modeGradeCount:
                # Return the higher grade, such as S if there are 6 S's and 6 A's
                if gradeValues[grade] > gradeValues[modeGrade]:
                    return grade

                else:
                    return modeGrade

        return modeGrade


def test(domain):
    
    recentPlay = domain.getRecentPlay()

    if recentPlay is not None:
        print(f"Found recent play on {recentPlay.beatmapset.title} ({recentPlay.beatmap.version})")
        print(f"Found recent play {recentPlay}")
        print(f"{domain.getScores()}")
        print(f"{domain.getInheritedModScores()}")
        print(f"{domain.getInheritedModPlayCount()} plays with recent play mods on recent play map")
        print(f"Recent play created at {convert_to_format(convert_to_unix_time(recentPlay.created_at))}")
        print(f"Recent play mods {recentPlay.mods}")
        print(f"Recent play mods skinned {skinnables.getSkinnedMods(recentPlay.mods.value)}")
        print(f"Recent stats {domain.getRecentPlayStats()}")

        if domain.getInheritedModPlayCount() > 0:
            print(f"Inherited scores {domain.getInheritedModScores()}")
            print(f"Inherited scores {domain.getInheritedModPlayCount()}")
            print(f"Best stats {domain.getBestStats(domain.getInheritedModScores())}")
            print(f"Test best play stats {domain.getBestPlayStats()}")
            print(f"Average stats {domain.getAverageStats(domain.getInheritedModScores())}")

    else:
        print(f"Could not find recent play")


if __name__ == "__main__":
    target = "tomm13"

    lazer = Lazer(domain=Domain.LAZER)
    lazer.createAPI(target=target)
    test(domain=lazer)

    stable = Lazer(domain=Domain.OSU)
    stable.createAPI(target=target)
    test(domain=stable)

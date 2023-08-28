import discord
import skinnables
import traceback
from timeconversion import convert_to_unix_time, convert_to_format
from discord.ext import commands
from ossapi import Domain, enums

import lazer as lz

color = discord.Color.from_rgb(195, 167, 151)
bot = commands.Bot(command_prefix="lz", intents=discord.Intents.all())

scoreLink = {Domain.LAZER: "https://lazer.ppy.sh/scores/",
             Domain.OSU: "https://osu.ppy.sh/scores/"}

mapLink = {Domain.LAZER: "https://lazer.ppy.sh/beatmapsets/",
           Domain.OSU: "https://osu.ppy.sh//beatmapsets/"}


# TODO: Generate png for discord


class MessageEmbed:
    @staticmethod
    def requestReceived(target):
        return discord.Embed(
            title=f"Generating results for {target}",
            description="For both osu and lazer",
            color=color)

    @staticmethod
    def hasNoRecentPlays(target):
        return discord.Embed(
            title=f"{target} has no recent plays in the last day",
            description=f"For both osu and lazer",
            color=color)

    @staticmethod
    def hasNoRecentPlaysWithModsOnMap(target, map, mods):
        return discord.Embed(
            title=f"{target} has no plays on {map} with {mods}",
            description=f"For both osu and lazer",
            color=color)

    @staticmethod
    def warningEmbed():
        return discord.Embed(
            title="The lazer score submission system is WIP",
            description="Known issue: Displayed PP value is ~20% lower than actual",
            color=color)

    # TODO: Recent play embed


@bot.event
async def on_ready():
    print(">>> Restarted Bot Successfully")


@bot.command()
async def rp(ctx, target):
    try:
        # TODO: Add target user parameter
        # target = ctx.author
        await ctx.send(embed=MessageEmbed.requestReceived(target=target))

        lazer = lz.Lazer(domain=Domain.LAZER)
        stable = lz.Lazer(domain=Domain.OSU)

        lazer.createAPI(target=target)
        stable.createAPI(target=target)

        lazerRecentPlay = lazer.getRecentPlay()
        stableRecentPlay = stable.getRecentPlay()

        lazerInheritedModPlayCount = lazer.getInheritedModPlayCount()
        stableInheritedModPlayCount = stable.getInheritedModPlayCount()

        # TODO: Fix embed generation logic

        if lazerRecentPlay is None and stableRecentPlay is None:
            # No further stats or information can be displayed, and the function ends
            # Generate no recent plays on both domains embed
            await ctx.send(embed=MessageEmbed.hasNoRecentPlays(target=target))

        else:
            # There is a recent play and an inherited play
            # Decide which domain to prefer, based on which domain's recent play is more recent

            if convert_to_unix_time(lazerRecentPlay.created_at) >= convert_to_unix_time(stableRecentPlay.created_at):
                # Lazer has a more recent play
                recentPlay = lazerRecentPlay
                recentPlayDomain = Domain.LAZER

                recentPlayAccuracy, recentPlayMissCount, recentPlayPP, \
                    recentPlayGrade, recentPlayDate = lazer.getRecentPlayStats()

                bestPlayAccuracy, bestPlayMissCount, bestPlayPP, \
                    bestPlayGrade, bestPlayDate = lazer.getBestPlayStats()

                bestAccuracy, bestAccuracyDate, \
                    bestMissCount, bestMissCountDate, \
                    bestPP, bestPPDate, \
                    bestGrade, bestGradeDate = lazer.getBestStats(plays=lazer.getInheritedModScores())

                averageAccuracy, averageMissCount, \
                    averagePP, averageGrade = lazer.getAverageStats(plays=lazer.getInheritedModScores())

                inheritedModPlayCount = lazerInheritedModPlayCount

            else:
                # Stable has a more recent play
                recentPlay = stableRecentPlay
                recentPlayDomain = Domain.OSU

                recentPlayAccuracy, recentPlayMissCount, recentPlayPP, \
                    recentPlayGrade, recentPlayDate = stable.getRecentPlayStats()

                bestPlayAccuracy, bestPlayMissCount, bestPlayPP, \
                    bestPlayGrade, bestPlayDate = stable.getBestPlayStats()

                bestAccuracy, bestAccuracyDate, \
                    bestMissCount, bestMissCountDate, \
                    bestPP, bestPPDate, \
                    bestGrade, bestGradeDate = stable.getBestStats(plays=stable.getInheritedModScores())

                averageAccuracy, averageMissCount, \
                    averagePP, averageGrade = stable.getAverageStats(plays=stable.getInheritedModScores())

                inheritedModPlayCount = stableInheritedModPlayCount

            print(f"Prefer {recentPlayDomain} as {lazerRecentPlay.created_at} vs {stableRecentPlay.created_at}")

            # Generate warning embed for lazer
            if recentPlayDomain == Domain.LAZER:
                await ctx.send(embed=MessageEmbed.warningEmbed())

            # Generate score link except for fails on stable, in which case generate map link
            if recentPlayDomain == Domain.OSU and recentPlayGrade == enums.Grade.F:
                # Create recent play embed with map link
                playLink = mapLink[
                               recentPlayDomain] + f"{recentPlay.beatmap.beatmapset_id}#{recentPlay.beatmap.mode.name.lower()}/{recentPlay.beatmap.id}"

            else:
                # Create recent play embed with score link
                playLink = scoreLink[recentPlayDomain] + str(recentPlay.id)

            embed = discord.Embed(
                title=f"{target}'s recent play on {recentPlay.beatmapset.title} ({recentPlay.beatmap.version}) by "
                      f"{recentPlay.beatmapset.creator}",
                description="",
                color=color,
                url=playLink)

            embed.set_thumbnail(url=f"{recentPlay.beatmapset.covers.card_2x}")

            embed.set_footer(text=f"Statistics generated from {recentPlayDomain.name.lower()}")

            #if [recentPlayAccuracy, recentPlayMissCount, recentPlayPP, recentPlayGrade, recentPlayDate] == \
            #        [bestPlayAccuracy, bestPlayMissCount, bestPlayPP, bestPlayGrade, bestPlayDate]:
                # Recent play is best play
            #    fieldTitle = "This play (best play on this map!)"
            #    generateBestPlay = False
            #    generateBestPlayStats = True

            #    if [bestPlayAccuracy, bestPlayMissCount, bestPlayPP, bestPlayGrade] == \
            #            [bestAccuracy, bestMissCount, bestPP, bestGrade] and \
            #            bestAccuracyDate == bestPlayDate and \
            #            bestMissCountDate == bestPlayDate and \
            #            bestPPDate == bestPlayDate and \
            #            bestGradeDate == bestPlayDate:
            #        # If best play and best play stats are the same

            #        fieldTitle = "This play (best play + best stats on this map!)"
            #        generateBestPlayStats = False

            #        print(">>> best play and best stats are the same")

            #else:
            #    fieldTitle = "This play"
            #    generateBestPlay = True
            #    generateBestPlayStats = True

            # TODO: Fix above code which is meant to prevent duplicate info from being shown
            # TODO: below is a temporary fix to remove

            fieldTitle = "This play"
            generateBestPlay = True
            generateBestPlayStats = True

            # Mods
            mods = skinnables.getSkinnedMods(recentPlay.mods.value)
            if mods is not None and mods != "NM":
                embed.add_field(name=f"{skinnables.Snow} Mods", value=f"{mods}", inline=False)

            # Recent play
            embed.add_field(name=f"{skinnables.Snow} {fieldTitle}" + f" {convert_to_format(convert_to_unix_time(recentPlayDate))}",
                            value="",
                            inline=False)

            embed.add_field(
                name=f"{skinnables.getSkinnedGrade(recentPlayGrade)}",
                value="",
                inline=True)

            embed.add_field(
                name=skinnables.getSkinnedString(f"{'{:.2f}'.format(round(recentPlayPP))}pp"),
                value="",
                inline=True)

            embed.add_field(
                name=skinnables.getSkinnedString(f"{'{:.2f}'.format(round(recentPlayAccuracy * 100, 2))}%"),
                value="",
                inline=True)

            embed.add_field(
                name=skinnables.getSkinnedString(f"{recentPlayMissCount}x"),
                value="",
                inline=True)

            if inheritedModPlayCount > 0 and generateBestPlay is True:
                # Best play
                embed.add_field(name=f"{skinnables.Snow} Best play" + f" {convert_to_format(convert_to_unix_time(bestPlayDate))}",
                                value="",
                                inline=False)

                embed.add_field(
                    name=skinnables.getSkinnedGrade(bestPlayGrade),
                    value="",
                    inline=True)

                embed.add_field(
                    name=skinnables.getSkinnedString(f"{'{:.2f}'.format(round(bestPlayPP))}pp"),
                    value="",
                    inline=True)

                embed.add_field(
                    name=skinnables.getSkinnedString(f"{'{:.2f}'.format(round(bestPlayAccuracy * 100, 2))}%"),
                    value="",
                    inline=True)

                embed.add_field(
                    name=skinnables.getSkinnedString(f"{bestPlayMissCount}x"),
                    value="",
                    inline=True)

            # Add best and average stats to embed, if available
            # TODO: Test following line
            if all(i is not None for i in [bestAccuracy, bestAccuracyDate,
                                           bestMissCount, bestMissCountDate,
                                           bestPP, bestPPDate,
                                           bestGrade, bestGradeDate]) and generateBestPlayStats is True:
                # Best stats are available and need to be added to recent play embed
                # TODO: Verify stats are based on inherited plays
                embed.add_field(name=f"{skinnables.Snow} Best statistics from all plays", value="", inline=False)

                embed.add_field(
                    name=skinnables.getSkinnedGrade(bestGrade) + f" {convert_to_format(convert_to_unix_time(bestGradeDate))}",
                    value="",
                    inline=True)

                embed.add_field(
                    name=skinnables.getSkinnedString(f"{'{:.2f}'.format(round(bestPP))}pp") + f" {convert_to_format(convert_to_unix_time(bestPPDate))}",
                    value="",
                    inline=True)

                embed.add_field(
                    name=skinnables.getSkinnedString(f"{'{:.2f}'.format(round(bestAccuracy * 100, 2))}%") + f" {convert_to_format(convert_to_unix_time(bestAccuracyDate))}",
                    value="",
                    inline=True)

                embed.add_field(
                    name=skinnables.getSkinnedString(f"{bestMissCount}x") + f" {convert_to_format(convert_to_unix_time(bestMissCountDate))}",
                    value="",
                    inline=True)

            if [averageAccuracy, averageMissCount,
                averagePP, averageGrade] != [None for _ in range(4)] and inheritedModPlayCount > 1:
                # Average stats are available and need to be added to recent play embed
                # TODO: Verify stats are based on inherited plays
                embed.add_field(name=f"{skinnables.Snow} On average (from {inheritedModPlayCount} plays)", value="",
                                inline=False)

                embed.add_field(
                    name=f"{skinnables.getSkinnedGrade(averageGrade)}",
                    value="",
                    inline=True)

                embed.add_field(
                    name=skinnables.getSkinnedString(f"{'{:.2f}'.format(round(averagePP))}pp"),
                    value="",
                    inline=True)

                embed.add_field(
                    name=skinnables.getSkinnedString(f"{'{:.2f}'.format(round(averageAccuracy * 100, 2))}%"),
                    value="",
                    inline=True)

                embed.add_field(
                    name=skinnables.getSkinnedString(f"{averageMissCount}x"),
                    value="",
                    inline=True)

            await ctx.send(embed=embed)

    except Exception:
        await ctx.send(embed=discord.Embed(
            title=f"An error occured",
            description=f"{traceback.format_exc()}",
            color=discord.Color.red()))


bot.run("MTEzMzA5NTI5MTg2ODkzODM2MQ.GppHFG.ODJ00Tx1zHoUed_G8uGj-KE-4V69qM2-8xnZV8")

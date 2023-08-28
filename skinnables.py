from ossapi import Mod, mod

numbers = ["<:combo02x:1133456585197371462>",
           "<:combo12x:1133456588011733094>",
           "<:combo22x:1133456593321730048>",
           "<:combo32x:1133456598380064889>",
           "<:combo42x:1133456602138165336>",
           "<:combo52x:1133456606101782698>",
           "<:combo62x:1133456610212188160>",
           "<:combo72x:1133456613173379235>",
           "<:combo82x:1133456618030387201>",
           "<:combo92x:1133456621801050234>"]

percent = "<:scorepercent2x:1133461733814579310>"
cross = "<:combox2x:1133461518751629403>"
dot = "<:scoredot2x:1133461849975836764>"
star = "<:star2x:1133470560517632121>"

gradeA = "<:rankingAsmall2x:1133491765752631336>"
gradeB = "<:rankingBsmall2x:1133491767984005220>"
gradeC = "<:rankingCsmall2x:1133491772958453811>"
gradeD = "<:rankingDsmall2x:1133491777073066095>"
gradeS = "<:rankingSsmall2x:1133491781569351731>"
gradeSH = "<:rankingSHsmall2x:1133491786086613132>"
gradeX = "<:rankingXsmall2x:1133491792550039593>"
gradeXH = "<:rankingXHsmall2x:1133491795016306880>"

# TODO MODS

HR = "<:selectionmodhardrock2x:1133844145769824347>"
DT = "<:selectionmoddoubletime2x:1133844206612385884>"
HD = "<:selectionmodhidden2x:1133844253244653608>"
NC = "<:selectionmodnightcore2x:1133844290204876802>"
Relax = "<:selectionmodrelax2x:1134192869624791101>"
Autopilot = "<:selectionmodrelax22x:1134192873194135633>"

Snow = "<:menusnow:1134359871131750400>"


def getSkinnedString(string):
    return string

    newchars = ""

    for char in str(string):
        if char.isdigit():
            newchars += numbers[int(char)]

        elif char == "x":
            newchars += cross

        elif char == ".":
            newchars += dot

        elif char == "%":
            newchars += percent

        else:
            newchars += char

    return newchars


def getSkinnedGrade(grade):
    # TODO: use enums
    if str(grade) == "Grade.A":
        return gradeA

    elif str(grade) == "Grade.B":
        return gradeB

    elif str(grade) == "Grade.C":
        return gradeC

    elif str(grade) == "Grade.D" or str(grade) == "Grade.F":
        return gradeD

    elif str(grade) == "Grade.S":
        return gradeS

    elif str(grade) == "Grade.SH":
        return gradeSH

    elif str(grade) == "Grade.X":
        return gradeX

    elif str(grade) == "Grade.SSH":
        return gradeXH


def getSkinnedMods(mods):
    # TODO: mods=ModCombination(value=24)
    if mods == Mod.HD.value:
        return HD

    elif mods == Mod.HR.value:
        return HR

    elif mods == Mod.DT.value:
        return DT

    elif mods == Mod.NC.value:
        return NC

    elif mods == Mod.Relax.value:
        return Relax

    elif mods == Mod.Autopilot.value:
        return Autopilot

    elif mods == Mod.HDDT.value:
        return HD + DT

    elif mods == Mod.HDHR.value:
        return HD + HR

    elif mods == Mod.HDDT.value:
        return HR + DT

    elif mods == Mod.HDDTHR.value:
        return HD + DT + HR

    else:
        try:
            return mod.int_to_mod[mods][0]

        except KeyError:
            return

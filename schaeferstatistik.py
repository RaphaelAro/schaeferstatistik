from bs4 import BeautifulSoup
import requests
import re

MYTISCHTENNIS_URI = "https://www.mytischtennis.de"

def readTableDataLink(link):
    request = requests.get(link)
    if request.status_code != 200:
        return None

    data = request.content
    soup = BeautifulSoup(data, 'html.parser')
    table = soup.find('table')

    tableData = []
    row = 0
    for tr in table.findAll("tr"):
        trs = tr.findAll("td")
        column = 0
        rowData = []
        for e in trs:
            text = e.text.replace('\n', '')
            link = None
            try:
                link = e.find('a')['href']
                # Some links seem to be internal.
                if link[:5] != 'https':
                    link = MYTISCHTENNIS_URI + link
            except:
                pass
            rowData.append((text, link))
            column += 1
        if len(rowData) > 0:
            tableData.append(rowData)
        row += 1
    return tableData


setPattern = re.compile(r'(\d+):(\d+)')
def parseSets(listSets):
    parsedList = []
    for s in listSets:
        parsed = setPattern.match(s)
        if parsed is not None:
            parsedList.append((int(parsed.group(1)), int(parsed.group(2))))
        else:
            parsedList.append(None)

    return parsedList




mannschaften = readTableDataLink("https://www.mytischtennis.de/clicktt/TTBW/22-23/verein/21015/TTC-GW-Konstanz/mannschaften/")

schaeferPositiv = []
schaeferNegativ = []

for m in mannschaften:
    mannschaft, begegnungenLink = m[0]
    begegnungen = readTableDataLink(begegnungenLink)
    print('\n________ Mannschaft: %s ________' % mannschaft)
    for b in begegnungen:
        heim = b[3][0]
        gast = b[4][0]
        weAreLeftSide = True
        if "TTC GW Konstanz" in gast:
            weAreLeftSide = False

        ergebnisBegegnung, link = b[7]
        if link is not None:
            spiele = readTableDataLink(link)
            print("Begegnung %s - %s - %s" % (heim, gast, ergebnisBegegnung))
            for s in spiele:
                if len(s) < 10:
                    continue
                name1 = s[2][0]
                name2 = s[4][0]
                sets = [s[5][0], s[6][0], s[7][0], s[8][0], s[9][0]]
                sets = parseSets(sets)
                for set in sets:
                    if set is None or "nicht anwesend" in name1 or "nicht anwesend" in name2:
                        break
                    if set[0] == 11 and set[1] == 0:
                        schaeferDoku = [heim, gast, name1, name2, link]
                        print(schaeferDoku)
                        if weAreLeftSide:
                            schaeferPositiv.append(schaeferDoku)
                        else:
                            schaeferNegativ.append(schaeferDoku)
                    if set[0] == 0 and set[1] == 11:
                        schaeferDoku = [heim, gast, name1, name2, link]
                        print(schaeferDoku)
                        if weAreLeftSide:
                            schaeferNegativ.append(schaeferDoku)
                        else:
                            schaeferPositiv.append(schaeferDoku)

print("\n\n ____ ERGEBNISSE ____")
print("Für uns:")
print(schaeferPositiv)
print("\nGegen uns:")
print(schaeferNegativ)
print("\n\nEndergebnis:")
print(len(schaeferPositiv), ':', len(schaeferNegativ))







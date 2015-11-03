# Uses one and optionally two command-line arguments
# The first is the series name
# Optionally the second is the episode name
# Prints to console

from mind import getMind
import config
import sys

config.init([])
config.init_logging()

tsn = '8490001XXXXXXXXX'  # Insert your TSN
mmind = getMind(tsn)

lang = "English"
title = sys.argv[1]
if len(sys.argv) > 2:
    subtitle = sys.argv[2]
else:
    subtitle = ''
offset = 0
bottom = False
result = []
while bottom is False:
    if subtitle:
        data = {
            'bodyId': 'tsn:' + tsn,
            'type': 'contentSearch',
            'title': title,
            "descriptionLanguage": "English",
            "subtitle": subtitle,
            "offset": str(offset),
            'orderBy': 'partnerContentId',
            'count': '50',
            'levelOfDetail': 'medium'
        }
    else:
         data = {
            'bodyId': 'tsn:' + tsn,
            'type': 'contentSearch',
            'title': title,
            # 'collectionType': 'series',
            "descriptionLanguage": lang,
            "offset": str(offset),
            'orderBy': 'partnerContentId',
            'count': '50',
            'levelOfDetail': 'medium'
        }
    sr = mmind._Mind__dict_request(data, 'contentSearch&bodyId=tsn:' + tsn)  # Access private member
    cL = sr.findall('content')
    for content in cL:
        try:
            en = content.find('episodeNum').text
            if len(en)<2:
                en = '0%s' % en
            sn = content.find('seasonNumber').text
            if len(sn)<2:
                sn = '0%s' % sn
            se = 'S%sE%s' % (sn, en)
            st = content.find('subtitle').text
            ti = content.find('title').text
            seriesID = content.find('partnerCollectionId').text
            seriesID = seriesID[seriesID.find('SH'):]
            programID = content.find('partnerContentId').text
            programID = programID[programID.find('EP'):]
            oad = content.find('originalAirdate').text
            result.append((ti, st, se, oad, seriesID, programID))
        except:
            pass
    if sr.find('isBottom').text == 'true':
        bottom = True
    else:
        offset += 50
sortresult = sorted(result, key=lambda sn: sn[2])
for i in sortresult:
    print '%s - %s (%s) %s :: seriesId: %s programId: %s' % i

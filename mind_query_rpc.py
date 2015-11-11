#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#     Copyright (C) 2015 KenV99
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#

import rpcSearch102

class RemoteExt(rpcSearch102.Remote):

    def __init__(self, username, password, tsn=''):
        self.un = username
        self.pw = password
        self.tsn = tsn
        super(RemoteExt, self).__init__(username, password)


    def Auth(self):
        self.Write(rpcSearch102.RpcRequest('bodyAuthenticate',
                                           credential={
                                               'type': 'mmaCredential',
                                               'username': self.un,
                                               'password': self.pw,
                                           }
                                           ))
        result = self.Read()
        if result['status'] != 'success':
            rpcSearch102.logging.error('Authentication failed!  Got: %s', result)
            rpcSearch102.sys.exit(1)

    def WriteReadX(self, rtype, **kwargs):
        offsetx = 0
        isBottom = False
        results = []
        resultD = {'contentSearch':'content', 'offerSearch':'offer', 'collectionSearch':'collection'}
        while isBottom is False:
            try:
                req = rpcSearch102.RpcRequest(rtype, offset=offsetx, count=50, **kwargs)
                self.Write(req)
                result = self.Read()
            except Exception as e:
                pass
            if 'type' in result.keys():
                if result['type'] == u'error':
                    print result['text']
                    return [{'error' : result['text']}]
            returntype = resultD[rtype]
            if returntype in result.keys():
                for resultDict in result[returntype]:
                    if 'subtitle' in resultDict.keys():
                        if ';' not in resultDict['subtitle']:
                            results.append(resultDict)
                    else:
                        results.append(resultDict)
            if result['isBottom'] is True:
                isBottom = True
            else:
                offsetx = offsetx + 50
        return results

    def genericSearch(self, searchType, **kwargs):
        if searchType == 'offerSearch':
            results = self.WriteReadX(searchType, bodyId='tsn:'+self.tsn, **kwargs)
        else:
            results = self.WriteReadX(searchType, orderBy='strippedTitle', **kwargs)
        if 'error' in results[0].keys():
            return results
        for result in results:
            try:
                en = str(result['episodeNum'][0])
                if len(en)<2:
                    en = '0%s' % en
                sn = str(result['seasonNumber'])
                if len(sn)<2:
                    sn = '0%s' % sn
                se = 'S%sE%s' % (sn, en)
            except:
                se = ''
            if 'partnerCollectionId' in result.keys():
                if 'collectionType' in result.keys():
                    if result['collectionType'] == 'series' or result['collectionType'] == 'special':
                        seriesID = result['partnerCollectionId']
                        result['partnerCollectionId'] = seriesID[seriesID.find('SH'):]
                    elif result['collectionType'] == 'movie':
                        seriesID = result['partnerCollectionId']
                        if seriesID.find('MV') != -1:
                            result['partnerCollectionId'] = seriesID[seriesID.find('MV'):]
                else:
                    result['partnerCollectionId'] = ''
            else:
                result['partnerCollectionId'] = ''
            if 'partnerContentId' in result.keys():
                if 'collectionType' in result.keys():
                    if result['collectionType'] == 'series' or result['collectionType'] == 'special':
                        programID = result['partnerContentId']
                        result['partnerContentId'] = programID[programID.find('EP'):]
                    elif result['collectionType'] == 'movie':
                        programID = result['partnerContentId']
                        if programID.find('MV') != -1:
                            result['partnerContentId'] = programID[programID.find('MV'):]
                else:
                    result['partnerContentId'] = ''
            else:
                result['partnerContentId'] = ''
            if 'collectionType' in result.keys():
                if result['collectionType'] == 'series':
                    if 'isEpisode' in result.keys():
                        if result['isEpisode'] is True:
                            result['collectionType'] = 'episode'
                elif result['collectionType'] == 'movie':
                    if 'movieYear' in result.keys():
                        if 'orignalAirdate' not in result.keys():
                            result['originalAirdate'] = str(result['movieYear'])
            else:
                pass
            if 'originalAirdate' not in result.keys():
                result['originalAirdate'] = ''
            result['seasonEpisodeNum'] = se
        try:
            sresults = sorted(results, key=lambda sx: sx['originalAirdate'])
        except:
            sresults = results
        return sresults


def printToConsole(results, *args):
    print 'Count = %s' % len(results)
    for result in results:
        out = []
        for arg in args:
            try:
                x = result[arg]
            except:
                x = ' '
            if isinstance(x, list):
                x = x[0]
            out.append(str(x))
        print ' | '.join(out)



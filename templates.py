#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#     Copyright (C) 2014 KenV99
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

contentTemplate = {"responseTemplate":[
    {
        "type":"responseTemplate",
        "fieldName": ["content", "isBottom"],
        "typeName": "contentList"
    },
    {
        "type": "responseTemplate",
        "fieldName":[
            "collectionType",
            "collectionId",
            "contentId",
            "partnerCollectionId",
            "partnerContentId",
            "seasonNumber",
            "episodeNum",
            "isEpisode",
            "title",
            "subtitle",
            "description",
            "originalAirdate",
            "movieYear"
        ],
        "typeName":"content"
    }
]}

offerTemplate = {"responseTemplate":[
    {
        "type":"responseTemplate",
        "fieldName": ["offer", "isBottom"],
        "typeName": "offerList"
    },
    {
        "type": "responseTemplate",
        "fieldName":[
            "collectionType",
            "collectionId",
            "contentId",
            "partnerCollectionId",
            "partnerContentId",
            "seasonNumber",
            "episodeNum",
            "isEpisode",
            "title",
            "subtitle",
            "description",
            "originalAirdate",
            # "movieYear"
            # "channel",
            "startTime"
        ],
        "fieldInfo": [
            {
                "type": "responseTemplateFieldInfo",
                "fieldName":"channel",
                "maxArity": 1
            }
        ],
        "typeName":"offer"
    },
    {
        "type": "responseTemplate",
        "fieldName": ["callSign"],
        "typeName": "channel"
    }
]}
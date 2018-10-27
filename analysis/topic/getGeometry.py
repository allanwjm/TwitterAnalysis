import json

f1 = open("data_sydney.json", "r")
#f2 = open("data5960259180870908140.json", "r")
o = open("sydney.geojson", "w")
test1 = json.load(f1)
#test2 = json.load(f2)
#trueList = []
#for item in test2["features"]:
#    trueList.append(item["properties"]["sa2_main16"])
#codeList = []
newJson = {"type":"FeatureCollection", "features":[]}
for item in test1["features"]:
#    if item["properties"]["sa2_maincode_2016"] not in codeList and item["properties"]["sa2_maincode_2016"] in trueList:
#        print item["properties"]["sa2_maincode_2016"], item["properties"]["sa2_name_2016"]
#        codeList.append(item["properties"]["sa2_maincode_2016"])
#        print item["geometry"]
    newJson["features"].append({"type":"Feature", "geometry":item["geometry"], "properties":{"sa2_name_2016": item["properties"]["sa2_name_2016"], "sa2_maincode_2016": item["properties"]["sa2_maincode_2016"], "sa1_maincode_2016": item["properties"]["sa1_maincode_2016"], "dwelling": item["properties"]["dwelling"], "person": item["properties"]["person"]}})
#print newJson
json.dump(newJson, o)
print 'done'

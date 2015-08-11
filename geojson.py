import json
import scipy.stats
from math import sin, cos, sqrt, atan2, radians


"""
Runs all functions and starts from a new file
"""
def runAll():
	firstBlockJson()
	addMinLocations()
	addData2()

"""
Loads a geojson file
"""
def loadJson(filename):
	json_data = open('static/data/'+filename)
	data = json.load(json_data)
	json_data.close()
	return data

"""
Function creates the json file and populates with asthma rate data
Asthma Rate
Numbers roughly range from 1-16
Assumed to be population with asthma, numbers match up to data at http://www.californiabreathing.org/asthma-data/county-asthma-profiles/san-francisco-county-asthma-profile
Normalized curve and then inverted percentile
Summary: Lower asthma rate => higher percentile
"""
def firstBlockJson():
	data = loadJson('AsthmaRates_CB00.json')
	features = data['features']
	blockMap = []
	for each in features:
		blockMap.append(each['properties'])

	jsonArray = []
	values = []
	for each in blockMap:
		dataDict = {}
		jsonDict = {}
		keys = each.keys()
		format = None
		for key in keys:
			if key != 'BLOCKGROUP':
				values.append(each[key])

	jsonDict = {}
	format = None
	returnDict = {}
	for each in blockMap:
		keys = each.keys()
		for key in keys:
			format = key
			if key != 'BLOCKGROUP':
				jsonDict[each['BLOCKGROUP']] = [1-scipy.stats.percentileofscore(values,each[key])/100.0]
	returnDict['data'] = jsonDict
	returnDict['format'] = [format]
	with open('static/data/SF.json', 'w') as outfile:
		json.dump(returnDict, outfile)

"""
SF Rent Affordability given by the estimated median income necessary to live in the neighborhood
Formula to obtain the estimated median income unknown, provided by data.sfgov.org
Because the goal is to help find affordable housing, we catered towards low income individuals
Therefore we inverted the percentile scores
Summary: Low median income necessary => High Score
"""
def SFRentAffordability():
	data = loadJson('SanFranciscoRentAffordability.json')
	features = data['features']
	featureMap = []
	values = []
	for each in features:
		featureDict = {}
		if each['geometry']['type'] == 'Polygon':
			featureDict['polygon'] = each['geometry']['coordinates'][0]
			income = each['properties']['MedInc_d']
			if income == None:
				income = "60000"
				featureDict['income'] = float(income.replace(',',''))
			else:
				featureDict['income'] = float(income.replace(',',''))
			values.append(float(income.replace(',','')))
			featureMap.append(featureDict)
		else:
			polygons = each['geometry']['coordinates'][0]
			for polygon in polygons:
				featureDict['polygon'] = polygon
				income = each['properties']['MedInc_d']
				if income == None:
					income = "60000"
					featureDict['income'] = float(income.replace(',',''))
				else:
					featureDict['income'] = float(income.replace(',',''))
				values.append(float(income.replace(',','')))
				featureMap.append(featureDict)
			values.append(float(income.replace(',','')))
	for each in featureMap:
		income = each['income']
		each['income'] = 1-scipy.stats.percentileofscore(values,income)/100.0
	jsonData = parseBlocks(loadJson('AsthmaRates_CB00.json'))

	for block in jsonData:
		coord = block['center']
		for each in featureMap:
			if point_in_poly(coord[0], coord[1], each['polygon'])=="IN":
				# print "In!"
				block['income'] = each['income']
				break
		if 'income' not in block.keys():
			block['income'] = 0.5
	return jsonData

"""
Air quality determined by MaxPM2.5
Information on PM2.5 found at http://www.epa.gov/pmdesignations/faq.htm#0
Numbers range from 1-7
Normalized curve and inverted curve so that lower PM2.5 was a higher score
Summary: Lower PM2.5 => Higher score
Note: We normalized to provide relative data, but all of SF has great air quality
"""
def AirQuality():
	data = loadJson('AirQuality_CB00.json')
	features = data['features']
	featureMap = {}
	valueArray = []
	for each in features:
		properties = each['properties']
		featureMap[properties['BLOCKGROUP']] = properties['MAXPM25']
		valueArray.append(properties['MAXPM25'])

	for key in featureMap:
		value = featureMap[key]
		featureMap[key] = 1-scipy.stats.percentileofscore(valueArray,value)/100.0

	return featureMap

"""
Population density as population by square mile
Numbers vary from a 1000s to 100000s
Impact of high density on page 33: http://hiaconnect.edu.au/wp-content/uploads/2013/04/housing_density_HIA_review1.pdf
Although study in New Zealand, a generalization is that high density is bad
Normalized curve and inverted
Summary: Lower density => Higher Score
"""
def PopulationDensity():
	data = loadJson('PopulationDensity_CB00.json')
	features = data['features']
	featureMap = {}
	valueArray = []
	for each in features:
		properties = each['properties']
		featureMap[properties['BLOCKGROUP']] = properties['Pop_psmi']
		valueArray.append(properties['Pop_psmi'])

	for key in featureMap:
		value = featureMap[key]
		featureMap[key] = 1-scipy.stats.percentileofscore(valueArray,value)/100.0

	return featureMap

"""
Poverty as poverty percent taken to mean the percent of population below the poverty line
Percentages vary from 0-100, most range from 1-40 percent roughly
Normalized curve accounts for outliers of cases where the percent is 100
Inverted the percentiles
Summary: Lower poverty => Higher score
"""
def Poverty():
	data = loadJson('Poverty_CB00.json')
	features = data['features']
	featureMap = {}
	valueArray = []
	for each in features:
		properties = each['properties']
		featureMap[properties['BLOCKGROUP']] = properties['Pover_pct']
		valueArray.append(properties['Pover_pct'])

	for key in featureMap:
		value = featureMap[key]
		featureMap[key] = 1-scipy.stats.percentileofscore(valueArray,value)/100.0

	return featureMap

"""
Formula from: http://geospatialpython.com/2011/08/point-in-polygon-2-on-line.html
"""
def point_in_poly(x,y,poly):

   # check if point is a vertex
   if (x,y) in poly: return "IN"

   # check if point is on a boundary
   for i in range(len(poly)):
      p1 = None
      p2 = None
      if i==0:
         p1 = poly[0]
         p2 = poly[1]
      else:
         p1 = poly[i-1]
         p2 = poly[i]
      if p1[1] == p2[1] and p1[1] == y and x > min(p1[0], p2[0]) and x < max(p1[0], p2[0]):
         return "IN"

   n = len(poly)
   inside = False
   p1x,p1y = poly[0]
   for i in range(n+1):
      p2x,p2y = poly[i % n]
      if y > min(p1y,p2y):
         if y <= max(p1y,p2y):
            if x <= max(p1x,p2x):
               if p1y != p2y:
                  xints = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
               if p1x == p2x or x <= xints:
                  inside = not inside
      p1x,p1y = p2x,p2y

   if inside: return "IN"
   else: return "OUT"

"""
Maps each blockid to its centroid
"""
def parseBlocks(json):
	features = json['features']
	blocksArray = []
	for each in features:
		blocksDict = {}
		blocksDict['blockid'] = each['properties']['BLOCKGROUP']
		blocksDict['center'] = polygonCentroid(each['geometry']['coordinates'][0])
		blocksArray.append(blocksDict)
	return blocksArray

"""
Adds poverty, popdensity, airquality, affordability
"""
def addData2():
	currJson = loadJson('SF.json')
	poverty = Poverty()
	popDensity = PopulationDensity()
	airQuality = AirQuality()
	affordability = SFRentAffordability()
	affordabilityMap = {}
	for block in affordability:
		if 'income' in block.keys():
			affordabilityMap[block['blockid']] = block['income']
		# Couple block ids are missing income for some odd reason
		else:
			affordabilityMap[block['blockid']] = 0.5
	blockData = currJson['data']
	for key in blockData:
		blockData[key].append(poverty[key])
		blockData[key].append(popDensity[key])
		blockData[key].append(airQuality[key])
		blockData[key].append(affordabilityMap[key])
	currJson['format'].append('POVERTY')
	currJson['format'].append('POPDENSITY')
	currJson['format'].append('AIRQUALITY')
	currJson['format'].append('AFFORDABILITY')
	with open('static/data/SF.json', 'w') as outfile:
		json.dump(currJson, outfile)

"""
Adds closest healthfacility, closest garden and closest market
"""
def addMinLocations():
	facilities = SFHealthFacilities()
	gardens = SFGardens()
	markets = SFFarmersMarkets()
	currJson = loadJson('SF.json')
	facilityMap = {}
	for block in facilities:
		facilityMap[block['blockid']] = block['closest']
	gardenMap = {}
	for block in gardens:
		gardenMap[block['blockid']] = block['closest']
	marketMap = {}
	for block in markets:
		marketMap[block['blockid']] = block['closest']
	blockData = currJson['data']
	for key in blockData:
		blockData[key].append(facilityMap[key])
		blockData[key].append(gardenMap[key])
		blockData[key].append(marketMap[key])
	currJson['format'].append('HEALTHFACILITY')
	currJson['format'].append('GARDEN')
	currJson['format'].append('FARMERSMARKET')
	with open('static/data/SF.json', 'w') as outfile:
		json.dump(currJson, outfile)

"""
List of SF Health Facilities as given by data.sfgov.org
For each block we calculated a centroid of the polygon
Found the minimum distance, aka the closest health facility
Created a standard curve of each block's closest health facility and ranked each block as a percentile
The closer the nearest health facility the better
Inverted the percentile score
Summary: Close distance => High Score
"""
def SFHealthFacilities():
	jsonData = parseBlocks(loadJson('AsthmaRates_CB00.json'))
	healthFacilities = loadJson('SanFranciscoHealthFacilities.json')
	features = healthFacilities['features']
	healthCoords = []
	for each in features:
		healthCoords.append(each['geometry']['coordinates'])

	for block in jsonData:
		distanceArray = []
		coord = block['center']
		for each in healthCoords:
			distanceArray.append(distanceBetweenPoints(coord, each))
		block['closestHospital'] = min(distanceArray)

	distanceArray = []
	for block in jsonData:
		distanceArray.append(block['closestHospital'])

	for block in jsonData:
		block['closest'] = 1-scipy.stats.percentileofscore(distanceArray,block['closestHospital'])/100.0

	return jsonData

"""
List of SF Community Gardens as given by data.sfgov.org
Same methodology as health facilities
Summary: Close distance => High Score
"""
def SFGardens():
	jsonData = parseBlocks(loadJson('AsthmaRates_CB00.json'))
	gardens = loadJson('SanFranciscoCommunityGardens.json')
	features = gardens['features']
	gardenCoords = []
	for each in features:
		gardenCoords.append(each['geometry']['coordinates'])

	for block in jsonData:
		distanceArray = []
		coord = block['center']
		for each in gardenCoords:
			distanceArray.append(distanceBetweenPoints(coord, each))
		block['closestGarden'] = min(distanceArray)

	distanceArray = []
	for block in jsonData:
		distanceArray.append(block['closestGarden'])

	for block in jsonData:
		block['closest'] = 1-scipy.stats.percentileofscore(distanceArray,block['closestGarden'])/100.0

	return jsonData

"""
List of SF Farmers Markets as given by data.sfgov.org
Same methodology as health facilities
Indication that farmers markets may be beneficial for low-income communities: http://depts.washington.edu/uwcphn/reports/fm_brief.pdf
Most SF Farmers Markets accept EBT: http://www.sfhsa.org/156.htm
Summary: Close distance => High Score
"""
def SFFarmersMarkets():
	jsonData = parseBlocks(loadJson('AsthmaRates_CB00.json'))
	markets = loadJson('SanFranciscoFarmersMarkets.json')
	features = markets['features']
	marketCoords = []
	for each in features:
		marketCoords.append(each['geometry']['coordinates'])

	for block in jsonData:
		distanceArray = []
		coord = block['center']
		for each in marketCoords:
			distanceArray.append(distanceBetweenPoints(coord, each))
		block['closestMarket'] = min(distanceArray)

	distanceArray = []
	for block in jsonData:
		distanceArray.append(block['closestMarket'])

	for block in jsonData:
		block['closest'] = 1- scipy.stats.percentileofscore(distanceArray,block['closestMarket'])/100.0


	return jsonData

"""
Implementation of haversine formula based on:
http://stackoverflow.com/questions/19412462/getting-distance-between-two-points-based-on-latitude-longitude-python
"""
def distanceBetweenPoints(point1, point2):
	R = 6373.0

	lat1 = radians(point1[0])
	lon1 = radians(point1[1])
	lat2 = radians(point2[0])
	lon2 = radians(point2[1])

	dlon = lon2 - lon1
	dlat = lat2 - lat1
	a = (sin(dlat/2))**2 + cos(lat1) * cos(lat2) * (sin(dlon/2))**2
	c = 2 * atan2(sqrt(a), sqrt(1-a))
	distance = R * c
	return distance*1000

"""
Implementation of centroid of polygon formula found at:
http://en.wikipedia.org/wiki/Centroid#By_geometric_decomposition
"""
def polygonCentroid(coordinates):
	xArray = []
	yArray = []
	for each in coordinates:
		xArray.append(each[0])
		yArray.append(each[1])

	areaInnerTotal = 0
	xInnerTotal = 0
	yInnerTotal = 0
	length = len(xArray)
	for i in range(0,length-1):
		areaInnerTotal += xArray[i]*yArray[i+1]-xArray[i+1]*yArray[i]
		latterHalf = (xArray[i]*yArray[i+1] - xArray[i+1]*yArray[i])
		xInnerTotal += (xArray[i]+xArray[i+1])*latterHalf
		yInnerTotal += (yArray[i]+yArray[i+1])*latterHalf
	area = areaInnerTotal/2
	centerX = (1.0/(6.0*area))*xInnerTotal
	centerY = (1.0/(6.0*area))*yInnerTotal
	return [centerX, centerY]




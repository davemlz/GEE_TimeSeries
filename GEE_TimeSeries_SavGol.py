# Use it with Google Colab
# !pip install google-api-python-client
# !pip install earthengine-api
# !earthengine authenticate

from datetime import datetime as dt
from scipy import signal
import pandas as pd
import numpy as np
import ee

ee.Initialize()

def cloudMask(image):
  # Quality image
  qa = image.select('QA60')
  # Thick and thin clouds bitmasks
  cloudBitMask = 1 << 10
  cirrusBitMask = 1 << 11
  maskCloud = qa.bitwiseAnd(cloudBitMask).eq(0)
  maskCirrus = qa.bitwiseAnd(cirrusBitMask).eq(0)
  # Blue band threshold mask
  maskThreshold = image.select('B2').lte(2000)
  return image.updateMask(maskCloud).updateMask(maskCirrus).updateMask(maskThreshold).select("B.*").copyProperties(image, ["system:time_start"])

def setGNDVI(image):  
  # GNDVI Vegetation Index
  img = image.normalizedDifference(["B8","B3"])
  # FeatureCollection GNDVI mean
  dict_nd = img.reduceRegion(ee.Reducer.mean(),fc)  
  # Add GNDVI mean as new property
  return img.set(dict_nd).copyProperties(image,["system:time_start"])

def timeSeriesSavGol(imageCollection,window,order):
  # Set GNDVI mean property
  imageCollection = imageCollection.map(setGNDVI)
  # Get features
  features = imageCollection.getInfo()["features"]
  index = []
  date = []
  # Creating date and vegetation index vectors
  for i in range(len(features)):
    fp = features[i]["properties"]
    # There is data
    if "nd" in fp:
      index.append(fp["nd"])
      date.append(fp["system:time_start"])
    # There is no data
    else:
      index.append(np.nan)
      date.append(fp["system:time_start"])
  # Dictionary
  data = {"Date":date,"Index":index}
  # Data frame
  df = pd.DataFrame(data,columns = ["Date","Index"])
  # Date to datetime
  df["Date"] = pd.to_datetime(df["Date"]*1000000)
  # Change format
  df["Date"] = df["Date"].map(lambda x: x.strftime('%Y-%m-%d'))
  # Interpolate missing data in time series
  df["Index"] = pd.Series(df["Index"]).interpolate(limit = len(date))
  # Drop duplicates
  df = df.drop_duplicates()
  # Apply Savitzky-Golay filter
  df["SavGol"] = signal.savgol_filter(df["Index"],window,order,mode = "nearest")
  return df

# Example polygon
polygon = ee.Geometry.Polygon([
  [[-76.33072249944837,3.404583946423481],
   [-76.32970326002271,3.4040056116216846],
   [-76.33004658277662,3.407561294164939],
   [-76.33093707616956,3.4071650289896263],
   [-76.33072249944837,3.404583946423481]]
]);

# polygon to feature collection
fc = ee.FeatureCollection(polygon)

# Sentinel-2 image collection over the feature collection and cloudmask
S2 = ee.ImageCollection("COPERNICUS/S2").filterBounds(fc).map(cloudMask)

# Get data drame with filtered time series
df = timeSeriesSavGol(S2,7,4)

print(df)

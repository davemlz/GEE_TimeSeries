# Google Earth Engine time series with Savitzky-Golay filter

Example that shows how to extract image collection values for a feature collection, create a vegetaion index time series dataframe and apply a Savitzky-Golay filter over it.

## Note

A better version of this function was implemented in [eemont](https://github.com/davemlz/eemont) as an extended method for the ee.ImageCollection object:

```python
f1 = ee.Feature(ee.Geometry.Point([3.984770,48.767221]).buffer(50),{'ID':'A'})
f2 = ee.Feature(ee.Geometry.Point([4.101367,48.748076]).buffer(50),{'ID':'B'})
fc = ee.FeatureCollection([f1,f2])

S2 = (ee.ImageCollection('COPERNICUS/S2_SR')
  .filterBounds(fc)
  .filterDate('2020-01-01','2021-01-01')
  .maskClouds()
  .scale()
  .index(['EVI','NDVI']))

# By Region
ts = S2.getTimeSeriesByRegion(reducer = [ee.Reducer.mean(),ee.Reducer.median()],
                             geometry = fc,
                             bands = ['EVI','NDVI'],
                             scale = 10)

# By Regions
ts = S2.getTimeSeriesByRegions(reducer = [ee.Reducer.mean(),ee.Reducer.median()],
                              collection = fc,
                              bands = ['EVI','NDVI'],
                              scale = 10)
```

# Bellingham Tidal Observatory (BTO)

This is application gathers data from the [NOAA CO-OPS API](https://api.tidesandcurrents.noaa.gov/api/prod/) for visualizing the waters of the Bellingham Bay across different stations.

## Stations List

NOAA has provided the following stations within the Bellingham Bay:

| Name                            | Id      | Lat      | Lon       | Predictions |
| ------------------------------- | ------- | -------- | --------- | ----------- |
| Bellingham                      | 9449211 | +48.7450 | -122.4950 | Subordinate |
| Village Point, Lummi Island     | 9449161 | +48.7167 | -122.7080 | Harmonic    |
| Sandy Point, Lummi Bay          | 9449292 | +48.7900 | -122.7080 | Subordinate |
| Rosario, East Sound, Orcas Island | 9449771 | +48.6467 | -122.8700 | Harmonic    |
| Upright Head, Lopez Island      | 9449911 | +48.5717 | -122.8850 | Harmonic    |
| Orcas, Orcas Island             | 9449798 | +48.6000 | -122.9500 | Subordinate |


### Resources

I found [this reddit post](https://www.reddit.com/r/oceanography/comments/i0e8m5/calculation_of_subordinate_tide_stations_from/) helpful for understanding the Subordinate/Harmonic `Predictions` column. The Bellingham station data is an interpolation (estimate of unkown values from known values) of the readings from Port Townsend, and the curves are rendered as Bezier curves between the high and low points. That really takes me back to my Intro To Computer Graphics days at OSU. This would have been such a cool project for that assignment! Oh well.


# ncbi_pub_trend
An API server that allows users to get the number of scientific publications over years using NCBI API.

## Deployment
1. Create a virtual environment
2. Run `pip install -r requirements.txt` to install dependencies
3. Add the NCBI APP KEY to the `.env` file e.g. `NCBI_APP_KEY=xxxxxxxxxxxxxxxxx`. Alternatively, export the key to
the `NCBI_APP_KEY` environment variable.
4. Run the server by executing `python main.py`

## API
API documentation is available in Swagger e.g. `http://localhost:9000/docs`

## Example usages

1. Get the number of publications about **diabetes** in each year between **2000** and **2001**:
```shell
http://localhost:9000/trend?disease=diabetes&min_yr=2000&max_yr=2021
```

2. Get the publications in the past year (last 365 days) mentioning 'parkinson', cache the results in the
NCBI History Server, and retrieve the environment context info from the server:
```shell
localhost:9000/latest_pubs?disease=parkinson
```

3. From the 1000th to the 2000th articles in the 2nd example, extract the list of institutions that have published them:
```shell
localhost:9000/institutions?env=MCID_62efc70194f5d977d221e601&qid=1&idx=1000&retmax=1000
```
We can then search the institutions on Google and plot their geolocations on the map.
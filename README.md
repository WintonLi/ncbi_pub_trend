# ncbi_pub_trend
An API server that allows users to get the number of scientific publications over years using NCBI API.

## Deployment
1. Create a virtual environment
2. Run `pip install -r requirements.txt` to install dependencies
3. Add the NCBI APP KEY to the `.env` file e.g. `NCBI_APP_KEY=xxxxxxxxxxxxxxxxx`. Alternatively, export the key to
the `NCBI_APP_KEY` environment variable.
4. Run the server by executing `python main.py`

## Example usage

1. Get the number of publications about **diabetes** in each year between **2000** and **2001**:
```shell
http://localhost:9000/trend?disease=diabetes&min_yr=2000&max_yr=2021
```
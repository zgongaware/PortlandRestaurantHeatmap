import requests
import pandas as pd


def retrieve_neighborhood_reviews(limit=50, search_term=""):
    """
    Import list of neighborhoods and iterate over, calling reviews for each.
    :param limit: Maximum number of reviews to retrieve for each neighborhood
    :param search_term: (Optional) Additional search term to add.
    :return:
    """

    # Define desired results
    columns = [
        "neighborhood",
        "name",
        "distance",
        "category",
        "address",
        "display_phone",
        "price",
        "rating",
        "review_count",
        "url",
        "latitude",
        "longitude",
    ]
    final = pd.DataFrame(columns=columns)

    # Bring in neighborhoods
    print("Importing neighborhoods...")
    nhoods = import_neighborhoods("Neighborhoods.csv")
    print("...Complete")

    # Find best restaurants in each neighborhood
    print("Retrieving reviews...")
    for i, r in nhoods.iterrows():
        print("......%s" % nhoods.iloc[i]["Names"])
        result = parse_reviews(columns, limit, nhoods.iloc[i]["Names"], search_term)
        final = pd.concat([final, result], ignore_index=True)

    print("...Complete")

    # Clean out duplicate restaurants
    clean = final.sort_values("distance", ascending=True).groupby(["name"]).head(1)

    # Write to restaurants.csv
    print("Saving to file...")
    clean.to_csv("restaurants.csv", encoding="utf-8")


def get_credentials():
    """
    Import in Yelp API credentials.  Head to https://www.yelp.com/developers to
    generate your own API credentials.

    Credentials file is formatted as -
    app_id
    app_secret
    :return:
    """
    with open("credentials.txt") as f:
        credentials = [x.strip().split(":") for x in f.readlines()]

    return credentials[0][0], credentials[1][0]


def call_yelp_api(limit=50, neighborhood="", search_term=""):
    """
    Collect credentials and retrieve data from Yelp's API
    :param limit: Maximum number of rows to retrieve.
    :param neighborhood: (Optional) Neighborhood to add to location search parameter.
    :param search_term: (Optional) Additional search term to add.
    :return:
    """
    app_id, app_secret = get_credentials()

    url = "https://api.yelp.com/v3/businesses/search"
    headers = {"Authorization": "bearer %s" % app_secret}
    params = {
        "location": neighborhood + ", Portland, OR",
        "term": "Restaurant " + search_term,
        "sort_by": "distance",
        "limit": limit,
    }

    resp = requests.get(url=url, params=params, headers=headers)

    if "businesses" in resp.json():
        return resp.json()["businesses"]


def parse_reviews(columns, limit=50, neighborhood="", search_term=""):
    """
    Retrieve reviews from Yelp API and parse results into a pandas dataframe
    :param columns: List of columns to pull from API results
    :param limit: Maximum number of rows to retrieve.
    :param neighborhood: (Optional) Neighborhood to add to location search parameter.
    :param search_term: (Optional) Additional search term to add.
    :return:
    """

    # Call API and parse to dataframe
    rd = pd.DataFrame.from_dict(call_yelp_api(limit, neighborhood, search_term))

    # Parse columns with embedded dictionaries to appropriate information
    if "categories" in rd.columns:
        # Category
        rd["category"] = rd.categories.apply(lambda x: x[0]["title"])

    if "coordinates" in rd.columns:
        # Latitude
        rd["latitude"] = rd.coordinates.apply(lambda x: x["latitude"])
        # Longitude
        rd["longitude"] = rd.coordinates.apply(lambda x: x["longitude"])

    if "location" in rd.columns:
        # Street Address
        rd["address"] = rd.location.apply(lambda x: x["display_address"][0])

    # Neighborhood
    rd["neighborhood"] = neighborhood

    return rd[columns]


def import_neighborhoods(file_name="neighborhoods.csv"):
    """
    Import list of neighborhoods into pandas dataframe
    :param file_name:
    :return:
    """
    df = pd.read_csv(file_name)

    return df


if __name__ == "__main__":
    retrieve_neighborhood_reviews()

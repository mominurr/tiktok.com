import json,time,os
from DrissionPage import ChromiumPage
from DrissionPage import ChromiumOptions
from bs4 import BeautifulSoup as bs
from pymongo import MongoClient
def save_top_influencer(TOP_INFULUENCER_COLLECTION,DATA_COLLECTION):
    """A function to get top influencers and save them in mongoDB.
    Args:
        TOP_INFULUENCER_COLLECTION: mongoDB collection
        DATA_COLLECTION: mongoDB collection

    return: None

    """
    valid_top_influencers = []
    top_influencer_lists = list(DATA_COLLECTION.find({},{"_id":0}))
    for item in top_influencer_lists:
        if item["follower_count"]>=100000 and item["like_count"]>=1000000:
            valid_top_influencers.append(item)

    print(f"Found {len(valid_top_influencers)} top influencers.")
    TOP_INFULUENCER_COLLECTION.insert_many(valid_top_influencers)
    print("Top Influencers saved successfully!")
        


def get_data(item_lists,search_value):
    data_lists=[]
    for item in item_lists:
        try:
            author_username=item["author"]["nickname"]
        except:
            author_username=None
        try:
            username=item["author"]["uniqueId"]
        except:
            username=None
        try:
            video_id=item["id"]
        except:
            video_id=None
        try:
            video_url=f"https://www.tiktok.com/@{username}/video/{video_id}"
        except:
            video_url=None
        try:
            video_caption=item["desc"]
        except:
            video_caption=None
        try:
            video_details_info=item["stats"]
        except:
            video_details_info=None
        
        try:
            follower_count=item["authorStats"]["followerCount"]
        except:
            follower_count=None
        try:
            following_count=item["authorStats"]["followingCount"]
        except:
            following_count=None
        try:
            like_count=item["authorStats"]["heartCount"]
        except:
            like_count=None
        try:
            author_details_info=item["authorStats"]
        except:
            author_details_info=None
        data_lists.append({
            "search_value":search_value,
            "author_username":author_username,
            "username":username,
            "follower_count":follower_count,
            "following_count":following_count,
            "like_count":like_count,
            "author_details_info":author_details_info,
            "video_url":video_url,
            "video_caption":video_caption,
            "video_details_info":video_details_info
        })

    return data_lists






def collect_data(DATA_COLLECTION,keyword=None,hashtag=None):
    """Collect data from tiktok.com

    Args:
        DATA_COLLECTION (MongoClient collection object): Store data in mongodb.
        keyword (str, optional): keyword. Defaults to None.
        hashtag (str, optional): hashtag. Defaults to None.

    return: None
    """

    # Define variables for getting response data from browser network tab
    network_listing_string=None

    # Define variables for dynamic search type (1=keyword, 2=hashtag)
    attr_str=None

    # Define variables 
    url=None
    if keyword is None and hashtag is None:
        print("Please enter a keyword or hashtag.")
        return
    elif keyword is not None:
        url=f"https://www.tiktok.com/search/video?q={keyword}"
        network_listing_string="/search/item/full"
        attr_str="search_video-item"
    else:
        url=f"https://www.tiktok.com/tag/{hashtag}"
        network_listing_string="/api/challenge/item_list"
        attr_str="challenge-item"
    options=ChromiumOptions()
    options.incognito()
    # create page object
    driver = ChromiumPage()

    driver.listen.start(network_listing_string)
    try:
        driver.get(url)
    except:
        pass

    time.sleep(10)
    print("Scrolling to the bottom until all data is loaded...")
    number_of_api_calls = 1
    # Since page is loading new elements after each scroll to bottom
    # Get scroll height
    last_number = len(bs(driver.html,"html.parser").find_all("div",attrs={"data-e2e":attr_str}))
    while True:
        # Scroll down to bottom
        driver.scroll.to_bottom()
        # Wait to load page
        time.sleep(10)
        # Calculate new scroll height and compare with last scroll height
        new_number = len(bs(driver.html,"html.parser").find_all("div",attrs={"data-e2e":attr_str}))
        number_of_api_calls += 1
        if new_number == last_number:
            break
        last_number = new_number

    print("Scrolling is done.")

    # Get response data from browser network tab
    for packet in driver.listen.steps(count=number_of_api_calls+5,timeout=1,gap=1):
        response_data=packet.response.body
        if response_data is not None:
            if keyword is not None:
                try:
                    item_lists=response_data["item_list"]
                except:
                    continue
                data_lists=get_data(item_lists,keyword)
                input_data_sets={data["video_url"] for data in data_lists}
                try:
                    # Check if video_url values exist in DATA_COLLECTION
                    existing_data = list(DATA_COLLECTION.find({"video_url": {"$in": list(input_data_sets)}}, {"_id": 0, "video_url": 1}))
                    # Create a set of existing video_url values for quick lookup
                    existing_data_set = {data["video_url"] for data in existing_data} #this set is used for unique values
                except:
                    existing_data_set = set()

                # Filter out dictionaries based on whether the data is in existing_data_set
                # filtered_data_lists gives the list of data that are not in previous processing data
                filtered_data_lists=[data for data in data_lists if data["video_url"] not in existing_data_set]
                if len(filtered_data_lists) != 0:
                    DATA_COLLECTION.insert_many(filtered_data_lists)
            else:
                try:
                    item_lists=response_data["itemList"]
                except:
                    continue
                data_lists=get_data(item_lists,hashtag)
                input_data_sets={data["video_url"] for data in data_lists}
                try:
                    # Check if video_url values exist in DATA_COLLECTION
                    existing_data = list(DATA_COLLECTION.find({"video_url": {"$in": list(input_data_sets)}}, {"_id": 0, "video_url": 1}))
                    # Create a set of existing video_url values for quick lookup
                    existing_data_set = {data["video_url"] for data in existing_data} #this set is used for unique values
                except:
                    existing_data_set = set()

                # Filter out dictionaries based on whether the data is in existing_data_set
                # filtered_data_lists gives the list of data that are not in previous processing data
                filtered_data_lists=[data for data in data_lists if data["video_url"] not in existing_data_set]
                if len(filtered_data_lists) != 0:
                    DATA_COLLECTION.insert_many(filtered_data_lists)

    driver.listen.stop()

    driver.quit()
    print("Data collection is done.")



if __name__ == '__main__':
    print("############### WELCOME TO THE TIKTOK SCRAPER ###############")
    print("############### BY: Mominur Rahman ###############\n")

    try:
        client=MongoClient("mongodb://localhost:27017/")
        DATA_COLLECTION=client["tiktok_db"]["data"]
        TOP_INFULUENCER_COLLECTION=client["tiktok_db"]["top_influencer"]
    except Exception as e:
        print(f"error : {e}")
        os._exit(0)
    while True:
        print("\nPlease select one of the following options:")
        print("1. Collect data with keyword")
        print("2. Collect data with hashtag")
        print("3. Identify and save Influencers Information")
        print("4. Exit")
        choice = input("Enter your choice (1/2/3/4): ")
        keyword, hashtag = None, None
        if choice == '1':
            keyword = input("Enter keyword: ")
            collect_data(DATA_COLLECTION,keyword,hashtag)
        elif choice == '2':
            hashtag = input("Enter hashtag(without #): ")
            collect_data(DATA_COLLECTION,keyword,hashtag)
        elif choice == '3':
            save_top_influencer(TOP_INFULUENCER_COLLECTION,DATA_COLLECTION)
        elif choice == '4':
            break
        else:
            print("Invalid choice. Please try again.")

    print("Thank you for using the TikTok scraper. Goodbye!")





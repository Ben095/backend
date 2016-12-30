from InstagramAPI import InstagramAPI
InstagramAPI = InstagramAPI("biplov_dahal", "123123123vb")
InstagramAPI.login()
InstagramAPI.tagFeed("cat") # get media list by tag #cat
media_id = InstagramAPI.LastJson # last response JSON
InstagramAPI.like(media_id["ranked_items"][0]["pk"]) # like first media
print media_id['ranked_items'][0]['user']['pk']
#print InstagramAPI.getUserFollowers(media_id["ranked_items"][0]["user"]["pk"])

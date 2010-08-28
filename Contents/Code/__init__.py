import re, string, datetime
from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import * 

PREFIX      = "/music/allmusic"
CACHE_INTERVAL    = 1800

BASE_PAGE = "http://www.allmusic.com"
GENRES = "http://www.allmusic.com/cg/amg.dll?p=amg&sql=73:p"
DIRECT_URL = "http://www.allmusic.com/cg/amg.dll?p=amg&sql=%s"

####################################################################################################
def Start():
  Plugin.AddPrefixHandler(PREFIX, MainMenu, "allmusic", "icon-default.png", "art-default.png")
  Plugin.AddViewGroup("Details", viewMode="InfoList", mediaType="items")
  MediaContainer.art = R('art-default.png')
  MediaContainer.title1 = 'allmusic'
  DirectoryItem.thumb=R("icon-default.png")
  HTTP.SetCacheTime(CACHE_INTERVAL) 
  
    
##################################
def MainMenu():
    dir = MediaContainer() 
    # TODO: order
    dir.Append(Function(DirectoryItem(Genres, "Genres")))
    #dir.Append(Function(DirectoryItem(Moods, "Moods")))
    #dir.Append(Function(DirectoryItem(NewReleases, "New Releases")))
    #dir.Append(Function(DirectoryItem(TopSearches, "Top Searches")))
    #dir.Append(Function(DirectoryItem(EditorsChoice, "Editors Choice")))
    #dir.Append(Function(DirectoryItem(Composers, "Composers")))
    #dir.Append(Function(DirectoryItem(Countries, "Countries")))
    #dir.Append(Function(DirectoryItem(Themes, "Themes (weird if you ask me)")))
    return dir
   
def Genres(sender):
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle)
    for genre in XML.ElementFromURL(GENRES, True).xpath('//tr[@class="visible"]'):
        href = DIRECT_URL % genre.get('onclick').split("'")[1]
        title = XML.ElementFromURL(href, True).xpath('//div[@id="genre"]//span[@class="title"]')[0].text
        summaries = XML.ElementFromURL(href, True).xpath('//div[@id="genre"]//p')
        thumbs = XML.ElementFromURL(href, True).xpath('//div[@id="genre"]//div[@id="featured"]//td/a/img')
        
        if len(summaries) > 0 and len(thumbs) > 1 :
            thumb = thumbs[0].get('src')
            dir.Append(Function(DirectoryItem(Genre, title=title, summary=summaries[0].text, thumb=thumb), thumb=thumb, url=href)) 
    return dir

def Genre(sender, thumb, url):
    dir = MediaContainer(title2=sender.itemTitle)
    dir.Append(Function(DirectoryItem(SubGenres, 'Sub-Genres', thumb=thumb), url=url, title2=sender.itemTitle)) # TODO
    dir.Append(Function(DirectoryItem(Albums, 'Albums', thumb=thumb), url=url+"~T3", title2=sender.itemTitle)) # TODO
    dir.Append(Function(DirectoryItem(Artists, 'Artists', thumb=thumb), url=url+"~T2", title2=sender.itemTitle)) 
    dir.Append(Function(DirectoryItem(Songs, 'Songs', thumb=thumb), url=url+"~T4", title2=sender.itemTitle)) # TODO
    return dir

def SubGenre(sender, url, title2, thumb=None):
    dir = MediaContainer(title2=title2)
    dir.Append(Function(DirectoryItem(Albums, 'Albums', thumb=thumb), url=url+"~T2", title2=sender.itemTitle))
    dir.Append(Function(DirectoryItem(Artists, 'Artists', thumb=thumb), url=url+"~T1", title2=sender.itemTitle)) 
    dir.Append(Function(DirectoryItem(Songs, 'Songs', thumb=thumb), url=url+"~T3", title2=sender.itemTitle)) # TODO
    return dir


def Albums(sender, url, title2):
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle)
    return dir


def Artists(sender, url, title2):
    dir = MediaContainer(viewGroup='Details', title2=title2)
    for artist in XML.ElementFromURL(url, True).xpath('//tr[@class="visible"]'):
        name = artist.xpath('.//td[@class="cell"]')[0].text
        onclick = artist.get('onclick')
        artistPage = DIRECT_URL % onclick.split("'")[1]
        thumbs = XML.ElementFromURL(artistPage, True).xpath('//div[@id="artistpage"]//td/a/img')
        thumb = None
        if len(thumbs) > 0:
            thumb = thumbs[0].get('src')
        summaries = XML.ElementFromURL(artistPage, True).xpath('//div[@id="artistpage"]//p')
        summary = None
        if len(summaries) > 0:
            summary = summaries[0].text
        dir.Append(Function(DirectoryItem(ArtistSongs, name, summary=summary, thumb=thumb), name=name, thumb=thumb, artistPage=artistPage)) 
    return dir

def ArtistSongs(sender, name, thumb, artistPage):
    dir = MediaContainer(mediaType='music', title2=sender.itemTitle)
    songsPage = artistPage + "~T3"
    for song in XML.ElementFromURL(songsPage, True).xpath('//tr[@class="visible"]'):
        for trackLink in song.xpath(".//a"):
            trackUrl = BASE_PAGE + trackLink.get('href')
            if trackUrl.endswith("~T"):
                content = HTTP.Request(trackUrl)
                title = song.xpath('.//a')[-1].text
                if title == None:
                    title = song.xpath('.//a')[-2].text
                
                dir.Append(Function(TrackItem(PlayTrack, title, thumb=thumb), ext=".mp3", track=content))
    return dir

def Songs(sender, url, title2):
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle)
    return dir

def SubGenres(sender, url, title2):
    dir = MediaContainer(viewGroup='Details', title2=title2)
    for subgenre in XML.ElementFromURL(url, True).xpath('//div[@class="large-list-subtitle"]/../../ul/li//a'):
        title = subgenre.text
        pageUrl = BASE_PAGE + subgenre.get('href')
        summaries = XML.ElementFromURL(pageUrl, True).xpath('//div[@id="bio"]//p')
        thumbs = XML.ElementFromURL(pageUrl, True).xpath('//td/a/img')
        summary = None
        if len(summaries) > 0:
            summary = summaries[0].text
        thumb = None
        if len(thumbs) > 0:
            thumb = thumbs[0].get('src')
        dir.Append(Function(DirectoryItem(SubGenre, title=title, summary=summary, thumb=thumb), url=pageUrl, title2=title, thumb=thumb)) 
    return dir


#########################################################
def PlayTrack(sender, track):
    return Redirect(track)

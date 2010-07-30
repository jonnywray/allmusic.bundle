import re, string, datetime
from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import * 

PREFIX      = "/music/allmusic"
CACHE_INTERVAL    = 1800

BASE_PAGE = "http://www.allmusic.com"
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
    dir.Append(Function(DirectoryItem(Genres, "Genres")))
    return dir
    
def Genres(sender):
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle)
    for genre in XML.ElementFromURL(BASE_PAGE, True).xpath('//div[@id="header_menu"]/div/a'):
        href = BASE_PAGE + genre.get('href')
        title = XML.ElementFromURL(href, True).xpath('//div[@id="genre"]//span[@class="title"]')[0].text
        summaries = XML.ElementFromURL(href, True).xpath('//div[@id="genre"]//p')
        thumbs = XML.ElementFromURL(href, True).xpath('//div[@id="genre"]//div[@id="featured"]//td/a/img')
        
        if len(summaries) > 0 and len(thumbs) > 1 :
            dir.Append(Function(DirectoryItem(Genre, title=title, summary=summaries[0].text, thumb=thumbs[0].get('src')), url=href)) 
    return dir

def Genre(sender, url):
    dir = MediaContainer(title2=sender.itemTitle)
    dir.Append(Function(DirectoryItem(SubGenres, 'Sub-Genres'), url=url))
    dir.Append(Function(DirectoryItem(Albums, 'Albums'), url=url+"~T3"))
    dir.Append(Function(DirectoryItem(Artists, 'Artists'), url=url+"~T2"))
    dir.Append(Function(DirectoryItem(Songs, 'Songs'), url=url+"~T4"))
    return dir


def Albums(sender, url):
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle)
    return dir


def Artists(sender, url):
    dir = MediaContainer(title2=sender.itemTitle)
    for artist in XML.ElementFromURL(url, True).xpath('//tr[@class="visible"]'):
        name = artist.xpath('.//td[@class="cell"]')[0].text
        onclick = artist.get('onclick')
        # Extract more meta data here
        artistPage = DIRECT_URL % onclick.split("'")[1]
        dir.Append(Function(DirectoryItem(ArtistSongs, name), name=name, artistPage=artistPage)) 
    return dir

def ArtistSongs(sender, name, artistPage):
    dir = MediaContainer(mediaType='music', title2=sender.itemTitle)
    songsPage = artistPage + "~T3"
    for song in XML.ElementFromURL(songsPage, True).xpath('//tr[@class="visible"]'):
        links = song.xpath('.//a')
        if len(links) == 2:
           title = links[1].text
           playlist = BASE_PAGE + links[0].get('href')
           content = HTTP.Request(playlist)
           dir.Append(Function(TrackItem(PlayTrack, title), ext=".mp3", track=content))
    return dir

def PlayTrack(sender, track):
    return Redirect(track)

def Songs(sender, url):
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle)
    return dir

def SubGenres(sender, url):
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle)
    for subgenre in XML.ElementFromURL(url, True).xpath('//div[@class="large-list-subtitle"]/../../ul/li//a'):
        title = subgenre.text
        pageUrl = BASE_PAGE + subgenre.get('href')
        dir.Append(Function(DirectoryItem(SubGenre, title=title, ext="mp3"), pageUrl=pageUrl, title=title))
    return dir

def SubGenre(sender, pageUrl, title):
    dir = MediaContainer(mediaType='music')
    
    return dir


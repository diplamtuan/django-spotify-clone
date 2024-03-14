from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.models import User,auth
from django.contrib.auth.decorators import login_required
# Create your views here.
import requests
def top_artists():
    url = "https://spotify23.p.rapidapi.com/artist_related/"
    querystring = {"id":"2w9zwq3AktTeYYMuhMjju8"}
    headers = {
        "X-RapidAPI-Key": "2d1b3841famshf6403fe9fed2175p15b6d0jsn941b5eb234c5",
        "X-RapidAPI-Host": "spotify23.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)
    respone_data=response.json()

    artists_info = []

    if 'artists' in respone_data:

        for artist in respone_data['artists']:
            name = artist.get('name','No Name')
            artist_id = artist.get('id','No ID')
            avatar_url = artist.get('images',[{}])[0].get('url','No URL')
            artists_info.append((name,avatar_url,artist_id))
    return artists_info

def top_tracks():
    url = "https://spotify23.p.rapidapi.com/recommendations/"
    querystring = {"limit":"20","seed_tracks":"0c6xIDDpzE81m2q797ordA","seed_artists":"4NHQUGzhtTLFvgF5SZesLK","seed_genres":"classical,country"}
    headers = {
        "X-RapidAPI-Key": "2d1b3841famshf6403fe9fed2175p15b6d0jsn941b5eb234c5",
        "X-RapidAPI-Host": "spotify23.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)
    data= response.json()
    track_details = []

    if 'tracks' in data:
        shortened_data = data['tracks'][:18]

        # id,name,artist,cover_url
        for track in shortened_data:
            track_id = track['id']
            track_name = track['name']
            artist_name = track['artists'][0]['name'] if track['artists'] else None
            cover_url = track['album']['images'][0]['url'] if track['album']['images'] else None

            track_details.append({
                'id':track_id,
                'track_name':track_name,
                'artist_name':artist_name,
                'cover_url':cover_url
            })
    else:
        print("Track Not found")
    return track_details

def get_audio_details(query):
    url = "https://spotify-scraper.p.rapidapi.com/v1/track/download"
    querystring = {"track":query}
    headers = {
        "X-RapidAPI-Key": "7741ebd7e4msh0958395311bc59cp14d430jsn282bbabbaa5a",
	"X-RapidAPI-Host": "spotify-scraper.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    audio_details = []
    
    if response.status_code == 200:
        response_data = response.json()

        if 'youtubeVideo' in response_data and 'audio' in response_data['youtubeVideo'] and 'spotifyTrack' in response_data and 'album' in response_data['spotifyTrack']:
            audio_list= response_data['youtubeVideo']['audio']
            image_url = response_data['spotifyTrack']['album']['cover'][0]['url']
            if audio_list:
                first_audio_url = audio_list[0]['url']
                duration_text = audio_list[0]['durationText']
                audio_details.append(first_audio_url)
                audio_details.append(duration_text)
                audio_details.append(image_url)
            else:
                print("No audio data avaliable")
        else:
            print("No 'youtubeVideo' or 'audio' key found")
    else:
        print("No response data")
    return audio_details
   
def music(request,pk):
    track_id =pk
    url = "https://spotify-scraper.p.rapidapi.com/v1/track/metadata"

    querystring = {"trackId":track_id}

    headers = {
        "X-RapidAPI-Key": "7741ebd7e4msh0958395311bc59cp14d430jsn282bbabbaa5a",
	"X-RapidAPI-Host": "spotify-scraper.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    if response.status_code == 200:
        data = response.json()
        # track_name,artist_name

        track_name = data.get('name')
        artists_list = data.get('artists',[])
        first_artist_name = artists_list[0].get("name") if artists_list else "No artist found"
        audio_details_query= track_name +first_artist_name
        audio_details = get_audio_details(audio_details_query)
        audio_url= audio_details[0]
        audio_durationText= audio_details[1]
        image_url= audio_details[2]
        context ={
            "track_name":track_name,
            "artist_name":first_artist_name,
            'audio_url':audio_url,
            'audio_durationText':audio_durationText,
            'image_url':image_url,
        }
    return render(request,'music.html',context)

@login_required(login_url='login') 
def index(request):
    artists_info = top_artists()
    top_tracks_list = top_tracks()

    # divide the list into three part
    first_tracks = top_tracks_list[:6]
    sencond_tracks = top_tracks_list[6:12]
    third_tracks = top_tracks_list[12:18]
    context ={
        'artists_info':artists_info,
        'first_tracks':first_tracks,
        'sencond_tracks':sencond_tracks,
        'third_tracks':third_tracks,
    }
    return render(request, 'index.html',context)

def search(request):

    if request.method == 'POST':
        search_query=request.POST['search_query'] 
        url = "https://spotify-scraper.p.rapidapi.com/v1/search"
        querystring = {"term":search_query,"type":"track"}

        headers = {
            "X-RapidAPI-Key": "2d1b3841famshf6403fe9fed2175p15b6d0jsn941b5eb234c5",
            "X-RapidAPI-Host": "spotify-scraper.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers, params=querystring)
        track_list=[]
         
        if response.status_code == 200:
            data=response.json()
            search_results_count =data['tracks']['totalCount']
            tracks = data['tracks']['items']

            for track in tracks:
                trackName=track['name']
                artistName = track['artists'][0]['name']
                durationText = track['durationText']
                trackId =track['id']
                if track['album']['cover']:
                    trackImage = track['album']['cover'][0]['url']
                else:
                    trackImage ="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRWmsrql9-T39L3j7Z8DrQkmw9WoZW779Dovw&s"
                track_list.append({
                    'trackName':trackName,
                    'artistName':artistName,
                    'durationText':durationText,
                    'trackId':trackId,
                    'trackImage':trackImage,
                })
            context ={
                'search_results_count':search_results_count,
                'track_list':track_list
            }
            return render(request,'search.html',context)

    else:
        return render(request,'search.html')
def profile(request,pk):
    artist_id = pk
    url = "https://spotify-scraper.p.rapidapi.com/v1/artist/overview"
    querystring = {"artistId":artist_id}
    headers = {
        "X-RapidAPI-Key": "7741ebd7e4msh0958395311bc59cp14d430jsn282bbabbaa5a",
	"X-RapidAPI-Host": "spotify-scraper.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)
    if response.status_code ==200:
        data=response.json()

        # name,header,monthlyListeners
        name = data['name']
        monthly_listeners = data['stats']['monthlyListeners']
        monnthlyListenersFormat ="{:,}".format(monthly_listeners)
        header_url=data['visuals']['header'][0]['url']

        top_tracks=[]

        for track in data['discography']['topTracks']:
            trackId = track['id']
            trackName=track['name']
            trackPlayCountFormat ="{:,}".format(track['playCount'])
            if track['album']['cover']:
                trackImage = track['album']['cover'][0]['url']
            else:
                trackImage ="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRWmsrql9-T39L3j7Z8DrQkmw9WoZW779Dovw&s"
        
            track_info={
                'trackId':trackId,
                'trackName':trackName,
                'durationText':track['durationText'],
                'playCount':trackPlayCountFormat,
                'trackImage':trackImage,
            }
            top_tracks.append(track_info)
        artist_data={
            'name':name,
            'monnthlyListenersFormat':monnthlyListenersFormat,
            'header_url':header_url,
            'top_tracks':top_tracks
        }
    else:
        artist_data={}
    return render(request,'profile.html',artist_data)
def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user=auth.authenticate(username=username,password=password)
        if user is not None:
           auth.login(request,user)
           return redirect('/')
        else:
            messages.info(request, 'Credentials Invalid')
            return redirect('/login')

    return render(request, 'login.html')

def signup(request):
    if request.method == 'POST':
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request,'Email Taken')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request,'Username Taken')
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username,email=email,password=password)
                user.save()

                #log user in
                user_login = auth.authenticate(username=username,password=password)
                auth.login(request,user_login)
                return redirect ('/')
        else:
            messages.info(request, 'Password not matching')
            return redirect('signup')
    else:
        return render(request, 'signup.html')

@login_required(login_url='login') 
def logout(request):
    auth.logout(request)
    return redirect('login')
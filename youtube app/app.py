from flask import Flask, jsonify, request, render_template
from googleapiclient.discovery import build

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recommend', methods=['GET'])
def recommend():
    # Get the YouTube link from the query parameter
    youtube_link = request.args.get('link')

    # Parse the video ID from the link
    video_id = youtube_link.split('v=')[-1]

    # Initialize the YouTube API client
    youtube = build('youtube', 'v3', developerKey='AIzaSyB2rAOxatQXUzwYpg1G_hWZxexrA-P4mVE')

    # Get the details of the video
    video_response = youtube.videos().list(
        part='snippet',
        id=video_id
    ).execute()

    # Extract the video title and channel ID
    video_title = video_response['items'][0]['snippet']['title']
    channel_id = video_response['items'][0]['snippet']['channelId']

    # Get the details of the channel
    channel_response = youtube.channels().list(
        part='snippet,statistics',
        id=channel_id
    ).execute()

    # Extract the channel title and subscriber count
    channel_title = channel_response['items'][0]['snippet']['title']
    subscriber_count = channel_response['items'][0]['statistics']['subscriberCount']

    # Get the related videos for the video
    related_response = youtube.search().list(
        part='id,snippet',
        type='video',
        relatedToVideoId=video_id
    ).execute()

    # Filter the related videos to only include videos from channels with less than 1000 subscribers
    recommendations = []
    for item in related_response['items']:
        channel_id = item['snippet']['channelId']
        video_id = item['id']['videoId']

        channel_response = youtube.channels().list(
            part='statistics',
            id=channel_id
        ).execute()

        subscriber_count = int(channel_response['items'][0]['statistics']['subscriberCount'])
        if subscriber_count < 1000:
            recommendations.append({
                'id': video_id,
                'title': item['snippet']['title']
            })

    return jsonify(recommendations)

if __name__ == '__main__':
    app.run(debug=True)
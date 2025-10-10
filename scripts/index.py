from langchain_community.document_loaders import YoutubeLoader

loader = YoutubeLoader.from_youtube_url(
    "https://www.youtube.com/watch?v=09vU-wVwW3U",
    add_video_info=False,
)
docs = loader.load()

print(docs)
import axios from 'axios'

const API_KEY = import.meta.env.VITE_YOUTUBE_API_KEY

export const searchVideos = (query) => {
  return axios.get(
    'https://www.googleapis.com/youtube/v3/search',
    {
      params: {
        part: 'snippet',
        q: query,
        type: 'video',
        maxResults: 12,
        key: API_KEY,
      },
    }
  )
}
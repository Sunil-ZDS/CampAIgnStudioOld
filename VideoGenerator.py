import requests
import time
import webbrowser

# === Configuration ===
API_TOKEN = "MSi9Hu12HZcPVaH2sR6RHTHWEbD4e1Yp"
TEMPLATE_ID = "default"  # You can change this if you have a specific template
WEBHOOK_URL = "https://webhook.site/be52380a-4a44-4364-bad1-c06cdc2c5790" 

GENERATE_VIDEO_URL = "https://api.elai.io/api/video/render" 
GET_VIDEO_URL = "https://api.elai.io/api/video/" 

HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}"
}

def generate_video_from_text(prompt):
    payload = {
        "template_id": TEMPLATE_ID,
        "presentation_data": {
            "slides": [
                {
                    "text": prompt
                }
            ]
        },
        "webhook": WEBHOOK_URL  # Optional, but good for production
    }

    print("📨 Sending request to Elai.io...")
    response = requests.post(GENERATE_VIDEO_URL, headers=HEADERS, json=payload)

    if response.status_code != 200:
        raise Exception(f"❌ Failed to start video generation. Status code: {response.status_code}, Response: {response.text}")

    video_id = response.json().get("videoId")
    print(f"🎥 Video ID received: {video_id}")
    return video_id


def wait_for_video_to_be_ready(video_id):
    print("🔄 Waiting for video to be generated (this may take 1-3 minutes)...")
    video_url = None

    for _ in range(60):  # Try up to 60 times with 5 sec delay = 5 min max
        response = requests.get(f"{GET_VIDEO_URL}{video_id}", headers=HEADERS)
        data = response.json()

        status = data.get("status")
        if status == "ready":
            video_url = data.get("videoUrl")
            break
        elif status == "error":
            raise Exception("❌ Error generating video: Video generation failed on server.")
        else:
            print("⏳ Still processing...")

        time.sleep(5)

    if not video_url:
        raise Exception("⏰ Timeout: Video was not generated within the expected time.")

    return video_url


if __name__ == "__main__":
    user_prompt = input("📝 Enter your video description: ")

    try:
        video_id = generate_video_from_text(user_prompt)
        video_url = wait_for_video_to_be_ready(video_id)
        print(f"🎥 Final video URL: {video_url}")
        print("🌐 Opening video in your default browser...")
        webbrowser.open(video_url)
    except Exception as e:
        print(f"💥 An error occurred: {e}")
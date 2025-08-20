import streamlit as st
import asyncio
import time
from services.openai_config import create_azure_openai_model
from pydantic_ai import Agent
from pydantic import BaseModel
from typing import List

class CreativeVariation(BaseModel):
    name: str
    text: str

class ABTestSuggestion(BaseModel):
    variation_name: str
    hypothesis: str
    metric: str

class SocialPost(BaseModel):
    variation_name: str
    hashtags: List[str]
    social_post: str

def get_azure_model():
    if "creative_azure_model" not in st.session_state:
        st.session_state.creative_azure_model = create_azure_openai_model()
    return st.session_state.creative_azure_model

async def generate_creative_variations(prompt, tone, format_type, num_variations):
    azure_model = get_azure_model()
    agent = Agent(
        model=azure_model,
        result_type=List[CreativeVariation],
        system_prompt=(
            "You are a creative marketing copywriter. "
            "Given a campaign brief, tone, and format, generate a list of creative ad copy variations. "
            "For each, provide a meaningful, catchy name and the ad copy text. "
            "Return a list of dicts: [{'name': ..., 'text': ...}]"
        )
    )
    user_prompt = (
        f"CAMPAIGN BRIEF: {prompt}\n"
        f"TONE: {tone or 'Any'}\n"
        f"FORMAT: {format_type or 'Any'}\n"
        f"Generate {num_variations} creative ad copy variations. "
        "Each should have a unique, catchy name and the ad copy text. "
        "Return as a list of dicts: [{'name': ..., 'text': ...}]"
    )
    result = await agent.run(user_prompt)
    return result.output

async def generate_ab_testing_suggestions(prompt, variations):
    azure_model = get_azure_model()
    agent = Agent(
        model=azure_model,
        result_type=List[ABTestSuggestion],
        system_prompt=(
            "You are a digital marketing strategist. "
            "Given a campaign brief and a list of creative variations, "
            "suggest A/B testing hypotheses and what to measure for each variation. "
            "Return a list of dicts: [{'variation_name': ..., 'hypothesis': ..., 'metric': ...}]"
        )
    )
    user_prompt = (
        f"CAMPAIGN BRIEF: {prompt}\n"
        f"CREATIVE VARIATIONS: {', '.join([v.name for v in variations])}\n"
        "For each variation, suggest a hypothesis for A/B testing and the key metric to measure. "
        "Return as a list of dicts: [{'variation_name': ..., 'hypothesis': ..., 'metric': ...}]"
    )
    result = await agent.run(user_prompt)
    return result.output

async def generate_hashtags_and_social_posts(prompt, variations):
    azure_model = get_azure_model()
    agent = Agent(
        model=azure_model,
        result_type=List[SocialPost],
        system_prompt=(
            "You are a social media marketer. "
            "Given a campaign brief and a list of creative variations, "
            "generate for each: 3-5 relevant hashtags and a short social post (max 120 chars). "
            "Return a list of dicts: [{'variation_name': ..., 'hashtags': [...], 'social_post': ...}]"
        )
    )
    user_prompt = (
        f"CAMPAIGN BRIEF: {prompt}\n"
        f"CREATIVE VARIATIONS: {', '.join([v.name for v in variations])}\n"
        "For each variation, generate 3-5 hashtags and a short social post (max 120 chars). "
        "Return as a list of dicts: [{'variation_name': ..., 'hashtags': [...], 'social_post': ...}]"
    )
    result = await agent.run(user_prompt)
    return result.output

def generate_image(prompt):
    base_url = "https://image.pollinations.ai/prompt/"
    encoded_prompt = prompt.replace(" ", "%20")
    cache_buster = str(int(time.time() * 1000))
    return f"{base_url}{encoded_prompt}?cb={cache_buster}"

def show_creative_asset_generator():
    st.markdown("## 📝 Creative Asset Generator")
    st.markdown("Generate ad copy, headlines, CTAs, and visual ideas for your campaign.")

    creative_container = st.container()
    with creative_container:
        with st.form("creative_asset_form"):
            campaign_brief = st.text_area(
                "Campaign Brief or Prompt",
                placeholder="Describe your campaign or product...",
                key="creative_campaign_brief"
            )

            tone_options = [
                "Playful", "Professional", "Friendly", "Inspirational", "Urgent", "Confident",
                "Conversational", "Witty", "Empowering", "Trustworthy", "Exciting", "Casual",
                "Bold", "Elegant", "Persuasive", "Educational", "Humorous", "Direct", "Luxury", "Minimalist"
            ]
            format_options = [
                "Banner", "Poster", "Social Media Post", "Email Header", "Landing Page", "Carousel",
                "Story", "Video Thumbnail", "Infographic", "Brochure", "Flyer", "Newsletter",
                "Push Notification", "Ad Copy", "Billboard", "Popup", "Podcast Cover", "YouTube Ad", "Facebook Ad", "Instagram Story"
            ]

            tone_preference = st.selectbox(
                "Tone Preference",
                options=tone_options,
                index=0,
                key="creative_tone_preference"
            )
            format_type = st.selectbox(
                "Desired Format",
                options=format_options,
                index=0,
                key="creative_format_type"
            )
            num_variations = st.number_input(
                "Number of Text Variations",
                min_value=1, max_value=10, value=3,
                key="creative_num_variations"
            )
            submitted = st.form_submit_button("Generate Creative Assets")

        # Placeholders for each result section
        variations_placeholder = st.empty()
        images_placeholder = st.empty()
        abtest_placeholder = st.empty()
        social_placeholder = st.empty()
        tips_placeholder = st.empty()

        if submitted:
            # Immediately clear previous results
            variations_placeholder.empty()
            images_placeholder.empty()
            abtest_placeholder.empty()
            social_placeholder.empty()
            tips_placeholder.empty()

            if not campaign_brief:
                st.error("Please enter a campaign brief or prompt.")
                return

            with st.spinner("Generating creative assets..."):
                variations = asyncio.run(
                    generate_creative_variations(
                        campaign_brief, tone_preference, format_type, num_variations
                    )
                )

                with variations_placeholder.container():
                    st.markdown("### ✅ Generated Creative Variations:")
                    for i, v in enumerate(variations, start=1):
                        st.markdown(f"**{i}. {v.name}**")
                        st.markdown(f"`{v.text}`")

                with images_placeholder.container():
                    st.markdown("### 🖼️ Generated Images for Each Variation:")
                    for i, v in enumerate(variations, start=1):
                        image_url = generate_image(v.text)
                        st.markdown(f"**{v.name} Image:**")
                        st.image(image_url, caption=v.text)
                        st.markdown(f"[Open Image in New Tab]({image_url})")

                ab_tests = asyncio.run(generate_ab_testing_suggestions(campaign_brief, variations))
                with abtest_placeholder.container():
                    st.markdown("### 🧪 Dynamic A/B Testing Suggestions:")
                    for ab in ab_tests:
                        st.markdown(f"**{ab.variation_name}**")
                        st.markdown(f"- Hypothesis: {ab.hypothesis}")
                        st.markdown(f"- Metric: {ab.metric}")

                posts = asyncio.run(generate_hashtags_and_social_posts(campaign_brief, variations))
                with social_placeholder.container():
                    st.markdown("### 🔖 Hashtags & Social Posts:")
                    for post in posts:
                        st.markdown(f"**{post.variation_name}**")
                        st.markdown(f"- Hashtags: {' '.join(post.hashtags)}")
                        st.markdown(f"- Social Post: {post.social_post}")

                with tips_placeholder.container():
                    st.markdown("### 💡 Additional Tips:")
                    st.markdown("""
                    - Use the generated variations and images for A/B testing across your channels.
                    - Try the suggested hashtags and social posts for organic reach.
                    - Monitor the suggested metrics to determine the most effective creative assets.
                    """)


######### Without dropdowns #############
# import streamlit as st
# import asyncio
# import time
# from services.openai_config import create_azure_openai_model
# from pydantic_ai import Agent
# from pydantic import BaseModel
# from typing import List

# class CreativeVariation(BaseModel):
#     name: str
#     text: str

# class ABTestSuggestion(BaseModel):
#     variation_name: str
#     hypothesis: str
#     metric: str

# class SocialPost(BaseModel):
#     variation_name: str
#     hashtags: List[str]
#     social_post: str

# def get_azure_model():
#     if "creative_azure_model" not in st.session_state:
#         st.session_state.creative_azure_model = create_azure_openai_model()
#     return st.session_state.creative_azure_model

# async def generate_creative_variations(prompt, tone, format_type, num_variations):
#     azure_model = get_azure_model()
#     agent = Agent(
#         model=azure_model,
#         result_type=List[CreativeVariation],
#         system_prompt=(
#             "You are a creative marketing copywriter. "
#             "Given a campaign brief, tone, and format, generate a list of creative ad copy variations. "
#             "For each, provide a meaningful, catchy name and the ad copy text. "
#             "Return a list of dicts: [{'name': ..., 'text': ...}]"
#         )
#     )
#     user_prompt = (
#         f"CAMPAIGN BRIEF: {prompt}\n"
#         f"TONE: {tone or 'Any'}\n"
#         f"FORMAT: {format_type or 'Any'}\n"
#         f"Generate {num_variations} creative ad copy variations. "
#         "Each should have a unique, catchy name and the ad copy text. "
#         "Return as a list of dicts: [{'name': ..., 'text': ...}]"
#     )
#     result = await agent.run(user_prompt)
#     return result.output

# async def generate_ab_testing_suggestions(prompt, variations):
#     azure_model = get_azure_model()
#     agent = Agent(
#         model=azure_model,
#         result_type=List[ABTestSuggestion],
#         system_prompt=(
#             "You are a digital marketing strategist. "
#             "Given a campaign brief and a list of creative variations, "
#             "suggest A/B testing hypotheses and what to measure for each variation. "
#             "Return a list of dicts: [{'variation_name': ..., 'hypothesis': ..., 'metric': ...}]"
#         )
#     )
#     user_prompt = (
#         f"CAMPAIGN BRIEF: {prompt}\n"
#         f"CREATIVE VARIATIONS: {', '.join([v.name for v in variations])}\n"
#         "For each variation, suggest a hypothesis for A/B testing and the key metric to measure. "
#         "Return as a list of dicts: [{'variation_name': ..., 'hypothesis': ..., 'metric': ...}]"
#     )
#     result = await agent.run(user_prompt)
#     return result.output

# async def generate_hashtags_and_social_posts(prompt, variations):
#     azure_model = get_azure_model()
#     agent = Agent(
#         model=azure_model,
#         result_type=List[SocialPost],
#         system_prompt=(
#             "You are a social media marketer. "
#             "Given a campaign brief and a list of creative variations, "
#             "generate for each: 3-5 relevant hashtags and a short social post (max 120 chars). "
#             "Return a list of dicts: [{'variation_name': ..., 'hashtags': [...], 'social_post': ...}]"
#         )
#     )
#     user_prompt = (
#         f"CAMPAIGN BRIEF: {prompt}\n"
#         f"CREATIVE VARIATIONS: {', '.join([v.name for v in variations])}\n"
#         "For each variation, generate 3-5 hashtags and a short social post (max 120 chars). "
#         "Return as a list of dicts: [{'variation_name': ..., 'hashtags': [...], 'social_post': ...}]"
#     )
#     result = await agent.run(user_prompt)
#     return result.output

# def generate_image(prompt):
#     base_url = "https://image.pollinations.ai/prompt/"
#     encoded_prompt = prompt.replace(" ", "%20")
#     cache_buster = str(int(time.time() * 1000))
#     return f"{base_url}{encoded_prompt}?cb={cache_buster}"

# def show_creative_asset_generator():
#     st.markdown("## 📝 Creative Asset Generator")
#     st.markdown("Generate ad copy, headlines, CTAs, and visual ideas for your campaign.")

#     creative_container = st.container()
#     with creative_container:
#         with st.form("creative_asset_form"):
#             campaign_brief = st.text_area(
#                 "Campaign Brief or Prompt",
#                 placeholder="Describe your campaign or product...",
#                 key="creative_campaign_brief"
#             )
#             tone_preference = st.text_input(
#                 "Tone Preference",
#                 placeholder="e.g., playful, professional",
#                 key="creative_tone_preference"
#             )
#             format_type = st.text_input(
#                 "Desired Format",
#                 placeholder="e.g., banner, poster",
#                 key="creative_format_type"
#             )
#             num_variations = st.number_input(
#                 "Number of Text Variations",
#                 min_value=1, max_value=10, value=3,
#                 key="creative_num_variations"
#             )
#             submitted = st.form_submit_button("Generate Creative Assets")

#         # Placeholders for each result section
#         variations_placeholder = st.empty()
#         images_placeholder = st.empty()
#         abtest_placeholder = st.empty()
#         social_placeholder = st.empty()
#         tips_placeholder = st.empty()

#         if submitted:
#             # Immediately clear previous results
#             variations_placeholder.empty()
#             images_placeholder.empty()
#             abtest_placeholder.empty()
#             social_placeholder.empty()
#             tips_placeholder.empty()

#             if not campaign_brief:
#                 st.error("Please enter a campaign brief or prompt.")
#                 return

#             with st.spinner("Generating creative assets..."):
#                 variations = asyncio.run(
#                     generate_creative_variations(
#                         campaign_brief, tone_preference, format_type, num_variations
#                     )
#                 )

#                 with variations_placeholder.container():
#                     st.markdown("### ✅ Generated Creative Variations:")
#                     for i, v in enumerate(variations, start=1):
#                         st.markdown(f"**{i}. {v.name}**")
#                         st.markdown(f"`{v.text}`")

#                 with images_placeholder.container():
#                     st.markdown("### 🖼️ Generated Images for Each Variation:")
#                     for i, v in enumerate(variations, start=1):
#                         image_url = generate_image(v.text)
#                         st.markdown(f"**{v.name} Image:**")
#                         st.image(image_url, caption=v.text)
#                         st.markdown(f"[Open Image in New Tab]({image_url})")

#                 ab_tests = asyncio.run(generate_ab_testing_suggestions(campaign_brief, variations))
#                 with abtest_placeholder.container():
#                     st.markdown("### 🧪 Dynamic A/B Testing Suggestions:")
#                     for ab in ab_tests:
#                         st.markdown(f"**{ab.variation_name}**")
#                         st.markdown(f"- Hypothesis: {ab.hypothesis}")
#                         st.markdown(f"- Metric: {ab.metric}")

#                 posts = asyncio.run(generate_hashtags_and_social_posts(campaign_brief, variations))
#                 with social_placeholder.container():
#                     st.markdown("### 🔖 Hashtags & Social Posts:")
#                     for post in posts:
#                         st.markdown(f"**{post.variation_name}**")
#                         st.markdown(f"- Hashtags: {' '.join(post.hashtags)}")
#                         st.markdown(f"- Social Post: {post.social_post}")

#                 with tips_placeholder.container():
#                     st.markdown("### 💡 Additional Tips:")
#                     st.markdown("""
#                     - Use the generated variations and images for A/B testing across your channels.
#                     - Try the suggested hashtags and social posts for organic reach.
#                     - Monitor the suggested metrics to determine the most effective creative assets.
#                     """)
"""Word cloud generation for derby names."""

import io
import base64
from wordcloud import WordCloud
import httpx

# API base URL
API_BASE = "http://localhost:8001/api"


async def generate_wordcloud_image() -> str:
    """
    Generate a word cloud from all derby names in the database.

    Returns:
        Base64 encoded PNG image string
    """
    try:
        # Fetch all names from the API
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE}/names", timeout=10.0)
            response.raise_for_status()
            names_data = response.json()

        # Extract just the names
        names = [item["name"] for item in names_data]

        if not names:
            # Return a placeholder if no names exist
            names = ["Generate", "Some", "Derby", "Names", "First!"]

        # Create word cloud text (repeat names based on favorites for emphasis)
        text_parts = []
        for item in names_data:
            # Add name once normally
            text_parts.append(item["name"])
            # Add favorites 3 more times to make them bigger
            if item.get("is_favorite", False):
                text_parts.extend([item["name"]] * 3)

        text = " ".join(text_parts) if text_parts else " ".join(names)

        # Generate word cloud
        wordcloud = WordCloud(
            width=1200,
            height=600,
            background_color="#1a1a2e",
            colormap="plasma",
            relative_scaling=0.5,
            min_font_size=10,
            max_words=100,
            prefer_horizontal=0.7,
            collocations=False,  # Don't treat phrases as single words
        ).generate(text)

        # Convert to PNG image in memory
        img_buffer = io.BytesIO()
        wordcloud.to_image().save(img_buffer, format="PNG")
        img_buffer.seek(0)

        # Encode as base64
        img_base64 = base64.b64encode(img_buffer.read()).decode()

        return f"data:image/png;base64,{img_base64}"

    except Exception as e:
        print(f"Error generating word cloud: {e}")
        # Return a simple error placeholder
        return ""

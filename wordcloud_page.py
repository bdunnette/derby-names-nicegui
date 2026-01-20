"""Simplified word cloud page with auto-load and colorful names."""

import httpx
import json

# API base URL
API_BASE = "http://localhost:8001/api"


async def create_wordcloud_page():
    """Create a simple animated word cloud visualization page."""
    from nicegui import ui

    # Header with navigation
    with ui.header().classes("items-center justify-between"):
        with ui.row().classes("items-center gap-4"):
            ui.label("🛼 Derby Names Word Cloud").classes("text-2xl font-bold")
            ui.link("← Back to Generator", "/").classes("text-white hover:underline")

    # Main content
    with ui.column().classes("w-full max-w-6xl mx-auto p-8 gap-4"):
        with ui.card().classes("w-full p-8"):
            ui.label("Animated Word Cloud").classes("text-2xl font-bold mb-4")
            ui.label(
                "Larger names appear more frequently. Favorites are emphasized!"
            ).classes("text-gray-600 mb-4")

            # Fetch names data
            async def get_words_data():
                """Fetch names and convert to word cloud format."""
                try:
                    async with httpx.AsyncClient() as client:
                        response = await client.get(f"{API_BASE}/names", timeout=10.0)
                        response.raise_for_status()
                        names_data = response.json()

                    if not names_data:
                        return []

                    # Convert to simple list with sizes
                    words = []
                    for item in names_data:
                        # Base size of 20, favorites get size of 40
                        size = 40 if item.get("is_favorite", False) else 20
                        words.append({"text": item["name"], "size": size})

                    return words
                except Exception as e:
                    print(f"Error fetching names: {e}")
                    return []

            # Initial data load
            words_data = await get_words_data()
            words_json = json.dumps(words_data)

            # Simple word cloud using CSS animations
            ui.html(
                """
                <div id="wordcloud-display" style="width: 100%; min-height: 600px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; padding: 40px; display: flex; flex-wrap: wrap; align-items: center; justify-content: center; gap: 20px;">
                    <!-- Words will be inserted here -->
                </div>

                <style>
                    .word-item {
                        font-family: 'Inter', 'Roboto', sans-serif;
                        font-weight: bold;
                        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                        transition: all 0.3s ease;
                        cursor: pointer;
                        animation: fadeIn 1s ease-in;
                    }

                    .word-item:hover {
                        transform: scale(1.2);
                        filter: brightness(1.3);
                    }

                    @keyframes fadeIn {
                        from { opacity: 0; transform: scale(0.5); }
                        to { opacity: 1; transform: scale(1); }
                    }
                </style>
            """,
                sanitize=False,
            ).classes("w-full")

            # Add JavaScript to populate the word cloud with varied colors
            ui.add_body_html(f"""
                <script>
                    // Color palette for word cloud
                    const colors = ['#fbbf24', '#f59e0b', '#fde68a', '#fcd34d', '#ffffff', '#fef3c7', '#fb923c', '#fdba74'];

                    function populateWordCloud(words) {{
                        const container = document.getElementById('wordcloud-display');

                        if (container && words.length > 0) {{
                            // Clear container
                            container.innerHTML = '';

                            // Shuffle words for random placement
                            const shuffled = words.sort(() => Math.random() - 0.5);

                            // Add each word
                            shuffled.forEach((word, index) => {{
                                const span = document.createElement('span');
                                span.className = 'word-item';
                                span.textContent = word.text;
                                span.style.fontSize = word.size + 'px';
                                span.style.animationDelay = (index * 0.1) + 's';

                                // Random color from palette
                                span.style.color = colors[Math.floor(Math.random() * colors.length)];

                                // Random rotation
                                if (Math.random() > 0.7) {{
                                    span.style.transform = 'rotate(90deg)';
                                }}

                                container.appendChild(span);
                            }});
                        }} else if (container) {{
                            container.innerHTML = '<p style="color: white; font-size: 24px;">No names generated yet. Go back and generate some!</p>';
                        }}
                    }}

                    // Auto-load on page load
                    setTimeout(function() {{
                        const words = {words_json};
                        populateWordCloud(words);
                    }}, 100);

                    // Make function globally available for refresh
                    window.refreshWordCloud = function(newWords) {{
                        populateWordCloud(newWords);
                    }};
                </script>
            """)

            # Refresh button
            async def refresh_cloud():
                """Refresh the word cloud data."""
                words_data = await get_words_data()
                words_json = json.dumps(words_data)

                # Update the word cloud
                ui.run_javascript(f"""
                    if (window.refreshWordCloud) {{
                        window.refreshWordCloud({words_json});
                    }}
                """)
                ui.notify("Word cloud refreshed!", type="positive")

            ui.button("🔄 Refresh Now", on_click=refresh_cloud).classes("mt-4").props(
                "color=purple"
            )

from datetime import timezone
import httpx
from nicegui import ui, app
from datetime import datetime
import uvicorn
import threading
from config import settings

API_BASE = f"http://localhost:{settings.API_PORT}/api"
API_PORT = settings.API_PORT
UI_PORT = settings.UI_PORT


class DerbyNameApp:
    """NiceGUI application for roller derby name generator."""

    def __init__(self):
        self.current_name = ""
        self.name_display = None
        self.names_container = None
        self.theme_toggle = None

        # Initialize storage if not exists
        if "saved_names" not in app.storage.user:
            app.storage.user["saved_names"] = []
        if "theme" not in app.storage.user:
            app.storage.user["theme"] = "auto"  # auto, light, or dark

    @property
    def saved_names(self):
        """Get saved names from app.storage."""
        return app.storage.user.get("saved_names", [])

    def toggle_theme(self):
        """Cycle through theme options: auto -> light -> dark -> auto."""
        current = app.storage.user.get("theme", "auto")
        themes = ["auto", "light", "dark"]
        next_index = (themes.index(current) + 1) % len(themes)
        new_theme = themes[next_index]
        app.storage.user["theme"] = new_theme

        # Update UI based on theme
        if new_theme == "auto":
            ui.dark_mode().auto()
        elif new_theme == "dark":
            ui.dark_mode().enable()
        else:
            ui.dark_mode().disable()

        # Update button icon
        if self.theme_toggle:
            icons = {
                "auto": "brightness_auto",
                "light": "light_mode",
                "dark": "dark_mode",
            }
            self.theme_toggle.props(f"icon={icons[new_theme]}")

    def save_name(self, name: str):
        """Save a name to app.storage."""
        names = self.saved_names
        # Create name entry with metadata
        name_entry = {
            "name": name,
            "created_at": datetime.now(timezone.utc),
            "is_favorite": False,
            "id": len(names) + 1,  # Simple ID generation
        }
        names.append(name_entry)
        app.storage.user["saved_names"] = names
        return name_entry

    async def generate_name(self):
        """Generate a new derby name via API and save to storage."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{API_BASE}/generate", timeout=30.0)
                response.raise_for_status()
                data = response.json()
                self.current_name = data["name"]

                # Save to app.storage
                self.save_name(self.current_name)

                # Update the display
                if self.name_display:
                    self.name_display.set_text(self.current_name)

                # Refresh the saved names list
                self.refresh_names_display()

                ui.notify(f"Generated: {self.current_name}", type="positive")
        except Exception as e:
            ui.notify(f"Error generating name: {str(e)}", type="negative")
            print(f"Error: {e}")

    def refresh_names_display(self):
        """Refresh the names display from app.storage."""
        if self.names_container:
            self.names_container.clear()
            with self.names_container:
                names = self.saved_names
                if not names:
                    ui.label("No saved names yet. Generate some!").classes(
                        "text-gray-500 italic"
                    )
                else:
                    # Show most recent first
                    for name_data in reversed(names):
                        self.create_name_card(name_data)

    def delete_name(self, name_id: int):
        """Delete a name from app.storage."""
        try:
            names = self.saved_names
            # Filter out the name with matching ID
            updated_names = [n for n in names if n["id"] != name_id]
            app.storage.user["saved_names"] = updated_names

            ui.notify("Name deleted", type="positive")
            self.refresh_names_display()
        except Exception as e:
            ui.notify(f"Error deleting name: {str(e)}", type="negative")

    def toggle_favorite(self, name_id: int):
        """Toggle favorite status of a name in app.storage."""
        try:
            names = self.saved_names
            for name in names:
                if name["id"] == name_id:
                    name["is_favorite"] = not name["is_favorite"]
                    break
            app.storage.user["saved_names"] = names

            self.refresh_names_display()
        except Exception as e:
            ui.notify(f"Error toggling favorite: {str(e)}", type="negative")

    def create_name_card(self, name_data: dict):
        """Create a card for a single derby name."""
        with ui.card().classes(
            "w-full p-4 hover:shadow-lg transition-shadow bg-white dark:bg-gray-700"
        ):
            with ui.row().classes("w-full items-center justify-between"):
                # Name and favorite star
                with ui.row().classes("items-center gap-2 flex-grow"):
                    star_icon = "⭐" if name_data["is_favorite"] else "☆"
                    ui.button(
                        star_icon,
                        on_click=lambda nid=name_data["id"]: self.toggle_favorite(nid),
                    ).props("flat round dense").classes("text-xl")

                    ui.label(name_data["name"]).classes(
                        "text-lg font-semibold text-purple-700 dark:text-purple-300"
                    )

                # Created date and delete button
                with ui.row().classes("items-center gap-2"):
                    try:
                        dt = datetime.fromisoformat(
                            name_data["created_at"].replace("Z", "+00:00")
                        )
                        date_str = dt.strftime("%Y-%m-%d %H:%M")
                    except Exception:
                        date_str = name_data["created_at"]

                    ui.label(date_str).classes(
                        "text-sm text-gray-500 dark:text-gray-400"
                    )
                    ui.button(
                        icon="delete",
                        on_click=lambda nid=name_data["id"]: self.delete_name(nid),
                    ).props("flat round dense color=red-6")

    async def build_ui(self):
        """Build the NiceGUI interface."""

        # Set initial theme
        theme = app.storage.user.get("theme", "auto")
        if theme == "auto":
            ui.dark_mode().auto()
        elif theme == "dark":
            ui.dark_mode().enable()
        else:
            ui.dark_mode().disable()

        # Header
        with ui.header().classes("items-center justify-between"):
            with ui.row().classes("items-center gap-4 flex-grow"):
                ui.label("🛼 Roller Derby Name Generator").classes("text-2xl font-bold")
                ui.link("Word Cloud", "/wordcloud").classes(
                    "text-white dark:text-gray-200 hover:underline"
                )

            # Theme toggle button
            with ui.row().classes("items-center gap-2"):
                icons = {
                    "auto": "brightness_auto",
                    "light": "light_mode",
                    "dark": "dark_mode",
                }
                self.theme_toggle = (
                    ui.button(icon=icons[theme], on_click=self.toggle_theme)
                    .props("flat round")
                    .classes("text-white")
                )
                ui.tooltip("Toggle theme (Auto/Light/Dark)").classes("text-sm")

        # Main content
        with ui.column().classes("w-full max-w-4xl mx-auto p-8 gap-8"):
            # Generator section
            with ui.card().classes("w-full p-8 bg-white dark:bg-gray-800"):
                ui.label("Generate Your Derby Name").classes(
                    "text-2xl font-bold mb-4 text-gray-900 dark:text-gray-100"
                )

                # Current name display
                with ui.card().classes("w-full p-6 bg-purple-50 dark:bg-purple-900/30"):
                    self.name_display = ui.label(
                        self.current_name or "Click generate to create a name!"
                    ).classes(
                        "text-3xl font-bold text-center text-purple-600 dark:text-purple-300 min-h-[60px]"
                    )

                # Generate button
                ui.button("🎲 Generate New Name", on_click=self.generate_name).classes(
                    "w-full mt-4 text-lg"
                ).props("color=purple")

            # Saved names section
            with ui.card().classes("w-full p-8 bg-white dark:bg-gray-800"):
                with ui.row().classes("w-full items-center justify-between mb-4"):
                    ui.label("📋 Saved Names").classes(
                        "text-2xl font-bold text-gray-900 dark:text-gray-100"
                    )
                    ui.label(f"{len(self.saved_names)} names").classes(
                        "text-gray-500 dark:text-gray-400"
                    )

                # Names container
                self.names_container = ui.column().classes("w-full gap-2")

        # Load initial data from storage
        self.refresh_names_display()


@ui.page("/")
async def index():
    """Main page."""
    derby_app = DerbyNameApp()
    await derby_app.build_ui()


@ui.page("/wordcloud")
async def wordcloud_page():
    """Word cloud visualization page using VueWordCloud."""
    from wordcloud_page import create_wordcloud_page

    await create_wordcloud_page()


def run_fastapi():
    """Run FastAPI server in a separate thread."""
    from api import app as fastapi_app
    from database import init_db

    # Initialize database
    init_db()

    # Run uvicorn
    uvicorn.run(fastapi_app, host="127.0.0.1", port=API_PORT, log_level="error")


def main():
    """Main entry point for the application."""
    # Start FastAPI in a background thread
    api_thread = threading.Thread(target=run_fastapi, daemon=True)
    api_thread.start()

    # Give FastAPI time to start
    import time

    time.sleep(2)

    # Run NiceGUI with storage
    ui.run(
        title="Roller Derby Name Generator",
        favicon="🛼",
        port=UI_PORT,
        reload=False,
        show=False,
        storage_secret="derby-names-secret-key-change-in-production",  # Required for app.storage
    )


if __name__ == "__main__":
    main()

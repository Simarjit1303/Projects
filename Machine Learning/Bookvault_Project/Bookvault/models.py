from typing import Dict, Any, List, Union


class Book:
    def __init__(self, **kwargs: Any) -> None:
        self.__dict__.update(kwargs)

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__

    @staticmethod
    def from_google_api(item: Dict[str, Any]) -> 'Book':
        info = item.get("volumeInfo", {})
        image_links = info.get("imageLinks", {})

        cover_url = (
            image_links.get("thumbnail") or image_links.get("smallThumbnail") or
            image_links.get("small") or image_links.get("medium") or
            image_links.get("large") or ""
        )

        if cover_url.startswith("http://"):
            cover_url = cover_url.replace("http://", "https://")
        if "zoom=" in cover_url:
            cover_url = cover_url.replace("zoom=1", "zoom=2")
        elif cover_url:
            cover_url = f"{cover_url}&zoom=2"

        return Book(
            id=item.get("id", ""),
            title=info.get("title", "Unknown"),
            author=", ".join(info.get("authors", ["Unknown"])),
            description=info.get("description", ""),
            cover_url=cover_url,
            publisher=info.get("publisher", ""),
            published_date=info.get("publishedDate", ""),
            page_count=info.get("pageCount", "N/A"),
            language=info.get("language", "en"),
            categories=info.get("categories", []),
            rating=info.get("averageRating", 0),
            info_link=info.get("infoLink", "")
        )

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class ArtworksItem(Item):
    """
    url: (string) URL of the work being scraped
    artist: (list of strings) List of artists for the work (we assume photographer, sculptor, designer etc are all artists)
    title: (string) Title of the work
    image: (string) URL of the image
    height: (float) Physical height in cm, only if available in cm
    width: (float) Physical width in cm, only if available in cm
    description: (string) Description of the work
    categories: (list of strings) Names of the categories visited to reach the item via the browse tree. Ex: ["Summertime", "Wrapper From", "Ao Shu"]
    """
    url: str = Field()
    artist: list[str] = Field()
    title: str = Field()
    image: str = Field()
    height: float = Field()
    width: float = Field()
    description: str = Field()
    categories: list[str] = Field()

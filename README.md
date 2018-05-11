# Cite Reddit

Creating a reference database from citations made on reddit.

**Database** is located at [citereddit Zotero Group][]  
**Complete Bibtex File** is ```citereddit.bib```.

# Intro

Many subreddits revolve around academic citations. [/r/Nootropics/][], [/r/DrugNerds/][], [/r/FoodNerds/][] are among my favorite sources for new science. Unfortunately, these academic reddits consist of a loose collection of urls. They lack the sharability of a bibliographic database.

I propose creating a research database through a popular reference manager like Zotero or Mendeley. We could, of course, do this manually, but ain't nobody got time for that. Scraping for citations automatically sounds like a better option.

The [announcement post][] on reddit explains the impetus and initial planning comments.

# Right now
The current version of citereddit is quite messy. It is controlled via command line like this:
```bash
python scrape.py -s [API_SECRET] -i [API_ID] -r [SUBREDDIT] -u [USERNAME] -p [PASSWORD]
```
In order for this to work, you must also have an active zotero translation server running (built from source) and have compiled the PRAW library with my changes yourself. I don't expect anyone to be able to do this. Future versions will be considerably more user friendly. For now, the script outputs three files for each call.

- library.bib
- main.log
- urls.txt

So a call for subreddit ```Nootropics``` produces ```Nootropics_library.bib``` etc.

Library.bib is in bibtex format and can be imported using a reference manager like Zotero. Main.log is a complete debug log for each run. ```urls.txt``` is a one-per-line list of urls imported by the script. If a url was successfully imported, the url is followed by ```**(successful)**```. This file and the debug information is intended to be used later to prevent duplicates.

# Process

1. scrape subreddit for links
2. import links to [Zotero][] using web translators
3. export group to [Mendeley][] or other formats

# Future Considerations

## Storage

- integrated reference manager group storage
- hosted storage
  - self
  - commercial
  - crypto

## Legality

Sharing the full-text content of references which are obtained from behind a paywall probably infringes copyright.

## Note Sharing

Zotero offers annotation syncing with each reference. Mendeley has group editing of pdfs. The bibtex citation format has a key for "notes".

## Integration

Reddit is not the only informal source of citations. [Examine][] is a very reputable source in the world of supplements, boasting hundreds of thousands of citations. It is referenced often on these subreddits. Integration with their internal reference database (if they have one) would be mutually beneficial.

# Current Issues
See ```TODO``` items in ```scrape.py```. There are many.

*Donations appreciated*
- BTC ```3M3K3YB1AwFG4kU1ssW4BUUJNyYTE2ueRg```
- LTC ```MVYaKVyzzdjmWLKeaPTayVhkpErRrn6qQd```
- ETH ```0x14F9eEF5FAeE331D5D7C352bBcdBa92E077E346d```
- BCH ```qq3ruthwuzj5z2ng20ct2jsxevumpgs7fgzx7c5rgv```

<!--links-->
[/r/Nootropics/]: https://reddit.com/r/Nootropics
[/r/DrugNerds/]: https://reddit.com/r/DrugNerds
[/r/FoodNerds/]: https://reddit.com/r/FoodNerds
[Zotero]: https://www.zotero.org/groups/2185229/citereddit/items
[Zotero translator dev]: https://www.zotero.org/support/dev/translators
[Mendeley]: https://www.mendeley.com/community/citereddit/
[announcement post]: https://www.reddit.com/r/Nootropics/comments/8hrwrh/nootropics_citation_database/
[Examine]: https://examine.com
[citereddit Zotero Group]:  https://www.zotero.org/groups/2185229/citereddit/items
<!--annotations-->

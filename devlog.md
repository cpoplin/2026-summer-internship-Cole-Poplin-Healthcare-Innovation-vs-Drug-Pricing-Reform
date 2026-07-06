# Starting Process
- Initially, I spent some time doing basic background research to form a foundation by which I could come to a conclusion, I looked into what regulations/acts affected what parts of the industry, what subsectors were affected in which way by these laws, and more. This is also where I formed the conclusion that regulations are pushing healthcare alpha away from small molecules into complex biologics.
- Next, I started to think about how I wanted to show this in data, and spent some time exploring different options on specifically subsector data (since within the pharmaceutical sector, all meaningfully large companies are diversified across multiple subsectors), this led to much "wasted" time researching and trying out different methods that didn't work.  Eventually I had to fall back onto simple yfinance, and basing my subsector data on companies that are most heavily concentrated in those subsectors, while still acknowledging the fact that this is a compromise in accuracy.
- After deciding how I was going to get data and the basic data I was going to use, I moved onto the "bronze" tier and began designing a basic data pipeline using python, yfinance, matplotlib, and pandas.

# Bronze tier
- After fetching the basic data, I had to spend some time tinkering with the graphs to make them presentable.
- Next, once I had the basic data down (essentially the "complex_biologics" and "small_molecules" basket graphs), I moved onto properly transforming the data to truly support my conclusion, and at this point I formed the more specific graphs, like the 2 event driven ones ("medicare_negot_event" and "small_molecule_patent_cliff") though technically those were added later to replace less effective graphs.
- Finally for the bronze tier, I added a verdict image ("verdict_summary") summarizing my findings and formally stating my conclusion, and the initial form of the powerpoint presentation.

# Silver tier
- After all of my data was set up, I created an interactive streamlit ui for the project, which in large part consisted of prompting an AI with my vision of a UI and how it should showcase the data I already had, down to the 3 pages and what each should show. Though I also spent some time refining its output to be more in line with my vision.

# Gold tier
- tbd

# Miscellaneous
- Minor details were edited all throughout to as my vision for the project evolved.
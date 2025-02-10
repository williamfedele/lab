Small experiment to see if obsidian could handle displaying wikipedia as a graph (it can't, on my machine at least).

Using the wikipedia dump, I preprocess the file and only keep page titles and link labels. Then I cleaned the links. I could've done these simultaneously, but the file is quite hard to work with at over 100GB, so I chose to sequentially clean it up. Finally, I create a directory for the vault and create a file for each page title, and insert its links inside in Obsidian format with double square brackets.

In total, there were 6.8 million pages with 233 million links. There are surprisingly more redirect links than real pages, 11 million pages redirecting to 6.8 million real pages. The original wikipedia dump is about 108GB. The cleaned XML file took 8.1GB. The Obsidian vault was nearly 38GB. Unfortunately, Obsidian becomes unresponsive and crashes on the machine used for the experiment.

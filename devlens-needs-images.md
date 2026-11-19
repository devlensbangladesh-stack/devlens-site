# Devlens stories waiting for a better image

Images: Gemini in Chrome first, to the Devlens standard (realistic editorial illustration, Bangladesh setting, no real faces, no text or logos, alt text starting "AI-generated illustration:"). When Chrome is not available, use a free-licence real photo (public domain, CC0, CC BY or CC BY-SA) from Wikimedia Commons or Openverse, with credit. A clearly labelled file photo (credit starting "File photo") is fine for running stories, as the owner asked for the COP31 lead. Never use Canva or free online AI image generators. Never reuse an image already on the site. Do not use photos of identifiable politicians or public figures, except official government photos of an official event the story reports (see below). Check every photo before publishing: reject any with political posters, party banners or portraits of politicians in the background.

Prime Minister rule (owner, 11 Nov 2026): when the Bangladeshi Prime Minister is in the news, use a PID photo of that event as the story image, ahead of Gemini or other photos.

Real photos for news events (owner asked on 11 Nov 2026 to use Bangladesh government official photos too):
- Use: Press Information Department (PID, pressinform.gov.bd) photos. Wikimedia Commons hosts them as public domain, in categories "PID-BD images from <Month> <Year>" and "Bangladesh photographs taken on <date>". In a Chrome tab on a commons.wikimedia.org page, fetch '/w/api.php?action=query&list=categorymembers&cmtitle=Category:PID-BD_images_from_<Month>_<Year>&cmsort=timestamp&cmdir=desc&cmlimit=40&format=json' with javascript_tool and match the event and date (WebFetch cannot reach the Commons API). Check the licence says public domain, and credit "Press Information Department, Government of Bangladesh, via Wikimedia Commons (public domain)" with a link to the Commons file page.
- Do not use: BSS (bssnews.net) photos. The site footer says "Copyright © 2026 BSS. All Rights Reserved." Newspaper and agency photos (Daily Star, Prothom Alo, AP, Getty and similar) are also off limits.
- International events: European Commission audiovisual photos on Commons are CC BY 4.0 (credit the photographer / European Union). UN Climate Change Flickr photos are CC BY-NC-SA, so do not use them.

How to get free-licence photos onto the site:
- With Chrome (12 Nov 2026): search Commons from a Chrome tab on commons.wikimedia.org (open a normal page first, then run the API in javascript_tool) with generator=search, namespace 6, prop=imageinfo, iiurlwidth=1280, origin=*; filter to PD, CC0, CC BY, CC BY-SA, landscape, 1200 px or wider. Show 330px thumbnails in a grid in the tab and screenshot to choose. Printing URLs from the page is blocked by the tool; print titles, licence and author only.
- Without Chrome (13 Nov 2026): dispatch the repo's photos.yml workflow with a queries map; read the contact sheets and JSON from the photo-candidates branch (git archive). This worked for "COP31 Antalya" (PID and EU photos) and "Bangladesh coastal embankment".
- Queue each pick in photo-queue.json with a Special:FilePath URL (or the candidate's url) and a NEW, unique path; the GitHub Action downloads, crops and sets the image. It skips a path that already exists, so never reuse a file name.
- Then open each saved file and check it before calling it done.
- Good search terms that worked: "Karail", "NGO Affairs Bureau", "Union Building" (Union Parishad offices by Rafi Bin Tofa), "Government Primary school buildings", "Rajshahi Medical College Hospital" wards, "Aedes aegypti", "Padma Bridge Road", "Karwan Bazar", "Bangladesh coastal embankment".
- Dengue: PID dengue photos all show officials with identifiable patients; do not use them. Generic Aedes photos are mostly used already.
- Note (13 Nov afternoon and 10pm runs, 14 Nov morning runs, 15 Nov morning run): the cloud session had no GitHub push access and could not reach commons.wikimedia.org, upload.wikimedia.org or api.openverse.org (egress proxy refuses them), so no photos could be searched, queued or checked. The stories below were saved in the pending patch with "image": null.

Gemini in Chrome: images can be generated, but Chrome blocks reading the image data out of the page, and saving needs the owner's Downloads folder. The owner declined Downloads access on 12 Nov 2026, so do not ask again unless the owner raises it.

Still waiting:
- Note (19 Nov 2026, 08:30 Dhaka): all 22 stories that had "image": null (the fertiliser story, 11 from 18 Nov and 10 from 19 Nov) got free-licence photos via the photos.yml workflow (dispatched through the REST API, gh api .../actions/workflows/photos.yml/dispatches) and were queued in photo-queue.json. Every story on the site now has an image. Good new search terms: "Dhaka Shanty Slum", "Mugda hospital", "tobacco Kushtia", "rice seedlings Bangladesh", "solar panels Bangladesh", "Savar garment", "Grand Hall de Justice".
- Note (19 Nov 2026, afternoon run): no GitHub push access and commons.wikimedia.org refused by the egress proxy, so these 12 stories went out in the patch with "image": null. Suggested searches in brackets:
  - titumir-brac-dialogue-multi-year-funding-rohingya-youth-income-return-study ("Kutupalong camp youth")
  - un-third-committee-rohingya-resolution-128-votes-jrp-funding-access ("UN General Assembly Hall")
  - ipc-18-1-million-acute-food-insecurity-prices-squeeze-families ("Bangladesh market rice stall")
  - measles-deaths-1336-health-scorecard-leaves-out-measles ("measles vaccine vial")
  - sylhet-measles-223-deaths-three-infants-die-osmani-hospital ("Osmani Medical College Hospital")
  - cyclone-akvan-heavy-rain-five-divisions-saint-martins-tourists-stranded ("Saint Martin's Island jetty")
  - grameen-bank-office-muksudpur-gopalganj-set-on-fire ("Grameen Bank branch")
  - garment-workers-council-demands-tk-32000-wage-buyers-hold-orders-factories-shut ("Gazipur garment factory")
  - pm-10000-workers-malaysia-cost-cap-recruitment-syndicates-parliament ("Hazrat Shahjalal Airport migrant workers")
  - pm-3500-hospital-beds-added-40-lakh-patients-on-floors-rangabali ("Rangabali" or "Patuakhali hospital")
  - financial-inclusion-survey-35-percent-excluded-women-agent-banking-half ("mobile banking agent Bangladesh")
  - haor-farmers-brri-dhan-118-early-rice-beat-flash-floods ("Tanguar haor paddy")

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
- dengue-1960-admissions-481-deaths-november-12 (13 Nov; idea: an empty hospital corridor or ward with mosquito nets, no faces; or a dengue-related street scene such as water collecting in discarded containers)
- measles-deaths-1304-dengue-483-november-13 (13 Nov afternoon; idea: a vaccination cold box or vaccine vials at a health centre, a children's ward building exterior, no identifiable children)
- cop31-bangladesh-adaptation-need-8-5-billion-under-half-billion-international (13 Nov afternoon; idea: a cyclone shelter in coastal Bangladesh, search "cyclone shelter Bangladesh"; or an EU audiovisual COP31 venue photo)
- government-plans-cancer-centres-divisions-national-molecular-biology-lab (13 Nov afternoon; idea: National Institute of Cancer Research and Hospital building in Mohakhali, or a laboratory scene, no patients)
- cpd-nazneen-ahmed-late-wage-board-garment-unrest (13 Nov afternoon; idea: a garment factory exterior or workers' commute in Savar/Ashulia not yet used on the site; no portraits)
- plan-international-ceo-reena-ghelani-visits-bangladesh-girls-education (13 Nov, 10pm run; idea: a learning centre building or classroom exterior in Kutupalong camp not yet used, no identifiable children; or a girls' secondary school exterior)
- rohingya-food-aid-funded-until-april-2027-rations-malnutrition (14 Nov morning, lead on 14 Nov, now Also today; idea: a WFP e-voucher food outlet or food distribution point in Kutupalong camp, sacks of rice and lentils, no identifiable children; search "Kutupalong", "WFP Rohingya", "Rohingya camp market")
- malaysia-migration-cost-capped-tk-1-54-lakh-boesl-zero-cost (14 Nov morning; idea: Probashi Kalyan Bhaban or BMET building exterior, or migrant workers at Dhaka airport departure seen from behind)
- diabetes-seven-in-10-unaware-bdhs-world-diabetes-day (14 Nov morning; idea: a glucometer and test strips, or a hospital building exterior such as BIRDEM, no patients' faces)
- garment-workers-oms-rice-tk-30-kg-66-trucks (14 Nov morning; idea: an OMS/TCB rice truck queue seen from behind, or sacks of rice at a market such as Karwan Bazar not yet used)
- information-commission-resumes-rti-hearings-november-16-after-two-years (14 Nov late morning; idea: a government office building exterior in Dhaka such as the Secretariat or Agargaon offices, or shelves of files; no officials' faces)
- class-one-admission-age-raised-to-six-government-schools-2027 (14 Nov late morning; idea: a government school building exterior not yet used, or an empty classroom with benches; no identifiable children)
- government-plans-tk-300-crore-animal-vaccine-plant-cut-imports (14 Nov late morning; idea: cattle or goats in a rural Bangladeshi homestead, or poultry farm; search "cattle Bangladesh", "Black Bengal goat")
- cyber-law-revised-draft-rumour-penalty-cut-five-years-comments-november-25 (15 Nov morning, HOMEPAGE LEAD, highest priority; idea: a laptop or phone screen with no readable text, or the ICT Tower / Bangladesh Computer Council building in Agargaon; no faces)
- bgmea-no-work-no-pay-section-13-147-factories-wage-board-november-16 (15 Nov; idea: a closed factory gate in Ashulia or Gazipur, or the BGMEA complex in Uttara; no identifiable workers)
- dengue-64-deaths-23880-admissions-first-13-days-november (15 Nov; idea: larvicide spraying or stagnant water at a construction site, no faces)
- press-council-act-amendment-journalist-registration-education-criteria (15 Nov; idea: newspaper stacks at a stall or the National Press Club building exterior; avoid readable mastheads)
- usda-cuts-bangladesh-rice-import-forecast-1-1-million-tonnes (15 Nov; idea: aman paddy harvest in a field, or rice sacks at a government warehouse; search "aman harvest Bangladesh", "paddy field Bangladesh")
- adp-implementation-record-low-6-53-percent-july-october-health-disaster (17 Nov evening; idea: Planning Commission buildings in Sher-e-Bangla Nagar, or a stalled construction site)
- cyclone-akvan-bay-of-bengal-signal-2-seaports (17 Nov evening; idea: fishing trawlers moored at Cox's Bazar or Mongla, or a cyclone shelter exterior)
- upazila-health-complexes-48-percent-doctor-posts-vacant-parliament (17 Nov evening; idea: an upazila health complex building exterior, no patients' faces)
- bangladesh-health-watch-report-corruption-health-sector-governance (17 Nov evening; idea: medical supply boxes in a storeroom, or an empty hospital corridor)
- bangladeshi-workers-stranded-sri-lanka-false-job-promises-survivor-group (17 Nov evening; idea: Bandaranaike airport exterior in Katunayake, or luggage seen from behind)
- Note (18 Nov night): all 11 stories from the 18 Nov morning update now have free-licence photos, found with the photos.yml workflow (push photo-searches.json to main, read the photo-candidates branch) and queued in photo-queue.json. Good new search terms: "Kutupalong refugee camp", "Pashur River Mongla", "Grameen Bank building", "MAG Osmani Medical College Hospital", "upazila health complex Bangladesh".

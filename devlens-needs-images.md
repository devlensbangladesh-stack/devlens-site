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
- Note (18 Nov night): all 11 stories from the 18 Nov morning update now have free-licence photos, found with the photos.yml workflow (push photo-searches.json to main, read the photo-candidates branch) and queued in photo-queue.json. Good new search terms: "Kutupalong refugee camp", "Pashur River Mongla", "Grameen Bank building", "MAG Osmani Medical College Hospital", "upazila health complex Bangladesh".
- fertiliser-dealerships-party-ties-bribery-allegations-boro-season (15 Nov; no usable free photo found on 18 Nov: Commons results were PID ceremonies with politicians or composting demos. Idea: a fertiliser dealer's shop or sacks of urea at a rural market, or a boro seedbed; try "boro seedbed", "fertiliser shop Bangladesh")
- Note (18 Nov night, second pass): every other story on the site now has an image. The 13-17 Nov entries above had already been given photos in earlier runs and were stale on this list; 8 more stories (ADP, cyclone Akvan, upazila doctor posts, Health Watch, Sri Lanka workers, Cox's Bazar debt conference, HRW Rohingya education, narrow bridges/rivers) got photos tonight.
- Note (18 Nov afternoon run, fired late at 23:34): GitHub push refused again (git proxy 403, repository not in this session's authorised set) and commons.wikimedia.org refused by the egress proxy, so no photos could be searched or queued. The stories below are in the patch with "image": null.
- un-rapporteur-kelley-currie-dhaka-warns-violence-rohingya-icj-ruling (idea: UN House Dhaka exterior, or Kutupalong camp from a distance, no identifiable children)
- cyclone-akvan-severe-signal-3-chattogram-coxs-bazar-mongla-payra (idea: fishing trawlers moored at Cox's Bazar or Chattogram, search "fishing boats Cox's Bazar")
- adb-report-adaptive-social-protection-bangladesh-climate-shocks (idea: a cyclone shelter in coastal Bangladesh, search "cyclone shelter Bangladesh")
- global-shield-climate-risk-grants-bangladesh-30-million-euros (idea: a flooded rural road or embankment, search "flood Bangladesh embankment"; or an EU audiovisual COP31 photo)
- foreign-aid-disbursement-down-60-percent-default-loans-32-percent (idea: Sher-e-Bangla Nagar planning area or ERD building exterior, search "Sher-e-Bangla Nagar")
- hrss-111-people-faced-action-expressing-views-january-october-2026 (idea: Jatiya Press Club building exterior, search "National Press Club Dhaka")
- dengue-1674-admissions-508-deaths-november-18 (idea: mosquito net over an empty hospital bed, no patients)
- wewb-tk-564-crore-deposits-stuck-sammilito-islami-bank-migrant-welfare (idea: Probashi Kallyan Bhaban, Eskaton, exterior; search "Probashi Kallyan Bhaban")
- alrd-angoc-land-food-sovereignty-conference-farmer-input-card (idea: smallholder farmer's paddy field, no identifiable faces; a view not yet used on the site)
- brick-kilns-phase-out-7-8-years-environment-minister-parliament (idea: brick kiln chimneys near Dhaka, search "brick kiln Bangladesh")
- cpd-garment-minimum-wage-range-tk-18578-24204 (idea: garment factory exterior in Gazipur not yet used; no portraits)
- Note (19 Nov morning run): GitHub push refused again (git proxy 403) and commons.wikimedia.org refused by the egress proxy, so no photos could be searched or queued. Search terms for all 11 stories below are in photo-searches.json, so the photos workflow runs as soon as this patch reaches main. The stories below have "image": null.
- icj-rohingya-genocide-verdict-today-dhaka-seeks-accountability-repatriation (19 Nov, HOMEPAGE LEAD, highest priority; idea: Peace Palace in The Hague exterior, search "Peace Palace The Hague"; or Kutupalong camp from a distance, no identifiable children)
- devlens-analysis-icj-rohingya-ruling-what-it-can-and-cannot-change (idea: International Court of Justice courtroom or Peace Palace, a different view from the lead; search "International Court of Justice Great Hall of Justice")
- garment-unrest-640-factories-shut-union-leaders-arrested-wage-board-23-november (idea: closed factory gate or highway in Ashulia/Gazipur, no identifiable workers)
- ecnec-approves-16-projects-tk-33298-crore-canal-excavation-64-districts (idea: a canal or khal in rural Bangladesh, search "canal Bangladesh village")
- adb-1000-mw-solar-battery-storage-ppp-monitor-country-strategy-2028-2032 (idea: a solar farm in Bangladesh, search "solar park Bangladesh")
- mohakhali-sattola-slum-fire-100-families-homeless (idea: a Dhaka slum skyline or Korail from a distance, no faces; search "Korail slum")
- coxs-bazar-jhau-trees-felled-tourism-carnival-forest-department-no-permission (idea: casuarina trees on Cox's Bazar beach, search "Casuarina Cox's Bazar")
- tobacco-control-law-amendment-awareness-ngo-affairs-bureau-csr-curbs (idea: a no-smoking sign, or cigarette packs at a tea stall without readable brands)
- secondary-education-project-revision-laptops-e-buses-library-grants-cut (idea: a school library or secondary school building exterior, no identifiable children)
- special-solar-power-installation-bill-2026-passed-farmland-tender-concerns (idea: rooftop solar panels or solar home system in rural Bangladesh, search "solar home system Bangladesh")
- high-court-halts-public-university-admission-tests-december-31-hsc (idea: Supreme Court of Bangladesh building, search "Supreme Court of Bangladesh")

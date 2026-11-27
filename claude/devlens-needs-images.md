# Devlens stories waiting for a better image

**Lead story rule (owner, 24 Nov 2026): the lead must always have a photo.** Do the lead's photo first, before other stories, using the steps in `homepage-rules.md` (Lead photo). If no photo of the event is available, use any public domain or openly licensed photo of the subject (Wikimedia Commons, Openverse, Flickr Commons, PID), with credit. Other new stories may go out with `"image": null` and be listed below.

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
- Note (24 Nov 2026, morning run): photos queued in photo-queue.json for 10 of the 12 stories above, picked from the photo-candidates contact sheets. Still waiting:
  - measles-deaths-1336-health-scorecard-leaves-out-measles (no suitable photo: the PID vaccination photos show ministers; try "measles rubella vaccine Bangladesh" or "child vaccination Bangladesh clinic")
  - financial-inclusion-survey-35-percent-excluded-women-agent-banking-half (the "bKash agent" search found nothing usable; try "mobile banking Bangladesh" or "bKash")
- Note (24 Nov 2026, 11:20 Dhaka): photos queued and checked for 3 of the 9 new stories (ICJ verdict, Teknaf trafficking, maternal deaths research summary). Still "image": null, with better search ideas:
  - wage-board-owners-tk-15800-workers-tk-22000-talks-resume-november-24 ("Savar garment factory", "sewing machine Bangladesh"; the Gazipur search returned only PID ceremonies and a protest photo)
  - uk-400-million-climate-investment-funds-bangladesh-rohingya-icj-pressure ("solar panels Bangladesh rooftop"; PID results showed politicians)
  - faridpur-medical-college-hospital-1425-patients-500-beds-staff-shortage ("Faridpur Medical College Hospital building"; only hostels and a mosque came back)
  - high-court-orders-policy-social-media-children-16-icddrb-screen-time ("smartphone child", "Supreme Court of Bangladesh building")
  - draft-national-sme-policy-2026-25-lakh-jobs-2031-women-entrepreneurs ("Bangladesh handicrafts", "nakshi kantha")
  - walk-for-humanity-teknaf-dhaka-hill-children-education-bandarban ("Bandarban village", "Lama Bandarban")
- Note (24 Nov 2026, 20:07 Dhaka morning run, fired late): 9 new pieces published with "image": null. No photo search was run this session. Suggested searches in brackets:
  - wage-board-owners-tk-15700-workers-tk-22000-481-factories-halted: DONE 25 Nov, file photo "RMG Bangladesh" (Fahad Faisal, CC BY-SA 4.0)
  - grameen-bank-nearly-100-branches-attacked-november-yunus-statement ("Grameen Bank branch", "Grameen Bank building Mirpur")
  - measles-nine-deaths-with-symptoms-1351-new-cases-day-after-first-zero-death-day ("measles rubella vaccine", "child vaccination Bangladesh clinic")
  - ilo-blf-project-keraniganj-garment-hub-child-labour-4500-children ("Keraniganj", "Buriganga Keraniganj"; no identifiable children)
  - incepta-medogen-subq-first-self-injectable-contraceptive-bangladesh ("contraceptive injection", "Sayana Press", "family planning Bangladesh")
  - canada-preferential-market-access-until-2032-ldc-graduation-bilateral-consultations ("Chittagong port containers", "Canada flag")
  - bangladeshi-workers-stranded-laos-bmet-clearance-no-jobs-passports-held ("Vientiane", "Bangladeshi passport")
  - rti-forum-information-commission-independence-commissioners-parity-judges ("Information Commission Bangladesh", "Agargaon Dhaka")
  - devlens-research-summary-bids-bci-industry-100-power-gas-cuts-stall-factory-output ("textile mill Bangladesh", "spinning mill", "electricity pylons Bangladesh")
- Note (25 Nov 2026, morning run): photos queued in photo-queue.json for 5 of 9 new pieces (wage board Tk 17,000 lead, battery-rickshaw study, antivenom project, HEU hospital-benefits study, MICS district atlas research summary). Still "image": null, with search ideas:
  - measles-vaccine-questions-iedcr-antibody-study-24-percent-unprotected ("measles rubella vaccine vial", "vaccine cold box"; no identifiable children)
  - mjf-dialogue-violence-against-women-only-7-percent-take-legal-action-16-days ("Orange the World", "16 Days of Activism")
  - ukraine-trafficking-probe-bangladeshis-russian-military-fortify-rights-104-recruited ("Hazrat Shahjalal International Airport", "Bangladeshi passport")
  - amnesty-cyber-security-amendment-draft-content-blocking-powers-free-expression ("smartphone social media", "internet cafe Dhaka")
- Note (26 Nov 2026, morning run): photos queued for the AMR lead (antibiotic blister packs, Thilini ukwaththage, CC BY-SA 4.0) and the children's hospitals story (Rangpur Medical College file photo). Still "image": null, with search ideas (both Kutupalong VOA photos are already used):
  - devlens-research-summary-unhcr-q3-2026-rohingya-protection-security-incidents-up-39-percent-registration-suspended ("Balukhali camp", "Rohingya camp shelters Ukhia", "Bhasan Char")
  - garment-workers-protest-tk-17000-wage-gazipur-300-factories-suspend-production ("Gazipur highway", "Dhaka-Mymensingh highway"; no protest photos with identifiable workers)
  - tax-justice-network-bangladesh-lost-2-26-billion-tax-abuse-2023-161-percent-health-spending ("NBR building Agargaon", "Bangladeshi taka notes")
  - police-887-dowry-murder-cases-five-years-odhikar-21627-rape-victims-since-2001-half-girls ("Orange the World Dhaka", "16 Days of Activism Bangladesh")
  - khulna-ngo-official-home-shot-at-after-tk-6-5-lakh-extortion-demand-cas-ava-centre ("Khulna city street", "Khulna Rupsha")
  - okup-study-91-percent-migrant-workers-no-written-contract-bmet-arbitration-recruitment-fees ("BMET Dhaka", "Bangladeshi passport"; PID airport photos show politicians)
  - government-bicycles-300000-schoolgirls-classes-six-to-ten-dropout-20000-schools ("bicycle rural road Bangladesh", "secondary school Bangladesh building"; no identifiable children)

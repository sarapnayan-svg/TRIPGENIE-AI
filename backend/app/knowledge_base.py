"""
Curated Travel Knowledge Base for TripGenie AI RAG Pipeline.

Each entry is a structured document chunk containing verified travel intelligence:
- destination: City/State name
- place_name: Specific sight, beach, fort, or area
- category: overview, attractions, food, stay, budget, best_time, tips
- description: Detailed factual explanation
- location: Geographical region or district
- activities: List of key things to do
- estimated_cost: Approximate expense or entry fee in INR
- best_time: Optimal visiting months / hours
- duration: Suggested time to spend
- travel_tips: Practical insider advice
- text: Unified semantic text representation used for vector embedding
"""

TRAVEL_DOCUMENTS = [
    # =========================================================================
    # GOA
    # =========================================================================
    {
        "id": "goa-overview-01",
        "destination": "Goa",
        "place_name": "Goa Coastal State",
        "category": "overview",
        "description": "Goa is India's premier coastal holiday state on the western Arabian Sea shore, famed for golden sandy beaches, Portuguese colonial churches, spice plantations, and relaxed seaside nightlife.",
        "location": "Konkan Coast, Western India",
        "activities": ["Beach leisure", "Heritage walks", "Seafood dining", "Coastal photography"],
        "estimated_cost": "Moderate (₹2,500 - ₹5,000 / day / person)",
        "best_time": "November to February",
        "duration": "4 to 7 days",
        "travel_tips": "Rent a two-wheeler for effortless transit between North and South beaches. Carry cash for beach shacks.",
        "text": "Goa coastal state on India's western shore known for beaches, Portuguese-era churches, relaxed nightlife, seafood shacks, and water sports. Suits families, couples, and adventure travelers."
    },
    {
        "id": "goa-attractions-baga",
        "destination": "Goa",
        "place_name": "Baga & Calangute Beach",
        "category": "attractions",
        "description": "The epicenter of North Goa's coastal action, offering continuous golden sand, lively beach shacks, parasailing, jet-skis, and evening music.",
        "location": "North Goa, 16 km from Panaji",
        "activities": ["Parasailing", "Jet-skiing", "Banana boat rides", "Shack lounging", "Sunset viewing"],
        "estimated_cost": "Free entry; Water sports combos ₹1,200 - ₹2,500",
        "best_time": "Early morning 8 AM or Sunset 5 PM",
        "duration": "Half day (3-4 hours)",
        "travel_tips": "Book water sports at authorized counters with safety jackets. Bargain for combo packages.",
        "text": "Top attractions in Goa include Baga Beach and Calangute Beach for watersports, jet-ski, parasailing, dolphin boat rides, and lively beachside shacks."
    },
    {
        "id": "goa-attractions-aguada",
        "destination": "Goa",
        "place_name": "Fort Aguada & Lighthouse",
        "category": "attractions",
        "description": "A well-preserved 17th-century Portuguese fortress and historic 4-tier lighthouse commanding panoramic views of the Mandovi River meeting the Arabian Sea.",
        "location": "Sinquerim, North Goa",
        "activities": ["Historical fort exploration", "Lighthouse sightseeing", "Panoramic sea photography"],
        "estimated_cost": "₹25 for Indians, ₹300 for Foreigners",
        "best_time": "9:30 AM to 5:30 PM (Late afternoon best for light)",
        "duration": "1.5 to 2 hours",
        "travel_tips": "Wear comfortable walking shoes. Climb to the upper ramparts for sweeping views of the coastline.",
        "text": "Fort Aguada is a 17th-century Portuguese coastal fortress overlooking the Arabian Sea in Sinquerim, North Goa. Key attraction for heritage, history, and sunset photography."
    },
    {
        "id": "goa-attractions-oldgoa",
        "destination": "Goa",
        "place_name": "Basilica of Bom Jesus & Old Goa",
        "category": "attractions",
        "description": "UNESCO World Heritage Site housing the sacred mortal remains of St. Francis Xavier, featuring baroque architecture and ornate gilded altars.",
        "location": "Old Goa (Velha Goa), 10 km east of Panaji",
        "activities": ["Heritage church visit", "Religious history tour", "Art gallery viewing"],
        "estimated_cost": "Free entry",
        "best_time": "9:00 AM to 6:00 PM (Sundays 10:30 AM to 6:00 PM)",
        "duration": "2 hours",
        "travel_tips": "Modest dress code required covering shoulders and knees. Visit Se Cathedral directly opposite.",
        "text": "Basilica of Bom Jesus in Old Goa is a UNESCO World Heritage site holding the mortal remains of St. Francis Xavier, showcasing Portuguese baroque architecture."
    },
    {
        "id": "goa-attractions-palolem",
        "destination": "Goa",
        "place_name": "Palolem Beach & Butterfly Island",
        "category": "attractions",
        "description": "A tranquil crescent bay framed by swaying coconut palms in South Goa, famous for calm swimming waters, colorful beach huts, and boat trips to secluded Butterfly Island.",
        "location": "Canacona, South Goa",
        "activities": ["Calm ocean swimming", "Kayaking", "Dolphin spotting boat rides", "Silent noise disco"],
        "estimated_cost": "Free entry; Boat to Butterfly Beach ₹1,000 - ₹1,500/boat",
        "best_time": "Sunrise to late evening",
        "duration": "Full day or overnight stay",
        "travel_tips": "Rent a kayak early morning to explore the sheltered northern end of the bay.",
        "text": "Palolem Beach in South Goa features a scenic crescent bay, gentle waters, colorful beach huts, and boat trips to Butterfly Beach and dolphin watching."
    },
    {
        "id": "goa-food-cuisine",
        "destination": "Goa",
        "place_name": "Goan Coastal & Portuguese Dining",
        "category": "food",
        "description": "Goan cuisine harmonizes Konkani coastal seafood with 450 years of Portuguese culinary influence, featuring tangy kokum, coconut milk, and fiery peri-peri spices.",
        "location": "Across beach shacks, Panaji Latin Quarter, and coastal taverns",
        "activities": ["Seafood tasting", "Beach shack dining", "Portuguese dessert indulgence"],
        "estimated_cost": "₹400 - ₹1,200 per person per meal",
        "best_time": "Lunch (12:30 PM - 3:30 PM) and Dinner (7:30 PM - 11:00 PM)",
        "duration": "1-2 hours",
        "travel_tips": "Try authentic Goan fish thali at local eateries like Ritz Classic or Fisherman's Wharf.",
        "text": "Goan food highlights include fish curry rice, prawn balchao, crab xec xec, bebinca layered dessert, chicken cafreal, and Portuguese-influenced pork vindaloo."
    },
    {
        "id": "goa-stay-resorts",
        "destination": "Goa",
        "place_name": "Goa Resorts & Boutique Stays",
        "category": "stay",
        "description": "North Goa provides lively resorts near nightlife corridors (Candolim, Baga, Vagator), while South Goa offers tranquil luxury beachfront havens (Benaulim, Cavelossim, Palolem).",
        "location": "North & South Goa coastal strips",
        "activities": ["Resort pool relaxation", "Spa therapies", "Beachfront breakfast"],
        "estimated_cost": "Budget hostels ₹1,200 - ₹2,500; 3/4-star ₹4,000 - ₹8,500; 5-star ₹14,000+",
        "best_time": "Year-round (Peak pricing Dec 20 - Jan 5)",
        "duration": "Overnight",
        "travel_tips": "Stay in North Goa for nightlife and sports; choose South Goa for peace, couples, and family relaxation.",
        "text": "Accommodation in Goa: North Goa (Baga, Calangute, Candolim) features lively resorts and nightlife; South Goa (Palolem, Colva, Agonda) offers quiet beach resorts and wellness retreats."
    },
    {
        "id": "goa-budget-estimate",
        "destination": "Goa",
        "place_name": "Goa Financial Planning",
        "category": "budget",
        "description": "A comprehensive 5-day holiday for a group of 4 travelers covers 3-star comfortable resorts, hired transport, water sports packages, and multi-cuisine dining.",
        "location": "Goa State",
        "activities": ["Budget allocation", "Group travel planning"],
        "estimated_cost": "Rs 80,000 to Rs 1,20,000 for 4 people across 5 days",
        "best_time": "Shoulder season (Oct-Nov or Feb-Mar) offers great rates",
        "duration": "5 Days",
        "travel_tips": "Splitting private cab rentals or scooter hires across 4 travelers significantly lowers transit expenses.",
        "text": "A mid-range 5-day Goa trip for 4 people typically costs Rs 80,000 to Rs 1,20,000 including 3-star stay, local transport, food, and water sports activities."
    },
    {
        "id": "goa-tips-besttime",
        "destination": "Goa",
        "place_name": "Goa Seasonality & Practical Tips",
        "category": "tips",
        "description": "Practical guidelines on optimal weather windows, safety precautions for water sports, and local transport options.",
        "location": "Goa State",
        "activities": ["Travel scheduling", "Safety planning"],
        "estimated_cost": "N/A",
        "best_time": "November to February (Cool, dry 28°C weather)",
        "duration": "All stay",
        "travel_tips": "Rent a scooter (₹350-₹500/day). Book water sports through licensed operators only. Respect red flag sea warnings during monsoon.",
        "text": "Best time to visit Goa is November to February when skies are clear. Rent a scooter for easy travel between beaches. Book water sports through registered shacks. Carry cash."
    },

    # =========================================================================
    # KERALA
    # =========================================================================
    {
        "id": "kerala-overview-01",
        "destination": "Kerala",
        "place_name": "God's Own Country",
        "category": "overview",
        "description": "Kerala on India's tropical Malabar Coast is acclaimed for tranquil emerald backwater lagoons, mist-cloaked Western Ghats tea plantations, Ayurvedic wellness, and rich cultural traditions.",
        "location": "Southwest Coast of India",
        "activities": ["Houseboat cruising", "Tea plantation trekking", "Ayurvedic massage", "Kathakali viewing"],
        "estimated_cost": "Moderate to Luxury (₹3,000 - ₹7,000 / day / person)",
        "best_time": "September to March",
        "duration": "5 to 8 days",
        "travel_tips": "Combine Munnar hill station with Alleppey backwaters for the quintessential Kerala experience.",
        "text": "Kerala, on India's southwest coast, is famous for its backwaters, houseboats, tea plantations, and Ayurvedic wellness retreats. Suits travelers seeking nature, culture, and relaxation."
    },
    {
        "id": "kerala-attractions-alleppey",
        "destination": "Kerala",
        "place_name": "Alleppey Backwaters & Houseboats",
        "category": "attractions",
        "description": "A world-famous network of interconnected palm-fringed canals, rivers, and lagoons on Vembanad Lake, best navigated aboard a traditional thatched Kettuvallam houseboat.",
        "location": "Alappuzha (Alleppey), 60 km south of Kochi",
        "activities": ["Overnight houseboat cruising", "Shikara boat rides", "Village canoeing", "Sunset lagoon watching"],
        "estimated_cost": "Houseboats ₹8,500 - ₹16,000 / night (all meals included); Shikaras ₹1,000 / hour",
        "best_time": "Check-in at 12:00 PM for overnight cruise",
        "duration": "Overnight (21 hours)",
        "travel_tips": "Choose an AC Deluxe or Luxury houseboat with transparent lake-facing bedrooms. Try fresh pearl spot fish caught and fried on board.",
        "text": "Must-visit spot: Alleppey backwaters for overnight houseboat stays, village canal canoeing, scenic coconut lagoons, and traditional Kerala onboard meals."
    },
    {
        "id": "kerala-attractions-munnar",
        "destination": "Kerala",
        "place_name": "Munnar Tea Plantations & Top Station",
        "category": "attractions",
        "description": "Rolling emerald hills carpeted in manicured tea gardens, cool mountain mist, sparkling waterfalls, and habitat of the endangered Nilgiri Tahr at Eravikulam National Park.",
        "location": "Idukki District, Western Ghats (1,600m altitude)",
        "activities": ["Tea garden walks", "Tea factory museum tour", "Nilgiri Tahr safari", "Kolukkumalai sunrise trek"],
        "estimated_cost": "National Park entry ₹200; Tea Museum ₹150",
        "best_time": "October to April",
        "duration": "2 to 3 days",
        "travel_tips": "Book the early morning jeep safari to Kolukkumalai (world's highest organic tea estate) for an incredible cloud-bed sunrise.",
        "text": "Munnar tea gardens, Eravikulam National Park, Mattupetty Dam, and Western Ghats mist-clad hills offer tea plantation strolls and cool mountain climate."
    },
    {
        "id": "kerala-attractions-kochi",
        "destination": "Kerala",
        "place_name": "Fort Kochi & Chinese Fishing Nets",
        "category": "attractions",
        "description": "A charming historical port town where Portuguese, Dutch, British, and Jewish heritage blends with fixed cantilevered Chinese Fishing Nets and contemporary art cafes.",
        "location": "Kochi (Cochin) Port City",
        "activities": ["Chinese fishing nets photography", "Jew Town & Synagogue stroll", "Kathakali dance show"],
        "estimated_cost": "Free entry; Kathakali performance ₹400 - ₹600",
        "best_time": "Late afternoon 4:00 PM to 7:30 PM",
        "duration": "1 full day",
        "travel_tips": "Attend the Kathakali face-makeup session at 5:00 PM before the evening performance starts.",
        "text": "Fort Kochi historical sights include the cantilevered Chinese Fishing Nets, colonial heritage buildings, St. Francis Church, and classical Kathakali dance performances."
    },
    {
        "id": "kerala-food-cuisine",
        "destination": "Kerala",
        "place_name": "Traditional Kerala Cuisine",
        "category": "food",
        "description": "Richly aromatic dishes prepared with freshly grated coconut, curry leaves, and Malabar spices, accompanied by soft fermented rice delicacies.",
        "location": "Across Kerala coastal diners and heritage restaurants",
        "activities": ["Banana leaf Sadhya feast", "Seafood tasting", "Street banana chips sampling"],
        "estimated_cost": "₹300 - ₹900 per person",
        "best_time": "Lunch time for grand Sadhya feasts",
        "duration": "1 hour",
        "travel_tips": "Try Karimeen Pollichathu (pearl spot fish marinated in spicy masala and baked in banana leaves).",
        "text": "Kerala cuisine features appam with stew, fish molee, puttu with kadala curry, Malabar parotta, Karimeen Pollichathu, and the traditional festive Sadhya served on banana leaf."
    },
    {
        "id": "kerala-budget-estimate",
        "destination": "Kerala",
        "place_name": "Kerala Holiday Budget Guide",
        "category": "budget",
        "description": "A comprehensive 5-day holiday covering Kochi arrival, Munnar hill resort stays, and an overnight luxury houseboat in Alleppey for 4 travelers.",
        "location": "Kerala",
        "activities": ["Financial planning", "Houseboat package booking"],
        "estimated_cost": "Rs 90,000 to Rs 1,30,000 for 4 people including houseboat and private cab",
        "best_time": "September to March",
        "duration": "5 Days",
        "travel_tips": "Hiring a private AC Innova cab for the entire circuit (Kochi - Munnar - Alleppey - Kochi) is the most comfortable and cost-effective method for 4 people.",
        "text": "A 5-day Kerala trip for 4 people including a houseboat night, mid-range hill resorts, private AC cab, and food typically costs Rs 90,000 to Rs 1,30,000."
    },
    {
        "id": "kerala-tips-besttime",
        "destination": "Kerala",
        "place_name": "Kerala Travel Advice & Best Season",
        "category": "tips",
        "description": "Seasonal climate recommendations and packing advice for backwater and hill station variations.",
        "location": "Kerala",
        "activities": ["Travel scheduling", "Health & comfort planning"],
        "estimated_cost": "N/A",
        "best_time": "September to March (Dry weather with clear skies)",
        "duration": "All stay",
        "travel_tips": "Carry mosquito repellent for backwater and forest reserves. Carry light woolen clothes for Munnar where nighttime temperatures drop below 12°C.",
        "text": "Best time to visit Kerala is September to March after the monsoon. Book houseboats well in advance during peak season (December-January). Carry mosquito repellent."
    },

    # =========================================================================
    # MANALI
    # =========================================================================
    {
        "id": "manali-overview-01",
        "destination": "Manali",
        "place_name": "Manali Alpine Valley",
        "category": "overview",
        "description": "Nestled in Himachal Pradesh at the northern end of the Kullu Valley, Manali offers snow-crested Himalayan peaks, pine forests, rushing Beas river rapids, and high-altitude adventures.",
        "location": "Kullu District, Himachal Pradesh (2,050m altitude)",
        "activities": ["High-altitude trekking", "Paragliding", "River rafting", "Old Manali cafe exploration"],
        "estimated_cost": "Moderate (₹2,500 - ₹5,500 / day / person)",
        "best_time": "March to June (Summer greenery) or Dec to Feb (Snowfall)",
        "duration": "4 to 6 days",
        "travel_tips": "Keep buffer time for mountain road travel. Book Rohtang Pass permits in advance.",
        "text": "Manali is a Himalayan hill town in Himachal Pradesh popular for snow activities, paragliding, trekking, pine valleys, and scenic mountain views. Suits adventure and nature travelers."
    },
    {
        "id": "manali-attractions-solang",
        "destination": "Manali",
        "place_name": "Solang Valley & Atal Tunnel",
        "category": "attractions",
        "description": "An adventure haven 14 km northwest of Manali offering tandem paragliding, zorbing, skiing, and access through the 9.02 km Atal Tunnel to the surreal cold desert of Sissu in Lahaul.",
        "location": "Solang Valley & Rohtang Highway",
        "activities": ["Tandem paragliding", "Zorbing", "Skiing", "Cable car ride", "Atal Tunnel drive"],
        "estimated_cost": "Paragliding ₹1,800 - ₹3,500; Cable car ₹600",
        "best_time": "Early morning before 9:30 AM to beat traffic jams",
        "duration": "Full day (6-7 hours)",
        "travel_tips": "Confirm weather conditions before booking paragliding. Ensure the pilot has valid tourism certification.",
        "text": "Solang Valley in Manali is key for paragliding, skiing, zorbing, and ropeways. Atal Tunnel allows scenic day trips into Sissu and Lahaul Valley."
    },
    {
        "id": "manali-attractions-oldmanali",
        "destination": "Manali",
        "place_name": "Hadimba Temple & Old Manali Village",
        "category": "attractions",
        "description": "A 16th-century four-tier wooden pagoda shrine dedicated to Hadimba Devi set amidst giant deodar cedar trees, adjoining the bohemian live-music cafes of Old Manali.",
        "location": "Old Manali, 2 km from Mall Road",
        "activities": ["Ancient wooden shrine visit", "Cedar forest walks", "Cafe hopping", "Riverside dining"],
        "estimated_cost": "Free entry",
        "best_time": "Morning 8:30 AM for temple; Evening 6 PM for cafes",
        "duration": "3-4 hours",
        "travel_tips": "Walk from the temple through the cedar forest into Old Manali village for artisan wood-fired pizza and momos.",
        "text": "Hadimba Temple is an ancient wooden pagoda temple in cedar woods. Old Manali village offers bohemian cafes, bakeries, live music, and scenic apple orchards."
    },
    {
        "id": "manali-food-cuisine",
        "destination": "Manali",
        "place_name": "Himachali Cuisine & Mountain Cafes",
        "category": "food",
        "description": "Hearty mountain cuisine featuring fermented wheat breads, slow-cooked lentils, freshly caught Beas river rainbow trout, and steaming Tibetan dumplings.",
        "location": "Old Manali, Mall Road, and Vashisht village",
        "activities": ["Trout fish dining", "Siddu tasting", "Tibetan momo & thukpa crawls"],
        "estimated_cost": "₹350 - ₹800 per person per meal",
        "best_time": "Hot breakfast and cozy evening dinners",
        "duration": "1 hour",
        "travel_tips": "Order Siddu with melted ghee and spicy green chutney for a true local Himachali taste.",
        "text": "Manali food highlights include Siddu (stuffed steamed bread with ghee), Himachali dham feast, fresh Beas river trout fish, and Tibetan momos and thukpa in Old Manali cafes."
    },
    {
        "id": "manali-budget-estimate",
        "destination": "Manali",
        "place_name": "Manali Trip Budget Guide",
        "category": "budget",
        "description": "An adventurous 5-day mountain trip for 4 travelers including river rafting, Solang paragliding, Atal Tunnel cab, cottage stays, and dining.",
        "location": "Manali & Kullu Valley",
        "activities": ["Expense planning", "Activity packages"],
        "estimated_cost": "Rs 70,000 to Rs 1,10,000 for 4 people including adventure passes",
        "best_time": "March to June & Oct to Dec",
        "duration": "5 Days",
        "travel_tips": "Booking adventure packages as a group in Solang Valley secures 20-30% discounts.",
        "text": "A 5-day Manali trip for 4 people including mountain stays, Solang Valley adventure activities like paragliding and river rafting typically costs Rs 70,000 to Rs 1,10,000."
    },
    {
        "id": "manali-tips-besttime",
        "destination": "Manali",
        "place_name": "Manali Weather Advisory & Packing Tips",
        "category": "tips",
        "description": "Practical packing advice for high-altitude mountain climate, Rohtang permits, and road safety.",
        "location": "Manali",
        "activities": ["Packing preparation", "Permit management"],
        "estimated_cost": "Rohtang Permit ₹550 online",
        "best_time": "March to June for pleasant weather; Dec to Feb for snow activities",
        "duration": "All trip",
        "travel_tips": "Carry warm fleece layers even in peak summer evenings. Apply online for Rohtang permits 3-4 days in advance as vehicle quotas are capped.",
        "text": "Best time: March-June for sightseeing; Dec-Feb for snow. Carry warm layers even in summer. Book Rohtang Pass permits online in advance as visitor numbers are strictly limited."
    },

    # =========================================================================
    # JAIPUR
    # =========================================================================
    {
        "id": "jaipur-overview-01",
        "destination": "Jaipur",
        "place_name": "The Pink City",
        "category": "overview",
        "description": "The regal capital of Rajasthan, celebrated for formidable hilltop fortresses, opulent marble palaces, vibrant UNESCO-listed pink sandstone architecture, and rich gemstone bazaars.",
        "location": "Rajasthan, 260 km southwest of New Delhi",
        "activities": ["Royal fort exploration", "Palace architecture photography", "Bazaar textile shopping", "Rajasthani royal dining"],
        "estimated_cost": "Moderate (₹2,500 - ₹6,000 / day / person)",
        "best_time": "October to March",
        "duration": "3 to 5 days",
        "travel_tips": "Purchase the composite entry ticket at Amber Fort covering 5 major monuments for significant savings.",
        "text": "Jaipur, the Pink City, is Rajasthan's capital known for its forts, palaces, royal heritage, and vibrant markets. Suits travelers interested in history, architecture, and shopping."
    },
    {
        "id": "jaipur-attractions-amber",
        "destination": "Jaipur",
        "place_name": "Amber Fort & Sheesh Mahal",
        "category": "attractions",
        "description": "A majestic Rajput fortress crowned atop Cheel ka Teela above Maota Lake, famous for intricate mirrored halls (Sheesh Mahal), expansive courtyards, and Mughal gardens.",
        "location": "Amer, 11 km north of Jaipur city",
        "activities": ["Fort tour", "Mirror palace viewing", "Elephant or jeep ride", "Panoramic lake photography"],
        "estimated_cost": "₹100 for Indians, ₹500 for Foreigners; Jeep ride ₹500",
        "best_time": "8:00 AM to 5:30 PM (or Light & Sound show at 7:30 PM)",
        "duration": "3 hours",
        "travel_tips": "Hire an official licensed audio guide or government guide at the gate to appreciate the ingenious water-cooling systems and mirrored ceilings.",
        "text": "Amber Fort in Jaipur features formidable ramparts above Maota Lake, intricate Sheesh Mahal (Palace of Mirrors), royal courtyards, and magnificent Rajput architecture."
    },
    {
        "id": "jaipur-attractions-hawamahal",
        "destination": "Jaipur",
        "place_name": "Hawa Mahal & City Palace",
        "category": "attractions",
        "description": "The Palace of Winds with 953 honeycombed jharokha windows built for royal women to observe city parades unnoticed, situated beside the grand royal residence of the Maharaja.",
        "location": "Badi Choupad, Old Pink City",
        "activities": ["Honeycomb facade photography", "City palace royal costume museum", "Astronomical viewing at Jantar Mantar"],
        "estimated_cost": "Hawa Mahal ₹50; City Palace ₹300",
        "best_time": "Morning 9:00 AM when the sun illuminates the pink facade",
        "duration": "2.5 hours",
        "travel_tips": "Visit Wind View Cafe on the opposite rooftop terrace for the most iconic full-facade photograph.",
        "text": "Hawa Mahal with 953 pink sandstone windows and nearby City Palace complex and Jantar Mantar UNESCO observatory showcase Jaipur's royal heritage."
    },
    {
        "id": "jaipur-food-cuisine",
        "destination": "Jaipur",
        "place_name": "Royal Rajasthani Gastronomy",
        "category": "food",
        "description": "Rich royal fare featuring baked wheat balls soaked in pure ghee and spicy lentils, fiery red mutton curry, and crisp round kachoris bursting with sweet and spicy fillings.",
        "location": "Old City bazaars, MI Road, and Chokhi Dhani ethnic village",
        "activities": ["Dal Baati Churma feast", "Laal Maas tasting", "Street kachori and lassi sampling"],
        "estimated_cost": "₹350 - ₹1,100 per person",
        "best_time": "Lunch and Evening Snacks",
        "duration": "1 hour",
        "travel_tips": "Enjoy a thick creamy sweet lassi served in traditional earthenware clay cups at Lassiwala on MI Road.",
        "text": "Jaipur signature dishes include dal baati churma, laal maas spicy mutton curry, pyaaz kachori from Rawat Mishthan Bhandar, and ghewar sweets."
    },
    {
        "id": "jaipur-budget-estimate",
        "destination": "Jaipur",
        "place_name": "Jaipur Tour Budget Guide",
        "category": "budget",
        "description": "A 5-day cultural holiday for 4 travelers covering heritage haveli stays, private AC vehicle for forts, monument ticketing, and fine Rajasthani dining.",
        "location": "Jaipur & Amer",
        "activities": ["Budget tracking", "Private chauffeur hire"],
        "estimated_cost": "Rs 75,000 to Rs 1,15,000 for 4 people across 5 days",
        "best_time": "October to March",
        "duration": "5 Days",
        "travel_tips": "Book a heritage haveli hotel near Bani Park or Old City for an authentic royal ambiance at reasonable rates.",
        "text": "A 5-day Rajasthan trip for 4 people covering Jaipur, Amber Fort, heritage havelis, and local transport typically costs Rs 75,000 to Rs 1,15,000."
    },
    {
        "id": "jaipur-tips-besttime",
        "destination": "Jaipur",
        "place_name": "Jaipur Seasonality & Shopping Advice",
        "category": "tips",
        "description": "Optimal visiting months and insider shopping advice for authentic gemstones, blue pottery, and block-printed textiles.",
        "location": "Jaipur",
        "activities": ["Seasonal planning", "Bazaar bargaining"],
        "estimated_cost": "N/A",
        "best_time": "October to March (Avoid extreme 42°C summer heat from April to June)",
        "duration": "All trip",
        "travel_tips": "Bargain politely in Johari and Bapu Bazaars. Buy precious gems and jewelry only from certified government-approved emporiums.",
        "text": "Best time: October to March. Hire official guides at forts. Bargain at local bazaars for textiles, and prefer fixed-price government shops for certified gemstones."
    },

    # =========================================================================
    # RISHIKESH
    # =========================================================================
    {
        "id": "rishikesh-overview-01",
        "destination": "Rishikesh",
        "place_name": "Yoga Capital & Adventure Hub",
        "category": "overview",
        "description": "Situated at the Himalayan foothills where the holy Ganges emerges into the northern plains, Rishikesh is renowned globally for meditation ashrams, spiritual Ganga Aarti, and thrilling white-water river rafting.",
        "location": "Dehradun / Tehri Garhwal District, Uttarakhand",
        "activities": ["White-water river rafting", "Ganga Aarti participation", "Yoga & meditation retreats", "Bungee jumping"],
        "estimated_cost": "Budget to Moderate (₹2,000 - ₹4,500 / day / person)",
        "best_time": "September to November & February to May",
        "duration": "3 to 5 days",
        "travel_tips": "Rishikesh is a strictly vegetarian and alcohol-free sacred town near the river banks.",
        "text": "Rishikesh, on the banks of the Ganges in Uttarakhand, is known as the yoga capital of the world and a hub for white-water river rafting, camping, and spiritual retreats."
    },
    {
        "id": "rishikesh-attractions-rafting",
        "destination": "Rishikesh",
        "place_name": "Ganges White-Water River Rafting",
        "category": "attractions",
        "description": "An adrenaline-pumping rafting descent through grade III and IV rapids (Roller Coaster, Golf Course, Club House) flanked by pristine forested mountain gorges.",
        "location": "Shivpuri to Laxman Jhula stretch (16 km or 26 km Marine Drive)",
        "activities": ["White-water rafting", "Cliff jumping", "Body surfing in the Ganges"],
        "estimated_cost": "₹800 to ₹1,500 per person including safety gear",
        "best_time": "9:00 AM to 3:00 PM (Closed during monsoon June 15 - Sept 15)",
        "duration": "3 to 4 hours",
        "travel_tips": "Verify that your rafting operator is licensed by Uttarakhand Tourism and provides CE-certified lifejackets and helmets.",
        "text": "Ganges white-water rafting features grade III and IV rapids like Roller Coaster, Golf Course, and Three Blind Mice, with cliff jumping and body surfing."
    },
    {
        "id": "rishikesh-attractions-aarti",
        "destination": "Rishikesh",
        "place_name": "Triveni Ghat Evening Maha Aarti",
        "category": "attractions",
        "description": "A deeply moving spiritual gathering on the riverbanks as dusk falls, featuring synchronized brass lamp ceremonies, Vedic chanting, conch shells, and hundreds of floating leaf diyas.",
        "location": "Triveni Ghat, Mayakund, Rishikesh",
        "activities": ["Ganga Aarti prayer", "Floating diya offering", "Spiritual chant listening"],
        "estimated_cost": "Free; Diya offerings ₹30 - ₹50",
        "best_time": "Arrive by 5:30 PM (Aarti starts around sunset 6:15 PM)",
        "duration": "1.5 hours",
        "travel_tips": "Remove footwear before stepping onto the ghat steps. Arrive 45 minutes early for front-row seating on the stone steps.",
        "text": "Triveni Ghat hosts the spiritual evening Ganga Aarti with priests circling flaming brass lamps, rhythmic Vedic chants, conch shells, and floating flower diyas."
    },
    {
        "id": "rishikesh-food-cuisine",
        "destination": "Rishikesh",
        "place_name": "Sattvic & Global Riverside Dining",
        "category": "food",
        "description": "wholesome Sattvic pure vegetarian Ayurvedic thalis alongside world cuisine cafes serving wood-fired thin-crust pizza, Israeli shakshuka, and organic smoothie bowls overlooking the Ganges.",
        "location": "Tapovan, Swarg Ashram, and Laxman Jhula banks",
        "activities": ["Ayurvedic thali lunch", "Rooftop riverside dining", "Organic herbal tea sipping"],
        "estimated_cost": "₹250 - ₹600 per person per meal",
        "best_time": "Breakfast & Sunset dinner",
        "duration": "1 hour",
        "travel_tips": "Tapovan cafes offer excellent organic espresso and plant-based vegan treats with serene river views.",
        "text": "Rishikesh dining is completely vegetarian and alcohol-free, offering Sattvic Ayurvedic thalis, fresh cold-pressed juices, and riverside cafes serving Israeli and continental food."
    },
    {
        "id": "rishikesh-budget-estimate",
        "destination": "Rishikesh",
        "place_name": "Rishikesh Adventure & Camping Budget",
        "category": "budget",
        "description": "A 4-day budget-friendly and active retreat for 4 travelers including riverside Swiss tents, rafting passes, cliff jumping, temple excursions, and meals.",
        "location": "Rishikesh & Shivpuri",
        "activities": ["Riverside camping", "Adventure budget planning"],
        "estimated_cost": "Rs 50,000 to Rs 85,000 for 4 people across 4 days",
        "best_time": "September to November & March to May",
        "duration": "4 Days",
        "travel_tips": "Opt for tented adventure camps in Shivpuri that bundle night stays, bonfires, all meals, and 16 km rafting into one package.",
        "text": "A 4-day Rishikesh trip for 4 people including 16km rafting, riverside camping in Shivpuri, meals, and local transport typically costs Rs 50,000 to Rs 85,000."
    },
    {
        "id": "rishikesh-tips-besttime",
        "destination": "Rishikesh",
        "place_name": "Rishikesh Cultural & Safety Tips",
        "category": "tips",
        "description": "Essential etiquette guidelines for sacred riverbanks and safety standards for outdoor extreme sports.",
        "location": "Rishikesh",
        "activities": ["Safety preparation", "Cultural respect"],
        "estimated_cost": "N/A",
        "best_time": "September to November and February to April",
        "duration": "All trip",
        "travel_tips": "Book adventure activities through government-registered operators. Strictly respect the vegetarian and alcohol-free local culture near the ghats.",
        "text": "Best time: September-November & February-April for rafting. Book rafting through registered operators. Respect the alcohol-free and vegetarian local customs near the sacred ghats."
    }
]

# -*- coding: utf-8 -*-
# canonical id -> surface forms seen in the sheet + official aliases + mascots + this-pool joke aliases
TEAMS = {
"ALA":["Alabama","Bama","Crimson Tide","Tide","Elephant","Elefante","Roll Tide"],
"APP":["App State","Appalachian State","App","Mountaineers","Neers","Foliage"],
"ARIZ":["Arizona","Zona","AZ","Wildcats","HMS Wildcat"],
"ASU":["Arizona State","Arizona St","ASU","Sun Devils","Sparky","Forks"],
"ARK":["Arkansas","Arky","Hogs","Hog","Razorbacks","Poo Big","Woo Pig"],
"ARST":["Arkansas State","Ark State","Arky State","Red Wolves"],
"ARMY":["Army","Black Knights","HOOAH","Troops","Salute"],
"AUB":["Auburn","Tigers","War Eagle","Eagle"],
"BYU":["BYU","Byu","Cougars","Mormon"],
"BAY":["Baylor","Bears","Sic Em","Chip and Joanna"],
"BOIS":["Boise State","Boise","Broncos"],
"BC":["Boston College","Boston Col","BC","Eagles"],
"BUF":["Buffalo","Bulls"],
"CAL":["Cal","California","Golden Bears","Bears"],
"CMU":["Central Michigan","Chippewas"],
"CHAR":["Charlotte","49ers"],
"CIN":["Cincinnati","Cincy","Bearcats"],
"CLEM":["Clemson","Clemons","Clesn","Tigers","Dabo","Newspring"],
"CCU":["Coastal Carolina","Coastal","Chanticleers"],
"COLO":["Colorado","Buffaloes","Buffs"],
"DEL":["Delaware","Deleware","Blue Hens"],
"DUKE":["Duke","Blue Devils","Nerds"],
"EMU":["E. Michigan","Eastern Michigan","EMU","Eagles"],
"ECU":["East Carolina","ECU","Pirates"],
"FIU":["FIU","Panthers"],
"FLA":["Florida","Fla","UF","Gators","Gator"],
"FSU":["Florida State","FSU","Noles","Seminoles","Oseola","Osceola"],
"FRES":["Fresno State","Fresno St","Fresno","Bulldogs"],
"GASO":["Georgia Southern","GA Southern","Ga Southern","GaSo","GSU","GATA"],
"GT":["Georgia Tech","GA Tech","GT","Yellow Jackets","Jacket","Bee","Buzz"],
"UGA":["Georgia","UGA","Dawgs","Dawg","Bulldogs","Honk"],
"HAW":["Hawaii","Rainbow Warriors"],
"HOU":["Houston","Cougars","Phog"],
"ILL":["Illinois","Illini","Fighting Illini","Iliad"],
"ILST":["Illinois State","Redbirds"],
"IND":["Indiana","IU","Hoosiers","Hoosier Daddy"],
"IOWA":["Iowa","Hawkeyes","Hawk"],
"ISU":["Iowa State","Iowa St","Iowastate","ISU","Cyclones","Cyclone","Clones","Twister","Tweester"],
"JMU":["James Madison","JMU","JMI","Dukes"],
"JXST":["Jacksonville State","Jax State","Jax","Gamecocks","Cocks","Cock","Cock Tuah","Jacking it State","JACKIN IT","Gamecocks 2","Fear the beak"],
"KU":["Kansas","Jayhawks","Hawk","Phog"],
"KSU":["Kansas State","Kansas St","K-State","K State","KState","Wildcats"],
"KENN":["Kennesaw State","Kennesaw","Owls","Owl","Hooty Hoo","Hoot"],
"UK":["Kentucky","Wildcats"],
"LT":["Louisiana Tech","LA Tech","La Tech","LT","Bulldogs"],
"LSU":["LSU","Tigers","Geaux","Nussbussy"],
"LIB":["Liberty","Flames","Abstinence"],
"UL":["Louisiana","Ragin Cajuns","Cajuns"],
"LOU":["Louisville","UL","L","Cardinals","Ville","The 6","Tweet"],
"MRSH":["Marshall","Thundering Herd"],
"MD":["Maryland","Terps","Terrapins","Turtles","Turt"],
"MEM":["Memphis","Mephis","Tigers"],
"MER":["Mercer","Bears"],
"MIA":["Miami","Miami FL","U","Da U","Hurricanes","Canes","Raisin Canes"],
"M-OH":["Miami OH","Miami Ohio","RedHawks","Red Hawks"],
"MICH":["Michigan","Mich","Wolverines","Rine"],
"MSU":["Michigan State","Michigan St","MichSt","MSU","Sparty","Spartans"],
"MINN":["Minnesota","Gophers","Gopher","Goph","Golden Gophers"],
"MSST":["Mississippi State","Miss State","Miss St","Mississippi St","MSU","Bulldogs","Cowbells","Cowbell","Clanga"],
"MIZ":["Missouri","Mizzou","Miz","Misery","Mizery","Tigers"],
"MOST":["Missouri State","Mo State","Bears","Gamer Bears"],
"MONT":["Montana","Griz","Grizz","Grizzlies"],
"MTST":["Montana State","Montana St","MSU","Bobcats"],
"NCST":["NC State","NCSU","N.C. State","Pack","Wolfpack","Mandate"],
"NDSU":["North Dakota State","NDSU","Bison","Bisonburger","SNUD"],
"NMSU":["NMSU","New Mexico State"],
"NAVY":["Navy","Midshipmen","Mids"],
"NEB":["Nebraska","Corn","Huskers","Cornhuskers","Kermit","Keisei Tominaga","Connor Essegian","Rienk Mast","Jamarques Lawrence","Mini Mahomes"],
"UNM":["New Mexico","Lobos"],
"UNC":["North Carolina","UNC","Tar Heels","Heels"],
"UNT":["North Texas","UNT","N Texas","Mean Green","Angry broccoli"],
"NW":["Northwestern","NW","Wildcats"],
"ND":["Notre Dame","ND","Irish","Fighting Irish","Ginger","Midget"],
"OHIO":["Ohio","OH","Bobcats"],
"OSU":["Ohio State","OSU","OH","Buckeyes","Nut","Nuts","Ohio St."],
"OU":["Oklahoma","OU","OK","Sooners","Boomer","Boomer Sooner","Brent Venables Raping"],
"OKST":["Oklahoma St","Oklahoma State","Cowboys","Pokes"],
"ODU":["Old Dominion","ODU","OFU","Monarchs"],
"MISS":["Ole Miss","Piss","Ole piss","Mississippi","Rebels","Papou's Rebels","Landsharks","Shark"],
"ORE":["Oregon","Ducks","Duck","Quack","Quck"],
"ORST":["Oregon State","Oregon St","OSU","Beavers","Beavs"],
"PSU":["Penn State","PSU","Nittany Lions"],
"PITT":["Pitt","Pittsburgh","Panthers","Bryce Young"],
"RICE":["Rice","Owls","Food"],
"RUT":["Rutgers","Scarlet Knights"],
"SDSU-CA":["San Diego State","San Diego St","SDSU","Aztecs"],
"SAC":["Sac State","Sacramento State","Hornets"],
"SJSU":["SJSU","San Jose State","Spartans"],
"SMU":["SMU","Mustangs","Ponies"],
"SC":["South Carolina","S Carolina","SC","Gamecocks","Cocks","Cock"],
"SDST":["S Dakota St","South Dakota State","SDSU","Jackrabbits"],
"USM":["Southern Miss","So Miss","USM","Southernmiss","Golden Eagles"],
"STAN":["Stanford","Cardinal"],
"SYR":["Syracuse","Cuse","Orange","Citrus"],
"TAMU":["Texas A&M","TAMU","A&M","Aggies","Aggy","Cult","My beloved Aggies"],
"TCU":["TCU","Horned Frogs","Frogs"],
"TEM":["Temple","Owls"],
"TENN":["Tennessee","UTK","Vols","Volunteers","Vol"],
"TEX":["Texas","Longhorns","Longhorn","Horns","Cow","Something horse"],
"TXST":["Texas State","Texas St","TX State","Bobcats"],
"TTU":["Texas Tech","TTU","Red Raiders","Tortilla","Tortillas","Oil Money"],
"TOL":["Toledo","Rockets"],
"TROY":["Troy","Trojans"],
"TULN":["Tulane","Green Wave","Wave","Ocean","School that accepted me"],
"TLSA":["Tulsa","Golden Hurricane"],
"UCF":["UCF","Knights"],
"UCLA":["UCLA","Bruins"],
"UCONN":["UConn","Huskies"],
"UNLV":["UNLV","Rebels","Gamblin and Sex"],
"USC":["USC","Southern Cal","Trojans"],
"USF":["USF","South Florida","Bulls"],
"UTSA":["UTSA","Roadrunners","Meep"],
"UTAH":["Utah","Utes","Ute","Urah","UTah"],
"USU":["Utah State","Utah St","Aggies","My beloved Aggies"],
"VT":["Virginia Tech","VA Tech","VT","Hokies","Gobble"],
"VAN":["Vanderbilt","Vandy","Dores","Commodores"],
"UVA":["Virginia","UVA","Hoos","Hoo","Cavaliers","VA"],
"WCU":["Western Carolina","W Carolina","Western","Wester","Catamounts"],
"WAKE":["Wake Forest","Wake","Demon Deacons","Deacs"],
"WASH":["Washington","UDub","U Dub","Huskies"],
"WSU":["Washington State","Washington St","Wazzu","WAZ","Cougars"],
"WKU":["Western Kentucky","WKU","Hilltoppers","Tops"],
"WMU":["Western Michigan","W Michigan","WMU","Broncos"],
"WVU":["West Virginia","WVU","Mountaineers","Country roads","Rich Rod"],
"WIS":["Wisconsin","Wiscy","Badgers"],
"WOF":["Wofford","Terriers"],
"WYO":["Wyoming","Cowboys"],
}

# picks that carry no team signal at all -- must be hand-mapped to (tab, game) context
HARD_OVERRIDES = {
 ("Week 2","Fresno St @ Oregon St -3.5","Robert"):"ORST",
 ("Week 2","Boston Col @ Michigan St -4.5","Robert"):"BC",      # "Bandans"  (grading checksum)
 ("Week 2","Boston Col @ Michigan St -4.5","Jackson"):"MSU",    # "Revenge"
 ("Week 3","Wazzu @ North Texas -5.5","Michael"):"UNT",         # "Angry broccoli"
 ("Week 5","#21 USC -7.5 @ #23 Illinois","Michael"):"USC",      # "Something horse" -> Trojan horse
 ("Week 5","UCF @ Kansas State -6.5","Jackson"):"KSU",          # "Daddy and Bro Fighting"
 ("Week 5","#17 Alabama @ #5 Georgia -2.5","Jackson"):"UGA",    # "Honk"
 ("Week 5","Arizona @ #14 Iowa State -6.5","Jackson"):"ISU",    # "Twister"
 ("Week 5","Louisville -3.5 @ Pitt","Jackson"):"LOU",           # "Tweet" (Cardinal)
 ("Week 5","Duke -4.5 @ Syracuse","Jackson"):"SYR",             # "Citrus" (Orange)
 ("Week 5","#8 Florida State -7.5 @ Virginia","Jackson"):"FSU", # "Oseola"
 ("Week 5","Tulane -14.5 @ Tulsa","Jackson"):"TULN",            # "Ocean"
 ("Week 5","Tulane -14.5 @ Tulsa","Michael"):"TULN",            # "School that accepted me"
 ("Week 4","Arkansas -6.5 @ Memphis","Michael"):"ARK",          # "Poo Big"
 ("Week 4","#21 Michigan -1.5 @ Nebraska","Michael"):"NEB",     # "Kermit"
 ("BOWLS","Xbox: Arkansas State vs Missouri State","JP"):"MOST",# "Gamer Bears"
 ("BOWLS","Myrtle Beach: Western Michigan vs Kennesaw State","JP"):"KENN", # "Hooty Hoo"
 ("BOWLS","Gasparilla: NC State vs Memphis","Michael"):"NCST",  # "Mandate"
 ("BOWLS","Armed Forces: Rice vs Texas State","Jackson"):"RICE",# "Food"
 ("BOWLS","Fenway: Army vs UConn","JP"):"ARMY",                 # "HOOAH"
 ("BOWLS","First Responder: FIU vs UTSA","Jackson"):"UTSA",     # "Meep" (Roadrunner)
 ("BOWLS","Pinstripe: Penn State vs Clemson","Robert"):"CLEM",  # "Clemson or maybe a gun perhaps"
 ("BOWLS","Pinstripe: Penn State vs Clemson","Michael"):"PSU",  # "I told myself to never pick Clemson so Penn State I guess"
 ("Week 2","Liberty -6.5 @ Jax State","Michael"):"JXST",        # "Fear the beak"
 ("Week 3","Jax State @ GA Southern -2.5","Michael"):"JXST",    # "Fear the beak"
}

# picks that are non-picks (author declined / joked instead of picking) -> treat as BLANK
NON_PICKS = {"Remind me to pick this shit"}

# Jackson's Week 6 "joke week" leftovers + other zero-signal strings, keyed by (tab, game, player)
EXTRA_OVERRIDES = {
 ("Week 6","Western Carolina @ Wofford","Jackson"):"WCU",        # "Period Man"
 ("Week 6","#9 Texas -6.5 @ Florida","Jackson"):"FLA",           # "Arched Back"  (graded miss => Florida)
 ("Week 6","#24 Virginia @ Louisville -7.5","Jackson"):"UVA",    # "JP Barry"     (graded miss => Virginia)
 ("Week 14","#13 Miami FL -6.5 @ #24 Pitt","Michael"):"PITT",    # "Super weapon" (grading checksum)
 ("Conf Champ","Kennesaw State @ Jax State -1.5","Jackson"):"KENN", # "Mandate"   (graded miss => Kennesaw)
}

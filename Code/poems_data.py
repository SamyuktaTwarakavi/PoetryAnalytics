# poems_data.py -- the data: word lists and the poet-year table.


# Word lists for step 2 (word-count dimensions).
POSITIVE = ["love", "joy", "bright", "light", "beauty", "beautiful", "sweet", "golden",
            "dancing", "glory", "blest", "bless", "fair", "delight", "hope", "warm",
            "gentle", "song", "spring", "bloom", "rose", "loveliest"]
NEGATIVE = ["death", "dark", "darkness", "grave", "weary", "desolate", "broken", "fear",
            "fearful", "cold", "sorrow", "grief", "pain", "tears", "gloom", "lonely",
            "shattered", "knell", "weakening", "sunless", "vain", "wounds"]
CONCRETE = ["sea", "tree", "trees", "stone", "iron", "hand", "eye", "eyes", "cloud",
            "daffodils", "lake", "breeze", "desert", "sand", "river", "gate", "frost",
            "bird", "cherry", "bough", "boughs", "sky", "moon", "herd", "leaf", "leaves",
            "fruit", "vines", "cow", "trout", "wings", "coast", "cliffs", "engine",
            "smoke", "sail", "rose"]
ABSTRACT = ["truth", "soul", "beauty", "time", "immortal", "fate", "mind", "study",
            "struggle", "circumstance", "wonder", "vision", "future", "change",
            "sacrifice", "symmetry", "observation", "state", "glory"]
# --- The three dimensions that have NO lexicon equivalent live or die by these
# lists, so they are kept broad and balanced across sub-themes. Scoring matches
# exact lowercased tokens (clean() splits on every non-letter), so singular AND
# plural forms are listed, plus solid compounds like "moonlight"/"nightingale".
# Words that double as common verbs (pine, swallow, crane, cross, train, fall)
# are left out on purpose to keep the counts honest.

NATURE = [
    # flora -- general
    "flower", "flowers", "blossom", "blossoms", "bloom", "blooms", "bud", "buds",
    "petal", "petals", "leaf", "leaves", "branch", "branches", "bough", "boughs",
    "twig", "twigs", "root", "roots", "vine", "vines", "fern", "ferns", "moss",
    "grass", "reed", "reeds", "thorn", "thorns", "bramble", "brambles", "hedge",
    "hedgerow", "meadow", "meadows", "field", "fields", "garden", "gardens",
    "grove", "groves", "wood", "woods", "woodland", "forest", "forests", "orchard",
    "thicket", "copse", "bower", "bowers", "dell", "glade", "glades", "glen",
    "heath", "moor", "moorland", "fen", "marsh", "pasture", "pastures",
    # trees
    "tree", "trees", "oak", "oaks", "elm", "elms", "fir", "firs", "birch", "beech",
    "willow", "willows", "yew", "cedar", "cypress", "poplar", "maple", "chestnut",
    "sycamore", "hawthorn", "holly", "ivy", "laurel",
    # flowers
    "rose", "roses", "lily", "lilies", "daffodil", "daffodils", "violet", "violets",
    "daisy", "daisies", "primrose", "primroses", "tulip", "tulips", "poppy",
    "poppies", "bluebell", "bluebells", "lavender", "jasmine", "honeysuckle",
    "marigold", "snowdrop", "snowdrops", "foxglove", "heather", "clover",
    "buttercup", "buttercups", "cowslip", "cowslips", "dandelion", "dandelions",
    # fruit / crops
    "fruit", "fruits", "apple", "apples", "cherry", "cherries", "plum", "plums",
    "grape", "grapes", "berry", "berries", "acorn", "acorns", "corn", "wheat",
    "harvest", "seed", "seeds", "grain", "hay", "sheaf", "sheaves",
    # birds
    "bird", "birds", "lark", "larks", "nightingale", "nightingales", "sparrow",
    "sparrows", "robin", "robins", "dove", "doves", "raven", "ravens", "crow",
    "crows", "owl", "owls", "eagle", "eagles", "hawk", "hawks", "swan", "swans",
    "thrush", "finch", "wren", "cuckoo", "blackbird", "starling", "gull", "gulls",
    "heron", "falcon", "wing", "wings", "feather", "feathers", "plume", "plumes",
    "nest", "nests",
    # animals
    "deer", "hare", "hares", "fox", "foxes", "wolf", "wolves", "lamb", "lambs",
    "sheep", "ewe", "ewes", "herd", "herds", "flock", "flocks", "cattle", "cow",
    "cows", "ox", "oxen", "horse", "horses", "steed", "steeds", "colt", "foal",
    "hound", "hounds", "stag", "stags", "doe", "fawn", "fawns", "rabbit", "rabbits",
    "squirrel", "squirrels", "bee", "bees", "butterfly", "butterflies", "moth",
    "moths", "beetle", "ant", "ants", "spider", "spiders", "worm", "worms", "snail",
    "snails", "serpent", "serpents", "snake", "snakes", "adder", "viper", "frog",
    "frogs", "toad", "toads", "fish", "trout", "salmon", "minnow", "whale",
    "whales", "dolphin", "dolphins", "hoof", "hooves", "claw", "claws", "paw",
    "paws", "fang", "fangs", "fleece",
    # sky / weather / celestial
    "sky", "skies", "cloud", "clouds", "sun", "suns", "moon", "moons", "star",
    "stars", "starlight", "sunlight", "moonlight", "dawn", "dusk", "twilight",
    "sunrise", "sunset", "rainbow", "rainbows", "lightning", "thunder", "storm",
    "storms", "tempest", "tempests", "wind", "winds", "breeze", "breezes", "gale",
    "gales", "zephyr", "zephyrs", "gust", "gusts", "rain", "rains", "shower",
    "showers", "snow", "snows", "frost", "frosts", "hail", "mist", "mists", "fog",
    "dew", "dews", "sleet",
    # water / landscape
    "sea", "seas", "ocean", "oceans", "river", "rivers", "stream", "streams",
    "brook", "brooks", "lake", "lakes", "pond", "ponds", "pool", "pools",
    "fountain", "fountains", "waterfall", "waterfalls", "cascade", "cascades",
    "wave", "waves", "tide", "tides", "shore", "shores", "beach", "beaches",
    "coast", "coasts", "cliff", "cliffs", "bay", "cove", "coves", "creek",
    "creeks", "rill", "rills", "billow", "billows", "surf", "foam", "mountain",
    "mountains", "hill", "hills", "valley", "valleys", "vale", "vales", "dale",
    "dales", "peak", "peaks", "summit", "summits", "ridge", "ridges", "slope",
    "slopes", "cave", "caves", "cavern", "caverns", "rock", "rocks", "stone",
    "stones", "crag", "crags", "boulder", "boulders", "sand", "sands", "soil",
    "earth", "ground", "dust", "isle", "isles", "island", "islands", "plains",
    "desert", "deserts", "wilderness", "wilds",
    # seasons / general
    "spring", "summer", "autumn", "winter", "season", "seasons", "springtime",
    "midsummer", "nature", "natural", "landscape", "countryside", "foliage",
    "greenery", "verdant",
]

INDUSTRIAL = [
    # machines and their parts
    "machine", "machines", "machinery", "engine", "engines", "motor", "motors",
    "mechanic", "mechanical", "mechanism", "gear", "gears", "cog", "cogs", "wheel",
    "wheels", "piston", "pistons", "lever", "levers", "crank", "cranks", "valve",
    "valves", "pulley", "pulleys", "axle", "axles", "rivet", "rivets", "spindle",
    "spindles", "loom", "looms", "shuttle", "shuttles", "groove", "grooves",
    "treadmill", "treadmills",
    # power / steam / fuel
    "steam", "coal", "smoke", "soot", "furnace", "furnaces", "boiler", "boilers",
    "forge", "forges", "foundry", "foundries", "kiln", "kilns", "fuel", "cinder",
    "cinders", "gas",
    # metal / materials
    "iron", "steel", "brass", "copper", "tin", "bronze", "metal", "metals", "ore",
    "anvil", "anvils", "hammer", "hammers", "nail", "nails", "chain", "chains",
    "wire", "wires", "girder", "girders", "rail", "rails", "railway", "railways",
    "railroad", "railroads",
    # factory / works
    "factory", "factories", "mill", "mills", "workshop", "workshops", "warehouse",
    "warehouses", "chimney", "chimneys", "smokestack", "smokestacks", "wharf",
    "wharves", "dock", "docks", "industry", "industries", "industrial",
    "manufacture", "manufactory",
    # transport
    "locomotive", "locomotives", "steamboat", "steamboats", "steamship",
    "steamships", "steamer", "steamers", "funnel", "funnels", "propeller",
    "propellers",
    # the industrial city (the claim is "machines and cities")
    "city", "cities", "street", "streets", "pavement", "gutter", "gutters", "slum",
    "slums", "alley", "alleys", "brick", "bricks", "smog", "grime", "grimy",
]

RELIGIOUS = [
    # the divine
    "god", "gods", "goddess", "christ", "jesus", "jehovah", "almighty", "creator",
    "maker", "savior", "saviour", "redeemer", "messiah", "providence", "deity",
    "godhead", "trinity", "divine", "divinity",
    # heaven / afterlife
    "heaven", "heavens", "heavenly", "paradise", "eden", "hell", "hades",
    "purgatory", "eternity", "eternal", "everlasting", "immortal", "immortality",
    "resurrection", "salvation", "damnation", "judgment", "judgement",
    # spirit / beings
    "soul", "souls", "spirit", "spirits", "spiritual", "angel", "angels",
    "angelic", "seraph", "seraphim", "cherub", "cherubim", "saint", "saints",
    "saintly", "devil", "devils", "satan", "demon", "demons",
    # worship / practice
    "pray", "prays", "prayed", "praying", "prayer", "prayers", "worship",
    "worshipped", "praise", "psalm", "psalms", "hymn", "hymns", "bless", "blessed",
    "blest", "blessing", "blessings", "grace", "mercy", "faith", "faithful",
    "creed", "gospel", "scripture", "scriptures", "bible", "sabbath", "communion",
    "sacrament", "baptism", "confession", "repent", "repentance", "penance",
    "pilgrimage", "pilgrim", "pilgrims", "devotion", "devout", "pious", "piety",
    "reverence", "kneel",
    # places / objects
    "church", "churches", "chapel", "cathedral", "temple", "temples", "shrine",
    "shrines", "altar", "altars", "sanctuary", "crucifix", "choir", "font",
    "steeple", "incense", "relic", "relics", "ark", "tabernacle", "pulpit",
    "cloister", "abbey", "monastery", "convent",
    # sin / holiness
    "sin", "sins", "sinful", "sinner", "sinners", "holy", "holiness", "hallowed",
    "sacred", "sanctify", "righteous", "righteousness", "redemption", "atonement",
    "forgiveness",
    # scripture figures / places
    "prophet", "prophets", "apostle", "apostles", "disciple", "disciples",
    "martyr", "martyrs", "calvary", "zion", "gethsemane", "golgotha",
]


# Poet -> rough active year, used to date PoetryDB poems (which carry no date).
AUTHOR_YEARS = {
    "Geoffrey Chaucer": 1380, "Thomas Wyatt": 1535, "Edmund Spenser": 1590,
    "Philip Sidney": 1580, "Walter Raleigh": 1590, "Christopher Marlowe": 1590,
    "William Shakespeare": 1600, "Michael Drayton": 1600,
    "John Donne": 1610, "Ben Jonson": 1610, "William Browne": 1620,
    "George Herbert": 1630, "Robert Herrick": 1640, "Richard Crashaw": 1640,
    "John Suckling": 1640, "Richard Lovelace": 1645, "Anne Bradstreet": 1650,
    "Henry Vaughan": 1655, "Andrew Marvell": 1660, "John Milton": 1660,
    "Thomas Flatman": 1670, "John Wilmot": 1675, "John Dryden": 1680,
    "Edward Taylor": 1685, "Anne Killigrew": 1683,
    "Lady Mary Chudleigh": 1700, "Anne Kingsmill Finch": 1700, "Matthew Prior": 1700,
    "Isaac Watts": 1715, "Jonathan Swift": 1715, "Alexander Pope": 1730,
    "James Thomson": 1730, "Samuel Johnson": 1750, "Thomas Gray": 1750,
    "William Collins": 1746, "Christopher Smart": 1755, "Joseph Warton": 1755,
    "Thomas Warton": 1765, "Oliver Goldsmith": 1765, "Charlotte Smith": 1785,
    "William Cowper": 1785, "Thomas Chatterton": 1768, "George Crabbe": 1790,
    "Robert Burns": 1790, "William Blake": 1794, "William Lisle Bowles": 1795,
    "John Keble": 1827,
    "Phillis Wheatley": 1773, "Philip Freneau": 1785, "John Trumbull": 1782,
    "Hugh Henry Brackenridge": 1780, "Henry Livingston": 1785,
    "Walter Scott": 1805, "William Wordsworth": 1805, "Samuel Taylor Coleridge": 1800,
    "Robert Southey": 1805, "Walter Savage Landor": 1810, "Charles Lamb": 1810,
    "Thomas Campbell": 1805, "Thomas Moore": 1810, "Leigh Hunt": 1815,
    "George Gordon Byron": 1815, "Percy Bysshe Shelley": 1819, "John Keats": 1819,
    "John Clare": 1820, "Jane Taylor": 1806,
    "Thomas Hood": 1830, "Elizabeth Barrett Browning": 1845, "Alfred Tennyson": 1845,
    "Robert Browning": 1845, "Edward Lear": 1850, "Emily Bronte": 1846,
    "Anne Bronte": 1846, "Charlotte Bronte": 1847, "Arthur Hugh Clough": 1850,
    "Charles Kingsley": 1855, "Matthew Arnold": 1860, "Coventry Patmore": 1860,
    "George Eliot": 1860, "Eliza Cook": 1850, "William Allingham": 1860,
    "Dante Gabriel Rossetti": 1865, "Christina Rossetti": 1860, "George Meredith": 1865,
    "Lewis Carroll": 1870, "William Morris": 1870, "Algernon Charles Swinburne": 1870,
    "Adam Lindsay Gordon": 1865, "William Topaz McGonagall": 1880,
    "Gerard Manley Hopkins": 1880, "Robert Bridges": 1885, "Oscar Wilde": 1885,
    "William Ernest Henley": 1888, "Francis Thompson": 1893, "Ernest Dowson": 1895,
    "Robert Louis Stevenson": 1885, "Katharine Tynan": 1895,
    "Mary Elizabeth Coleridge": 1895,
    "Thomas Hardy": 1895, "Rudyard Kipling": 1892, "Alfred Edward Housman": 1896,
    "Rupert Brooke": 1914, "Wilfred Owen": 1917, "John McCrae": 1915,
    "Charles Sorley": 1915, "Edward Thomas": 1915, "Joyce Kilmer": 1913,
    "William Cullen Bryant": 1820, "Ralph Waldo Emerson": 1840,
    "Henry Wadsworth Longfellow": 1850, "John Greenleaf Whittier": 1850,
    "Edgar Allan Poe": 1845, "Oliver Wendell Holmes": 1855, "Henry David Thoreau": 1850,
    "James Russell Lowell": 1855, "Walt Whitman": 1860, "Julia Ward Howe": 1862,
    "Emily Dickinson": 1862, "Helen Hunt Jackson": 1870, "Louisa May Alcott": 1870,
    "Mark Twain": 1875, "Emma Lazarus": 1880, "Sidney Lanier": 1875,
    "Eugene Field": 1885, "Ambrose Bierce": 1885, "James Whitcomb Riley": 1890,
    "Paul Laurence Dunbar": 1896, "Stephen Crane": 1895, "William Vaughn Moody": 1900,
    "Sara Teasdale": 1915, "Alan Seeger": 1916,
}

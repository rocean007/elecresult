/* ============================================================
   NEPAL ELECTION 2082 — LIVE RESULTS
   assets/app.js — All frontend logic
   ============================================================ */

'use strict';

/* ══════════════════════════════════════════════════════════════
   PARTY DEFINITIONS
══════════════════════════════════════════════════════════════ */
const PARTIES = {
  'CPN-UML': { name: 'CPN (UML)',           full: 'Communist Party of Nepal (UML)',  color: '#C0392B', abbr: 'UML'    },
  'NC':      { name: 'Nepali Congress',      full: 'Nepali Congress',                color: '#2563C4', abbr: 'NC'     },
  'RSP':     { name: 'Rastriya Swatantra',   full: 'Rastriya Swatantra Party',       color: '#1A7D52', abbr: 'RSP'    },
  'CPN-MC':  { name: 'CPN Maoist Centre',    full: 'CPN (Maoist Centre)',            color: '#7B3FA0', abbr: 'Maoist' },
  'RPP':     { name: 'Rastriya Prajatantra', full: 'Rastriya Prajatantra Party',     color: '#C07820', abbr: 'RPP'    },
  'LSP':     { name: 'Loktantrik Samajwadi', full: 'Loktantrik Samajwadi Party',     color: '#E85A20', abbr: 'LSP'    },
  'IND':     { name: 'Independent',          full: 'Independent',                    color: '#4A5568', abbr: 'IND'    },
};

/* ══════════════════════════════════════════════════════════════
   ALL 165 CONSTITUENCIES DATA  (demo — replace with /api/constituencies)
══════════════════════════════════════════════════════════════ */
function getAllConstituencies() {
  return [
    /* ── KOSHI ─────────────────────────────────────── */
    { id: 'TAP1', num: 1,  name: 'Taplejung-1',   district: 'Taplejung', province: 'Koshi', status: 'counting', reported: 42, candidates: [{ name: 'Dorje Lama',      party: 'NC',     votes: 12800 }, { name: 'Bir Bahadur',    party: 'CPN-UML', votes: 11900 }, { name: 'Pema Sherpa',   party: 'RSP',     votes: 5200  }] },
    { id: 'PAN1', num: 2,  name: 'Panchthar-1',   district: 'Panchthar', province: 'Koshi', status: 'counting', reported: 55, candidates: [{ name: 'Kumar Limbu',     party: 'CPN-UML', votes: 14200 }, { name: 'Sita Rai',       party: 'NC',     votes: 13100 }, { name: 'Gopal Subba',  party: 'RSP',     votes: 4800  }] },
    { id: 'ILA1', num: 3,  name: 'Ilam-1',        district: 'Ilam',      province: 'Koshi', status: 'counting', reported: 60, candidates: [{ name: 'Subarna Rai',     party: 'NC',     votes: 16700 }, { name: 'Tanka Angbuhang',party: 'CPN-UML', votes: 15400 }, { name: 'Binod Karki',   party: 'RSP',     votes: 7200  }] },
    { id: 'JHP1', num: 6,  name: 'Jhapa-1',       district: 'Jhapa',     province: 'Koshi', status: 'counting', reported: 58, candidates: [{ name: 'Bharat Prasai',   party: 'NC',     votes: 18400 }, { name: 'Gyan Bahadur',   party: 'CPN-UML', votes: 17200 }, { name: 'Prem Khatri',   party: 'RSP',     votes: 6500  }] },
    { id: 'JHP5', num: 10, name: 'Jhapa-5',        district: 'Jhapa',     province: 'Koshi', status: 'counting', reported: 65, candidates: [{ name: 'Balendra Shah',   party: 'RSP',    votes: 34215 }, { name: 'KP Sharma Oli',  party: 'CPN-UML', votes: 31087 }, { name: 'Ram Kumar Rai', party: 'NC',     votes: 8432  }] },
    { id: 'MOR1', num: 11, name: 'Morang-1',       district: 'Morang',    province: 'Koshi', status: 'counting', reported: 50, candidates: [{ name: 'Rajesh Hagam',    party: 'CPN-UML', votes: 21300 }, { name: 'Madhav Sapkota', party: 'NC',     votes: 19800 }, { name: 'Anita Rai',    party: 'RSP',     votes: 8700  }] },
    { id: 'SNS2', num: 18, name: 'Sunsari-2',      district: 'Sunsari',   province: 'Koshi', status: 'counting', reported: 48, candidates: [{ name: 'Shankar Pokhrel', party: 'CPN-UML', votes: 19200 }, { name: 'Shekhar Koirala',party: 'NC',     votes: 18100 }, { name: 'Dipak Kharal',  party: 'RSP',     votes: 9800  }] },
    { id: 'DHA1', num: 19, name: 'Dhankuta-1',     district: 'Dhankuta',  province: 'Koshi', status: 'declared',reported: 100,candidates: [{ name: 'Surendra Pandey', party: 'CPN-UML', votes: 22100 }, { name: 'Chanda Lal',     party: 'NC',     votes: 19400 }, { name: 'Sunita KC',     party: 'RSP',     votes: 9800  }] },
    { id: 'TRH1', num: 22, name: 'Terhathum-1',    district: 'Terhathum', province: 'Koshi', status: 'counting', reported: 36, candidates: [{ name: 'Prakash Kafle',   party: 'NC',     votes: 9800  }, { name: 'Hari Khawas',    party: 'CPN-UML', votes: 9200  }, { name: 'Sabita Rai',   party: 'RSP',     votes: 4100  }] },
    { id: 'OKH1', num: 27, name: 'Okhaldhunga-1',  district: 'Okhaldhunga',province: 'Koshi', status: 'counting', reported: 45, candidates: [{ name: 'Nawaraj Silwal',  party: 'CPN-UML', votes: 11200 }, { name: 'Hira Bahadur',   party: 'NC',     votes: 10700 }, { name: 'Pradeep Rai',   party: 'RSP',     votes: 4200  }] },

    /* ── MADHESH ────────────────────────────────────── */
    { id: 'SRL3', num: 35, name: 'Sarlahi-3',      district: 'Sarlahi',   province: 'Madhesh', status: 'counting', reported: 39, candidates: [{ name: 'Rajendra Mahato',  party: 'LSP',    votes: 16800 }, { name: 'Anil Jha',       party: 'NC',     votes: 15900 }, { name: 'Umesh Yadav',   party: 'CPN-UML', votes: 11200 }] },
    { id: 'RTH2', num: 40, name: 'Rautahat-2',     district: 'Rautahat',  province: 'Madhesh', status: 'counting', reported: 44, candidates: [{ name: 'Bijay K. Gachhadar',party: 'NC',    votes: 14500 }, { name: 'Saroj K. Yadav', party: 'LSP',    votes: 13800 }, { name: 'Dev K. Prasad',  party: 'CPN-UML', votes: 10200 }] },
    { id: 'BAR1', num: 42, name: 'Bara-1',          district: 'Bara',      province: 'Madhesh', status: 'counting', reported: 53, candidates: [{ name: 'Shyam K. Mahato',  party: 'LSP',    votes: 18200 }, { name: 'Gita Devi',      party: 'NC',     votes: 16400 }, { name: 'Ram Prasad',    party: 'CPN-UML', votes: 12100 }] },
    { id: 'PRH1', num: 44, name: 'Parsa-1',         district: 'Parsa',     province: 'Madhesh', status: 'counting', reported: 47, candidates: [{ name: 'Ajay Prasad',      party: 'NC',     votes: 15300 }, { name: 'Santosh Yadav',  party: 'LSP',    votes: 14200 }, { name: 'Nirmala Sah',   party: 'CPN-UML', votes: 9800  }] },
    { id: 'MTH1', num: 51, name: 'Mahottari-1',     district: 'Mahottari', province: 'Madhesh', status: 'counting', reported: 32, candidates: [{ name: 'Ramchandra Jha',   party: 'LSP',    votes: 12100 }, { name: 'Binod Chaudhary',party: 'NC',     votes: 11200 }, { name: 'Lalbabu Yadav', party: 'CPN-UML', votes: 7800  }] },
    { id: 'DHN1', num: 56, name: 'Dhanusa-1',       district: 'Dhanusa',   province: 'Madhesh', status: 'counting', reported: 29, candidates: [{ name: 'Mahendra Yadav',   party: 'LSP',    votes: 9800  }, { name: 'Punam Kumari',   party: 'NC',     votes: 8900  }, { name: 'Naresh Jha',    party: 'CPN-UML', votes: 6200  }] },
    { id: 'SRH1', num: 62, name: 'Siraha-1',        district: 'Siraha',    province: 'Madhesh', status: 'counting', reported: 41, candidates: [{ name: 'Rajesh Yadav',     party: 'NC',     votes: 13400 }, { name: 'Sanjay Raut',    party: 'LSP',    votes: 12800 }, { name: 'Bhola Nath',    party: 'CPN-UML', votes: 8900  }] },

    /* ── BAGMATI ────────────────────────────────────── */
    { id: 'SIN1', num: 69, name: 'Sindhuli-1',      district: 'Sindhuli',  province: 'Bagmati', status: 'counting', reported: 63, candidates: [{ name: 'Laxmi Prasad',     party: 'NC',     votes: 17800 }, { name: 'Govinda Rijal',  party: 'CPN-UML', votes: 16200 }, { name: 'Shiva Poudel',  party: 'RSP',     votes: 6900  }] },
    { id: 'KVR2', num: 72, name: 'Kavre-2',          district: 'Kavre',     province: 'Bagmati', status: 'declared',reported: 100,candidates: [{ name: 'Ramesh Lekhak',   party: 'NC',     votes: 31500 }, { name: 'Pradeep Gyawali',party: 'CPN-UML', votes: 29400 }, { name: 'Bidur Karki',   party: 'RSP',     votes: 11800 }] },
    { id: 'BHK1', num: 74, name: 'Bhaktapur-1',     district: 'Bhaktapur', province: 'Bagmati', status: 'declared',reported: 100,candidates: [{ name: 'Sunil Prajapati',  party: 'RSP',    votes: 29800 }, { name: 'Narayan K. Shrestha',party:'CPN-MC', votes: 27300 }, { name: 'Bidhan Giri',   party: 'CPN-UML', votes: 15700 }] },
    { id: 'LAL1', num: 75, name: 'Lalitpur-1',      district: 'Lalitpur',  province: 'Bagmati', status: 'counting', reported: 74, candidates: [{ name: 'Kiran Gurung',     party: 'RSP',    votes: 26800 }, { name: 'Bimala Gurung',  party: 'NC',     votes: 24200 }, { name: 'Yubraj Khatri', party: 'CPN-UML', votes: 14100 }] },
    { id: 'KTM1', num: 78, name: 'Kathmandu-1',     district: 'Kathmandu', province: 'Bagmati', status: 'counting', reported: 81, candidates: [{ name: 'Prakash Sharan',   party: 'RSP',    votes: 38600 }, { name: 'Mahesh Basnet',  party: 'NC',     votes: 35100 }, { name: 'Narayan Khadgi',party: 'CPN-UML', votes: 18200 }] },
    { id: 'KTM4', num: 81, name: 'Kathmandu-4',     district: 'Kathmandu', province: 'Bagmati', status: 'counting', reported: 78, candidates: [{ name: 'Rabi Lamichhane',  party: 'RSP',    votes: 42100 }, { name: 'Gagan Thapa',    party: 'NC',     votes: 39854 }, { name: 'Bhim Rawal',    party: 'CPN-UML', votes: 12320 }] },
    { id: 'CTW3', num: 84, name: 'Chitwan-3',       district: 'Chitwan',   province: 'Bagmati', status: 'counting', reported: 55, candidates: [{ name: 'Renu Dahal',       party: 'CPN-MC', votes: 27800 }, { name: 'Shekhar Koirala',party: 'NC',     votes: 26900 }, { name: 'Tek B. Gurung', party: 'CPN-UML', votes: 14200 }] },
    { id: 'DHD2', num: 87, name: 'Dhading-2',       district: 'Dhading',   province: 'Bagmati', status: 'counting', reported: 71, candidates: [{ name: 'Ishwor Pokhrel',   party: 'CPN-UML', votes: 24700 }, { name: 'Dhan B. Shrestha',party: 'NC',    votes: 23100 }, { name: 'Sita Gurung',   party: 'RSP',     votes: 13400 }] },
    { id: 'MAK1', num: 89, name: 'Makwanpur-1',     district: 'Makwanpur', province: 'Bagmati', status: 'counting', reported: 67, candidates: [{ name: 'Raj K. Rai',       party: 'NC',     votes: 22400 }, { name: 'Sashi Shrestha', party: 'CPN-UML', votes: 20800 }, { name: 'Devi Gurung',   party: 'CPN-MC',  votes: 11200 }] },

    /* ── GANDAKI ────────────────────────────────────── */
    { id: 'GOR1', num: 93, name: 'Gorkha-1',        district: 'Gorkha',    province: 'Gandaki', status: 'counting', reported: 58, candidates: [{ name: 'Narayan Dahal',    party: 'CPN-MC', votes: 19200 }, { name: 'Mohan B. Shahi', party: 'NC',     votes: 17800 }, { name: 'Chet B. Gurung',party: 'CPN-UML', votes: 13200 }] },
    { id: 'KSK1', num: 96, name: 'Pokhara-1',       district: 'Kaski',     province: 'Gandaki', status: 'counting', reported: 82, candidates: [{ name: 'Krishna Sitaula',  party: 'NC',     votes: 38200 }, { name: 'Ram B. Thapa',   party: 'CPN-MC', votes: 26500 }, { name: 'Khadga B. Bisht',party: 'CPN-UML', votes: 19100}] },
    { id: 'KSK3', num: 98, name: 'Pokhara-3',       district: 'Kaski',     province: 'Gandaki', status: 'counting', reported: 77, candidates: [{ name: 'Man B. Budha',     party: 'NC',     votes: 34100 }, { name: 'Rajendra Lingden',party:'RPP',    votes: 28800 }, { name: 'Hari Lamsal',   party: 'CPN-UML', votes: 16400 }] },
    { id: 'MYG1', num: 99, name: 'Myagdi-1',        district: 'Myagdi',    province: 'Gandaki', status: 'counting', reported: 43, candidates: [{ name: 'Sanjay Gurung',    party: 'CPN-MC', votes: 11400 }, { name: 'Bimala Kandel',  party: 'NC',     votes: 10600 }, { name: 'Tek Gurung',    party: 'CPN-UML', votes: 6800  }] },
    { id: 'LMJ1', num: 103,name: 'Lamjung-1',       district: 'Lamjung',   province: 'Gandaki', status: 'counting', reported: 51, candidates: [{ name: 'Narahari Acharya',  party: 'NC',     votes: 14200 }, { name: 'Ram M. Paudel',  party: 'CPN-MC', votes: 13100 }, { name: 'Man B. Gurung', party: 'CPN-UML', votes: 8700  }] },

    /* ── LUMBINI ────────────────────────────────────── */
    { id: 'RPN4', num: 107,name: 'Rupandehi-4',     district: 'Rupandehi', province: 'Lumbini', status: 'counting', reported: 62, candidates: [{ name: 'Khagaraj Adhikari', party: 'RPP',    votes: 22400 }, { name: 'Surendra Pandey',party: 'CPN-UML', votes: 21900 }, { name: 'Prakash M. Singh',party:'NC',     votes: 18500 }] },
    { id: 'RKM1', num: 114,name: 'Rukum East-1',    district: 'Rukum E.',  province: 'Lumbini', status: 'counting', reported: 57, candidates: [{ name: 'Agni Sapkota',      party: 'CPN-MC', votes: 18400 }, { name: 'Dilli B. Chaudhary',party:'NC',  votes: 15200 }, { name: 'Bed P. Pandey', party: 'CPN-UML', votes: 12900 }] },
    { id: 'ROL1', num: 116,name: 'Rolpa-1',         district: 'Rolpa',     province: 'Lumbini', status: 'counting', reported: 49, candidates: [{ name: 'Narayankaji Shrestha',party:'CPN-MC',votes: 14800 }, { name: 'Tanka Dhamala', party: 'NC',     votes: 12100 }, { name: 'Gopal Bam',     party: 'CPN-UML', votes: 9200  }] },
    { id: 'PAL1', num: 119,name: 'Palpa-1',         district: 'Palpa',     province: 'Lumbini', status: 'counting', reported: 68, candidates: [{ name: 'Krishna B. Thapa',  party: 'NC',     votes: 18700 }, { name: 'Minnath Adhikari',party:'CPN-UML',votes: 17200 }, { name: 'Tara Bhattarai',party: 'CPN-MC',  votes: 9100  }] },
    { id: 'SYJ1', num: 121,name: 'Syangja-1',       district: 'Syangja',   province: 'Lumbini', status: 'counting', reported: 59, candidates: [{ name: 'Bhim Acharya',      party: 'NC',     votes: 16200 }, { name: 'Prem Thapa',     party: 'RPP',    votes: 14800 }, { name: 'Kali B. Khatri', party: 'CPN-UML', votes: 11400 }] },
    { id: 'CAP1', num: 124,name: 'Kapilvastu-1',    district: 'Kapilvastu',province: 'Lumbini', status: 'counting', reported: 44, candidates: [{ name: 'Manoj Tiwari',      party: 'NC',     votes: 14900 }, { name: 'Shankar Pokhrel',party: 'CPN-UML', votes: 13600 }, { name: 'Dambar Thapa',  party: 'RSP',     votes: 7200  }] },
    { id: 'BUT1', num: 127,name: 'Butwal-1',         district: 'Rupandehi', province: 'Lumbini', status: 'counting', reported: 70, candidates: [{ name: 'Sushil Gyawali',   party: 'NC',     votes: 24100 }, { name: 'Ram Prasad Khand',party:'CPN-UML', votes: 22800 }, { name: 'Priya Sharma',  party: 'RSP',     votes: 10400 }] },
    { id: 'DNG1', num: 130,name: 'Dang-1',           district: 'Dang',      province: 'Lumbini', status: 'counting', reported: 55, candidates: [{ name: 'Bikas Lamsal',      party: 'CPN-UML', votes: 17200 }, { name: 'Sunita Bogati',  party: 'NC',     votes: 15900 }, { name: 'Lal B. KC',     party: 'CPN-MC',  votes: 9800  }] },
    { id: 'BNK1', num: 133,name: 'Banke-1',          district: 'Banke',     province: 'Lumbini', status: 'counting', reported: 47, candidates: [{ name: 'Mahendra Rayamajhi',party:'NC',    votes: 15800 }, { name: 'Bam Dev Gautam',party: 'CPN-UML', votes: 14200 }, { name: 'Gita Thapa',    party: 'RSP',     votes: 6900  }] },

    /* ── KARNALI ────────────────────────────────────── */
    { id: 'KRN1', num: 136,name: 'Karnali-1',        district: 'Surkhet',   province: 'Karnali', status: 'counting', reported: 33, candidates: [{ name: 'Mahendra Bahadur', party: 'CPN-UML', votes: 11200 }, { name: 'Rekha Sharma',   party: 'NC',     votes: 9800  }, { name: 'Jeevan Pariyar',party: 'CPN-MC',  votes: 7400  }] },
    { id: 'SUR1', num: 137,name: 'Surkhet-1',         district: 'Surkhet',   province: 'Karnali', status: 'counting', reported: 40, candidates: [{ name: 'Bikas Pokharel',   party: 'NC',     votes: 12400 }, { name: 'Bhim Pariyar',   party: 'CPN-UML', votes: 11100 }, { name: 'Dil B. Dhami',  party: 'RPP',     votes: 5800  }] },
    { id: 'DLC1', num: 139,name: 'Dailekh-1',         district: 'Dailekh',   province: 'Karnali', status: 'counting', reported: 37, candidates: [{ name: 'Lekh Raj Bhatta',  party: 'CPN-UML', votes: 10800 }, { name: 'Parbati Kunwar', party: 'NC',     votes: 9600  }, { name: 'Nabin Budha',   party: 'CPN-MC',  votes: 6200  }] },
    { id: 'JML1', num: 141,name: 'Jajarkot-1',        district: 'Jajarkot',  province: 'Karnali', status: 'counting', reported: 28, candidates: [{ name: 'Bir B. Budha',      party: 'CPN-MC', votes: 8900  }, { name: 'Ram B. Shahi',   party: 'NC',     votes: 7800  }, { name: 'Man B. Buda',   party: 'CPN-UML', votes: 5400  }] },
    { id: 'MST1', num: 144,name: 'Mugu-1',             district: 'Mugu',      province: 'Karnali', status: 'counting', reported: 22, candidates: [{ name: 'Karna B. Buda',     party: 'NC',     votes: 5100  }, { name: 'Tulsi B. Sahi',  party: 'CPN-UML', votes: 4600  }, { name: 'Govinda Shahi', party: 'RPP',     votes: 2800  }] },
    { id: 'HUM1', num: 146,name: 'Humla-1',            district: 'Humla',     province: 'Karnali', status: 'counting', reported: 18, candidates: [{ name: 'Dhan B. Shahi',     party: 'RPP',    votes: 4200  }, { name: 'Sher B. Buda',   party: 'NC',     votes: 3800  }, { name: 'Kami Lama',     party: 'CPN-UML', votes: 2600  }] },

    /* ── SUDURPASHCHIM ──────────────────────────────── */
    { id: 'SDR1', num: 150,name: 'Kailali-1',         district: 'Kailali',   province: 'Sudurpashchim', status: 'counting', reported: 51, candidates: [{ name: 'Chitra Bahadur KC',party:'RSP',   votes: 17800 }, { name: 'Lal B. Kunwar',  party: 'RPP',    votes: 15200 }, { name: 'Tulsi Bhatta',  party: 'NC',     votes: 12900 }] },
    { id: 'KAI2', num: 151,name: 'Kailali-2',         district: 'Kailali',   province: 'Sudurpashchim', status: 'counting', reported: 46, candidates: [{ name: 'Top B. Rayamajhi', party: 'NC',    votes: 14200 }, { name: 'Dillu KC',       party: 'CPN-UML', votes: 13400 }, { name: 'Sita Dhami',    party: 'RSP',     votes: 8700  }] },
    { id: 'KCH1', num: 153,name: 'Kanchanpur-1',      district: 'Kanchanpur',province: 'Sudurpashchim', status: 'counting', reported: 55, candidates: [{ name: 'Bishnu Prasad',   party: 'CPN-UML', votes: 16800 }, { name: 'Tara Devi',      party: 'NC',     votes: 15100 }, { name: 'Man B. Bist',   party: 'RPP',     votes: 9200  }] },
    { id: 'BAJ1', num: 156,name: 'Bajhang-1',          district: 'Bajhang',   province: 'Sudurpashchim', status: 'counting', reported: 31, candidates: [{ name: 'Prakash Saud',     party: 'NC',     votes: 8900  }, { name: 'Sher B. Dhami',  party: 'CPN-UML', votes: 8100  }, { name: 'Karna B. Khatri',party:'RPP',    votes: 4800  }] },
    { id: 'DDL1', num: 158,name: 'Dadeldhura-1',       district: 'Dadeldhura',province: 'Sudurpashchim', status: 'counting', reported: 42, candidates: [{ name: 'Shankar Bhandari',party: 'CPN-UML',votes: 12100 }, { name: 'Khem Raj Ghimire',party:'NC',     votes: 11400 }, { name: 'Amrit KC',      party: 'RSP',     votes: 5600  }] },
    { id: 'BAI1', num: 159,name: 'Baitadi-1',          district: 'Baitadi',   province: 'Sudurpashchim', status: 'counting', reported: 36, candidates: [{ name: 'Prakash B. Thapa', party: 'NC',     votes: 10800 }, { name: 'Bam B. Deupa',   party: 'CPN-UML', votes: 9900  }, { name: 'Laxmi Rokka',   party: 'RPP',     votes: 5200  }] },
    { id: 'DRC1', num: 162,name: 'Darchula-1',         district: 'Darchula',  province: 'Sudurpashchim', status: 'counting', reported: 25, candidates: [{ name: 'Sher Singh Bist',  party: 'RPP',    votes: 7200  }, { name: 'Pooja Saud',     party: 'NC',     votes: 6800  }, { name: 'Prem B. Bista', party: 'CPN-UML', votes: 4900  }] },
  ];
}

/* ══════════════════════════════════════════════════════════════
   PARTY SEAT SUMMARY DATA (demo — replace with /api/party-seats)
══════════════════════════════════════════════════════════════ */
function getSeatData() {
  return [
    { id: 'CPN-UML', fptp: 47, pr: 30, total: 77 },
    { id: 'NC',      fptp: 38, pr: 26, total: 64 },
    { id: 'RSP',     fptp: 28, pr: 14, total: 42 },
    { id: 'CPN-MC',  fptp: 12, pr: 11, total: 23 },
    { id: 'RPP',     fptp:  9, pr:  7, total: 16 },
    { id: 'LSP',     fptp:  5, pr:  6, total: 11 },
    { id: 'IND',     fptp:  8, pr:  0, total:  8 },
  ];
}

/* ══════════════════════════════════════════════════════════════
   HELPERS
══════════════════════════════════════════════════════════════ */
const getParty = (id) => PARTIES[id] || { name: id, full: id, color: '#888', abbr: id.substring(0,4) };
const fmt = (n) => n.toLocaleString('en-IN');
const pctOf = (v, tot) => tot ? ((v / tot) * 100).toFixed(1) : '0.0';

function photoEl(img, name, cls = '') {
  if (img) return `<img src="images/candidates/${img}" alt="${name}" loading="lazy" onerror="this.parentElement.textContent='👤'">`;
  return '👤';
}

function escapeRe(s) { return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }

function highlight(text, q) {
  if (!q) return text;
  const re = new RegExp(`(${escapeRe(q)})`, 'gi');
  return text.replace(re, '<mark class="sh">$1</mark>');
}

function matchesSearch(zone, q) {
  if (!q) return true;
  const l = q.toLowerCase();
  if (zone.name.toLowerCase().includes(l)) return true;
  if (zone.district.toLowerCase().includes(l)) return true;
  if (zone.province.toLowerCase().includes(l)) return true;
  if (zone.id.toLowerCase().includes(l)) return true;
  if (String(zone.num).includes(l)) return true;
  for (const c of zone.candidates) {
    if (c.name.toLowerCase().includes(l)) return true;
    const p = getParty(c.party);
    if (p.abbr.toLowerCase().includes(l) || p.name.toLowerCase().includes(l) || c.party.toLowerCase().includes(l)) return true;
  }
  return false;
}

/* ══════════════════════════════════════════════════════════════
   GLOBAL STATE
══════════════════════════════════════════════════════════════ */
let ALL_ZONES      = [];
let ACTIVE_FILTER  = 'all';
let ZONE_QUERY     = '';
let HDR_FOCUS_IDX  = -1;

/* ══════════════════════════════════════════════════════════════
   SEATS BAR
══════════════════════════════════════════════════════════════ */
function renderSeatsBar(seats) {
  const bar = document.getElementById('seats-bar');
  if (!bar) return;
  bar.innerHTML = '<div class="majority-line"></div>';
  const total = 275;
  [...seats].sort((a,b) => b.total - a.total).forEach(s => {
    if (!s.total) return;
    const p = getParty(s.id);
    const pct = (s.total / total) * 100;
    const seg = document.createElement('div');
    seg.className = 'bar-seg';
    seg.style.cssText = `width:${pct}%;background:${p.color}`;
    seg.title = `${p.abbr}: ${s.total} seats`;
    if (pct > 4) seg.innerHTML = `<span class="bar-seg-lbl">${p.abbr}</span>`;
    bar.appendChild(seg);
  });
}

/* ══════════════════════════════════════════════════════════════
   PARTY CHIP GRID
══════════════════════════════════════════════════════════════ */
function renderPartyGrid(seats) {
  const g = document.getElementById('party-grid');
  if (!g) return;
  g.innerHTML = '';
  [...seats].sort((a,b) => b.total - a.total).forEach(s => {
    const p = getParty(s.id);
    const chip = document.createElement('div');
    chip.className = 'party-chip';
    chip.style.setProperty('--pc', p.color);
    chip.innerHTML = `
      <div class="pc-abbr">${p.abbr}</div>
      <div class="pc-name">${p.name}</div>
      <div class="pc-seats">${s.total}</div>
      <div class="pc-label">Total Seats</div>
      <div class="pc-breakdown"><span>FPTP <strong>${s.fptp}</strong></span><span>PR <strong>${s.pr}</strong></span></div>`;
    g.appendChild(chip);
  });
}

/* ══════════════════════════════════════════════════════════════
   LEAD TABLE + MAJORITY METER
══════════════════════════════════════════════════════════════ */
function renderLeadTable(seats) {
  const t = document.getElementById('lead-table');
  if (!t) return;
  t.innerHTML = '';
  [...seats].sort((a,b) => b.total - a.total).slice(0,7).forEach((s, i) => {
    const p = getParty(s.id);
    const row = document.createElement('div');
    row.className = 'lead-row';
    row.innerHTML = `
      <div class="lr-rank ${i===0?'r1':''}">${i+1}</div>
      <div class="lr-dot" style="background:${p.color}"></div>
      <div class="lr-name">${p.name}</div>
      <div class="lr-seats">${s.total}</div>`;
    t.appendChild(row);
  });

  const leader = [...seats].sort((a,b)=>b.total-a.total)[0];
  if (leader) {
    const p = getParty(leader.id);
    const pct = Math.min((leader.total/138)*100, 100);
    const mf = document.getElementById('majority-fill');
    const mn = document.getElementById('majority-note');
    if (mf) { mf.style.width = pct+'%'; mf.style.background = `linear-gradient(90deg,${p.color}88,${p.color})`; }
    const gap = 138 - leader.total;
    if (mn) mn.textContent = gap > 0 ? `${p.abbr} needs ${gap} more seats for majority` : `${p.abbr} has secured majority`;
  }
}

/* ══════════════════════════════════════════════════════════════
   ZONE CARD (tournament bracket)
══════════════════════════════════════════════════════════════ */
function buildZoneCard(zone, delay = 0, q = '') {
  const cands = zone.candidates.slice(0, 3);
  const totV  = cands.reduce((s,c) => s + c.votes, 0) || 1;
  const [c1, c2, c3] = cands;
  const p1 = c1 ? getParty(c1.party) : null;

  const buildChallenger = (c, rank) => {
    if (!c) return '';
    const p = getParty(c.party);
    return `
      <div class="challenger-card rank-${rank}">
        <div class="ch-rank">${rank===2?'2nd Place':'3rd Place'}</div>
        <div class="ch-photo-name">
          <div class="ch-photo">${photoEl(c.img, c.name)}</div>
          <div class="ch-name">${highlight(c.name, q)}</div>
        </div>
        <div class="ch-party"><div class="t-party-dot" style="background:${getParty(c.party).color}"></div><span style="color:${getParty(c.party).color}">${highlight(getParty(c.party).abbr, q)}</span></div>
        <div class="ch-votes">${fmt(c.votes)}</div>
        <div class="ch-pct">${pctOf(c.votes,totV)}%</div>
      </div>`;
  };

  const trackHtml = cands.map(c => `<div class="vote-track-seg" style="width:${pctOf(c.votes,totV)}%;background:${getParty(c.party).color}"></div>`).join('');
  const badgeClass = zone.status === 'declared' ? 'badge-declared' : 'badge-counting';
  const badgeText  = zone.status === 'declared' ? '✓ Declared' : '⚡ Counting';

  const card = document.createElement('div');
  card.className = 'zone-card';
  card.dataset.province = zone.province;
  card.dataset.id = zone.id;
  card.style.animationDelay = delay + 's';

  card.innerHTML = `
    <div class="zone-header">
      <div>
        <div class="zone-name">${highlight(zone.name, q)}</div>
        <div class="zone-meta">${highlight(zone.district, q)} · ${highlight(zone.province, q)}</div>
      </div>
      <div class="zone-status-badge ${badgeClass}">${badgeText}</div>
    </div>
    <div class="tournament-wrap">
      ${c1 ? `
        <div class="tournament-winner">
          <div class="t-rank-badge">🥇 Leading</div>
          <div class="t-candidate-inner">
            <div class="t-photo">${photoEl(c1.img||null, c1.name)}</div>
            <div class="t-info">
              <div class="t-name">${highlight(c1.name, q)}</div>
              <div class="t-party-tag">
                <div class="t-party-dot" style="background:${p1.color}"></div>
                <span style="color:${p1.color};font-weight:700">${highlight(p1.abbr, q)}</span>
                <span style="color:var(--text-3)">${p1.name}</span>
              </div>
            </div>
            <div class="t-votes-wrap">
              <div class="t-votes-num">${fmt(c1.votes)}</div>
              <div class="t-votes-pct">${pctOf(c1.votes,totV)}%</div>
            </div>
          </div>
        </div>` : ''}
      ${(c2||c3) ? `
        <div class="vs-divider"><div class="vs-line"></div><div class="vs-label">Challengers</div><div class="vs-line"></div></div>
        <div class="challengers-row">${buildChallenger(c2,2)}${buildChallenger(c3,3)}</div>` : ''}
    </div>
    <div class="vote-track">${trackHtml}</div>
    <div class="zone-footer">
      <div class="zf-reported">${zone.reported}% votes counted</div>
      <div class="zf-progress">
        <div class="zf-bar"><div class="zf-fill" style="width:${zone.reported}%"></div></div>
        <div class="zf-pct-lbl">${zone.reported}%</div>
      </div>
    </div>`;

  card.addEventListener('click', () => openModal(zone));
  return card;
}

/* ══════════════════════════════════════════════════════════════
   ZONE FILTER + RENDER
══════════════════════════════════════════════════════════════ */
function filterZones(province, btn) {
  document.querySelectorAll('.fpill').forEach(b => b.classList.remove('active'));
  if (btn) btn.classList.add('active');
  ACTIVE_FILTER = province;
  renderZones();
}
window.filterZones = filterZones;

function renderZones() {
  const grid     = document.getElementById('zones-grid');
  const countEl  = document.getElementById('search-count');
  if (!grid) return;
  grid.innerHTML = '';

  let filtered = ACTIVE_FILTER === 'all' ? ALL_ZONES : ALL_ZONES.filter(z => z.province === ACTIVE_FILTER);
  const q = ZONE_QUERY.trim();
  if (q) filtered = filtered.filter(z => matchesSearch(z, q));

  if (countEl) {
    countEl.innerHTML = q
      ? (filtered.length === 0
          ? `<span class="no-r">No results for "<strong>${q}</strong>"</span>`
          : `<span class="hl">${filtered.length}</span> result${filtered.length!==1?'s':''} for "<strong>${q}</strong>"`)
      : `Showing ${filtered.length} of ${ALL_ZONES.length} constituencies`;
  }

  if (filtered.length === 0) {
    const d = document.createElement('div');
    d.className = 'no-results-state';
    d.innerHTML = `<div class="nrs-icon">🔍</div><div class="nrs-title">No constituencies found</div><div class="nrs-sub">Try a different search term or select all provinces</div>`;
    grid.appendChild(d);
    return;
  }

  filtered.forEach((z, i) => grid.appendChild(buildZoneCard(z, i * 0.035, q)));
}

/* ══════════════════════════════════════════════════════════════
   CONSTITUENCY DETAIL MODAL
══════════════════════════════════════════════════════════════ */
function openModal(zone) {
  const backdrop = document.getElementById('const-modal');
  if (!backdrop) return;

  const cands = zone.candidates;
  const totV  = cands.reduce((s,c) => s+c.votes, 0) || 1;
  const [c1, c2, c3] = cands;

  const statusClass = zone.status === 'declared' ? 'ms-declared' : 'ms-counting';
  const statusText  = zone.status === 'declared' ? '✓ DECLARED' : '⚡ COUNTING';

  const buildModalCh = (c, rank) => {
    if (!c) return '';
    const p = getParty(c.party);
    return `
      <div class="modal-ch rank-${rank}">
        <div class="modal-ch-rank">${rank===2?'2nd Place':'3rd Place'}</div>
        <div class="modal-ch-inner">
          <div class="modal-photo sm">${photoEl(c.img||null, c.name)}</div>
          <div class="modal-ch-name">${c.name}</div>
        </div>
        <div class="modal-ch-party"><div class="party-dot" style="background:${p.color}"></div><span style="color:${p.color}">${p.abbr}</span><span style="color:var(--text-3);font-weight:400;font-size:.6rem">·  ${p.name}</span></div>
        <div class="modal-ch-votes">${fmt(c.votes)}</div>
        <div class="modal-ch-pct">${pctOf(c.votes,totV)}% of counted votes</div>
      </div>`;
  };

  const trackHtml = cands.map(c => `<div class="modal-track-seg" style="width:${pctOf(c.votes,totV)}%;background:${getParty(c.party).color}"></div>`).join('');

  backdrop.querySelector('.modal-title').textContent = zone.name;
  backdrop.querySelector('.modal-subtitle').textContent = `${zone.district} · ${zone.province} · Constituency #${zone.num}`;
  backdrop.querySelector('.modal-status').className   = `modal-status ${statusClass}`;
  backdrop.querySelector('.modal-status').textContent = statusText;

  const progFill = backdrop.querySelector('.modal-prog-fill');
  if (progFill) progFill.style.width = zone.reported + '%';
  const progLabel = backdrop.querySelector('.modal-prog-strong');
  if (progLabel) progLabel.textContent = zone.reported + '%';

  const winnerWrap = backdrop.querySelector('#modal-winner-wrap');
  if (winnerWrap && c1) {
    const p1 = getParty(c1.party);
    winnerWrap.innerHTML = `
      <div class="modal-winner">
        <div class="modal-photo">${photoEl(c1.img||null, c1.name)}</div>
        <div class="modal-cand-info">
          <div class="modal-cand-name">${c1.name}</div>
          <div class="modal-cand-party"><div class="party-dot" style="background:${p1.color}"></div><span style="color:${p1.color}">${p1.abbr}</span><span style="color:var(--text-3)"> · ${p1.name}</span></div>
        </div>
        <div class="modal-votes">
          <div class="modal-votes-num">${fmt(c1.votes)}</div>
          <div class="modal-votes-pct">${pctOf(c1.votes,totV)}%</div>
        </div>
      </div>`;
  }

  const challWrap = backdrop.querySelector('#modal-challengers-wrap');
  if (challWrap) {
    challWrap.innerHTML = `
      <div class="modal-vs-row"><div class="modal-vs-line"></div><div class="modal-vs-lbl">Challengers</div><div class="modal-vs-line"></div></div>
      <div class="modal-challengers">${buildModalCh(c2,2)}${buildModalCh(c3,3)}</div>`;
  }

  const trackWrap = backdrop.querySelector('#modal-track-wrap');
  if (trackWrap) trackWrap.innerHTML = `<div class="modal-vote-track">${trackHtml}</div>`;

  backdrop.classList.add('open');
  document.body.style.overflow = 'hidden';
}

function closeModal() {
  const b = document.getElementById('const-modal');
  if (b) b.classList.remove('open');
  document.body.style.overflow = '';
}

/* ══════════════════════════════════════════════════════════════
   GLOBAL HEADER SEARCH  (dropdown over full 165 list)
══════════════════════════════════════════════════════════════ */
function initHeaderSearch() {
  const input    = document.getElementById('hgs-input');
  const clear    = document.getElementById('hgs-clear');
  const dropdown = document.getElementById('hgs-dropdown');
  if (!input || !dropdown) return;

  function getMatches(q) {
    if (!q || q.trim().length < 1) return [];
    return ALL_ZONES.filter(z => matchesSearch(z, q.trim())).slice(0, 8);
  }

  function renderDropdown(q) {
    const matches = getMatches(q);
    HDR_FOCUS_IDX = -1;
    dropdown.innerHTML = '';

    if (!q.trim()) { dropdown.classList.remove('open'); return; }

    const header = document.createElement('div');
    header.className = 'hgs-dd-header';
    header.innerHTML = `<span>Search Results</span><span class="hgs-dd-count">${matches.length > 0 ? matches.length : '0'}</span>`;
    dropdown.appendChild(header);

    if (matches.length === 0) {
      const empty = document.createElement('div');
      empty.className = 'hgs-dd-empty';
      empty.innerHTML = `
        <div class="em-icon">🗺️</div>
        <p>No constituency found for "<strong>${q}</strong>"</p>
        <small>Try: constituency name, district, candidate, or party</small>`;
      dropdown.appendChild(empty);
      dropdown.classList.add('open');
      return;
    }

    const list = document.createElement('div');
    list.className = 'hgs-dd-list';

    matches.forEach(z => {
      const c1 = z.candidates[0];
      const p1 = c1 ? getParty(c1.party) : null;
      const statusClass = z.status === 'declared' ? 'hgs-status-declared' : 'hgs-status-counting';
      const statusText  = z.status === 'declared' ? 'Declared' : 'Counting';

      const item = document.createElement('div');
      item.className = 'hgs-result-item';
      item.tabIndex = -1;
      item.dataset.id = z.id;

      item.innerHTML = `
        <div class="hgs-result-icon">${z.num}</div>
        <div class="hgs-result-body">
          <div class="hgs-result-name">${highlight(z.name, q)}</div>
          <div class="hgs-result-meta">${highlight(z.district, q)} · ${z.province}</div>
        </div>
        ${p1 ? `
        <div class="hgs-result-leader">
          <div class="hgs-result-leader-name">${highlight(c1.name, q)}</div>
          <div class="hgs-result-leader-party" style="color:${p1.color}">${highlight(p1.abbr, q)}</div>
        </div>` : ''}
        <div class="hgs-result-status ${statusClass}">${statusText}</div>`;

      item.addEventListener('click', () => {
        openModal(z);
        input.value = '';
        clear.classList.remove('visible');
        dropdown.classList.remove('open');
      });

      list.appendChild(item);
    });

    dropdown.appendChild(list);
    dropdown.classList.add('open');
  }

  input.addEventListener('input', () => {
    const q = input.value;
    clear.classList.toggle('visible', q.length > 0);
    renderDropdown(q);
  });

  input.addEventListener('focus', () => {
    if (input.value.trim()) renderDropdown(input.value);
  });

  // Keyboard nav
  input.addEventListener('keydown', (e) => {
    const items = dropdown.querySelectorAll('.hgs-result-item');
    if (!items.length) return;
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      HDR_FOCUS_IDX = Math.min(HDR_FOCUS_IDX + 1, items.length - 1);
      items.forEach((it, i) => it.classList.toggle('focused', i === HDR_FOCUS_IDX));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      HDR_FOCUS_IDX = Math.max(HDR_FOCUS_IDX - 1, 0);
      items.forEach((it, i) => it.classList.toggle('focused', i === HDR_FOCUS_IDX));
    } else if (e.key === 'Enter' && HDR_FOCUS_IDX >= 0) {
      items[HDR_FOCUS_IDX].click();
    } else if (e.key === 'Escape') {
      dropdown.classList.remove('open');
      input.blur();
    }
  });

  clear.addEventListener('click', () => {
    input.value = '';
    clear.classList.remove('visible');
    dropdown.classList.remove('open');
    input.focus();
  });

  // Close on outside click
  document.addEventListener('click', (e) => {
    if (!input.closest('.h-global-search').contains(e.target)) {
      dropdown.classList.remove('open');
    }
  });
}

/* ══════════════════════════════════════════════════════════════
   INLINE ZONE SEARCH (section search bar)
══════════════════════════════════════════════════════════════ */
function initZoneSearch() {
  const searchInput = document.getElementById('zone-search');
  const searchClear = document.getElementById('zone-search-clear');
  if (!searchInput) return;

  searchInput.addEventListener('input', () => {
    ZONE_QUERY = searchInput.value;
    if (searchClear) searchClear.classList.toggle('visible', !!ZONE_QUERY);
    renderZones();
  });

  if (searchClear) {
    searchClear.addEventListener('click', () => {
      searchInput.value = '';
      ZONE_QUERY = '';
      searchClear.classList.remove('visible');
      searchInput.focus();
      renderZones();
    });
  }
}

/* ══════════════════════════════════════════════════════════════
   CLOCK
══════════════════════════════════════════════════════════════ */
function updateClock() {
  const el = document.getElementById('clock');
  if (el) el.textContent = new Date().toLocaleTimeString('en-US', { hour:'2-digit', minute:'2-digit', second:'2-digit', hour12: false });
}

/* ══════════════════════════════════════════════════════════════
   INIT
══════════════════════════════════════════════════════════════ */
function init() {
  const seats = getSeatData();

  // Counts
  const allZ = getAllConstituencies();
  const dec  = allZ.filter(z => z.status === 'declared').length;
  const cnt  = allZ.filter(z => z.status === 'counting').length;
  const decEl = document.getElementById('s-dec');
  const cntEl = document.getElementById('s-cnt');
  if (decEl) decEl.textContent = dec;
  if (cntEl) cntEl.textContent = cnt;

  renderSeatsBar(seats);
  renderPartyGrid(seats);
  renderLeadTable(seats);

  ALL_ZONES = allZ;
  renderZones();
}

document.addEventListener('DOMContentLoaded', () => {
  init();
  updateClock();

  // Modal close
  const modalBtn = document.getElementById('modal-close-btn');
  const backdrop = document.getElementById('const-modal');
  if (modalBtn) modalBtn.addEventListener('click', closeModal);
  if (backdrop) backdrop.addEventListener('click', e => { if (e.target === backdrop) closeModal(); });
  document.addEventListener('keydown', e => { if (e.key === 'Escape') closeModal(); });

  // Search init
  initHeaderSearch();
  initZoneSearch();

  setInterval(updateClock, 1000);
  setInterval(init, 60000);
});

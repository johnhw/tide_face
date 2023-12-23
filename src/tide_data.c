
/* Mean error for CLOCK in 2000-2001 is approximately 0.00010m */
char station_clock_2000_name [] = "CLOCK";                    
float station_clock_2000_speed [] = {1.4051890250864362e-04};                
uint16_t station_clock_2000_amp [] = {0x15AD};
uint16_t station_clock_2000_phase [] = {0x5FAB};
tidal_harmonic station_clock_2000_data = {
        .base_year = 2000,
        .n_years = 1,
        .lat = 0.0,
        .lon = 0.0,
        .neaps_range = 2.032399892807007,
        .springs_range = 2.032399892807007,
        .offset = 0.0,
        .speeds = station_clock_2000_speed,
        .amps = station_clock_2000_amp,
        .phases = station_clock_2000_phase,
        .n_constituents = 1,
        .mean_error = 0.00010209945858127338,

};                                        
tidal_station station_clock_2000 = {
        .type = STATION_TYPE_HARMONIC,
        .name = station_clock_2000_name,
        .previous = &NULL,
        .data = &station_clock_2000_data,                        
};



#ifdef TIDE_DEBUG
time_t station_clock_2000_test_times [] = {965250919, 969455418, 967558378, 972690095, 953199883, 958431554, 952054170, 966314852, 959184651, 952254208, 969118869, 962439562, 970739065, 948261080, 964418989, 971010717, 956765151, 969688707, 964085397, 960565699, 954996075, 963740967, 955975107, 963885172, 950285876, 959324788, 974028094, 954953841, 969583083, 955526632, 975955073, 949107007, 970874464, 947860753, 957183192, 971860730, 961037757, 951838264, 962003227, 959560035, 949206833, 954783209, 966594946, 953302732, 964587599, 957902888, 951569479, 949034617, 972660917, 961370522, 973727459, 972078365, 948054982, 968673296, 954457367, 975502702, 961393879, 970796764, 976726199, 947783357, 967311497, 949318737, 959090026, 955367862, 968167178, 973437690, 966400814, 961525694, 978115907, 952804585, 973859165, 970032682, 976604891, 953059012, 959756230, 950169380, 957326180, 969418231, 968405137, 953707231, 971792499, 954782742, 949516146, 952613221, 963558855, 969191541, 957729352, 970560065, 969456079, 950624418, 951194712, 964680968, 947237250, 966939023, 971948480, 967293172};
float station_clock_2000_test_tides [] = {-0.8526011869897171, -0.7313051611618813, 0.3368740213887792, 0.9894003153931701, 0.8940194363121567, 0.8861824655765558, -0.9772722472321079, -0.7650470944442763, 0.9021250306540797, 0.918150469513494, 0.8387654836074258, -0.20545763692050822, -0.48950275355806194, -0.7136410369013714, 1.0123010961295926, -0.8415219980869196, 0.39473658102184606, 0.5417650865531949, -1.0031745931302782, 0.3741201307325325, 0.003918616029068849, 0.4475331146616148, 0.6241972685671476, 0.9710472006770885, 0.8552123846131273, 0.9496312870220383, 0.7696008931826909, -0.3433443678711794, -1.0058698096222691, 0.762640700508006, 1.0098814894446453, -0.976501975528915, -0.6383120541153382, -0.47233642175440577, 0.5299896484842649, -0.8753934770628359, -0.6826945474131327, -0.7084536910611345, 0.9831226164631093, -0.4272166167855228, 0.17263307706500286, -1.0136811423211929, -0.5985411509178586, -0.7363607356299378, 0.04400935344847375, -0.0520792051777333, -0.7578511089975432, 0.9074113458011684, -0.3789653230311134, 0.369873294672158, 0.5267970717289436, -0.2058695493326522, 1.0105078615548937, 0.6930350186626572, 0.3044690501449051, 0.6734222347020214, -0.49878081460179435, -0.7390859905696067, 0.14053529512883906, 0.9498201972593956, -0.46187564445299456, -0.1892961482991981, 0.36006271141163854, -0.9348041852787192, 0.38353475645423396, -0.4164946191246661, -0.3630148970740842, -0.18790991912262592, -0.3606035243493612, 0.07466984339590538, 0.7879632179557471, -0.9954158619489696, -1.011718163595229, 0.9150084507931171, -0.2723597071057549, -0.3372344279491588, -0.6502172038567285, 0.2557566767648727, 0.6797696694264881, -0.9063689849758652, 0.7800607416287287, -1.0068104078401459, -0.3458405635721294, 0.9819755343159443, -0.0014170478322897832, -0.18581587683186954, -0.7282152805174832, -0.4714672659305413, -0.662709875366103, -1.0085305453772573, 0.09787257246341106, 0.571321474292939, -0.1345340048058855, -0.5701043215355511, -0.7305739430456607, -0.09614989700268214};
#endif


/* Mean error for Millport, Scotland in 2023-2028 is approximately 0.00036m */
char station_millport_scotland_2023_name [] = "Millport, Scotland";                    
float station_millport_scotland_2023_speed [] = {7.2921158357870547e-05, 1.4584231720055478e-04, 1.4315810553074262e-04, 1.4051890250864362e-04, 2.1077835376296543e-04, 2.8103780501728725e-04, 4.2155670752593087e-04, 1.3787969948654463e-04, 1.3524049646444563e-04, 6.7597744150773076e-05, 7.2522945974990243e-05, 6.4958541128674080e-05, 7.2722052166430395e-05, 1.4544410433286079e-04, 2.9088820866572158e-04, 1.4524500735288060e-04, 1.4280490131076179e-04, 1.3559370068442646e-04, 1.3823290370652545e-04, 2.1344006135132787e-04, 2.0811664665941671e-04, 2.7839860199518825e-04, 2.8596300684150439e-04, 1.5036930615707798e-04, 5.3234146919111522e-06, 1.9910619144015089e-07, 3.9821286769398287e-07, 4.1891750450383182e-04, 4.2648190935014801e-04, 1.3066849886020929e-04, 2.8636121970919838e-04, 1.3295449766232746e-04, 2.2859988021181762e-06, 1.4808330735495979e-04, 1.3519548781673247e-04, 1.4012068964094966e-04, 2.1836526269073135e-04, 1.5076751902477192e-04, 2.7575939897308925e-04, 7.0259451254321812e-05};                
uint16_t station_millport_scotland_2023_amp [] = {0x28D, 0x259, 0x16A, 0x170E, 0x10B, 0x1C2, 0x78, 0x45B, 0x7A, 0x266, 0xD0, 0xCD, 0x3E, 0x63F, 0x47, 0x68, 0xB1, 0xBD, 0x123, 0x6B, 0x48, 0xB7, 0x1C2, 0x7F, 0x93, 0x229, 0x6B, 0x38, 0x86, 0x2E, 0xAD, 0x3A, 0x39, 0x60, 0x7E, 0x3C, 0x66, 0x55, 0x3B, 0x27, 0x293, 0x26B, 0xCE, 0x16F3, 0x10A, 0x1BE, 0x77, 0x456, 0x7A, 0x26F, 0xD0, 0xD0, 0x3E, 0x63F, 0x47, 0x68, 0xB0, 0xBC, 0x122, 0x6C, 0x48, 0xB6, 0x1BF, 0x7E, 0x98, 0x229, 0x6B, 0x37, 0x84, 0x2D, 0xB1, 0x39, 0x38, 0x5F, 0x49, 0x3D, 0x67, 0x57, 0x3A, 0x25, 0x294, 0x26C, 0x15D, 0x16F1, 0x10A, 0x1BE, 0x77, 0x456, 0x7A, 0x270, 0xD0, 0xD0, 0x3E, 0x63F, 0x47, 0x68, 0xB0, 0xBC, 0x121, 0x6C, 0x48, 0xB6, 0x1BF, 0x7E, 0x98, 0x229, 0x6B, 0x37, 0x84, 0x2D, 0xB1, 0x39, 0x38, 0x5F, 0x7D, 0x3D, 0x67, 0x57, 0x3A, 0x25, 0x28E, 0x25D, 0x1CF, 0x1708, 0x10B, 0x1C1, 0x78, 0x45A, 0x7A, 0x268, 0xD0, 0xCD, 0x3E, 0x63F, 0x47, 0x68, 0xB0, 0xBD, 0x123, 0x6B, 0x48, 0xB7, 0x1C1, 0x7F, 0x94, 0x229, 0x6B, 0x37, 0x85, 0x2D, 0xAD, 0x3A, 0x39, 0x60, 0xA2, 0x3D, 0x66, 0x55, 0x3B, 0x26, 0x284, 0x240, 0x17C, 0x1735, 0x10E, 0x1C8, 0x7B, 0x463, 0x7B, 0x259, 0xD0, 0xC8, 0x3E, 0x63F, 0x47, 0x68, 0xB2, 0xBF, 0x125, 0x6A, 0x48, 0xBA, 0x1C5, 0x80, 0x8B, 0x229, 0x6B, 0x39, 0x87, 0x2F, 0xA6, 0x3B, 0x3B, 0x61, 0x80, 0x3B, 0x64, 0x52, 0x3C, 0x29};
uint16_t station_millport_scotland_2023_phase [] = {0x7B7F, 0x7055, 0x33B2, 0x7468, 0x512A, 0x9053, 0x6080, 0x4955, 0x202F, 0x455E, 0x73EC, 0x3379, 0x35DD, 0xE705, 0x784F, 0xF179, 0x42C5, 0x7C16, 0x2DDF, 0xD131, 0xA4CC, 0x5971, 0x13D8, 0xDC69, 0x88F8, 0x14AA, 0x18B2, 0x3542, 0xD6FE, 0x9001, 0x9D84, 0x4773, 0xFA24, 0x94B6, 0xCB, 0x734F, 0x3AD9, 0x685A, 0x2D77, 0x3D61, 0x7D15, 0x73B3, 0xADED, 0xBC88, 0x3D5C, 0x2095, 0x38E3, 0x525F, 0xEA1F, 0x8B30, 0x7418, 0x3A35, 0x35DD, 0xE705, 0x784F, 0xF1A9, 0x42A, 0xBDE, 0xFCBD, 0x1AE8, 0x3376, 0xAA99, 0x5BF9, 0x9449, 0x4575, 0x147E, 0x185C, 0xCE8B, 0x6740, 0x6863, 0xE903, 0x989B, 0x7367, 0xD3CD, 0x80B0, 0xB94C, 0x3C6F, 0x2399, 0x3F89, 0xE172, 0x7F75, 0x78AA, 0x1C1D, 0xF35C, 0xF98, 0x8E3A, 0xDD5B, 0x40CF, 0x902E, 0xBEE8, 0x7391, 0x258B, 0x35DD, 0xE705, 0x784F, 0xF124, 0xBC4C, 0x78FE, 0xB240, 0x541A, 0x9EBD, 0xCFDE, 0x92CC, 0x5D75, 0x14D7, 0x1505, 0x196B, 0x2AA3, 0xD4E5, 0xCDD, 0x24CC, 0xBDE0, 0xF4B5, 0x1C30, 0xD85B, 0xEC7D, 0x3ECF, 0xF1BB, 0x1C6C, 0x7CDC, 0x8110, 0x7C14, 0xB167, 0x3B7F, 0xFBCB, 0x1E7F, 0xB5C3, 0x49DA, 0x5A23, 0x4B8, 0x73BB, 0x2C44, 0x35DD, 0xE705, 0x784F, 0xF151, 0x7DB1, 0x8C8, 0x8120, 0x9DD9, 0x2D67, 0x210D, 0xDAEE, 0x1553, 0xD15C, 0x14DB, 0x1914, 0xC3F5, 0x652B, 0xE544, 0x705A, 0xF0F, 0x6DFA, 0x5B46, 0x7346, 0x3277, 0x406B, 0xAD04, 0x2E83, 0x20EE, 0x827A, 0x7F07, 0x46D5, 0x838B, 0xE7E0, 0xAE9C, 0x8DED, 0x52D2, 0x2402, 0x4AAE, 0x73E6, 0x3322, 0x35DD, 0xE705, 0x784F, 0xF180, 0x3F02, 0x987B, 0x4FEB, 0xE752, 0xBC17, 0x7211, 0x22FC, 0xCD45, 0x8D7C, 0x14AF, 0x18BD, 0x5D06, 0xF547, 0xBD6E, 0xBB5A, 0x6013, 0xE73C, 0x9A5F, 0xEB8, 0x789A, 0x41D5, 0x67E7, 0x406E, 0xC4F4};
tidal_harmonic station_millport_scotland_2023_data = {
        .base_year = 2023,
        .n_years = 5,
        .lat = 55.7496,
        .lon = -4.9058,
        .neaps_range = 1.1375986193561218,
        .springs_range = 3.389650545095997,
        .offset = 1.9962999820709229,
        .speeds = station_millport_scotland_2023_speed,
        .amps = station_millport_scotland_2023_amp,
        .phases = station_millport_scotland_2023_phase,
        .n_constituents = 40,
        .mean_error = 0.00035648637001886867,

};                                        
tidal_station station_millport_scotland_2023 = {
        .type = STATION_TYPE_HARMONIC,
        .name = station_millport_scotland_2023_name,
        .previous = &station_clock_2000,
        .data = &station_millport_scotland_2023_data,                        
};



#ifdef TIDE_DEBUG
time_t station_millport_scotland_2023_test_times [] = {1673975444, 1677688098, 1676732182, 1678784751, 1688741859, 1683989918, 1692386742, 1681698497, 1684240543, 1697904210, 1692836891, 1678814856, 1678777164, 1688173381, 1684575850, 1703422635, 1681868416, 1686768680, 1701866235, 1679719381, 1682826672, 1701940684, 1674066269, 1676018809, 1684537740, 1696510787, 1688422113, 1685623549, 1699683708, 1678694460, 1702857749, 1674914185, 1681748230, 1702451075, 1701620902, 1674821302, 1675948751, 1676112445, 1685433863, 1674848421, 1702972163, 1694826519, 1686923591, 1703523612, 1677347508, 1703573322, 1679369852, 1691540914, 1682395036, 1693227343, 1678289182, 1689538812, 1694645338, 1688790502, 1681811809, 1701965271, 1674008971, 1679727429, 1678919979, 1675603964, 1695342492, 1696329191, 1700590157, 1676090661, 1683816101, 1702407735, 1673172317, 1694793748, 1681919934, 1685935355, 1699021226, 1682302467, 1691430092, 1697851522, 1681562896, 1701877287, 1702353981, 1702817929, 1696250450, 1678447187, 1676186769, 1680748533, 1685831210, 1684290283, 1683833144, 1673710212, 1695969293, 1688705412, 1695104698, 1694869802, 1695906243, 1703515776, 1672999589, 1679238708, 1690724533, 1678667224, 1722657593, 1708763287, 1721627038, 1727158580, 1728152121, 1716005912, 1732887700, 1716477722, 1711845266, 1723281633, 1717201522, 1729392519, 1707712398, 1718089404, 1705367656, 1728037632, 1712877104, 1722146563, 1723927080, 1710448676, 1710347133, 1710533229, 1729414206, 1714666301, 1716702908, 1720438790, 1708829342, 1725832322, 1704196039, 1725372677, 1716254922, 1722740523, 1713013271, 1713313446, 1724683314, 1729565998, 1726457550, 1715230997, 1715555100, 1728078107, 1720952812, 1717152581, 1722930368, 1729448135, 1728840068, 1724220968, 1708689549, 1715445597, 1731477326, 1721120164, 1728923633, 1710390726, 1714036464, 1707782792, 1711193861, 1714194289, 1710821100, 1717993511, 1734989273, 1706906974, 1718011674, 1707866758, 1715110920, 1716143745, 1721342358, 1723059377, 1719544821, 1707929123, 1716945392, 1724035275, 1704785099, 1706619602, 1712308814, 1710684876, 1705966764, 1709451888, 1720383401, 1709543301, 1713427227, 1715101137, 1717558708, 1708811211, 1708465796, 1727495915, 1730986562, 1734745221, 1735407834, 1720984079, 1706310470, 1707926128, 1730445249, 1718555563, 1732708357, 1728109291, 1732863022, 1726165923, 1762646015, 1749841451, 1736939481, 1753488082, 1763031246, 1752634821, 1766715161, 1735749803, 1746623097, 1750890968, 1753357798, 1759163813, 1752785000, 1760739218, 1742292463, 1758120987, 1759212418, 1753252679, 1747043867, 1762408183, 1760799313, 1764026029, 1736556122, 1737646030, 1746761251, 1763285545, 1755325504, 1748447156, 1742613826, 1750814747, 1747138970, 1742391830, 1753651460, 1759915676, 1762040069, 1743348699, 1761127875, 1753107220, 1743152432, 1751114612, 1740072170, 1743008366, 1742496552, 1738301299, 1735962211, 1758180186, 1757310709, 1762346089, 1756623621, 1758812894, 1750134739, 1744672196, 1740156681, 1762425109, 1762894467, 1760985561, 1751447588, 1737806535, 1754046507, 1749835139, 1753943253, 1742691208, 1744163502, 1765969745, 1736498639, 1741463218, 1747369595, 1764460463, 1753417709, 1745845466, 1762241377, 1750601672, 1755219951, 1747219956, 1740681515, 1738171863, 1752471554, 1736866305, 1763281958, 1739338011, 1758689179, 1750542754, 1755893101, 1737095209, 1738303595, 1754136388, 1743632875, 1745984618, 1761755596, 1748812707, 1747855894, 1761506536, 1740029101, 1738052033, 1747818824, 1747487227, 1785989167, 1794134076, 1770838042, 1781300510, 1788822547, 1781238772, 1777021635, 1773990978, 1793330576, 1784728859, 1776370506, 1795068414, 1793925830, 1770327084, 1783817677, 1785706894, 1797826686, 1781824243, 1779585190, 1782141729, 1775896921, 1781556110, 1779737855, 1778562462, 1792845124, 1770912668, 1782297542, 1785720893, 1798540022, 1784524372, 1792246921, 1787306858, 1796339838, 1790257674, 1771822828, 1784711226, 1777303390, 1795716957, 1773666501, 1780255709, 1797412256, 1773820165, 1797681859, 1785749754, 1797695730, 1790699821, 1771066026, 1783438538, 1791998377, 1768536984, 1785858610, 1777382708, 1796348540, 1781590956, 1786783864, 1793976528, 1770518990, 1773716176, 1770313509, 1770628017, 1776863669, 1797746731, 1768786424, 1790860853, 1767228164, 1777289394, 1769995337, 1780949189, 1779059228, 1791550532, 1789979973, 1770539752, 1788010931, 1789183296, 1772503426, 1772165226, 1791228559, 1797820462, 1769645797, 1779056306, 1791611689, 1771581377, 1769558877, 1798258129, 1783629091, 1798337350, 1779854610, 1772260410, 1772105436, 1768069262, 1787940007, 1786373495, 1795292266, 1795944722, 1783745175, 1774252781, 1802021218, 1829115067, 1812908057, 1812308817, 1829013244, 1803705268, 1826976127, 1822338102, 1801707320, 1810327121, 1801499559, 1805910403, 1817102344, 1819097815, 1822931795, 1810194312, 1815544287, 1826472260, 1822826712, 1801466565, 1815851031, 1815063633, 1817437480, 1820074760, 1815336297, 1818701021, 1805198887, 1807526004, 1799966093, 1829845825, 1799969821, 1803901074, 1802897145, 1805989610, 1817700507, 1819844399, 1800164939, 1810315852, 1801871373, 1819888713, 1811198733, 1799416836, 1829181984, 1805349440, 1817435330, 1806114200, 1809233027, 1807815404, 1804446489, 1820988881, 1821954931, 1818502108, 1813205462, 1801562925, 1817730861, 1818072897, 1824601115, 1807431893, 1824460031, 1816344632, 1829594095, 1812098055, 1818659297, 1825075272, 1808941642, 1824800134, 1824649581, 1820407055, 1813424609, 1803898527, 1817140298, 1813144257, 1800684594, 1803979128, 1820011765, 1828184222, 1814445254, 1805701260, 1811643930, 1798889698, 1811590589, 1801635784, 1820415259, 1830000459, 1821020319, 1813786947, 1829625187, 1817515900, 1809034198, 1827673796, 1818207156, 1815623003, 1828071286, 1820453036, 1818203526, 1815046137};
float station_millport_scotland_2023_test_tides [] = {2.4605055575782275, 2.0056642284362547, 1.0316346156311886, 0.9141835082367818, 3.1315907872352633, 1.5690987441264157, 0.7250900885263801, 0.9955052021476705, 1.7622997100847848, 3.1783419616331376, 1.7090266061218768, 3.007916339236747, 1.9771122503447627, 1.8229000625320884, 2.179600171532252, 2.1343104154460946, 2.3472915425582004, 2.1564348729660643, 1.4678347730386105, 2.3054066438357443, 1.7601782485692141, 2.551949629898158, 2.47716626616407, 0.7961876508265504, 2.932692823768148, 2.1286607153813604, 2.642019836250654, 1.7815593418095264, 1.5470691907197414, 0.9437603668547538, 1.7578870829484403, 2.236381075136439, 0.35167897757209515, 1.3572488435595667, 3.2834627930808513, 1.7255542492260298, 3.207629109356728, 1.397681864396973, 2.7160977368277677, 1.866991070245077, 2.066301988656545, 3.325522465883969, 1.8318301624205149, 0.9038503449071985, 2.746585114350991, 1.4637912052108655, 1.1862565836309167, 1.1848473058382167, 3.1084930994185744, 1.7592879587988384, 2.2689658561079993, 2.1477204953111624, 3.1876653653317115, 3.2843383183352133, 3.1066612984544295, 2.132661475701627, 1.1042602243639557, 0.6453135842803838, 1.1859221504801714, 3.0506635011455856, 1.9516449268180192, 1.5030663731142273, 3.126675235755747, 2.7905261099740684, 2.5973620284018617, 1.4181445261794792, 2.4637155592805278, 1.6507953599755105, 0.5743136300066332, 2.060192930636766, 3.2237568624636594, 3.300733558130289, 2.901690457296329, 2.4444261525217805, 0.8435321118226762, 2.4135463683563945, 0.9130126725403906, 2.8514808722616736, 2.9653752453673845, 2.4106179552466824, 1.6452311262943256, 2.438233060825105, 2.7839344441606904, 1.0757821290387755, 1.8882596618209342, 3.0755680440786897, 0.7057451737151131, 2.6237502369088923, 0.9783728569032165, 3.0936525851189236, 2.7411308499393483, 1.4909019598666136, 2.933022349388334, 0.5671242297780973, 1.3763503875511178, 2.1417896942968677, 0.8108785394402679, 1.8686381056579715, 0.41355216962973496, 2.636160211299968, 0.8868413662477176, 1.800758209952481, 2.3526916435681806, 1.5120305601161126, 2.244413847092041, 0.6756755522441241, 1.0043859915616744, 3.3309109602968623, 2.078329634272748, 1.1406306040747993, 2.3867026651620153, 2.2401470537124784, 1.9966591591936347, 3.1448361056633884, 2.6604079706009527, 0.34924053521830084, 2.780813197267944, 1.0872273788963753, 1.0407368233922658, 2.0912314124340226, 1.0041647961696711, 2.202078677981181, 2.6352635597432177, 1.032506681699512, 1.7629296775206542, 2.800807966333716, 2.0246343610172683, 1.77689691884536, 2.3788441042480097, 1.3345863416469983, 2.3661763708720494, 3.43351453329612, 0.5753753956173338, 0.6187897432664008, 1.54989056056273, 2.032016321258796, 0.9412124607623426, 0.7416024299701218, 0.7403457967052544, 0.8360776738877271, 2.334012578526825, 0.10092880339122616, 3.2491621311695256, 2.3749019110577136, 1.823633136223165, 2.3597976502906235, 1.5172108523396566, 2.755822402855376, 1.7449319608230225, 2.3459155031318812, 3.1530435001008055, 1.7707536244395041, 2.149619266652279, 2.4445863338355722, 1.7620028994275396, 1.3736391199294014, 0.8711241253623895, 1.565598428644606, 1.5630412877227842, 1.8378415425475028, 2.8513858943886246, 0.7145136106643175, 3.114681420006227, 3.337421972950626, 2.4993783605399895, 1.7001329097545241, 2.3373366794596224, 2.848303874782305, 2.867413624809621, 1.9504872238442992, 2.803644190357202, 1.8172268532762277, 1.2565258817247926, 1.6803372046289806, 2.654361106824284, 0.13997036674077606, 0.682507080646631, 1.9030054804195418, 2.843806583705366, 1.252665381593558, 2.838103584853029, 2.2496306857151103, 1.4045101880233979, 2.514313335296865, 2.400609691461225, 3.6532641393127188, 1.4179543566795194, 1.7798126892350403, 2.52635797176569, 0.6496691305065047, 1.7818487500688562, 2.739231451037998, 2.615343480028612, 0.8220615999414228, 2.995084832549875, 3.281998193850792, 1.596949244500491, 3.284010573670362, 2.615174284790486, 1.6547794741669053, 1.0598726706765584, 2.922778406027969, 3.0197991493605065, 3.0119958210146622, 1.2837581427678755, 3.0628376874857595, 1.396209922894666, 1.240054361454722, 2.563259582164303, 1.628365190332797, 2.508708127181471, 0.322799097359977, 1.137463483137785, 1.9492632472367335, 1.8432097131257457, 2.072935805971098, 0.8952789047263242, 3.055327046822395, 2.8160674740407745, 1.9860053315078128, 2.734992863908997, 2.4544750893999163, 3.089210328231092, 2.911000631225519, 1.3587386167580324, 2.134169984198698, 2.0214245668515436, 2.0419720324391197, 2.37143820181289, 0.770200399680676, 2.5906922383584834, 2.5287696456341657, 2.9622682979231185, 0.9695176169321723, 1.6728810303880175, 1.1219349396262963, 3.1208493936566213, 2.309888777499551, 0.23245143440766525, 3.235873064411709, 2.1896831953304714, 3.0958314511511986, 3.0684429160774713, 2.359292672831727, 2.761125982655699, 2.9425777515138196, 1.1955424913085981, 1.296951428553173, 1.0554867520461204, 2.062620486857124, 0.939192579484072, 1.3587594862391714, 2.2325117713453984, 1.5862342190212289, 1.4509940168769695, 3.106580911918719, 3.000606770357061, 2.7556778301758844, 2.3207958898500487, 0.9837274864061792, 0.8216426685829771, 3.325329401880882, 2.137808734599589, 0.5584806877826243, 2.466847926703065, 2.3751041155735453, 0.6803273198653691, 0.5522462959058296, 1.512745819588723, 2.4763686441957904, 2.809675681689498, 0.7875946147064394, 1.442012033459777, 2.6122711623630255, 2.016105604893026, 1.2768060738574591, 0.8087912631250735, 1.1117083755505621, 1.075007376632256, 2.408140041586226, 3.032810203145958, 1.0725267278526154, 2.6281125550234354, 1.092714258261287, 2.8411065545267116, 2.2643555317889614, 1.7869306963584437, 2.434494299591446, 3.0900659350677553, 3.071695916380321, 2.6643630025810183, 2.9844937142781833, 2.3812423371119915, 1.5170171335268636, 1.3289359185402876, 0.7616418317300727, 3.297324455216284, 1.3781368822805862, 1.940719653131551, 2.6702700729240876, 1.7777505585168625, 0.8130446889951022, 1.5634911120299504, 1.2928870219030832, 1.265255179388669, 1.9129994410181863, 1.375139845935957, 1.8906591586175276, 2.1034369511997006, 2.0044156945077747, 2.740253275202889, 2.297424884903204, 2.652994952195714, 1.6310488793377518, 1.7850917410986384, 3.0435015830081396, 1.0487551085770088, 3.0972800595632775, 2.8609877403688264, 1.4114083801930157, 1.7560467287021784, 1.9524098976088182, 2.9866670116536573, 1.6309076038836159, 0.6186338191468406, 0.5274332131833661, 2.1911875115372483, 1.335791424842851, 1.2983954310157457, 1.8377706910823026, 1.372571726434231, 0.6646622174930312, 2.1798542093604985, 1.9327056906170141, 2.950200189511357, 2.587287117641209, 1.8458023074409864, 1.1865113288438607, 3.0738082089005316, 1.4784781207836153, 0.8386955052447411, 0.3115532676672465, 0.8537055710860232, 1.0621066258456833, 2.7066463530314926, 1.3852121182342318, 1.756928322007288, 1.3237073557110903, 2.296271454225854, 2.5630765382130547, 2.906768338261394, 2.8672712714782556, 1.8806162464646283, 2.1355714967002206, 3.1234123034578682, 2.075813106783571, 2.8884280164888922, 2.936803922911679, 2.4081863830702743, 1.144397589754211, 3.041787081504676, 1.9768718894153352, 2.721396218993282, 1.816323520074197, 2.9315506345630595, 0.8409360716232706, 1.4134684055906728, 2.540834985595867, 0.6254699197350077, 1.856841960664075, 0.9709398135948358, 2.319803518286564, 2.545142961182981, 3.339483453776383, 1.187586240527938, 2.320307298205116, 1.2789981503854566, 3.0045396585187247, 0.738788753684454, 0.9604865497761516, 2.9841691448325562, 1.012279565762051, 1.8506433696167057, 0.41357347256039373, 0.8172769808431902, 1.3150204626450193, 2.2788734882654698, 0.5698535179527983, 3.248381175235278, 2.95235268265448, 1.0924381668656904, 2.285450584290164, 1.8048274880737785, 2.703424560829973, 1.8182251819440767, 0.7278764931086424, 1.5042883988037217, 0.847278936171816, 2.8451090036957525, 2.0757888526398474, 2.2689873612299265, 1.6955520278306482, 2.094318955272415, 2.7565780549855354, 1.5602363465953486, 3.118154774783725, 2.8021664683694456, 2.8622923511097245, 2.480653797578511, 0.7081286286092989, 1.0441230176738678, 1.0011655525371024, 0.8001252199057832, 1.3165601193189675, 1.1699434046720454, 1.247578569106876, 2.8296676323168537, 2.8394442611187594, 3.3526607293086212, 3.5751233608713973, 2.931881710667734, 2.43343975112016, 2.9952491723286974, 3.121397627349967, 1.8136328700428705, 3.1487443424602684, 2.509266977373055, 2.565379674349026, 3.220813909799742, 3.1421364387391812, 1.7030855069163189, 2.654983915186465, 1.0421288030972171, 0.7385351088935554, 2.533825196137814, 2.7911874100809335, 0.6867653333113727, 2.775897832323961, 1.7024867795812002, 1.625355096713559, 1.1552989710425403, 0.45226537123982197, 2.5767616867599235, 1.9578205744370074, 3.2155002669771053, 2.229481923376566, 0.4591745251456513, 3.4385839681773893, 1.9408645026005262, 2.2568460435500204, 0.8700429614981354, 1.4329535546679024, 0.9934997827289944, 1.3402711433386019, 0.6948092223399791, 2.7729460797209096, 0.5713326396490537, 2.265589451462821, 2.145648360036843, 1.577557931705399, 1.6956712551769442, 1.5592867813958617, 1.6477917896091203, 1.718614688437507, 0.9009347318699324, 2.00260770567639, 2.2920526189297314, 3.3030419753884055, 1.9251831703820785, 1.2116674720430505, 1.7594546384797933, 3.435280973311735, 1.8323602999425612, 3.2687519859798657, 1.7168708669992365, 0.9155306064470674, 2.7561216322289632, 1.3341083274776024, 2.249762651943632, 1.3530940525255832};
#endif


tidal_station * tidal_stations  = &station_millport_scotland_2023;                    

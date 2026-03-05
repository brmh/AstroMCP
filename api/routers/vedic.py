"""Vedic Astrology Endpoints"""

from fastapi import APIRouter
from api.models.request_models import NatalChartRequest, CompatibilityRequest, DateRangeRequest
from api.dependencies import birth_data_to_jd, get_current_jd
from api.core.calculations import get_all_planet_positions, get_houses, get_aspects, assign_houses_to_planets
from api.core.charts import build_natal_chart, build_divisional_chart, build_all_divisional_charts
from api.core.dashas import get_mahadashas, get_antardashas, get_current_dasha, get_yogini_dashas, get_ashtottari_dashas, get_char_dashas, get_dasha_interpretation, get_kalachakra_dasha
from api.core.yogas import detect_all_yogas, detect_sade_sati, get_atmakaraka, get_amatyakaraka, detect_kala_sarpa_dosha, detect_mangal_dosha
from api.core.shadbala import calculate_shadbala
from api.core.ashtakavarga import get_sarvashtakavarga
from api.core.compatibility import get_gun_milan
from api.core.ephemeris import get_ayanamsa_value

router = APIRouter(prefix="/vedic", tags=["Vedic Astrology"])


@router.post("/kundli")
async def vedic_kundli(request: NatalChartRequest):
    jd = birth_data_to_jd(request.birth_data)
    bd = request.birth_data
    chart = build_natal_chart(jd, bd.latitude, bd.longitude, house_system="WHOLE_SIGN",
                              zodiac_type="SIDEREAL", ayanamsa=request.options.ayanamsa.value)
    chart["name"] = bd.name
    chart["chart_type"] = "vedic_kundli"
    return chart


@router.post("/navamsa")
async def vedic_navamsa(request: NatalChartRequest):
    jd = birth_data_to_jd(request.birth_data)
    bd = request.birth_data
    positions = get_all_planet_positions(jd, zodiac_type="SIDEREAL", ayanamsa=request.options.ayanamsa.value)
    houses = get_houses(jd, bd.latitude, bd.longitude, "WHOLE_SIGN", "SIDEREAL", request.options.ayanamsa.value)
    asc_lon = houses.get("ascendant")
    return build_divisional_chart(positions, 9, request.options.ayanamsa.value, jd, asc_lon)

@router.post("/varga/{division}")
async def vedic_varga_chart(division: int, request: NatalChartRequest):
    jd = birth_data_to_jd(request.birth_data)
    bd = request.birth_data
    positions = get_all_planet_positions(jd, zodiac_type="SIDEREAL", ayanamsa=request.options.ayanamsa.value)
    houses = get_houses(jd, bd.latitude, bd.longitude, "WHOLE_SIGN", "SIDEREAL", request.options.ayanamsa.value)
    asc_lon = houses.get("ascendant")
    return build_divisional_chart(positions, division, request.options.ayanamsa.value, jd, asc_lon)

@router.post("/divisional-charts")
async def vedic_divisional_charts(request: NatalChartRequest):
    jd = birth_data_to_jd(request.birth_data)
    bd = request.birth_data
    positions = get_all_planet_positions(jd, zodiac_type="SIDEREAL", ayanamsa=request.options.ayanamsa.value)
    houses = get_houses(jd, bd.latitude, bd.longitude, "WHOLE_SIGN", "SIDEREAL", request.options.ayanamsa.value)
    asc_lon = houses.get("ascendant")
    return build_all_divisional_charts(positions, jd, request.options.ayanamsa.value, asc_lon)

from api.core.sadesati import get_sade_sati_report
from api.core.ephemeris import get_julian_day
from api.core.charts import build_bhava_chalit_chart
from api.core.upagrahas import get_upagrahas
from api.core.remedies import get_remedies
from datetime import datetime

@router.post("/sade-sati")
async def vedic_sade_sati(request: NatalChartRequest):
    jd = birth_data_to_jd(request.birth_data)
    positions = get_all_planet_positions(jd, zodiac_type="SIDEREAL", ayanamsa=request.options.ayanamsa.value)
    natal_moon_lon = positions.get("moon", {}).get("longitude", 0)
    
    now = datetime.utcnow()
    current_jd = get_julian_day(now.year, now.month, now.day, now.hour, now.minute, now.second, "UTC")
    
    return get_sade_sati_report(jd, natal_moon_lon, current_jd, request.options.ayanamsa.value)

@router.post("/bhava-chalit")
async def vedic_bhava_chalit(request: NatalChartRequest):
    jd = birth_data_to_jd(request.birth_data)
    bd = request.birth_data
    return build_bhava_chalit_chart(jd, bd.latitude, bd.longitude, request.options.ayanamsa.value)

@router.post("/upagrahas")
async def vedic_upagrahas(request: NatalChartRequest):
    jd = birth_data_to_jd(request.birth_data)
    bd = request.birth_data
    positions = get_all_planet_positions(jd, zodiac_type="SIDEREAL", ayanamsa=request.options.ayanamsa.value)
    sun_lon = positions.get("sun", {}).get("longitude", 0)
    return get_upagrahas(jd, bd.latitude, bd.longitude, sun_lon, request.options.ayanamsa.value)

@router.post("/remedies")
async def vedic_remedies(request: NatalChartRequest):
    jd = birth_data_to_jd(request.birth_data)
    bd = request.birth_data
    positions = get_all_planet_positions(jd, zodiac_type="SIDEREAL", ayanamsa=request.options.ayanamsa.value)
    houses = get_houses(jd, bd.latitude, bd.longitude, "WHOLE_SIGN", "SIDEREAL", request.options.ayanamsa.value)
    positions = assign_houses_to_planets(positions, houses)
    return get_remedies(positions, houses)

from api.core.gochar import analyze_gochar
from api.models.request_models import TransitRequest
from api.core.charts import get_lagna_lord_analysis

@router.post("/lagna-lord")
async def vedic_lagna_lord(request: NatalChartRequest):
    jd = birth_data_to_jd(request.birth_data)
    bd = request.birth_data
    positions = get_all_planet_positions(jd, zodiac_type="SIDEREAL", ayanamsa=request.options.ayanamsa.value)
    houses = get_houses(jd, bd.latitude, bd.longitude, "WHOLE_SIGN", "SIDEREAL", request.options.ayanamsa.value)
    positions = assign_houses_to_planets(positions, houses)
    return get_lagna_lord_analysis(positions, houses)

@router.post("/gochar")
async def vedic_gochar(request: TransitRequest):
    natal_jd = birth_data_to_jd(request.natal)
    transit_jd = get_julian_day(request.transit_date.year, request.transit_date.month, request.transit_date.day, 
                                request.transit_date.hour, request.transit_date.minute, request.transit_date.second, "UTC") if request.transit_date else get_current_jd()
    
    opts = request.options
    natal_pos = get_all_planet_positions(natal_jd, zodiac_type=opts.zodiac_type.value, ayanamsa=opts.ayanamsa.value)
    transit_pos = get_all_planet_positions(transit_jd, zodiac_type=opts.zodiac_type.value, ayanamsa=opts.ayanamsa.value)
    
    return analyze_gochar(natal_pos, transit_pos)

from api.core.jaimini import get_chara_karakas, get_arudha_padas, get_karakamsa

@router.post("/jaimini-karakas")
async def vedic_jaimini_karakas(request: NatalChartRequest):
    jd = birth_data_to_jd(request.birth_data)
    bd = request.birth_data
    positions = get_all_planet_positions(jd, zodiac_type="SIDEREAL", ayanamsa=request.options.ayanamsa.value)
    houses = get_houses(jd, bd.latitude, bd.longitude, "WHOLE_SIGN", "SIDEREAL", request.options.ayanamsa.value)
    positions = assign_houses_to_planets(positions, houses)
    return get_chara_karakas(positions)

@router.post("/arudha-padas")
async def vedic_arudha_padas(request: NatalChartRequest):
    jd = birth_data_to_jd(request.birth_data)
    bd = request.birth_data
    positions = get_all_planet_positions(jd, zodiac_type="SIDEREAL", ayanamsa=request.options.ayanamsa.value)
    houses = get_houses(jd, bd.latitude, bd.longitude, "WHOLE_SIGN", "SIDEREAL", request.options.ayanamsa.value)
    positions = assign_houses_to_planets(positions, houses)
    return get_arudha_padas(positions, houses)

@router.post("/karakamsa")
async def vedic_karakamsa(request: NatalChartRequest):
    jd = birth_data_to_jd(request.birth_data)
    bd = request.birth_data
    positions = get_all_planet_positions(jd, zodiac_type="SIDEREAL", ayanamsa=request.options.ayanamsa.value)
    return get_karakamsa(positions)

from api.core.dashas import get_char_dashas, get_current_chara_dasha

@router.post("/dashas/chara")
async def vedic_chara_dasha(request: NatalChartRequest):
    jd = birth_data_to_jd(request.birth_data)
    bd = request.birth_data
    positions = get_all_planet_positions(jd, zodiac_type="SIDEREAL", ayanamsa=request.options.ayanamsa.value)
    houses = get_houses(jd, bd.latitude, bd.longitude, "WHOLE_SIGN", "SIDEREAL", request.options.ayanamsa.value)
    
    dashas = get_char_dashas(jd, houses, positions)
    current = get_current_chara_dasha(dashas, get_current_jd())
    
    return {"timeline": dashas, "current": current}

@router.post("/dashas/vimshottari")
async def vedic_vimshottari(request: NatalChartRequest):
    jd = birth_data_to_jd(request.birth_data)
    positions = get_all_planet_positions(jd, zodiac_type="SIDEREAL", ayanamsa=request.options.ayanamsa.value)
    moon_lon = positions.get("moon", {}).get("longitude", 0)
    ayanamsa_val = get_ayanamsa_value(jd, request.options.ayanamsa.value)
    moon_sid = (moon_lon - ayanamsa_val) % 360
    mahadashas = get_mahadashas(jd, moon_sid)
    result = []
    for md in mahadashas:
        antardashas = get_antardashas(md)
        result.append({**md, "antardashas": antardashas})
    return {"dashas": result}


@router.post("/dashas/current")
async def vedic_current_dasha(request: NatalChartRequest):
    jd = birth_data_to_jd(request.birth_data)
    positions = get_all_planet_positions(jd, zodiac_type="SIDEREAL", ayanamsa=request.options.ayanamsa.value)
    moon_lon = positions.get("moon", {}).get("longitude", 0)
    ayanamsa_val = get_ayanamsa_value(jd, request.options.ayanamsa.value)
    moon_sid = (moon_lon - ayanamsa_val) % 360
    return get_current_dasha(jd, moon_sid, get_current_jd())


@router.post("/dashas/yogini")
async def vedic_yogini_dasha(request: NatalChartRequest):
    jd = birth_data_to_jd(request.birth_data)
    positions = get_all_planet_positions(jd, zodiac_type="SIDEREAL", ayanamsa=request.options.ayanamsa.value)
    moon_lon = positions.get("moon", {}).get("longitude", 0)
    ayanamsa_val = get_ayanamsa_value(jd, request.options.ayanamsa.value)
    return get_yogini_dashas(jd, (moon_lon - ayanamsa_val) % 360)


@router.post("/dashas/kalachakra")
async def vedic_kalachakra_dasha(request: NatalChartRequest):
    jd = birth_data_to_jd(request.birth_data)
    positions = get_all_planet_positions(jd, zodiac_type="SIDEREAL", ayanamsa=request.options.ayanamsa.value)
    moon_lon = positions.get("moon", {}).get("longitude", 0)
    ayanamsa_val = get_ayanamsa_value(jd, request.options.ayanamsa.value)
    return get_kalachakra_dasha(jd, (moon_lon - ayanamsa_val) % 360)


from pydantic import BaseModel

class DashaInterpretationRequest(BaseModel):
    mahadasha_lord: str
    antardasha_lord: str = None

@router.post("/dashas/interpretation")
async def vedic_dasha_interpretation(request: DashaInterpretationRequest):
    return get_dasha_interpretation(request.mahadasha_lord, request.antardasha_lord)

from api.core.varshaphal import get_varshaphal_chart

@router.post("/varshaphal")
async def vedic_varshaphal(target_year: int, request: NatalChartRequest):
    jd = birth_data_to_jd(request.birth_data)
    bd = request.birth_data
    positions = get_all_planet_positions(jd, zodiac_type="SIDEREAL", ayanamsa=request.options.ayanamsa.value)
    sun_sid = positions.get("sun", {}).get("longitude", 0.0)
    houses = get_houses(jd, bd.latitude, bd.longitude, "WHOLE_SIGN", "SIDEREAL", request.options.ayanamsa.value)
    asc_sign = houses.get("cusps", {}).get("house_1", {}).get("sign", "Aries")
    
    return get_varshaphal_chart(jd, sun_sid, asc_sign, target_year, bd.latitude, bd.longitude, request.options.ayanamsa.value)

@router.post("/yogas")
async def vedic_yogas(request: NatalChartRequest):
    jd = birth_data_to_jd(request.birth_data)
    bd = request.birth_data
    positions = get_all_planet_positions(jd, zodiac_type="SIDEREAL", ayanamsa=request.options.ayanamsa.value)
    houses = get_houses(jd, bd.latitude, bd.longitude, "WHOLE_SIGN", "SIDEREAL", request.options.ayanamsa.value)
    positions = assign_houses_to_planets(positions, houses)
    return {"yogas": detect_all_yogas(positions, houses)}


@router.post("/shadbala")
async def vedic_shadbala(request: NatalChartRequest):
    jd = birth_data_to_jd(request.birth_data)
    bd = request.birth_data
    positions = get_all_planet_positions(jd, zodiac_type="SIDEREAL", ayanamsa=request.options.ayanamsa.value)
    houses = get_houses(jd, bd.latitude, bd.longitude, "WHOLE_SIGN", "SIDEREAL", request.options.ayanamsa.value)
    positions = assign_houses_to_planets(positions, houses)
    aspects = get_aspects(positions)
    return calculate_shadbala(positions, houses, aspects, jd)


@router.post("/ashtakavarga")
async def vedic_ashtakavarga(request: NatalChartRequest):
    jd = birth_data_to_jd(request.birth_data)
    bd = request.birth_data
    positions = get_all_planet_positions(jd, zodiac_type="SIDEREAL", ayanamsa=request.options.ayanamsa.value)
    houses = get_houses(jd, bd.latitude, bd.longitude, "WHOLE_SIGN", "SIDEREAL", request.options.ayanamsa.value)
    return get_sarvashtakavarga(positions, houses)


@router.post("/nakshatras")
async def vedic_nakshatras(request: NatalChartRequest):
    jd = birth_data_to_jd(request.birth_data)
    positions = get_all_planet_positions(jd, zodiac_type="SIDEREAL", ayanamsa=request.options.ayanamsa.value)
    return {name: {"nakshatra": p.get("nakshatra"), "pada": p.get("nakshatra_pada"),
                   "lord": p.get("nakshatra_lord"), "deity": p.get("nakshatra_deity")}
            for name, p in positions.items()}


@router.post("/atmakaraka")
async def vedic_atmakaraka(request: NatalChartRequest):
    jd = birth_data_to_jd(request.birth_data)
    positions = get_all_planet_positions(jd, zodiac_type="SIDEREAL", ayanamsa=request.options.ayanamsa.value)
    return {"atmakaraka": get_atmakaraka(positions), "amatyakaraka": get_amatyakaraka(positions)}


@router.post("/sade-sati")
async def vedic_sade_sati(request: NatalChartRequest):
    jd = birth_data_to_jd(request.birth_data)
    natal_pos = get_all_planet_positions(jd, zodiac_type="SIDEREAL", ayanamsa=request.options.ayanamsa.value)
    transit_pos = get_all_planet_positions(get_current_jd(), zodiac_type="SIDEREAL", ayanamsa=request.options.ayanamsa.value)
    natal_moon_idx = natal_pos.get("moon", {}).get("sign_index", 0)
    transit_saturn_idx = transit_pos.get("saturn", {}).get("sign_index", 0)
    return detect_sade_sati(natal_moon_idx, transit_saturn_idx)


@router.post("/doshas")
async def vedic_doshas(request: NatalChartRequest):
    jd = birth_data_to_jd(request.birth_data)
    bd = request.birth_data
    positions = get_all_planet_positions(jd, zodiac_type="SIDEREAL", ayanamsa=request.options.ayanamsa.value)
    houses = get_houses(jd, bd.latitude, bd.longitude, "WHOLE_SIGN", "SIDEREAL", request.options.ayanamsa.value)
    positions = assign_houses_to_planets(positions, houses)
    doshas = []
    doshas.extend(detect_kala_sarpa_dosha(positions))
    doshas.extend(detect_mangal_dosha(positions))
    return {"doshas": doshas}


@router.post("/remedies")
async def vedic_remedies(request: NatalChartRequest):
    jd = birth_data_to_jd(request.birth_data)
    bd = request.birth_data
    positions = get_all_planet_positions(jd, zodiac_type="SIDEREAL", ayanamsa=request.options.ayanamsa.value)
    houses = get_houses(jd, bd.latitude, bd.longitude, "WHOLE_SIGN", "SIDEREAL", request.options.ayanamsa.value)
    positions = assign_houses_to_planets(positions, houses)
    yogas = detect_all_yogas(positions, houses)
    return {"remedies": [y for y in yogas if y.get("remedies")]}


@router.post("/compatibility")
async def vedic_compatibility(request: CompatibilityRequest):
    jd1 = birth_data_to_jd(request.person1)
    jd2 = birth_data_to_jd(request.person2)
    pos1 = get_all_planet_positions(jd1, zodiac_type="SIDEREAL", ayanamsa=request.ayanamsa.value)
    pos2 = get_all_planet_positions(jd2, zodiac_type="SIDEREAL", ayanamsa=request.ayanamsa.value)
    ayanamsa_val = get_ayanamsa_value(jd1, request.ayanamsa.value)
    m1 = (pos1.get("moon", {}).get("longitude", 0) - ayanamsa_val) % 360
    m2 = (pos2.get("moon", {}).get("longitude", 0) - get_ayanamsa_value(jd2, request.ayanamsa.value)) % 360
    return get_gun_milan(m1, m2)

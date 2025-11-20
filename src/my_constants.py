# src/my_constants.py
DB_CONTAINER_DIR = "./bin/database.db"
DB_TABLES = {
    "profile": "PROFILE",
    "property_product": "PROPERTY_PRODUCT",
    "misc_product": "MISC_PRODUCT",
    "property_template": "PROPERTY_TEMPLATE",
    "setting": "SETTING",
}
PROFILE__NAME_OPTIONS = {
    "real_estate": "REAL_ESTATE",
    "tire": "TIRE",
    "fashion": "FASHION",
}
PROFILE__STATUS_OPTIONS = {
    "dead": "DEAD",
    "live": "LIVE",
}
PROPERTY_PRODUCT__STATUS_OPTIONS = {
    "selling": "đang bán",
    "sold": "đã bán",
    "paused": "tạm dừng",
}

PROPERTY_PRODUCT__TRANSACTION_OPTIONS = {
    "sale": "bán",
    "rental": "cho thuê",
    "transfer": "sang nhượng",
}
PROPERTY_PRODUCT__PROVINCE_OPTIONS = {
    "lam_dong": "lâm đồng",
}
PROPERTY_PRODUCT__DISTRICT_OPTIONS = {
    "da_lat": "đà lạt",
}
PROPERTY_PRODUCT__WARD_OPTIONS = {
    "phuong_1_xuan_huong": "phường 1 (p.xuân hương)",
    "phuong_2_xuan_huong": "phường 2 (p.xuân hương)",
    "phuong_3_xuan_huong": "phường 3 (p.xuân hương)",
    "phuong_4_xuan_huong": "phường 4 (p.xuân hương)",
    "phuong_5_cam_ly": "phường 5 (p.cam ly)",
    "phuong_6_cam_ly": "phường 6 (p.cam ly)",
    "phuong_7_lang_biang": "phường 7 (p.lang biang)",
    "phuong_8_lam_vien": "phường 8 (p.lâm viên)",
    "phuong_9_lam_vien": "phường 9 (p.lâm viên)",
    "phuong_10_xuan_huong": "phường 10 (p.xuân hương)",
    "phuong_11_xuan_truong": "phường 11 (p.xuân trường)",
    "phuong_12_lam_vien": "phường 12 (p.lâm viên)",
    "xa_xuan_truong": "xã xuân trường (p.xuân trường)",
    "xa_xuan_tho": "xã xuân thọ (p.xuân trường)",
    "xa_ta_nung": "xã tà nung (p.cam ly)",
    "xa_tram_hanh": "xã trạm hành (p.xuân trường)",
    "thi_tran_lac_duong": "thị trấn lạc dương (p.lang biang)",
}

PROPERTY_PRODUCT__CATEGORY_OPTIONS = {
    "townhouse": "nhà phố",
    "street_front_house": "nhà mặt tiền",
    "apartment_condo": "căn hộ/ chung cư",
    "villa": "biệt thự",
    "land_plot": "đất nền",
    "warehouse_yard": "kho/bãi",
    "business_premises": "mbkd",
    "hotel": "khách sạn",
    "homestay": "homestay",
}

PROPERTY_PRODUCT__UNIT_OPTIONS = {
    "billion": "tỷ",
    "million": "triệu",
    "million_per_month": "triệu/tháng",
}

PROPERTY_PRODUCT__LEGAL_OPTIONS = {
    "vi_bang_purchase": "mua bán vi bằng",
    "shared_agriculture_deed": "sổ nông nghiệp chung",
    "decentralized_agriculture_deed": "sổ nông nghiệp phân quyền",
    "private_agriculture_deed": "sổ nông nghiệp riêng",
    "shared_construction_deed": "sổ xây dựng chung",
    "decentralized_construction_deed": "sổ xây dựng phân quyền",
    "private_construction_deed": "sổ xây dựng riêng",
}

PROPERTY_PRODUCT__BUILDING_LINE_OPTIONS = {
    "car_access_road": "đường xe hơi",
    "motorbike_access_road": "đường xe máy",
}

PROPERTY_PRODUCT__FURNITURE_OPTIONS = {
    "no_furniture": "không nội thất",
    "basic_furniture": "nội thất cơ bản",
    "full_furniture": "đầy đủ nội thất",
}

PROPERTY_TEMPLATE__TRANSACTION_OPTIONS = PROPERTY_PRODUCT__TRANSACTION_OPTIONS
PROPERTY_TEMPLATE__NAME_OPTIONS = {
    "title": "tiêu đề",
    "description": "mô tả",
}
PROPERTY_TEMPLATE__CATEGORY_OPTIONS = PROPERTY_PRODUCT__CATEGORY_OPTIONS

SETTING_NAME_OPTIONS = {
    "profile_container_dir": "PROFILE_CONTAINER_DIR",
    "image_container_dir": "IMAGE_CONTAINER_DIR",
    "logo_file": "LOGO_FILE",
    "proxy": "PROXY",
}

ROBOT_ACTION_OPTIONS = {
    "sell__by_marketplace": "SELL__BY_MARKETPLACE",
    "sell__by_group": "SELL__BY_GROUP",
    "discussion_to_group": "DISCUSSION_TO_GROUP",
    "discussion_to_new_feed": "DISCUSSION_TO_NEW_FEED",
    "share_listed_item": "SHARE_LISTED_ITEM",
    "launch": "LAUNCH",
    "take_care": "TAKE_CARE",
}

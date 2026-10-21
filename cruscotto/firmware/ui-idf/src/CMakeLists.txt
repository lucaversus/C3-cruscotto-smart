idf_component_register(SRCS "main.cpp"
                       INCLUDE_DIRS "." "../include" "../../common/include"
                       REQUIRES esp_lcd esp_timer driver esp_psram app_update)

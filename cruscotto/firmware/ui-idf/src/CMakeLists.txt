idf_component_register(SRCS "main.cpp" "link.cpp" "blackbox.cpp" "labels.cpp" "dashboard.cpp" "font_speed.c"
                       INCLUDE_DIRS "." "../include" "../../common/include"
                       REQUIRES esp_lcd esp_timer driver esp_psram app_update)

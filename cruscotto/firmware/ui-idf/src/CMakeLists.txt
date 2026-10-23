idf_component_register(SRCS "main.cpp" "link.cpp" "blackbox.cpp" "labels.cpp" "dashboard.cpp" "backlight.cpp" "startup.cpp" "font_speed.c" "font_check.c" "font_go.c" "icons.c"
                       INCLUDE_DIRS "." "../include" "../../common/include"
                       REQUIRES esp_lcd esp_timer driver esp_psram app_update)

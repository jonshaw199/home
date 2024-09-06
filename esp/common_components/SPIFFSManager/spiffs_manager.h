#include <esp_spiffs.h>
#include <esp_log.h>
#include <cstdio>

class SPIFFSManager
{
public:
    // Constructor to set base path and max files
    SPIFFSManager(const char *base_path = "/storage", size_t max_files = 5)
        : base_path(base_path), max_files(max_files) {}

    // Initialize SPIFFS
    bool begin(bool format_if_mount_failed = true)
    {
        esp_vfs_spiffs_conf_t conf = {
            .base_path = base_path,
            .partition_label = NULL,
            .max_files = max_files,
            .format_if_mount_failed = format_if_mount_failed};

        esp_err_t ret = esp_vfs_spiffs_register(&conf);
        if (ret != ESP_OK)
        {
            ESP_LOGE(TAG, "Failed to mount SPIFFS (%s)", esp_err_to_name(ret));
            return false;
        }

        size_t total = 0, used = 0;
        ret = esp_spiffs_info(NULL, &total, &used);
        if (ret == ESP_OK)
        {
            ESP_LOGI(TAG, "SPIFFS total: %d, used: %d", total, used);
        }
        else
        {
            ESP_LOGE(TAG, "Failed to get SPIFFS partition information (%s)", esp_err_to_name(ret));
            return false;
        }

        return true;
    }

    // Unmount SPIFFS
    void end()
    {
        esp_vfs_spiffs_unregister(NULL);
        ESP_LOGI(TAG, "SPIFFS unmounted");
    }

    // Check if a file exists
    bool exists(const char *file_path)
    {
        std::string full_path = std::string(base_path) + file_path;
        FILE *file = fopen(full_path.c_str(), "r");
        if (file)
        {
            fclose(file);
            return true;
        }
        return false;
    }

    // Read file into a buffer
    bool readFile(const char *file_path, std::vector<uint8_t> &buffer)
    {
        std::string full_path = std::string(base_path) + file_path;
        FILE *file = fopen(full_path.c_str(), "rb");
        if (!file)
        {
            ESP_LOGE(TAG, "Failed to open file: %s", file_path);
            return false;
        }

        fseek(file, 0, SEEK_END);
        size_t file_size = ftell(file);
        rewind(file);

        buffer.resize(file_size);
        size_t read_bytes = fread(buffer.data(), 1, file_size, file);
        fclose(file);

        if (read_bytes != file_size)
        {
            ESP_LOGE(TAG, "Failed to read entire file: %s", file_path);
            return false;
        }

        ESP_LOGI(TAG, "File %s read successfully", file_path);
        return true;
    }

    // Delete a file
    bool remove(const char *file_path)
    {
        std::string full_path = std::string(base_path) + file_path;
        if (std::remove(full_path.c_str()) == 0)
        {
            ESP_LOGI(TAG, "File %s deleted", file_path);
            return true;
        }
        else
        {
            ESP_LOGE(TAG, "Failed to delete file %s", file_path);
            return false;
        }
    }

private:
    const char *base_path;
    size_t max_files;
    static constexpr const char *TAG = "SPIFFSManager";
};

package com.salesforce.framework.utils;

import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;

public final class ConfigReader {

    private static final String CONFIG_FILE = "config.properties";
    private static final Properties PROPERTIES = new Properties();

    static {
        try (InputStream input = ConfigReader.class.getClassLoader().getResourceAsStream(CONFIG_FILE)) {
            if (input == null) {
                throw new IllegalStateException("Configuration file " + CONFIG_FILE + " not found in classpath");
            }
            PROPERTIES.load(input);
        } catch (IOException e) {
            throw new IllegalStateException("Failed to load configuration file " + CONFIG_FILE, e);
        }
    }

    private ConfigReader() {
    }

    public static String getProperty(String key) {
        String value = PROPERTIES.getProperty(key);
        if (value == null) {
            throw new IllegalStateException("Required configuration key '" + key + "' is missing");
        }
        return value.trim();
    }

    public static String getProperty(String key, String defaultValue) {
        String value = PROPERTIES.getProperty(key);
        return value == null ? defaultValue : value.trim();
    }
}

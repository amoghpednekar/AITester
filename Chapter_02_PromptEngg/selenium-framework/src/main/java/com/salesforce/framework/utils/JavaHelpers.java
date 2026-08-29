package com.salesforce.framework.utils;

import java.time.Duration;

public final class JavaHelpers {

    private JavaHelpers() {
    }

    public static Duration parseTimeoutSeconds(String value, Duration fallback) {
        try {
            return Duration.ofSeconds(Long.parseLong(value));
        } catch (NumberFormatException e) {
            return fallback;
        }
    }
}

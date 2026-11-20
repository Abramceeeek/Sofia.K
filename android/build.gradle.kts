plugins {
    id("com.android.application") version "8.9.3" apply false   // SEC-13: API 36 needs 8.9.1 or later
    id("org.jetbrains.kotlin.android") version "2.0.21" apply false
    id("org.jetbrains.kotlin.plugin.compose") version "2.0.21" apply false
    id("org.jetbrains.kotlin.plugin.serialization") version "2.0.21" apply false
}

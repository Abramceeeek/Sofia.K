// ODYS for Android (D125): the same app as app/ (SwiftUI), in Kotlin and Jetpack Compose. It talks to the same Brain.
pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}
rootProject.name = "ODYS"
include(":app")

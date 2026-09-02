# SANTINEL — Android app

Native Android client for the SANTINEL negotiation-coaching API. Single-activity
Jetpack Compose app that calls `POST /analyze` and renders the 10-framework
coaching read-out (close probability, top frameworks, per-framework finding +
confidence + suggestion). Bilingual EN / RO.

## Stack

| Component            | Version        |
|---------------------|----------------|
| Gradle              | 8.7            |
| Android Gradle Plugin | 8.5.2        |
| Kotlin              | 1.9.24         |
| Compose Compiler    | 1.5.14         |
| Compose BOM         | 2024.06.00     |
| compileSdk / target | 34             |
| minSdk              | 26             |
| JDK                 | 17+ (21 works) |

## Project layout

```
mobile/android/
├── settings.gradle          module list + repositories
├── build.gradle             root — plugin versions
├── gradle.properties        JVM args, AndroidX flags
├── gradlew / gradlew.bat    Gradle wrapper scripts
├── gradle/wrapper/          wrapper jar + distribution pointer
└── app/
    ├── build.gradle         app module — SDK levels, deps
    ├── proguard-rules.pro
    └── src/main/
        ├── AndroidManifest.xml
        ├── java/com/santinel/app/
        │   ├── MainActivity.kt         Compose UI + API client
        │   └── ui/theme/Theme.kt       Material 3 theme
        └── res/
            ├── values/      strings, colors, base theme
            ├── xml/         backup + network-security config
            ├── drawable/    launcher foreground (vector)
            └── mipmap-anydpi-v26/  adaptive launcher icon
```

## Prerequisites

1. **JDK 17+** — the Android Studio JBR works
   (`C:\Program Files\Android\Android Studio\jbr`, JDK 21).
2. **Android SDK** with `platforms;android-34` and `build-tools;34.0.0`.
   Point to it via one of:
   - `mobile/android/local.properties` → `sdk.dir=/absolute/path/to/android-sdk`
   - env var `ANDROID_HOME` / `ANDROID_SDK_ROOT`

## Build

From `mobile/android/`:

```bash
# Windows
set JAVA_HOME=C:\Program Files\Android\Android Studio\jbr
gradlew.bat assembleDebug

# POSIX
JAVA_HOME=/path/to/jdk17 ./gradlew assembleDebug
```

Output APK:

```
mobile/android/app/build/outputs/apk/debug/app-debug.apk
```

Install on a running emulator / device:

```bash
adb install -r app/build/outputs/apk/debug/app-debug.apk
```

## Talking to the API

`MainActivity.kt` sets `API_BASE = "http://10.0.2.2:8000"` — `10.0.2.2` is the
host loopback as seen from the Android emulator, so it reaches
`python start_api.py` running on the dev machine. For a physical device use the
machine's LAN IP (e.g. `http://192.168.1.50:8000`) and add that host to
`res/xml/network_security_config.xml`.

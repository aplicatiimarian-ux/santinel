# Legacy Phase-16 Android stubs

These Kotlin files were committed in an earlier phase ("Phase 16: Native Mobile
Apps") before this Gradle project existed. They live **outside** `app/src/` so
they are not part of the build.

- `com/santinel/SantinelApp.kt` — a full Compose UI mock (home / analytics /
  settings / login) in package `com.santinel`. Needs extra deps to compile:
  `androidx.compose.material:material-icons-extended` and
  `androidx.lifecycle:lifecycle-viewmodel-compose`.
- `com/santinel/models/Models.kt` — plain data classes.
- `com/santinel/services/AudioRecordingService.kt` — a background
  `MediaRecorder` service (needs `RECORD_AUDIO` + `FOREGROUND_SERVICE`
  permissions and a `<service>` entry in the manifest to actually run).

The live app is `com.santinel.app.MainActivity` under `app/src/main/`. To fold
this material back in, move the files into `app/src/main/java/`, add the missing
Gradle dependencies, and register the service in `AndroidManifest.xml`.

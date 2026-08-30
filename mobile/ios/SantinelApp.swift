// SANTINEL iOS App
// SwiftUI + Swift native iOS app
// iPhone 15 optimized, live coaching during calls

import SwiftUI
import AVFoundation
import UserNotifications

@main
struct SantinelApp: App {
    @StateObject var appState = AppState()
    @StateObject var audioManager = AudioManager()

    var body: some Scene {
        WindowGroup {
            if appState.isLoggedIn {
                MainTabView()
                    .environmentObject(appState)
                    .environmentObject(audioManager)
            } else {
                LoginView()
                    .environmentObject(appState)
            }
        }
    }
}

// MARK: - App State Management
class AppState: ObservableObject {
    @Published var isLoggedIn = false
    @Published var currentCall: CallSession?
    @Published var liveCoaching: CoachingInsight?
    @Published var user: User?

    func login(email: String, password: String) async {
        // API call
        isLoggedIn = true
    }

    func logout() {
        isLoggedIn = false
        currentCall = nil
    }
}

// MARK: - Main Tab View
struct MainTabView: View {
    @StateObject var tabState = TabState()

    var body: some View {
        TabView(selection: $tabState.selectedTab) {
            HomeView()
                .tabItem {
                    Label("Home", systemImage: "house.fill")
                }
                .tag(Tab.home)

            AnalyticsView()
                .tabItem {
                    Label("Analytics", systemImage: "chart.bar.fill")
                }
                .tag(Tab.analytics)

            SettingsView()
                .tabItem {
                    Label("Settings", systemImage: "gear")
                }
                .tag(Tab.settings)
        }
    }
}

enum Tab {
    case home, analytics, settings
}

class TabState: ObservableObject {
    @Published var selectedTab: Tab = .home
}

// MARK: - Home View with Quick Record
struct HomeView: View {
    @EnvironmentObject var appState: AppState
    @EnvironmentObject var audioManager: AudioManager
    @State var isRecording = false
    @State var coachingNotifications: [CoachingInsight] = []

    var body: some View {
        ZStack {
            // Background
            LinearGradient(
                gradient: Gradient(colors: [Color(.systemBlue), Color(.systemCyan)]),
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            .ignoresSafeArea()

            VStack(spacing: 20) {
                // Header
                VStack(alignment: .leading) {
                    Text("SANTINEL")
                        .font(.system(size: 32, weight: .bold))
                        .foregroundColor(.white)

                    Text("Ready for your negotiation?")
                        .font(.subheadline)
                        .foregroundColor(.white.opacity(0.8))
                }
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding()

                Spacer()

                // Quick Record Button (Floating)
                Button(action: toggleRecording) {
                    Image(systemName: isRecording ? "stop.circle.fill" : "record.circle")
                        .resizable()
                        .frame(width: 80, height: 80)
                        .foregroundColor(.white)
                        .background(Circle().fill(isRecording ? Color.red : Color.blue))
                }
                .frame(width: 100, height: 100)
                .hapticFeedback()

                Text(isRecording ? "Recording..." : "Tap to Start")
                    .font(.headline)
                    .foregroundColor(.white)

                Spacer()

                // Live Coaching Section
                if let coaching = appState.liveCoaching {
                    CoachingCardView(coaching: coaching)
                        .transition(.move(edge: .bottom).combined(with: .opacity))
                }

                // Recent Calls
                VStack(alignment: .leading, spacing: 10) {
                    Text("Recent Calls")
                        .font(.headline)
                        .foregroundColor(.white)

                    ScrollView {
                        VStack(spacing: 8) {
                            ForEach(coachingNotifications.prefix(3), id: \.id) { coaching in
                                HStack {
                                    VStack(alignment: .leading) {
                                        Text(coaching.situation.uppercased())
                                            .font(.caption)
                                            .foregroundColor(.gray)
                                        Text(coaching.summary)
                                            .font(.body)
                                            .foregroundColor(.white)
                                    }
                                    Spacer()
                                    Text("\(Int(coaching.effectiveness * 100))%")
                                        .font(.headline)
                                        .foregroundColor(.green)
                                }
                                .padding()
                                .background(Color.white.opacity(0.1))
                                .cornerRadius(8)
                            }
                        }
                    }
                }
                .padding()
                .background(Color.white.opacity(0.1))
                .cornerRadius(12)
                .padding()
            }
        }
        .onAppear {
            requestNotificationPermissions()
        }
    }

    private func toggleRecording() {
        if isRecording {
            audioManager.stopRecording()
            isRecording = false
        } else {
            audioManager.startRecording()
            isRecording = true

            // Simulate live coaching
            DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
                appState.liveCoaching = CoachingInsight(
                    id: UUID(),
                    situation: "closing",
                    personality: "driver",
                    primaryFinding: "Lead showing urgency signals",
                    summary: "Respond with directness - close now",
                    confidence: 0.92,
                    effectiveness: 0.87
                )
            }
        }
    }

    private func requestNotificationPermissions() {
        UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .sound, .badge]) { _, _ in }
    }
}

// MARK: - Coaching Card (Live Coaching Display)
struct CoachingCardView: View {
    let coaching: CoachingInsight

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                VStack(alignment: .leading) {
                    Text("LIVE COACHING")
                        .font(.caption)
                        .foregroundColor(.orange)
                    Text(coaching.summary)
                        .font(.headline)
                        .foregroundColor(.white)
                }
                Spacer()
                ZStack {
                    Circle()
                        .fill(Color.green)
                    Text("\(Int(coaching.confidence * 100))%")
                        .font(.caption)
                        .foregroundColor(.white)
                }
                .frame(width: 50, height: 50)
            }

            HStack(spacing: 8) {
                Label(coaching.personality.uppercased(), systemImage: "person.fill")
                Spacer()
                Label(coaching.situation.uppercased(), systemImage: "target")
            }
            .font(.caption)
            .foregroundColor(.white.opacity(0.7))
        }
        .padding()
        .background(Color.green.opacity(0.2))
        .borderRadius(12, color: .green)
        .padding()
    }
}

// MARK: - Analytics View
struct AnalyticsView: View {
    @State var winRate = 0.76
    @State var topScript = "script_closing_driver"

    var body: some View {
        NavigationView {
            List {
                Section("Performance") {
                    HStack {
                        Text("Win Rate")
                        Spacer()
                        Text("\(Int(winRate * 100))%")
                            .font(.headline)
                            .foregroundColor(.green)
                    }

                    HStack {
                        Text("Top Script")
                        Spacer()
                        Text(topScript)
                            .font(.caption)
                            .foregroundColor(.blue)
                    }
                }

                Section("This Week") {
                    Text("5 calls recorded")
                    Text("78% average effectiveness")
                }
            }
            .navigationTitle("Analytics")
        }
    }
}

// MARK: - Settings View
struct SettingsView: View {
    @EnvironmentObject var appState: AppState
    @State var notificationsEnabled = true
    @State var language = "en"

    var body: some View {
        NavigationView {
            List {
                Section("Preferences") {
                    Toggle("Push Notifications", isOn: $notificationsEnabled)

                    Picker("Language", selection: $language) {
                        Text("English").tag("en")
                        Text("Română").tag("ro")
                    }
                }

                Section("Account") {
                    Button(role: .destructive) {
                        appState.logout()
                    } label: {
                        Text("Logout")
                    }
                }
            }
            .navigationTitle("Settings")
        }
    }
}

// MARK: - Login View
struct LoginView: View {
    @EnvironmentObject var appState: AppState
    @State var email = ""
    @State var password = ""
    @State var isLoading = false

    var body: some View {
        NavigationView {
            VStack(spacing: 20) {
                Text("SANTINEL")
                    .font(.system(size: 40, weight: .bold))
                    .foregroundColor(.blue)

                Text("Real-time AI Coaching")
                    .font(.subheadline)
                    .foregroundColor(.gray)

                VStack(spacing: 12) {
                    TextField("Email", text: $email)
                        .textContentType(.emailAddress)
                        .padding()
                        .background(Color(.systemGray6))
                        .cornerRadius(8)

                    SecureField("Password", text: $password)
                        .textContentType(.password)
                        .padding()
                        .background(Color(.systemGray6))
                        .cornerRadius(8)
                }

                Button(action: login) {
                    if isLoading {
                        ProgressView()
                            .tint(.white)
                    } else {
                        Text("Sign In")
                    }
                }
                .frame(maxWidth: .infinity)
                .padding()
                .background(Color.blue)
                .foregroundColor(.white)
                .cornerRadius(8)
                .disabled(email.isEmpty || password.isEmpty)

                Spacer()
            }
            .padding()
        }
    }

    private func login() {
        isLoading = true
        Task {
            await appState.login(email: email, password: password)
            isLoading = false
        }
    }
}

// MARK: - Models
struct User: Codable {
    let id: String
    let email: String
    let name: String
}

struct CallSession: Codable {
    let id: String
    let startTime: Date
    let situation: String
    let personalityDetected: String
}

struct CoachingInsight: Codable {
    let id: UUID
    let situation: String
    let personality: String
    let primaryFinding: String
    let summary: String
    let confidence: Double
    let effectiveness: Double
}

// MARK: - Audio Manager
class AudioManager: NSObject, ObservableObject, AVAudioRecorderDelegate {
    @Published var isRecording = false
    private var audioRecorder: AVAudioRecorder?
    private var audioSession = AVAudioSession.sharedInstance()

    func startRecording() {
        do {
            try audioSession.setCategory(.record, mode: .default)
            try audioSession.setActive(true)

            let documentPath = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
            let audioFilename = documentPath.appendingPathComponent("call_\(Date().timeIntervalSince1970).m4a")

            let settings = [
                AVFormatIDKey: Int(kAudioFormatMPEG4AAC),
                AVSampleRateKey: 12000,
                AVNumberOfChannelsKey: 1,
                AVEncoderAudioQualityKey: AVAudioQuality.high.rawValue
            ]

            audioRecorder = try AVAudioRecorder(url: audioFilename, settings: settings)
            audioRecorder?.delegate = self
            audioRecorder?.record()
            isRecording = true
        } catch {
            print("Recording error: \(error)")
        }
    }

    func stopRecording() {
        audioRecorder?.stop()
        isRecording = false
    }
}

// MARK: - View Extensions
extension View {
    func hapticFeedback() -> some View {
        self.onTapGesture {
            let impact = UIImpactFeedbackGenerator(style: .heavy)
            impact.impactOccurred()
        }
    }

    func borderRadius(_ radius: CGFloat, color: Color) -> some View {
        self.overlay(
            RoundedRectangle(cornerRadius: radius)
                .stroke(color, lineWidth: 1)
        )
    }
}

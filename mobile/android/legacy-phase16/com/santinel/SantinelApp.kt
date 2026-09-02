// SANTINEL Android App
// Kotlin + Jetpack Compose native app
// Material Design 3, same UX as iOS

package com.santinel

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewmodel.compose.viewModel
import com.santinel.models.CoachingInsight
import com.santinel.models.User
import com.santinel.services.AudioRecordingService
import kotlinx.coroutines.launch

class SantinelApp : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            SantinelTheme {
                val viewModel: AppViewModel = viewModel()
                SantinelAppContent(viewModel)
            }
        }
    }
}

// MARK: - App State Management
class AppViewModel : ViewModel() {
    private val _isLoggedIn = mutableStateOf(false)
    val isLoggedIn: State<Boolean> = _isLoggedIn

    private val _user = mutableStateOf<User?>(null)
    val user: State<User?> = _user

    private val _liveCoaching = mutableStateOf<CoachingInsight?>(null)
    val liveCoaching: State<CoachingInsight?> = _liveCoaching

    private val _isRecording = mutableStateOf(false)
    val isRecording: State<Boolean> = _isRecording

    fun login(email: String, password: String) {
        _isLoggedIn.value = true
        _user.value = User(id = "user_1", email = email, name = "User")
    }

    fun logout() {
        _isLoggedIn.value = false
        _user.value = null
    }

    fun setLiveCoaching(coaching: CoachingInsight) {
        _liveCoaching.value = coaching
    }

    fun setRecording(recording: Boolean) {
        _isRecording.value = recording
    }
}

// MARK: - Theme
@Composable
private fun SantinelTheme(content: @Composable () -> Unit) {
    val primaryColor = Color(0xFF2196F3)
    val secondaryColor = Color(0xFF00BCD4)
    val tertiaryColor = Color(0xFF4CAF50)

    MaterialTheme(
        colorScheme = darkColorScheme(
            primary = primaryColor,
            secondary = secondaryColor,
            tertiary = tertiaryColor,
            background = Color(0xFF121212),
            surface = Color(0xFF1E1E1E),
        ),
        content = content
    )
}

// MARK: - Main App Content
@Composable
private fun SantinelAppContent(viewModel: AppViewModel) {
    if (viewModel.isLoggedIn.value) {
        MainTabView(viewModel)
    } else {
        LoginView(viewModel)
    }
}

// MARK: - Tab Navigation
@Composable
private fun MainTabView(viewModel: AppViewModel) {
    var selectedTab by remember { mutableIntStateOf(0) }

    Scaffold(
        bottomBar = {
            NavigationBar {
                NavigationBarItem(
                    icon = { Icon(Icons.Default.Home, contentDescription = "Home") },
                    label = { Text("Home") },
                    selected = selectedTab == 0,
                    onClick = { selectedTab = 0 }
                )
                NavigationBarItem(
                    icon = { Icon(Icons.Default.BarChart, contentDescription = "Analytics") },
                    label = { Text("Analytics") },
                    selected = selectedTab == 1,
                    onClick = { selectedTab = 1 }
                )
                NavigationBarItem(
                    icon = { Icon(Icons.Default.Settings, contentDescription = "Settings") },
                    label = { Text("Settings") },
                    selected = selectedTab == 2,
                    onClick = { selectedTab = 2 }
                )
            }
        }
    ) { innerPadding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
        ) {
            when (selectedTab) {
                0 -> HomeView(viewModel)
                1 -> AnalyticsView()
                2 -> SettingsView(viewModel)
            }
        }
    }
}

// MARK: - Home View with Quick Record
@Composable
private fun HomeView(viewModel: AppViewModel) {
    val scope = rememberCoroutineScope()
    var isRecording by remember { mutableStateOf(false) }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(
                brush = Brush.linearGradient(
                    colors = listOf(Color(0xFF2196F3), Color(0xFF00BCD4))
                )
            )
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(24.dp),
            verticalArrangement = Arrangement.Top,
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            // Header
            Text(
                "SANTINEL",
                fontSize = 40.sp,
                fontWeight = FontWeight.Bold,
                color = Color.White,
                modifier = Modifier.fillMaxWidth()
            )

            Text(
                "Ready for your negotiation?",
                fontSize = 14.sp,
                color = Color.White.copy(alpha = 0.8f),
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(top = 8.dp)
            )

            Spacer(modifier = Modifier.height(60.dp))

            // Quick Record Button
            FloatingActionButton(
                onClick = {
                    isRecording = !isRecording
                    viewModel.setRecording(isRecording)

                    if (isRecording) {
                        scope.launch {
                            // Simulate live coaching
                            kotlinx.coroutines.delay(2000)
                            viewModel.setLiveCoaching(
                                CoachingInsight(
                                    id = "coaching_1",
                                    situation = "closing",
                                    personality = "driver",
                                    primaryFinding = "Lead showing urgency signals",
                                    summary = "Respond with directness - close now",
                                    confidence = 0.92,
                                    effectiveness = 0.87
                                )
                            )
                        }
                    }
                },
                modifier = Modifier.size(100.dp),
                containerColor = if (isRecording) Color.Red else Color(0xFF2196F3),
                contentColor = Color.White
            ) {
                Icon(
                    imageVector = if (isRecording) Icons.Default.Stop else Icons.Default.Mic,
                    contentDescription = "Record",
                    modifier = Modifier.size(48.dp)
                )
            }

            Text(
                if (isRecording) "Recording..." else "Tap to Start",
                fontSize = 18.sp,
                fontWeight = FontWeight.Bold,
                color = Color.White,
                modifier = Modifier.padding(top = 16.dp)
            )

            Spacer(modifier = Modifier.height(40.dp))

            // Live Coaching Section
            viewModel.liveCoaching.value?.let { coaching ->
                CoachingCard(coaching)
                Spacer(modifier = Modifier.height(20.dp))
            }

            // Recent Calls Section
            Text(
                "Recent Calls",
                fontSize = 16.sp,
                fontWeight = FontWeight.Bold,
                color = Color.White,
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(top = 20.dp)
            )

            Spacer(modifier = Modifier.height(12.dp))

            // Mock recent calls
            repeat(3) {
                RecentCallItem(
                    situation = "Closing",
                    guidance = "Respond with directness",
                    effectiveness = 0.87
                )
            }
        }
    }
}

// MARK: - Coaching Card
@Composable
private fun CoachingCard(coaching: CoachingInsight) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp),
        colors = CardDefaults.cardColors(
            containerColor = Color.Green.copy(alpha = 0.2f)
        ),
        border = CardDefaults.outlinedCardBorder()
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        "LIVE COACHING",
                        fontSize = 12.sp,
                        color = Color(0xFFFF9800)
                    )
                    Text(
                        coaching.summary,
                        fontSize = 16.sp,
                        fontWeight = FontWeight.Bold,
                        color = Color.White
                    )
                }

                Card(
                    modifier = Modifier.size(50.dp),
                    colors = CardDefaults.cardColors(
                        containerColor = Color.Green
                    ),
                    shape = androidx.compose.foundation.shape.CircleShape
                ) {
                    Box(
                        modifier = Modifier
                            .fillMaxSize()
                            .wrapContentSize(),
                        contentAlignment = Alignment.Center
                    ) {
                        Text(
                            "${(coaching.confidence * 100).toInt()}%",
                            fontSize = 12.sp,
                            color = Color.White,
                            fontWeight = FontWeight.Bold
                        )
                    }
                }
            }

            Spacer(modifier = Modifier.height(12.dp))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(
                    coaching.personality.uppercase(),
                    fontSize = 12.sp,
                    color = Color.White.copy(alpha = 0.7f)
                )
                Text(
                    coaching.situation.uppercase(),
                    fontSize = 12.sp,
                    color = Color.White.copy(alpha = 0.7f)
                )
            }
        }
    }
}

// MARK: - Recent Call Item
@Composable
private fun RecentCallItem(situation: String, guidance: String, effectiveness: Double) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 8.dp),
        colors = CardDefaults.cardColors(
            containerColor = Color.White.copy(alpha = 0.1f)
        )
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    situation.uppercase(),
                    fontSize = 12.sp,
                    color = Color.Gray
                )
                Text(
                    guidance,
                    fontSize = 14.sp,
                    color = Color.White
                )
            }
            Text(
                "${(effectiveness * 100).toInt()}%",
                fontSize = 16.sp,
                fontWeight = FontWeight.Bold,
                color = Color.Green
            )
        }
    }
}

// MARK: - Analytics View
@Composable
private fun AnalyticsView() {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        Text(
            "Analytics",
            fontSize = 28.sp,
            fontWeight = FontWeight.Bold,
            color = Color.White
        )

        Spacer(modifier = Modifier.height(24.dp))

        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(
                containerColor = Color(0xFF1E1E1E)
            )
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 8.dp),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text("Win Rate", color = Color.White)
                    Text("76%", fontWeight = FontWeight.Bold, color = Color.Green)
                }

                Divider(color = Color.White.copy(alpha = 0.1f))

                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 8.dp),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text("Top Script", color = Color.White)
                    Text("script_closing_driver", fontSize = 12.sp, color = Color(0xFF2196F3))
                }

                Divider(color = Color.White.copy(alpha = 0.1f))

                Text(
                    "This Week",
                    fontSize = 14.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color.White,
                    modifier = Modifier.padding(top = 16.dp)
                )
                Text("5 calls recorded", fontSize = 12.sp, color = Color.Gray)
                Text("78% average effectiveness", fontSize = 12.sp, color = Color.Gray)
            }
        }
    }
}

// MARK: - Settings View
@Composable
private fun SettingsView(viewModel: AppViewModel) {
    var notificationsEnabled by remember { mutableStateOf(true) }
    var language by remember { mutableStateOf("en") }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        Text(
            "Settings",
            fontSize = 28.sp,
            fontWeight = FontWeight.Bold,
            color = Color.White
        )

        Spacer(modifier = Modifier.height(24.dp))

        // Notifications Toggle
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 12.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text("Push Notifications", color = Color.White)
            Switch(
                checked = notificationsEnabled,
                onCheckedChange = { notificationsEnabled = it }
            )
        }

        Divider(color = Color.White.copy(alpha = 0.1f))

        // Language Selection
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 12.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text("Language", color = Color.White)
            Text(
                if (language == "en") "English" else "Română",
                color = Color(0xFF2196F3)
            )
        }

        Divider(color = Color.White.copy(alpha = 0.1f))

        Spacer(modifier = Modifier.height(32.dp))

        // Logout Button
        Button(
            onClick = { viewModel.logout() },
            modifier = Modifier.fillMaxWidth(),
            colors = ButtonDefaults.buttonColors(
                containerColor = Color(0xFFD32F2F)
            )
        ) {
            Text("Logout")
        }
    }
}

// MARK: - Login View
@Composable
private fun LoginView(viewModel: AppViewModel) {
    var email by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var isLoading by remember { mutableStateOf(false) }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(
                brush = Brush.linearGradient(
                    colors = listOf(Color(0xFF2196F3), Color(0xFF00BCD4))
                )
            )
            .padding(24.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            "SANTINEL",
            fontSize = 48.sp,
            fontWeight = FontWeight.Bold,
            color = Color.White
        )

        Text(
            "Real-time AI Coaching",
            fontSize = 16.sp,
            color = Color.White.copy(alpha = 0.8f),
            modifier = Modifier.padding(top = 8.dp)
        )

        Spacer(modifier = Modifier.height(48.dp))

        OutlinedTextField(
            value = email,
            onValueChange = { email = it },
            label = { Text("Email") },
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 8.dp),
            colors = OutlinedTextFieldDefaults.colors(
                focusedTextColor = Color.White,
                unfocusedTextColor = Color.White
            )
        )

        OutlinedTextField(
            value = password,
            onValueChange = { password = it },
            label = { Text("Password") },
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 8.dp),
            visualTransformation = androidx.compose.ui.text.input.PasswordVisualTransformation(),
            colors = OutlinedTextFieldDefaults.colors(
                focusedTextColor = Color.White,
                unfocusedTextColor = Color.White
            )
        )

        Spacer(modifier = Modifier.height(32.dp))

        Button(
            onClick = {
                isLoading = true
                viewModel.login(email, password)
                isLoading = false
            },
            modifier = Modifier
                .fillMaxWidth()
                .height(48.dp),
            enabled = email.isNotEmpty() && password.isNotEmpty() && !isLoading
        ) {
            if (isLoading) {
                CircularProgressIndicator(
                    modifier = Modifier.size(24.dp),
                    color = Color.White
                )
            } else {
                Text("Sign In", fontSize = 16.sp)
            }
        }
    }
}

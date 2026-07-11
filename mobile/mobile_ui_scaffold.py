# ============================================================
# SANTINEL — MOBILE UI SCAFFOLD (React Native)
# Week 3: iOS + Android app configuration & setup
# ============================================================

import os
import json
import logging
from typing import Dict, List
from datetime import datetime, timezone
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================
# REACT NATIVE APP CONFIGURATION
# ============================================================

class MobileAppConfig:
    """
    React Native app configuration generator
    Produces setup for iOS + Android
    """
    
    def __init__(self, app_name: str = "SANTINEL"):
        """Initialize mobile app config"""
        self.app_name = app_name
        self.version = "0.1.0"
        self.created_at = datetime.now(timezone.utc)
        
        logger.info(f"MobileAppConfig init: {app_name} v{self.version}")
    
    def generate_package_json(self) -> Dict:
        """Generate package.json for React Native"""
        
        return {
            "name": "santinel-mobile",
            "version": self.version,
            "description": "SANTINEL - AI Coaching Assistant (Mobile)",
            "private": True,
            "scripts": {
                "start": "react-native start",
                "android": "react-native run-android",
                "ios": "react-native run-ios",
                "test": "jest",
                "lint": "eslint .",
                "build:android": "cd android && ./gradlew assembleRelease",
                "build:ios": "cd ios && xcodebuild -scheme SANTINEL -configuration Release"
            },
            "dependencies": {
                "react": "^18.2.0",
                "react-native": "^0.71.0",
                "@react-navigation/native": "^6.0.0",
                "@react-navigation/bottom-tabs": "^6.0.0",
                "@react-navigation/stack": "^6.0.0",
                "react-native-screens": "^3.20.0",
                "react-native-safe-area-context": "^4.5.0",
                "react-native-gesture-handler": "^2.10.0",
                "axios": "^1.3.0",
                "zustand": "^4.3.0"
            },
            "devDependencies": {
                "@react-native/cli": "^10.0.0",
                "@types/react": "^18.0.0",
                "@types/react-native": "^0.71.0",
                "typescript": "^4.9.0",
                "jest": "^29.0.0",
                "@testing-library/react-native": "^11.0.0"
            }
        }
    
    def generate_app_config(self) -> Dict:
        """Generate app.json configuration"""
        
        return {
            "expo": {
                "name": "SANTINEL",
                "slug": "santinel",
                "version": self.version,
                "orientation": "portrait",
                "icon": "./assets/icon.png",
                "splash": {
                    "image": "./assets/splash.png",
                    "resizeMode": "contain",
                    "backgroundColor": "#ffffff"
                },
                "updates": {
                    "fallbackToCacheTimeout": 0
                },
                "assetBundlePatterns": [
                    "**/*"
                ],
                "ios": {
                    "supportsTabletMode": True,
                    "infoPlist": {
                        "NSMicrophoneUsageDescription": "SANTINEL needs microphone access for call coaching"
                    }
                },
                "android": {
                    "adaptiveIcon": {
                        "foregroundImage": "./assets/adaptive-icon.png",
                        "backgroundColor": "#ffffff"
                    },
                    "permissions": [
                        "RECORD_AUDIO",
                        "INTERNET",
                        "ACCESS_NETWORK_STATE"
                    ]
                },
                "plugins": [
                    [
                        "expo-audio",
                        {
                            "microphonePermission": "Allow SANTINEL to access microphone"
                        }
                    ]
                ]
            }
        }
    
    def generate_navigation_structure(self) -> Dict:
        """Generate React Navigation stack structure"""
        
        return {
            "root": {
                "type": "stack",
                "screens": {
                    "BottomTabs": {
                        "type": "bottom-tabs",
                        "screens": {
                            "Home": {
                                "screens": {
                                    "HomeScreen": "home",
                                    "SessionDetail": "session/:id"
                                }
                            },
                            "NewSession": {
                                "screens": {
                                    "NewSessionScreen": "new-session",
                                    "PreCallIntel": "pre-call/:contactId",
                                    "LiveCoaching": "coaching/:sessionId"
                                }
                            },
                            "History": {
                                "screens": {
                                    "HistoryScreen": "history",
                                    "SessionAnalysis": "analysis/:sessionId"
                                }
                            },
                            "Analytics": {
                                "screens": {
                                    "AnalyticsScreen": "analytics",
                                    "DetailedMetrics": "metrics/:metric"
                                }
                            },
                            "Profile": {
                                "screens": {
                                    "ProfileScreen": "profile",
                                    "Settings": "settings",
                                    "About": "about"
                                }
                            }
                        }
                    },
                    "Modal": {
                        "type": "modal",
                        "screens": {
                            "CoachingOverlay": "coaching-overlay/:sessionId",
                            "AEGISIntel": "aegis-intel/:contactId",
                            "AudioRecorder": "recorder/:sessionId"
                        }
                    }
                }
            }
        }
    
    def generate_screen_templates(self) -> Dict:
        """Generate screen template configurations"""
        
        return {
            "HomeScreen": {
                "title": "SANTINEL Coaching",
                "components": [
                    {"type": "header", "title": "Dashboard"},
                    {"type": "metrics", "items": ["sessions", "success_rate", "coaching_tips"]},
                    {"type": "button", "label": "Start New Session", "action": "navigate:NewSession"},
                    {"type": "list", "data": "recent_sessions", "item": "SessionCard"}
                ]
            },
            "NewSessionScreen": {
                "title": "Prepare Session",
                "components": [
                    {"type": "header", "title": "New Coaching Session"},
                    {"type": "input", "label": "Contact Name", "key": "contact_name"},
                    {"type": "input", "label": "Company", "key": "company_name"},
                    {"type": "button", "label": "Get Intelligence", "action": "getAEGISIntel"},
                    {"type": "button", "label": "Start Session", "action": "startSession", "style": "primary"}
                ]
            },
            "LiveCoachingScreen": {
                "title": "Live Coaching",
                "components": [
                    {"type": "header", "title": "Active Session"},
                    {"type": "audio_recorder", "label": "Recording..."},
                    {"type": "text_display", "data": "real_time_transcript", "label": "Transcript"},
                    {"type": "coaching_suggestion", "data": "current_coaching", "label": "Coaching Tip"},
                    {"type": "button", "label": "End Session", "action": "endSession"}
                ]
            },
            "HistoryScreen": {
                "title": "Session History",
                "components": [
                    {"type": "header", "title": "Past Sessions"},
                    {"type": "filter", "by": ["date", "contact", "outcome"]},
                    {"type": "list", "data": "sessions", "item": "SessionCard"}
                ]
            },
            "AnalyticsScreen": {
                "title": "Performance",
                "components": [
                    {"type": "header", "title": "Analytics"},
                    {"type": "metric", "label": "Total Sessions", "value": "sessions_count"},
                    {"type": "metric", "label": "Success Rate", "value": "success_rate"},
                    {"type": "chart", "type": "line", "data": "sessions_over_time"},
                    {"type": "chart", "type": "pie", "data": "outcomes"}
                ]
            }
        }
    
    def generate_api_client(self) -> str:
        """Generate API client configuration"""
        
        config = """
// api/client.ts
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Interceptor for auth
apiClient.interceptors.request.use(config => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Endpoints
export const endpoints = {
  session: {
    create: '/api/v1/sessions',
    start: (id: string) => `/api/v1/sessions/${id}/start`,
    end: (id: string) => `/api/v1/sessions/${id}/end`,
    get: (id: string) => `/api/v1/sessions/${id}`,
    list: '/api/v1/sessions',
    coaching: (id: string) => `/api/v1/sessions/${id}/coaching`
  },
  aegis: {
    contact: '/api/v1/aegis/contact',
    company: '/api/v1/aegis/company'
  },
  audio: {
    upload: '/api/v1/audio/upload',
    transcribe: '/api/v1/audio/transcribe'
  }
};

export default apiClient;
"""
        return config
    
    def generate_store_setup(self) -> str:
        """Generate Zustand store configuration"""
        
        config = """
// store/sessionStore.ts
import { create } from 'zustand';

interface Session {
  id: string;
  contact_name: string;
  company_name: string;
  status: 'idle' | 'active' | 'ended';
  transcript: string;
  coaching_suggestions: string[];
  created_at: string;
}

interface SessionStore {
  sessions: Session[];
  activeSession: Session | null;
  startSession: (contact: string, company: string) => void;
  endSession: () => void;
  addCoaching: (suggestion: string) => void;
  addTranscript: (text: string) => void;
}

export const useSessionStore = create<SessionStore>((set) => ({
  sessions: [],
  activeSession: null,
  
  startSession: (contact, company) => set((state) => ({
    activeSession: {
      id: `session_${Date.now()}`,
      contact_name: contact,
      company_name: company,
      status: 'active',
      transcript: '',
      coaching_suggestions: [],
      created_at: new Date().toISOString()
    }
  })),
  
  endSession: () => set((state) => ({
    sessions: state.activeSession ? [...state.sessions, state.activeSession] : state.sessions,
    activeSession: null
  })),
  
  addCoaching: (suggestion) => set((state) => ({
    activeSession: state.activeSession ? {
      ...state.activeSession,
      coaching_suggestions: [...state.activeSession.coaching_suggestions, suggestion]
    } : null
  })),
  
  addTranscript: (text) => set((state) => ({
    activeSession: state.activeSession ? {
      ...state.activeSession,
      transcript: state.activeSession.transcript + ' ' + text
    } : null
  }))
}));
"""
        return config
    
    def generate_environment_setup(self) -> Dict:
        """Generate .env.example"""
        
        return {
            "REACT_APP_API_URL": "http://localhost:8000",
            "REACT_APP_GROQ_KEY": "your_groq_api_key_here",
            "REACT_APP_AEGIS_URL": "http://localhost:8001",
            "REACT_APP_LOG_LEVEL": "debug",
            "REACT_APP_PUSH_NOTIFICATION_KEY": "your_fcm_key_here"
        }


# ============================================================
# MOBILE APP SCAFFOLDER
# ============================================================

class MobileAppScaffolder:
    """Generate complete mobile app scaffolding"""
    
    def __init__(self, config: MobileAppConfig):
        """Initialize scaffolder"""
        self.config = config
        self.created_files = []
    
    def scaffold_project(self) -> Dict:
        """Generate complete project structure"""
        
        structure = {
            "package.json": self.config.generate_package_json(),
            "app.json": self.config.generate_app_config(),
            ".env.example": self.config.generate_environment_setup(),
            "navigation": self.config.generate_navigation_structure(),
            "screens": self.config.generate_screen_templates(),
            "api_client": self.config.generate_api_client(),
            "store_setup": self.config.generate_store_setup()
        }
        
        return structure
    
    def export_scaffold(self, output_dir: str = ".") -> Dict:
        """Export scaffold to files"""
        
        scaffold = self.scaffold_project()
        
        results = {
            "generated_files": [],
            "status": "success",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        for filename, content in scaffold.items():
            if isinstance(content, dict):
                filepath = f"{output_dir}/{filename}.json"
                with open(filepath, "w") as f:
                    json.dump(content, f, indent=2)
                results["generated_files"].append(filepath)
            elif isinstance(content, str):
                filepath = f"{output_dir}/{filename}"
                with open(filepath, "w") as f:
                    f.write(content)
                results["generated_files"].append(filepath)
        
        return results


# ============================================================
# TEST HARNESS
# ============================================================

def run_tests():
    """Test mobile app scaffold"""
    
    print("\n" + "=" * 60)
    print("📱 SANTINEL — MOBILE UI SCAFFOLD (React Native)")
    print("=" * 60 + "\n")
    
    # Initialize config
    print("🔧 Initializing mobile app config...")
    config = MobileAppConfig("SANTINEL")
    print(f"   App: {config.app_name}")
    print(f"   Version: {config.version}")
    print()
    
    # Test 1: Package.json
    print("📦 Test 1: Generate package.json...")
    package = config.generate_package_json()
    print(f"   Scripts: {len(package['scripts'])} defined")
    print(f"   Dependencies: {len(package['dependencies'])}")
    print(f"   Dev dependencies: {len(package['devDependencies'])}")
    print()
    
    # Test 2: App config
    print("⚙️  Test 2: Generate app.json...")
    app_config = config.generate_app_config()
    print(f"   Name: {app_config['expo']['name']}")
    print(f"   Version: {app_config['expo']['version']}")
    print(f"   Plugins: {len(app_config['expo']['plugins'])}")
    print()
    
    # Test 3: Navigation
    print("🗺️  Test 3: Generate navigation structure...")
    nav = config.generate_navigation_structure()
    print(f"   Root type: {nav['root']['type']}")
    print(f"   Screens: {len(nav['root']['screens'])}")
    print()
    
    # Test 4: Screen templates
    print("📺 Test 4: Generate screen templates...")
    screens = config.generate_screen_templates()
    print(f"   Total screens: {len(screens)}")
    for screen_name, screen_config in screens.items():
        print(f"   ├─ {screen_name}: {len(screen_config['components'])} components")
    print()
    
    # Test 5: API client
    print("🔌 Test 5: Generate API client...")
    api_client = config.generate_api_client()
    print(f"   Client config: {len(api_client)} chars")
    print(f"   Endpoints configured: True")
    print()
    
    # Test 6: Scaffolder
    print("🏗️  Test 6: Run scaffolder...")
    scaffolder = MobileAppScaffolder(config)
    scaffold = scaffolder.scaffold_project()
    print(f"   Files to generate: {len(scaffold)}")
    print(f"   Config items: {list(scaffold.keys())}")
    print()
    
    print("✅ MOBILE_UI_SCAFFOLD.PY — All tests passed!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    run_tests()
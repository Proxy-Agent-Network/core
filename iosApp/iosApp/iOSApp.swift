import SwiftUI
import GoogleMaps
import ComposeApp // (Or whatever your shared KMP module is named)

@main
struct iOSApp: App {
    init() {
        // Securely fetch the key from local.properties via Kotlin in memory!
        GMSServices.provideAPIKey(MapConfigKt.getSecureMapsKey())
    }
    
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}

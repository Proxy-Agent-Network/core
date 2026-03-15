import SwiftUI
import GoogleMaps // We will add this

@main
struct iOSApp: App {
    init() {
        GMSServices.provideAPIKey("YOUR_GOOGLE_MAPS_API_KEY")
    }

    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}
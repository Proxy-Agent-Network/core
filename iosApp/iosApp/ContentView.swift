import SwiftUI
import ComposeApp
import GoogleMaps

struct ContentView: View {
    var body: some View {
        ComposeView()
            .ignoresSafeArea(.keyboard)
    }
}

struct ComposeView: UIViewControllerRepresentable {
    func makeUIViewController(context: Context) -> UIViewController {
        
        let camera = GMSCameraPosition.camera(withLatitude: 0, longitude: 0, zoom: 14.2)
        let mapView = GMSMapView.map(withFrame: .zero, camera: camera)
        
        MapConfigKt.iosMapViewFactory = {
            return mapView
        }
        
        // --- THE FIX: We explicitly declare the types (NSNumber, String, Array) so Swift doesn't panic! ---
        MapConfigKt.iosMapUpdater = { (lat: NSNumber, lon: NSNumber, styleJson: String?, routeList: [Any]) in
            
            let target = CLLocationCoordinate2D(latitude: lat.doubleValue, longitude: lon.doubleValue)
            mapView.animate(toLocation: target)
            
            if let json = styleJson {
                do { mapView.mapStyle = try GMSMapStyle(jsonString: json) }
                catch { print("Failed to load map style") }
            }
            
            // 1. Clear any old routes/markers off the map
            mapView.clear()
            
            // 2. Safely cast the KMP Array into Swift NSNumbers and draw the Polyline
            if let route = routeList as? [KotlinPair<NSNumber, NSNumber>] {
                if !route.isEmpty {
                    let path = GMSMutablePath()
                    for point in route {
                        if let pLat = point.first?.doubleValue, let pLon = point.second?.doubleValue {
                            path.add(CLLocationCoordinate2D(latitude: pLat, longitude: pLon))
                        }
                    }
                    
                    // Draw the line
                    let polyline = GMSPolyline(path: path)
                    polyline.strokeColor = UIColor(red: 0.0, green: 188.0/255.0, blue: 212.0/255.0, alpha: 1.0) // PAN Tactical Cyan
                    polyline.strokeWidth = 6.0
                    polyline.map = mapView
                    
                    // Optional: Drop a red marker at the very end of the route so you see the target!
                    if let lastPoint = route.last, let tLat = lastPoint.first?.doubleValue, let tLon = lastPoint.second?.doubleValue {
                         let marker = GMSMarker(position: CLLocationCoordinate2D(latitude: tLat, longitude: tLon))
                         marker.map = mapView
                    }
                }
            }
        }
        
        return MainViewControllerKt.MainViewController()
    }

    func updateUIViewController(_ uiViewController: UIViewController, context: Context) {}
}

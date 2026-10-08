# SPORTS TALENT AI — Mobile App

Premium mobile application module for the **AI-Powered Mobile Platform for Democratising Sports Talent Assessment**.

## Arya's module
- Mobile application UI/UX
- Authentication UI
- Athlete dashboard
- Test selection
- Sit-up assessment flow
- Vertical-jump mobile flow
- Camera/video recording
- Offline local storage
- Mock AI/API integration
- History and performance screens

## Important boundaries
This project intentionally does **not** implement:
- MediaPipe or real computer vision
- The real backend/database
- Real benchmarking/percentiles
- The Admin/SAI dashboard

Those are integration boundaries for the other team members.

## Run locally

1. Install Node.js 20.19+ or newer.
2. Open this folder in VS Code.
3. Run:
   ```bash
   npm install
   ```
4. Start Expo:
   ```bash
   npx expo start
   ```
5. For a physical phone, install Expo Go and scan the QR code.

For the camera/recording flow, use a physical device or a development build. Camera functionality is not available in a normal desktop browser.

## Notes
The app uses a mock service for assessment results. Sit-up currently returns 32 repetitions and vertical jump returns 46 cm. Replace the mock service with the backend contract later without changing the presentation layer.

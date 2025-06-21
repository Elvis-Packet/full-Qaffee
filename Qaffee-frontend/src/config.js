// Configuration for external services
export const config = {
    // Google Maps configuration
    googleMaps: {
        apiKey: 'AIzaSyBNLrJhOMz6idD05pzfn5lhA-TAw-mAZCU', // Replace with your actual API key
        options: {
            componentRestrictions: { country: 'ke' },
            fields: ['formatted_address', 'geometry']
        }
    },
    
    // Add other configuration settings here
}; 
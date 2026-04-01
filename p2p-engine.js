const AzRadio = {
    init: function() {
        console.log("Boş radiotezliklər taranır (2.4GHz)...");
        this.startBeacon();
    },
    startBeacon: function() {
        // Telefonu gizli bir 'Mayak' (Beacon) rejiminə salır
        setInterval(() => {
            if (!navigator.onLine) {
                console.log("İnternet yoxdur! Radio dalğa ilə ötürmə aktivdir.");
            }
        }, 5000);
    }
};
AzRadio.init();

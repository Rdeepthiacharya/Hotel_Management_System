document.addEventListener("DOMContentLoaded", () => {
    const arrival = document.getElementById("arrival_date");
    const departure = document.getElementById("departure_date");

    // set today's date as min
    const today = new Date().toISOString().split("T")[0];
    arrival.min = today;
    departure.min = today;

    // update departure min when arrival changes
    arrival.addEventListener("change", function () {
        departure.min = this.value;
        if (departure.value < this.value) {
            departure.value = this.value;
        }
        // auto-set to next day
        const nextDay = new Date(this.value);
        nextDay.setDate(nextDay.getDate() + 1);
        departure.value = nextDay.toISOString().split("T")[0];
    });
});

/* Manages the playback of the images for a particular station
 */
class ForecastPlayer {

    constructor(station, image_id) {
        this.station = station;
        this.image_elem = document.getElementById(image_id);
    }

    /* Returns the latest forecast times
     */ 
    async getLatestForecastTimes() {
        const response = await fetch(`/latest/${this.station}`);
        let times = "Error";
        if (response.ok) {
            times = await response.json();
        }
        this.forecast_times = times[this.station];
    }

    /* Gets the forecast image for the given forecast time
     */
    async getForecast(fc_time) {
        const response = await fetch(`/forecast/${this.station}/${fc_time}`);
        let image;
        if (response.ok) {
            image = await response.blob();
        }
        return image;
    }

    /* Fetches all of the forecast times and images and caches them
     */
    async fetchForecasts() {
        return this.getLatestForecastTimes().then(
            async () => {
                let forecasts = {};
                for (let fc_time of this.forecast_times) {
                    let image = await this.getForecast(fc_time);
                    forecasts[fc_time] = image;
                }
                this.forecasts = forecasts; // Really not sure why this can't be defined directly
        });
    }

    /* Plays all of the forecasts in a loop
     * 
     * \param image_id The id for the image element
     */
    playForecast() {

        /* Generator to continuously loop over the forecast images
         * I kinda doubt this is necessary, we can probably just do the loop without a generator, but I'd need to play
         * with it to know for sure.
         */ 
        async function* forecastLoop(forecast_times, forecasts) {
            let i = 0;
            while (true) {
                let t = forecast_times[i];
                yield forecasts[t];
                i = (i + 1) % forecast_times.length;
                await new Promise(resolve => setTimeout(resolve, 1000));
            }
        }

        // Actually performs the loop
        (async () => {
            let loop = forecastLoop(this.forecast_times, this.forecasts);
            for await (let image of loop) {
                this.image_elem.src = window.URL.createObjectURL(image)
            }
        })();
    }

}

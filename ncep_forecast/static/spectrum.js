
const tEXt = "tEXt".split("").map(c => c.charCodeAt(0));

function findTEXt(buf) {
    let itext = 0;
    let u8v = new Uint8Array(buf);
    for (let i_n of u8v.entries()) {
        let i = i_n[0];
        let n = i_n[1];
        if (n == tEXt[itext]) {
            itext++;
            if (itext == tEXt.length)
                return i + 1;
        }
        else {
            itext = 0;
        }
    }
    return undefined;
}

async function getHsFromImage(image) {
    let reader = new Promise((resolve, reject) => {
        var fr = new FileReader();  
        fr.onload = () => resolve(fr.result);
        fr.readAsArrayBuffer(image);
    });

    let buf =  await reader;
    let itext = findTEXt(buf);
    let dv = new DataView(buf, itext);
    return dv.getFloat64(0, true);
}

/* Manages the playback of the images for a particular station
 */
class ForecastPlayer {

    constructor(station) {
        this.station = station;
        this.forecasts = {};
        this.forecast_times = undefined;
        this.play = false;
    }

    /* Returns the latest forecast times
     */ 
    async getLatestForecastTimes() {
        if (this.forecast_times === undefined) {
            const response = await fetch(`/latest/${this.station}`);
            let times = "Error";
            if (response.ok) {
                times = await response.json();
            }
            this.forecast_times = times[this.station];
        }
        return this.forecast_times;
    }

    /* Gets the forecast image for the given forecast time
     */
    async getForecast(fc_time) {
        if (!(fc_time in this.forecasts)) {
            const response = await fetch(`/forecast/${this.station}/${fc_time}`);
            
            if (response.ok) {
                this.forecasts[fc_time] = await response.blob();
            }
        }
        return this.forecasts[fc_time];
    }

    /* Fetches all of the forecast times and images and caches them
     */
    async fetchForecasts() {
        this.getLatestForecastTimes().then(
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
    async playForecast(image_id, date_id, hs_id) {
        let image_elem = document.getElementById(image_id);
        let date_elem = document.getElementById(date_id);
        let hs_elem = document.getElementById(hs_id);
        this.play = true;
        let i = 0;
        let fctimes = await this.getLatestForecastTimes();
        while (this.play) {
            let fct = fctimes[i];  // Get forecast time

            let image = await this.getForecast(fct);  // Get the image

            let hs = await getHsFromImage(image);  // Get significant wave height

            // Create date from forecast time
            let y = parseInt(fct.slice(0, 4));
            let m = parseInt(fct.slice(4, 6)) - 1;
            let d = parseInt(fct.slice(6, 8));
            let h = parseInt(fct.slice(8));
            let date = new Date(y, m, d, h);

            // Write header
            date_elem.innerText = `${date.toDateString()} ${date.getHours()}`;
            hs_elem.innerText = `${hs.toFixed(2)}m`;
            image_elem.src = window.URL.createObjectURL(image);
            i = (i + 1) % fctimes.length;
            await new Promise(resolve => setTimeout(resolve, 100));
        }
    }

}

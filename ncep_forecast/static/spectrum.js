
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

    constructor(station, image_id, date_id, hs_id) {
        this.station = station;
        this.forecasts = {};
        this.hs = {};
        this.forecast_times = null;
        this.run = false;
        this.period = 100;
        this.fctime_index = 0;

        this.image_id = image_id;
        this.date_id = date_id;
        this.hs_id = hs_id;
        this.img_el = null;

        this.latest_forecast = null;
        this.newDataTimer = setInterval(() => this.checkForNewData(), 60000);
    }

    async init() {
        this.fctimes = await this.getLatestForecastTimes();
    }

    async fetchLatestForecastTimes() {
        const response = await fetch(`/forecast/times/${this.station}`);
        let times = "Error";
        if (response.ok) {
            times = await response.json();
        }
        this.forecast_times = times[this.station];
    }

    /* Returns the latest forecast times
     */ 
    async getLatestForecastTimes() {
        if (this.forecast_times === null) {
            await this.fetchLatestForecastTimes();
            this.latest_forecast = await this.getLatestForecastRun();
        }
        return this.forecast_times;
    }

    async getLatestForecastRun() {
        let response = await fetch(`/latest/${this.station}`);
        if (response.ok) {
            let latest = await response.json();
            return latest[this.station];
        }
        return null;
    }

    async checkForNewData() {
        let latest = await this.getLatestForecastRun();
        if (this.latest_forecast != null && latest != this.latest_forecast) {
            window.location.reload();
        }
    }

    /* Gets the forecast image for the given forecast time
     */
    async getForecast(fc_time) {
        if (!(fc_time in this.forecasts)) {
            const response = await fetch(`/forecast/${this.station}/${fc_time}`);
            
            if (response.ok) {
                // Get the image and create a url
                let image = await response.blob();
                this.forecasts[fc_time] = window.URL.createObjectURL(image);

                let hs = await getHsFromImage(image);  // Get significant wave height
                this.hs[fc_time] = hs;
            }
        }
        return [this.forecasts[fc_time], this.hs[fc_time]];
    }

    faster() {
        if (this.period > 50)
            this.period -= 50;
    }

    slower() {
        if (this.period < 1000)
            this.period += 50;
    }

    stop() {
        this.run = false;
    }

    async next(stop=true) {
        if (stop) this.stop();
        this.fctime_index = (this.fctime_index + 1) % this.fctimes.length;
        await this.updateSpectrum(this.fctime_index);
    }

    async prev(stop=true) {
        if (stop) this.stop();
        this.fctime_index = (this.fctime_index - 1) % this.fctimes.length;
        await this.updateSpectrum(this.fctime_index);
    }

    async first(stop=true) {
        if (stop) this.stop();
        this.fctime_index = 0;
        await this.updateSpectrum(this.fctime_index);
    }

    async last(stop=true) {
        if (stop) this.stop();
        this.fctime_index = this.fctimes.length - 1;
        await this.updateSpectrum(this.fctime_index);
    }

    /* Plays all of the forecasts in a loop
     * 
     * \param image_id The id for the image element
     */
    async play() {
        if (this.run) {
            console.log("already playing");
            return;
        }
        this.run = true;
        while (this.run) {
            await this.next(false);
            await new Promise(resolve => setTimeout(resolve, this.period));
        }
    }

    async updateSpectrum(fct_i) {
        fct_i = Math.min(fct_i, this.fctimes.length - 1);
        fct_i = Math.max(fct_i, 0);

        let fct = this.fctimes[fct_i];
        let date_elem = document.getElementById(this.date_id);
        let hs_elem = document.getElementById(this.hs_id);

        let [img_url, hs] = await this.getForecast(fct);  // Get the image
        document.getElementById(this.image_id).src = img_url;

        // Create date from forecast time
        let y = parseInt(fct.slice(0, 4));
        let m = parseInt(fct.slice(4, 6)) - 1;
        let d = parseInt(fct.slice(6, 8));
        let h = parseInt(fct.slice(8));
        let date = new Date(y, m, d, h);

        // Write header
        date_elem.innerText = `${date.toDateString()} ${date.getHours()}:00`;
        hs_elem.innerText = `${hs.toFixed(2)}m`;
    }

    setUpSpecAnimation() {
        this.fakeScroll = document.createElement('div');
        this.fakeScroll.className = 'fake-scroll';
        document.body.appendChild(this.fakeScroll);

        let container = document.getElementById("spec-container");

        // Set `height` for the fake scroll element
        this.scroll_height = 10 * this.forecast_times.length;
        this.fakeScroll.style.height = (this.scroll_height + document.documentElement.clientHeight) + 'px';

        window.scroll(0, this.scroll_height - (10 * this.fctime_index));
    }

    tearDownSpecAnimation() {
        document.body.removeChild(this.fakeScroll);
    }

    handleEvent(event) {
        let target = event.target;

        switch (event.type) {
        case "click":
            if (target.tagName == "BUTTON" & target.closest("ul") == document.getElementById("control")) {
                eval(`this.${target.id}()`);
            }
            break;
        case "mouseover":
            this.mouse_on = target;
            if (target.id == "spectrum") {
                this.was_running = this.run;
                this.stop();

                this.setUpSpecAnimation();
                window.addEventListener("scroll", this);
            }
            break;
        case "mouseout":
            this.mouse_on = undefined;
            if (target.id == "spectrum") {
                this.tearDownSpecAnimation();
                window.removeEventListener("scroll", this);
                if (this.was_running) this.play();
            }
            break;
        case "scroll":
            if (this.mouse_on == document.getElementById("spectrum")) {
                this.fctime_index = Math.floor((this.scroll_height - window.scrollY) / 10);
                this.updateSpectrum(this.fctime_index);
                console.log(`height: ${this.scroll_height}, scrollY: ${window.scrollY}, index: ${this.fctime_index}`);
            }   
        }
    }

}

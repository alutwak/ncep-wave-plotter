
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
        this.hs = {};
        this.forecast_times = null;
        this.run = false;
        this.period = 100;
        this.fctime_index = 0;

        this.latest_forecast = null;
        this.newDataTimer = setInterval(() => this.checkForNewData(), 60000);

        this.mouse_on = null;
        this.shifted = false;
        this.fetching = false
    }

    async init(image_id, date_id, hs_id, container_id) {
        this.image = document.getElementById(image_id)
        this.image.ondragstart = () => { return false; }
        // this.image.ontouchstart = this.image.onclick;

        this.date = document.getElementById(date_id)
        this.hs = document.getElementById(hs_id)
        this.container = document.getElementById(container_id)

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

    async fetchForecasts() {
        if (!this.fetching) {
            this.fetching = true
            for (let i=0; i<this.fctimes.length; i++) {
                const fctime = this.fctimes[i]
                const response = await fetch(`/forecast/${this.station}/${fctime}`);
                if (response.ok) {
                    // Get the image and create a url
                    let image = await response.blob();
                    this.forecasts[fctime] = window.URL.createObjectURL(image);
                    this.hs[fctime] = await getHsFromImage(image);  // Get significant wave height
                }
            }
            this.fetching = false
        }
    }

    /* Gets the forecast image for the given forecast time
     */
    async getForecast(fc_time) {
        if (!(fc_time in this.forecasts)) {
            this.fetchForecasts()
            return null
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

    async next(stop=true, step=1) {
        if (stop) this.stop();
        this.fctime_index = (this.fctime_index + step) % this.fctimes.length;
        await this.updateSpectrum(this.fctime_index);
    }

    async prev(stop=true, step=1) {
        if (stop) this.stop();
        let next = this.fctime_index - step;
        // This modulo atrocity is due to the dumb way js does negative modulos
        this.fctime_index = ((next % this.fctimes.length) + this.fctimes.length) % this.fctimes.length;
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
     */
    async play() {
        if (this.run) {
            return;
        }
        this.run = true;
        while (this.run) {
            await this.next(false);
            await new Promise(resolve => setTimeout(resolve, this.period));
        }
    }

    toggle() {
        if (this.run)
            this.stop();
        else
            this.play();
    }

    async updateSpectrum(fct_i) {
        fct_i = Math.min(fct_i, this.fctimes.length - 1);
        fct_i = Math.max(fct_i, 0);

        const fct = this.fctimes[fct_i];

        // Try to get the image & move on if we can't
        const forecast = await this.getForecast(fct);
        if (!forecast) return

        const [img_url, hs] = forecast

        this.image.src = img_url;

        // Create date from forecast time
        const y = parseInt(fct.slice(0, 4));
        const m = parseInt(fct.slice(4, 6)) - 1;
        const d = parseInt(fct.slice(6, 8));
        const h = parseInt(fct.slice(8));
        const date = new Date(y, m, d, h);

        // Write header
        this.date.innerText = `${date.toDateString()} ${date.getHours()}:00`;
        this.hs.innerText = `${hs.toFixed(2)}m`;
    }

    setUpSpecAnimation() {
        this.fakeScroll = document.createElement('div');
        this.fakeScroll.className = 'fake-scroll';
        document.body.appendChild(this.fakeScroll);

        // let container = document.getElementById("spec-container");

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
        case "keydown":
            this.handleKeyDownEvent(event);
            break;
        case "keyup":
            this.handleKeyUpEvent(event);
            break;
        case "click":
            this.toggle()
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
            this.mouse_on = null;
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
            }
        }
    }

    handleKeyDownEvent(event) {
        let step;
        switch (event.code) {
        case "Space":
            this.toggle();
            break;
        case "ArrowRight":
            step = 1;  // Skip an hour by default
            if (this.shifted)  // Skip a day when shifted
                step = 24;
            this.next(false, step);
            break;
        case "ArrowLeft":
            step = 1;  // Back an hour by default
            if (this.shifted)  // Back a day when shifted
                step = 24;
            this.prev(false, step);
            break;
        case "ArrowUp":
            this.faster();
            break;
        case "ArrowDown":
            this.slower();
            break;
        case "ShiftLeft":
        case "ShiftRight":
            this.shifted = true;
            break;
        default:
            return;
        }
        event.preventDefault();
    }

    handleKeyUpEvent(event) {
        switch (event.code) {
        case "ShiftLeft":
        case "ShiftRight":
            this.shifted = false;
            break;
        default:
            return;
        }
        event.preventDefault();
    }

}

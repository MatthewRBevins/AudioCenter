// Spectrogram plugin
import WaveSurfer from 'https://unpkg.com/wavesurfer.js@beta'
import Spectrogram from 'https://unpkg.com/wavesurfer.js@beta/dist/plugins/spectrogram.js'
import RegionsPlugin from 'https://unpkg.com/wavesurfer.js@beta/dist/plugins/regions.js'

//TRACKDATA IS DEFINED IN HEAD 

var selectedRegions = []

class AudioTrack {
    constructor(fn, container, index) {
        // Create an instance of WaveSurfer
        this.ws = WaveSurfer.create({
            container: '#' + container,
            waveColor: 'rgb(200, 0, 200)',
            progressColor: 'rgb(100, 0, 100)',
            url: fn,
            sampleRate: 22050,
        })

        // Initialize the Spectrogram plugin
        this.ws.registerPlugin(
            Spectrogram.create({
                labels: true,
                height: 128,
            }),
        )

        this.wsRegions = this.ws.registerPlugin(RegionsPlugin.create())

        this.ws.on('decode', () => {
            // Regions
            this.wsRegions.addRegion({
                start: 4,
                end: 7,
                content: 'Selected',
                color: 'rgba(220, 255, 51, 0.3)',
            })
            selectedRegions[index] = [4, 7, this.wsRegions.regions[0].totalDuration]
            $('.selected').val(selectedRegions)

            const slider = document.querySelector('input[type="range"]')

            slider.addEventListener('input', (e) => {
                const minPxPerSec = e.target.valueAsNumber
                this.ws.zoom(minPxPerSec)
            })
        })

        this.wsRegions.on('region-updated', (region) => {
            console.log('Updated region', region)
            selectedRegions[index] = [region.start, region.end, region.totalDuration]
            $('.selected').val(selectedRegions)
        })
    }
}

let tracks = document.getElementsByClassName("track")
console.log(tracks)
for (let i = 0; i < tracks.length; i++) {
    trackData.push(new AudioTrack(tracks[i].getAttribute("fn"), "waveform" + i, i))
}




$('#deleteButton').on('click', () => {
    $('#totalWidth').val(totalWidth)
    $('#startPoint').val(startCut)
    $('#endPoint').val(endCut)
    $('#deleteForm').submit()
})

function effectForms() {
    $('#effectsTotalWidth').val(totalWidth);
    $('#effectsStartPoint').val(startCut);
    $('#effectsEndPoint').val(endCut);
    return true;
}

$('#file-open').on('change', () => {
    $('#file-open-form').submit()
})


<template>
    <v-container>
        <v-layout wrap>
            <v-flex xs4>
                <v-text-field label="Bot IP" v-model="botIp" />
                <v-btn :loading="loadingPicture" @click="start()">Start Recording</v-btn>
                <v-btn v-if="!stopped" @click="stop()">Stop</v-btn>
                <v-btn v-if="images.length > 0" @click="saveImages()">Download Images</v-btn>
            </v-flex>
            <v-flex xs8>
                <img :src="selectedImage || images[0] && images[0].withHeader" />
            </v-flex>
        </v-layout>
        <v-layout wrap>
            <v-flex xs1 v-for="i in images" :key="i">
                <img :src="i.withHeader" height="50px" width="50px" @click="selectedImage = i.withHeader"/>
            </v-flex>
        </v-layout>
    </v-container>
</template>

<script>
import base64Img from 'base64-img'
import uuid from 'uuid/v4'
import fs from 'fs'
import moment from 'moment'

function base64toBlob(base64Data, contentType) {
    contentType = contentType || '';
    var sliceSize = 1024;
    var byteCharacters = atob(base64Data);
    var bytesLength = byteCharacters.length;
    var slicesCount = Math.ceil(bytesLength / sliceSize);
    var byteArrays = new Array(slicesCount);

    for (var sliceIndex = 0; sliceIndex < slicesCount; ++sliceIndex) {
        var begin = sliceIndex * sliceSize;
        var end = Math.min(begin + sliceSize, bytesLength);

        var bytes = new Array(end - begin);
        for (var offset = begin, i = 0; offset < end; ++i, ++offset) {
            bytes[i] = byteCharacters[offset].charCodeAt(0);
        }
        byteArrays[sliceIndex] = new Uint8Array(bytes);
    }
    return new Blob(byteArrays, { type: contentType });
}

export default {
    data() {
        return {
            botIp: "10.10.0.7",
            loadingPicture: false,
            images: [],
            stopped: false,
            selectedImage: ""
        }
    },
    methods: {
        start() {
            this.stopped = false;
            this.takePictures();
        },
        stop() {
            this.stopped = true;
        },
        takePictures () {
            this.loadingPicture = true;
            Promise.race([
            fetch(`http://${this.botIp}/api/cameras/rgb?base64=true&fileName=asdf&width=500&height=500&displayOnScreen=true&overwriteExisting=false`, {
                method: 'GET'
            }),
            new Promise((_, reject) => setTimeout(() => reject(new Error('timeout')), 10000))
        ])
        .then(response => response.json())
        .then(jsonData => {
            console.log(jsonData);
            // the base64toBlob helper expects an encoding without the header
            // so we just store both so they can be easily displayed
            // and saved as well
            const withoutHeader = jsonData.result.base64;
            const withHeader = 'data:image/png;base64,' + jsonData.result.base64;
            this.images.push({withoutHeader, withHeader});
            this.loadingPicture = false;
            if (!this.stopped) {
                setTimeout(this.takePictures, 1000);
            }
        })
        },
        saveImages () {
            this.images.forEach((image, index) => {
                this.saveFile(image.withoutHeader, index + "-" + moment().format() + ".png");
            });
        },
        saveFile(data, filename) {
            var file = base64toBlob(data, "image/png");
            if (window.navigator.msSaveOrOpenBlob)
                // IE10+
                window.navigator.msSaveOrOpenBlob(file, filename);
            else {
                // Others
                var a = document.createElement("a"),
                url = URL.createObjectURL(file);
                a.href = url;
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                setTimeout(function() {
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
                }, 0);
            }
            },
    },

}
</script>